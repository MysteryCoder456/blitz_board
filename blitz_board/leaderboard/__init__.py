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
    query = (
        db.select(User, func.max(SessionStats.speed))
        .where(User.id == SessionStats.user_id)
        .group_by(User.id)
        .order_by(func.max(SessionStats.speed).desc())
    )
    ranked_players = db.session.execute(query).all()

    # HACK: try to integrate this logic into SQL query
    ranked_players = [
        player
        for player in ranked_players
        if Friends.check_friends(player[0].id, current_user.id)  # type: ignore
        or player[0] == current_user
    ]

    return render_template(
        "leaderboard.html",
        lb_name="Friends",
        ranked_players=ranked_players,
        enumerate=enumerate,
        round=round,
    )
