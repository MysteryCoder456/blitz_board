from sqlalchemy.sql.functions import now
from .. import db


class SessionStats(db.Model):
    __tablename__ = "session_stats"

    game_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey("users.id"), primary_key=True)
    speed = db.Column(db.Float, nullable=False)  # in WPM
    word_count = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=now)

    user = db.relationship("User", back_populates="sessions")
