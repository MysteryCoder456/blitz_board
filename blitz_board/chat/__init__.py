from pathlib import Path
from flask import Blueprint, flash, redirect, url_for

from .models import Message

templates = Path(__file__).parent / "templates"
chat_bp = Blueprint(
    "chat",
    __name__,
    url_prefix="/chat",
    template_folder=templates,
)


@chat_bp.route("/", methods=["GET"])
def chat_list():
    flash("Coming Soon!", "info")
    return redirect(url_for("main.home"))
