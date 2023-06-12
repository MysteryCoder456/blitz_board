from pathlib import Path

from flask import (
    Blueprint,
    render_template,
    request,
)
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import StringField, SubmitField
from wtforms.validators import Length

templates = Path(__file__).parent / "templates"
main_bp = Blueprint("main", __name__, template_folder=templates)


class JoinGameForm(FlaskForm):
    username = StringField(label="Username", description="John Doe")
    game_id = StringField(
        label="Game Code",
        description="12345",
        validators=[Length(min=5, max=5)],
    )
    submit = SubmitField()

    def validate_username(self, username: StringField):
        # Ignore empty username field if user is logged in
        # It will be automatically filled in the backend
        if current_user.is_authenticated:  # type: ignore
            return

        if len(username.data) < 3:
            raise ValidationError(
                "Username must be at least 3 characters long."
            )


@main_bp.route("/", methods=["GET", "POST"])
def home():
    form = JoinGameForm(request.form)

    if form.validate_on_submit():
        if current_user.is_authenticated:  # type: ignore
            form.username.data = current_user.username  # type: ignore

        # TODO: Do this

    return render_template("home.html", form=form)
