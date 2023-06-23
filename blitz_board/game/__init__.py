from pathlib import Path
from dataclasses import dataclass, field
from random import randint
from time import time
from json import loads as parse_json, dumps as to_json

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
from simple_websocket.ws import Server
from wtforms.fields import BooleanField, SubmitField

from blitz_board import web_sock


@dataclass
class Player:
    permanent_id: int | None
    username: str
    ws: Server | None = field(default=None)


@dataclass
class GameSession:
    game_id: int
    private: bool
    host_id: int
    players: dict[int, Player] = field(default_factory=dict)


class CreateRoomForm(FlaskForm):
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


@web_sock.route("/ws", bp=game_bp)
def game_ws(ws: Server):
    initial_data = parse_json(ws.receive())  # type: ignore
    my_id = initial_data["player_id"]

    game_room: GameSession | None = games.get(initial_data["game_id"])

    if not game_room or initial_data["player_id"] not in game_room.players:
        # Information is invalid
        ws.close()
        return

    # Copy socket player socket to player roster
    game_room.players[my_id].ws = ws

    player_data = [
        {
            "player_id": player_id,
            "permanent_id": player.permanent_id,
            "username": player.username,
        }
        for player_id, player in game_room.players.items()
    ]
    ws.send(to_json(player_data))


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
        game_id=game_id,
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

        new_game = GameSession(
            game_id,
            form.private.data,
            current_user.id,  # type: ignore
        )
        games[game_id] = new_game

        player_id = int(time() * 1000)
        session["my_id"] = player_id

        new_game.host_id = player_id
        new_game.players[player_id] = Player(
            current_user.id, current_user.username  # type: ignore
        )

        return redirect(url_for("game.play_game", game_id=game_id))

    return render_template("create_game.html", form=form)
