from quart import Blueprint, render_template, request
from quart_wtf import QuartForm
from wtforms import StringField, SubmitField
from wtforms.validators import Email


class LoginForm(QuartForm):
    email = StringField(label="Email", validators=[Email()])
    submit = SubmitField()


auth_bp = Blueprint(
    "auth", __name__, url_prefix="/auth", template_folder="templates/auth"
)


@auth_bp.route("/login", methods=["GET", "POST"])
async def login():
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(await request.form)

        if await form.validate_on_submit():
            print(f"Emailing link to {form.email.data}")
            # TODO: Do the link sending

    return await render_template("login.html", form=form)


@auth_bp.route("/signup")
async def signup():
    return await render_template("signup.html")
