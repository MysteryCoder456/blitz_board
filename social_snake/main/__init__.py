from datetime import timedelta
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import Length

from .. import db, app
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

        with app.app_context():
            query = db.select(Maze).where(
                Maze.author == current_user
                and (request.date - Maze.date_created) < MAZE_CREATION_COOLDOWN
            )
            recent_maze = db.session.scalar(query)

            if recent_maze:
                raise ValidationError(
                    "You have created a maze just recently. "
                    "Please try again later..."
                )


templates = Path(__file__).parent / "templates"
main_bp = Blueprint("main", __name__, template_folder=templates)


@main_bp.get("/")
def home():
    return render_template("home.html")


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
