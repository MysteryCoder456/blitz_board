from typing import Optional
from flask_login import UserMixin

from . import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)

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
