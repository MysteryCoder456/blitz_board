from pathlib import Path
from flask import Blueprint, render_template
from flask_login import current_user
from sqlalchemy.sql import func

from .. import db
from ..auth.models import User, Friends
from ..game.models import SessionStats

templates = Path(__file__).parent / "templates"
leaderboard_bp = Blueprint(
    "leaderboard",
    __name__,
    url_prefix="/lb",
    template_folder=templates,
)


@leaderboard_bp.route("/global")
def global_lb():
    # Rank users based on speed
    query = (
        db.select(User, func.max(SessionStats.speed))
        .where(User.id == SessionStats.user_id)
        .group_by(User.id)
        .order_by(func.max(SessionStats.speed).desc())
    )
    ranked_players = db.session.execute(query).all()

    return render_template(
        "leaderboard.html",
        lb_name="Global",
        ranked_players=ranked_players,
        enumerate=enumerate,
        round=round,
    )


@leaderboard_bp.route("/friends")
def friends_lb():
    # Retreive friend IDs
    friends_query = db.select(Friends).where(
        (Friends.left_user == current_user)
        | (Friends.right_user == current_user)
    )
    friends = db.session.execute(friends_query).scalars()
    friend_ids = [
        f.left_id if f.right_user == current_user else f.right_id
        for f in friends
    ]

    # Rank friends based on speed
    players_query = (
        db.select(User, func.max(SessionStats.speed))
        .where(
            (User.id == SessionStats.user_id)
            & ((User.id == current_user.id) | User.id.in_(friend_ids))  # type: ignore
        )
        .group_by(User.id)
        .order_by(func.max(SessionStats.speed).desc())
    )
    ranked_players = db.session.execute(players_query).all()

    return render_template(
        "leaderboard.html",
        lb_name="Friends",
        ranked_players=ranked_players,
        enumerate=enumerate,
        round=round,
    )
