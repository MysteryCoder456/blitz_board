from sqlalchemy.sql.functions import current_timestamp
from .. import db


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        default=current_timestamp(),
        nullable=False,
    )

    author = db.Column(db.ForeignKey("users.id"), nullable=False)
    recipient = db.Column(db.ForeignKey("users.id"), nullable=False)
