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
        default=current_timestamp(),
    )

    from_user = db.relationship(User, foreign_keys=[from_id])
    to_user = db.relationship(User, foreign_keys=[to_id])


class Friends(db.Model):
    __tablename__ = "friends"

    left_id = db.Column(db.ForeignKey(User.id), primary_key=True)
    right_id = db.Column(db.ForeignKey(User.id), primary_key=True)

    left_user = db.relationship(User, foreign_keys=[left_id])
    right_user = db.relationship(User, foreign_keys=[right_id])

    @classmethod
    def check_friends(cls, left_id: int, right_id: int) -> bool:
        """
        Check whether two users are friends with each other or not.
        `left_id` and `right_id` can be passed in any order.

        @param left_id: First user's ID
        @param right_id: Second user's ID
        @returns: Whether or not the users are friends
        """

        query = db.select(cls).where(
            ((cls.left_id == left_id) & (cls.right_id == right_id))
            | ((cls.left_id == right_id) & (cls.right_id == left_id))
        )
        return db.session.execute(query).scalar_one_or_none() is not None
