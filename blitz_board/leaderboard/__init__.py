from pathlib import Path
from flask import Blueprint, render_template
from sqlalchemy.sql import func

from .. import db
from ..auth.models import User
from ..game.models import SessionStats

templates = Path(__file__).parent / "templates"
leaderboard_bp = Blueprint(
    "leaderboard",
    __name__,
    url_prefix="/lb",
    template_folder=templates,
)


@leaderboard_bp.route("/global")
def global_leaderboard():
    query = (
        db.select(User, func.max(SessionStats.speed))
        .where(User.id == SessionStats.user_id)
        .group_by(User.id)
        .order_by(func.max(SessionStats.speed).desc())
    )
    ranked_players = db.session.execute(query).all()
    print(list(ranked_players))

    return render_template(
        "leaderboard.html",
        ranked_players=ranked_players,
        enumerate=enumerate,
        round=round,
    )
