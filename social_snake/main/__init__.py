from pathlib import Path

from flask import (
    Blueprint,
    render_template,
)

templates = Path(__file__).parent / "templates"
main_bp = Blueprint("main", __name__, template_folder=templates)


@main_bp.get("/")
def home():
    return render_template("home.html")
