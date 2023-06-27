from pathlib import Path
from dataclasses import dataclass, field
from random import randint, choices
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
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from flask_socketio import emit, join_room
from wtforms.fields import BooleanField, IntegerField, SubmitField
from wtforms.validators import NumberRange
from english_words import get_english_words_set

from blitz_board import socketio


def generate_random_sentence(word_count: int) -> str:
    """
    Generates a sentence with completely random words that make no sense.

    @param word_count: How many words the sentence must have.
    @returns: The random sentence generated.
    """

    word_set = get_english_words_set(["gcide"], lower=True)
    words = choices(list(word_set), k=word_count)
    return " ".join(words)


@dataclass
class Player:
    permanent_id: int | None
    username: str
    session_id: str | None = field(default=None)


@dataclass
class GameSession:
    game_id: int
    private: bool
    host_id: int
    test_sentence: str
    players: dict[int, Player] = field(default_factory=dict)
    started: bool = field(default=False)


class CreateRoomForm(FlaskForm):
    word_count = IntegerField(
        label="Word Count",
        validators=[NumberRange(min=5)],
        default=15,
    )
    private = BooleanField(label="Private Game?")
    submit = SubmitField(label="Create")


templates = Path(__file__).parent / "templates"
game_bp = Blueprint(
    "game",
    __name__,
    url_prefix="/game",
    template_folder=templates,
)
games: dict[int, GameSession] = {}


@socketio.on("connect")
def socket_connect(auth: dict):
    player_id = auth["player_id"]
    game_id = auth["game_id"]
    game_room: GameSession | None = games.get(game_id)

    if (
        not game_room
        or player_id not in game_room.players
        or game_room.started
    ):
        return False

    player = game_room.players[player_id]
    player.session_id = request.sid  # type: ignore

    # Notify existing players about new player
    emit(
        "player join",
        {
            "player_id": player_id,
            "permanent_id": player.permanent_id,
            "username": player.username,
        },
        to=game_id,
    )

    # Notify new player about existing players
    join_room(game_id)
    player_list = [
        {
            "player_id": player_id,
            "permanent_id": player.permanent_id,
            "username": player.username,
        }
        for player_id, player in game_room.players.items()
    ]
    emit("player list", player_list)


@socketio.on("disconnect")
def socket_disconnect():
    player_room = session["game_id"]
    player_id: int | None = None

    for p_id, p in games[player_room].players.items():
        if p.session_id == request.sid:  # type: ignore
            player_id = p_id

    if player_id:
        del games[player_room].players[player_id]
        emit("player leave", player_id, to=player_room)


@game_bp.route("/joinrandom")
def join_random():
    # TODO: Do this
    return redirect(url_for("main.home"))


@game_bp.route("/play/<int:game_id>")
def play_game(game_id: int):
    game_room: GameSession | None = games.get(game_id)
    player_id: int | None = session.get("my_id")

    if not game_room:
        flash("The requested game was not found!", "error")
        return redirect(url_for("main.home"))

    if player_id not in game_room.players:
        flash("Unable to join this game!", "error")
        return redirect(url_for("main.home"))

    return render_template(
        "play_game.html",
        player_id=player_id,
        game=game_room,
        socket_io=url_for("static", filename="js/socket.io.js"),
        play_script=url_for("static", filename="js/play.js"),
        default_pfp=url_for("static", filename="images/default-pfp.jpg"),
    )


@game_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_game():
    form = CreateRoomForm(request.form)

    if form.validate_on_submit():
        game_id = 0

        # 100 attempts to get a unique game ID
        for _ in range(100):
            game_id = randint(10000, 99999)

            if game_id not in games:
                break

        else:
            flash(
                "Something went wrong while creating your game, please try again!",
                "error",
            )
            return redirect(url_for("game.create_game"))

        player_id = int(time() * 1000)
        session["my_id"] = player_id
        session["game_id"] = game_id

        new_game = GameSession(
            game_id=game_id,
            private=form.private.data,
            host_id=player_id,
            test_sentence=generate_random_sentence(form.word_count.data),
        )
        games[game_id] = new_game

        new_game.host_id = player_id
        new_game.players[player_id] = Player(
            permanent_id=current_user.id,  # type: ignore
            username=current_user.username,  # type: ignore
        )

        return redirect(url_for("game.play_game", game_id=game_id))

    return render_template("create_game.html", form=form)
