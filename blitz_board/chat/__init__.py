from pathlib import Path
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from .. import app, db
from .models import Channel
from ..auth.models import User
from ..auth.signals import friend_added

templates = Path(__file__).parent / "templates"
chat_bp = Blueprint(
    "chat",
    __name__,
    url_prefix="/chat",
    template_folder=templates,
)


@friend_added.connect_via(app)
def create_chat_channel(sender, left_id, right_id, **extra):
    # TODO: Create a channel for two users
    ...


@chat_bp.route("/", methods=["GET"])
@login_required
def chat_list():
    query = db.select(Channel).where(
        (Channel.member_one == current_user) | (Channel.member_two == current_user)
    )
    channels = db.session.execute(query).scalars().all()

    for ch in channels:
        if not ch.name:
            if ch.member_one == current_user:
                ch.name = ch.member_two.username
            else:
                ch.name = ch.member_one.username

    return render_template("chat_list.html", channels=channels)


@chat_bp.route("/chat/<int:user_id>", methods=["GET", "POST"])
@login_required
def chat_page(user_id: int):
    user = db.get_or_404(User, user_id)

    query = db.select(Channel).where(
        ((Channel.member_one == current_user) & (Channel.member_two == user))
        | ((Channel.member_one == user) & (Channel.member_two == current_user))
    )
    channel: Channel = db.one_or_404(query)

    return render_template(
        "chat_page.html",
        channel=channel,
        user=user,
    )
