from pathlib import Path
from flask import Blueprint, redirect, render_template, url_for

templates = Path(__file__).parent / "templates"
game_bp = Blueprint(
    "game",
    __name__,
    url_prefix="/game",
    template_folder=templates,
)


@game_bp.route("/joinrandom")
def join_random():
    # TODO: Do this
    return redirect(url_for("main.home"))


@game_bp.route("/join/<game_id>")
def join_game(game_id: str):
    # TODO: Do this
    return render_template("join_game.html")


@game_bp.route("/new")
def create_game():
    # TODO: Do this
    return render_template("create_game.html")
