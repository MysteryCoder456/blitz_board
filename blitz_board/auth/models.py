from typing import Optional
from flask_login import UserMixin
from sqlalchemy.sql.functions import current_timestamp

from .. import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    avatar = db.Column(db.String, nullable=True)

    sessions = db.relationship("SessionStats", back_populates="user")
    outgoing_requests = db.relationship(
        "FriendRequest", back_populates="from_user"
    )
    incoming_requests = db.relationship(
        "FriendRequest", back_populates="to_user"
    )

    def __str__(self):
        return self.username


@login_manager.user_loader
def user_loader(user_id) -> Optional[User]:
    return db.session.get(User, user_id)


class UnverifiedUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    url_code = db.Column(db.Uuid, unique=True, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)


class MagicLink(db.Model):
    user_id = db.Column(db.ForeignKey(User.id), primary_key=True)
    url_code = db.Column(db.Uuid, unique=True, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)

    user = db.relationship(User)


class FriendRequest(db.Model):
    __tablename__ = "friend_requests"

    from_id = db.Column(db.ForeignKey(User.id), primary_key=True)
    to_id = db.Column(db.ForeignKey(User.id), primary_key=True)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=current_timestamp,
    )

    from_user = db.relationship(
        User, foreign_keys=[from_id], back_populates="outgoing_requests"
    )
    to_user = db.relationship(
        User, foreign_keys=[to_id], back_populates="incoming_requests"
    )
