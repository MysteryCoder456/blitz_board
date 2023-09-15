from sqlalchemy.sql.functions import current_timestamp
from .. import db


class Channel(db.Model):
    __tablename__ = "message_channels"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)

    member_one_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    member_two_id = db.Column(db.ForeignKey("users.id"), nullable=False)

    messages = db.relationship("Message", back_populates="channel")
    member_one = db.relationship("User", foreign_keys=[member_one_id])
    member_two = db.relationship("User", foreign_keys=[member_two_id])


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)

    author_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    channel_id = db.Column(db.ForeignKey(Channel.id), nullable=False)

    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        default=current_timestamp(),
        nullable=False,
    )

    channel = db.relationship("Channel", back_populates="messages")
