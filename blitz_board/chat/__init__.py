from pathlib import Path
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from .. import db
from .models import Channel

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
    query = db.select(Channel)
    all_channels = db.session.execute(query).scalars()
    user_channels = [ch for ch in all_channels if current_user.id in ch.members]
    return render_template("chat_list.html", channels=user_channels)
