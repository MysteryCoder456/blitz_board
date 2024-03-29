from pathlib import Path
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
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
    rank_by_avg = "avg" in request.args

    if rank_by_avg:
        # Rank users based on average speed
        query = (
            db.select(User, func.avg(SessionStats.speed))
            .where(User.id == SessionStats.user_id)
            .group_by(User.id)
            .order_by(func.avg(SessionStats.speed).desc())
        )
    else:
        # Rank users based on maximum speed
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
        rank_by_avg=rank_by_avg,
        ranked_players=ranked_players,
        enumerate=enumerate,
        round=round,
    )


@leaderboard_bp.route("/friends")
@login_required
def friends_lb():
    rank_by_avg = "avg" in request.args

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

    if rank_by_avg:
        # Rank friends based on average speed
        players_query = (
            db.select(User, func.avg(SessionStats.speed))
            .where(
                (User.id == SessionStats.user_id)
                & ((User.id == current_user.id) | User.id.in_(friend_ids))  # type: ignore
            )
            .group_by(User.id)
            .order_by(func.avg(SessionStats.speed).desc())
        )
    else:
        # Rank friends based on maximum speed
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
        rank_by_avg=rank_by_avg,
        ranked_players=ranked_players,
        enumerate=enumerate,
        round=round,
    )
