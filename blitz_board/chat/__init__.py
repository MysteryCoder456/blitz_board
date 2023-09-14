from pathlib import Path
from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import login_required, current_user

from .. import db
from .models import Channel, Message

templates = Path(__file__).parent / "templates"
chat_bp = Blueprint(
    "chat",
    __name__,
    url_prefix="/chat",
    template_folder=templates,
)


@chat_bp.route("/", methods=["GET"])
@login_required
def chat_list():
    channels = db.select(Channel).where(current_user.id in Channel.members)
    return render_template("chat_list.html", channels=channels)
