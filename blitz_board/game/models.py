from sqlalchemy.sql.functions import current_timestamp
from .. import db


class SessionStats(db.Model):
    __tablename__ = "session_stats"

    game_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey("users.id"), primary_key=True)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        default=current_timestamp(),
        primary_key=True,
    )

    speed = db.Column(db.Float, nullable=False)  # in WPM
    accuracy = db.Column(db.Float, nullable=False)
    word_count = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", back_populates="sessions")
