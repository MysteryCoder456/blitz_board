from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__, template_folder="templates/main")


@main_bp.get("/")
def home():
    return render_template("home.html")
