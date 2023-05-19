from datetime import datetime, timedelta
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import Length

from .. import db
from .models import Maze

MAZE_CREATION_COOLDOWN = timedelta(hours=12)


class CreateMazeForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[Length(min=5, max=80)],
        description="What will your maze be called?",
    )
    submit = SubmitField(label="Create")

    def validate_title(self, submit: SubmitField):
        if not submit.data:
            return

        if not current_user:
            raise ValidationError(
                "You must be logged in to create a new maze!"
            )

        query = (
            db.select(Maze)
            .where(Maze.author == current_user)
            .order_by(Maze.date_created.desc())
        )
        recent_maze = db.session.scalar(query)
        now = datetime.now(tz=recent_maze.date_created.tzinfo)

        if (now - recent_maze.date_created) < MAZE_CREATION_COOLDOWN:
            raise ValidationError(
                "You have created a maze just recently. "
                "Please try again later..."
            )


templates = Path(__file__).parent / "templates"
main_bp = Blueprint("main", __name__, template_folder=templates)


@main_bp.get("/")
def home():
    query = db.select(Maze).order_by(Maze.date_created.desc())
    page = db.paginate(query, per_page=20, error_out=False)

    return render_template("home.html", page=page)


@main_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_maze():
    form = CreateMazeForm(request.form)

    if form.validate_on_submit():
        new_maze = Maze()
        new_maze.author = current_user
        new_maze.title = form.title.data
        new_maze.maze_data = {}

        db.session.add(new_maze)
        db.session.commit()

        flash(
            f'"{form.title.data}" was created! Check it out in "My Account".',
            "success",
        )
        return redirect(url_for("main.home"))

    return render_template("create_maze.html", form=form)


@main_bp.get("/play/<int:maze_id>")
def play_maze(maze_id: int):
    # TODO: Implement gameplay
    maze = db.get_or_404(Maze, maze_id)
    return render_template("play_maze.html", maze=maze)


@main_bp.route("/editor/<int:maze_id>", methods=["GET", "POST"])
@login_required
def maze_editor(maze_id: int):
    query = db.select(Maze).where(
        Maze.id == maze_id and Maze.author == current_user
    )
    maze = db.first_or_404(query)

    return render_template(
        "edit_maze.html",
        maze=maze,
        p5_library=url_for("static", filename="p5.min.js"),
        editor_script=url_for("static", filename="editor.js"),
    )
