import csv
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from random import randint, choices, choice
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

from blitz_board import socketio, db
from .models import SessionStats
from ..auth.models import User

START_COUNTDOWN: int = 5
WORDS_PATH = Path(__file__).parents[1] / "NGSL_1.2_stats.csv"

with open(WORDS_PATH, "r") as f:
    reader = csv.reader(f)
    WORDS: list[str] = [rec[0].lower() for rec in reader]


def generate_random_sentence(word_count: int) -> str:
    """
    Generates a sentence with completely random words that make no sense.

    @param word_count: How many words the sentence must have.
    @returns: The random sentence generated.
    """

    words = choices(WORDS, k=word_count)
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
    player_limit: int
    players: dict[int, Player] = field(default_factory=dict)
    started: bool = field(default=False)
    started_at: datetime | None = field(default=None)

    def start(self, *, seconds_from_now: int = 0):
        if not self.started:
            self.started = True
            self.started_at = datetime.now() + timedelta(
                seconds=seconds_from_now
            )


class CreateRoomForm(FlaskForm):
    word_count = IntegerField(
        label="Word Count",
        validators=[NumberRange(min=5)],
        default=15,
    )
    player_limit = IntegerField(
        label="Player Limit",
        validators=[NumberRange(min=1, max=5)],
        default=5,
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


@socketio.on("connect", namespace="/game")
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

    avatar = (
        url_for("site_media", media_path=current_user.avatar)  # type: ignore
        if current_user.is_authenticated and current_user.avatar  # type: ignore
        else None
    )

    # Add new user to the room
    join_room(game_id)

    # Notify existing players about new player
    emit(
        "player join",
        {
            "player_id": player_id,
            "permanent_id": player.permanent_id,
            "username": player.username,
            "avatar": avatar,
        },
        to=game_id,
    )

    # Notify new player about existing players
    player_list = []

    for p_id, p in game_room.players.items():
        if p_id == player_id:
            continue

        avatar = None

        if p.permanent_id:
            user = db.session.get(User, p.permanent_id)
            avatar = (
                url_for("site_media", media_path=user.avatar)  # type: ignore
                if user.avatar  # type: ignore
                else None
            )

        player_list.append(
            {
                "player_id": p_id,
                "permanent_id": p.permanent_id,
                "username": p.username,
                "avatar": avatar,
            }
        )
    emit("player list", player_list)


@socketio.on("disconnect", namespace="/game")
def socket_disconnect():
    game_id = session["game_id"]
    player_id: int | None = None
    game_room = games[game_id]

    for p_id, p in game_room.players.items():
        if p.session_id == request.sid:  # type: ignore
            player_id = p_id
            break
    else:
        return

    del game_room.players[player_id]
    emit("player leave", player_id, to=game_id)

    # Delete game if all the players have left
    if not game_room.players:
        del games[game_id]


@socketio.on("test start", namespace="/game")
def test_start():
    player_room = session["game_id"]
    game_room = games[player_room]

    if game_room.started:
        return

    player_id: int | None = None

    for p_id, p in games[player_room].players.items():
        if p.session_id == request.sid:  # type: ignore
            player_id = p_id
            break
    else:
        return

    if game_room.host_id == player_id:
        game_room.start(seconds_from_now=START_COUNTDOWN)
        emit(
            "test start",
            {
                "test_sentence": game_room.test_sentence,
                "starting_in": START_COUNTDOWN,
            },
            to=game_room.game_id,
        )


@socketio.on("test progress", namespace="/game")
def test_progress(progress: float):
    player_room = session["game_id"]
    game_room = games[player_room]

    if not game_room.started:
        return

    player_id: int | None = None

    for p_id, p in games[player_room].players.items():
        if p.session_id == request.sid:  # type: ignore
            player_id = p_id
            break
    else:
        return

    emit(
        "test progress",
        {"player_id": player_id, "progress": progress},
        to=game_room.game_id,
    )


@socketio.on("test complete", namespace="/game")
def test_complete(typed_sentence: str):
    now = datetime.now()
    player_room = session["game_id"]
    game_room = games[player_room]

    if not game_room.started:
        return

    time_taken = now - game_room.started_at  # type: ignore
    test_char_count = len(game_room.test_sentence)
    test_word_count = game_room.test_sentence.count(" ") + 1
    correct_char_count = test_char_count

    if typed_sentence != game_room.test_sentence:
        for typed_char, test_char in zip(
            typed_sentence, game_room.test_sentence
        ):
            if typed_char != test_char:
                correct_char_count -= 1

    accuracy = correct_char_count / test_char_count
    correct_word_count = correct_char_count / 5
    typing_speed = (
        correct_word_count / time_taken.total_seconds() * 60
    )  # in WPM

    player_id: int | None = None
    player: Player | None = None

    for p_id, p in game_room.players.items():
        if p.session_id == request.sid:  # type: ignore
            player_id = p_id
            player = p
            break
    else:
        return

    emit(
        "test complete",
        {
            "player_id": player_id,
            "speed": int(typing_speed),
            "accuracy": int(accuracy * 100),
        },
        to=game_room.game_id,
    )

    # Update user statistics
    if user_id := player.permanent_id:
        stats = SessionStats(
            game_id=game_room.game_id,
            user_id=user_id,
            speed=typing_speed,
            accuracy=accuracy,
            word_count=test_word_count,
        )
        db.session.add(stats)
        db.session.commit()


@game_bp.route("/joinrandom")
@login_required
def join_random():
    public_games = [g for g in games.values() if not (g.private or g.started)]

    if not public_games:
        flash(
            "There are currently no public games available to join.", "warning"
        )
        return redirect(url_for("main.home"))

    game = choice(public_games)
    user_id = current_user.id  # type: ignore
    username = current_user.username  # type: ignore

    if len(game.players) >= game.player_limit:
        flash("This game is full!", "warning")
        return redirect(url_for("main.home"))

    player_id = int(time() * 1000)
    session["my_id"] = player_id
    session["game_id"] = game.game_id

    game.players[player_id] = Player(
        permanent_id=user_id,
        username=username,
    )

    return redirect(url_for("game.play_game", game_id=game.game_id))


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
        enumerate=enumerate,
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
            test_sentence=generate_random_sentence(
                form.word_count.data,  # type: ignore
            ),
            player_limit=form.player_limit.data,
        )
        games[game_id] = new_game

        new_game.host_id = player_id
        new_game.players[player_id] = Player(
            permanent_id=current_user.id,  # type: ignore
            username=current_user.username,  # type: ignore
        )

        return redirect(url_for("game.play_game", game_id=game_id))

    return render_template("create_game.html", form=form)
