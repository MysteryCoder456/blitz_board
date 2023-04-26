from quart import Blueprint, render_template

auth_bp = Blueprint(
    "auth", __name__, url_prefix="/auth", template_folder="templates/auth"
)


@auth_bp.route("/signup")
async def signup():
    return await render_template("signup.html")
