from pathlib import Path
from typing import Any
from flask import Blueprint, render_template, url_for
from flask_login import login_required, current_user

from .. import app, db
from .models import Channel, Message
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
def create_chat_channel(sender: Any, left_id: int, right_id: int, **extra):
    # Create a channel for the two users
    new_channel = Channel(member_one_id=left_id, member_two_id=right_id)  # type: ignore
    db.session.add(new_channel)
    db.session.commit()


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


@chat_bp.route("/<int:user_id>", methods=["GET", "POST"])
@login_required
def chat_page(user_id: int):
    user = db.get_or_404(User, user_id)

    channel_query = db.select(Channel).where(
        ((Channel.member_one == current_user) & (Channel.member_two == user))
        | ((Channel.member_one == user) & (Channel.member_two == current_user))
    )
    channel: Channel = db.one_or_404(channel_query)

    messages_query = (
        db.select(Message)
        .where(Message.channel_id == channel.id)
        .order_by(Message.timestamp)
    )
    messages = db.session.execute(messages_query).scalars()

    return render_template(
        "chat_page.html",
        user=user,
        channel=channel,
        messages=messages,
        chat_script=url_for("static", filename="js/chat.js"),
    )
