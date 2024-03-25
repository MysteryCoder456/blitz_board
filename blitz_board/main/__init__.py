from pathlib import Path
from time import time

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    session,
)
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import StringField, SubmitField
from wtforms.validators import Length

from ..game import Player, GameSession


class JoinGameForm(FlaskForm):
    username = StringField(label="Username", description="John Doe")
    game_id = StringField(
        label="Game Code",
        description="12345",
        validators=[Length(min=5, max=5)],
    )
    submit = SubmitField()

    def validate_username(self, username: StringField):
        # Ignore empty username field if user is logged in
        # It will be automatically filled in the backend
        if current_user.is_authenticated:  # type: ignore
            return

        if len(username.data) < 3:
            raise ValidationError(
                "Username must be at least 3 characters long."
            )

    def validate_game_id(self, game_id: StringField):
        if not game_id.data.isnumeric():
            raise ValidationError("Game Code must be a 5-digit number.")


templates = Path(__file__).parent / "templates"
main_bp = Blueprint("main", __name__, template_folder=templates)


@main_bp.route("/", methods=["GET", "POST"])
def home():
    form = JoinGameForm(request.form)

    if form.validate_on_submit():
        game_id = int(form.game_id.data)  # type: ignore
        user_id = None
        username: str = form.username.data  # type: ignore

        if current_user.is_authenticated:  # type: ignore
            user_id = current_user.id  # type: ignore
            username = current_user.username  # type: ignore

        if game := GameSession.get_from_redis(game_id):
            if len(game.players) >= game.player_limit:
                flash("This game is full!", "warning")
                return redirect(url_for("main.home"))

            player_id = int(time() * 1000)
            session["my_id"] = player_id
            session["game_id"] = game_id

            game.players[player_id] = Player(
                player_id=player_id,
                permanent_id=user_id,
                username=username,
            )
            game.save_to_redis()

            return redirect(url_for("game.play_game", game_id=game_id))

        else:
            flash("The requested game does not exist!", "warning")

    return render_template("home.html", form=form)
