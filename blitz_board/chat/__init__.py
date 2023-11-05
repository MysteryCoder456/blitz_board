from pathlib import Path
from typing import Any
from flask import Blueprint, render_template, url_for, make_response
from flask_login import login_required, current_user
from flask_socketio import emit, join_room

from .. import app, db, socketio
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

open_channels: dict[int, Channel] = {}


@friend_added.connect_via(app)
def create_chat_channel(sender: Any, left_id: int, right_id: int, **extra):
    """
    Create a channel for two users if one doesn't exist.
    `left_id` and `right_id` are interchangeable.

    @param 'left_id': First user's ID
    @param 'right_id': Second user's ID
    """

    query = db.select(Channel).where(
        (
            (Channel.member_one_id == left_id)
            & (Channel.member_two_id == right_id)
        )
        | (
            (Channel.member_one_id == right_id)
            & (Channel.member_two_id == left_id)
        )
    )

    if len(db.session.execute(query).all()):
        return

    new_channel = Channel(member_one_id=left_id, member_two_id=right_id)  # type: ignore
    db.session.add(new_channel)
    db.session.commit()


@socketio.on("connect", namespace="/chat")
def on_connect(auth: dict):
    channel_id: int = auth["channel_id"]

    query = db.select(Channel).where(
        (Channel.id == channel_id)
        & (
            (Channel.member_one == current_user)
            | (Channel.member_two == current_user)
        )
    )
    channel = db.session.execute(query).scalar()

    if not channel:
        return False

    open_channels[current_user.id] = channel  # type: ignore
    join_room(channel.id)


@socketio.on("disconnect", namespace="/chat")
def on_disconnect():
    del open_channels[current_user.id]  # type: ignore


@socketio.on("send message", namespace="/chat")
def on_send(msg_content: str):
    channel = open_channels[current_user.id]  # type: ignore
    new_msg = Message(  # type: ignore
        author=current_user,
        channel=channel,
        content=msg_content.strip(),
    )
    db.session.add(new_msg)
    db.session.flush()

    author_avatar = (
        url_for("site_media", media_path=new_msg.author.avatar)
        if new_msg.author.avatar
        else None
    )
    new_msg_json = {
        "id": new_msg.id,
        "author_id": new_msg.author_id,
        "author": new_msg.author.username,
        "author_avatar": author_avatar,
        "content": new_msg.content,
        "timestamp": new_msg.timestamp.strftime("%I:%M %p on %m %b %Y"),
    }

    emit("new message", new_msg_json, to=channel.id)
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


@chat_bp.route("/<int:channel_id>", methods=["GET", "POST"])
@login_required
def chat_page(channel_id):
    channel: Channel = db.get_or_404(Channel, channel_id)

    if channel.member_one == current_user:
        user = channel.member_two
    elif channel.member_two == current_user:
        user = channel.member_one
    else:
        return make_response("You cannot access this channel!", 403)

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
        socket_io=url_for("static", filename="js/socket.io.js"),
        chat_script=url_for("static", filename="js/chat.js"),
    )
