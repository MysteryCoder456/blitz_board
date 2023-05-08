from sqlalchemy.sql.functions import now
from .. import db


class Maze(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    author_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"))
    date_created = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=now(),
    )
    difficulty = db.Column(db.Integer, nullable=True)
    maze_data = db.Column(db.JSON, nullable=False)
    published = db.Column(db.Boolean, nullable=False, default=False)

    author = db.relationship("User", back_populates="mazes")