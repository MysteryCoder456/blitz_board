from pathlib import Path
from flask import (
    Blueprint,
    render_template,
    request,
)
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import Length

templates = Path(__file__).parent / "templates"
main_bp = Blueprint("main", __name__, template_folder=templates)


class JoinGameForm(FlaskForm):
    game_id = StringField(
        label="Game Code",
        description="12345",
        validators=[Length(min=5, max=5)],
    )
    submit = SubmitField()


@main_bp.route("/", methods=["GET", "POST"])
def home():
    form = JoinGameForm(request.form)

    if form.validate_on_submit():
        ...

    return render_template("home.html", form=form)
