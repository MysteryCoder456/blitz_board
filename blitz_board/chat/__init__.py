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
    query = db.select(Channel).where(
        (Channel.member_one == current_user)
        | (Channel.member_two == current_user)
    )
    channels = db.session.execute(query).scalars().all()

    for ch in channels:
        if not ch.name:
            if ch.member_one == current_user:
                ch.name = ch.member_two.username
            else:
                ch.name = ch.member_one.username

    return render_template("chat_list.html", channels=channels)
