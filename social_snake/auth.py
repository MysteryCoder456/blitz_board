from datetime import timedelta, datetime
from email.message import EmailMessage
from uuid import uuid4, UUID

from quart import Blueprint, flash, redirect, render_template, request, url_for
from quart_wtf import QuartForm
from wtforms import EmailField, SubmitField
from wtforms.validators import Email

from . import db, models, app, utils

LINK_DURATION = timedelta(hours=2)


class LoginForm(QuartForm):
    email = EmailField(label="Email", validators=[Email()])
    submit = SubmitField()


auth_bp = Blueprint(
    "auth", __name__, url_prefix="/auth", template_folder="templates/auth"
)


@auth_bp.route("/login", methods=["GET", "POST"])
async def login():
    form = LoginForm(await request.form)

    if await form.validate_on_submit():
        query = db.select(models.User).where(
            models.User.email == form.email.data
        )
        user = db.session.execute(query).scalar()

        if user is None:  # User has not registered yet
            query = db.select(models.UnverifiedUser).where(
                models.UnverifiedUser.email == form.email.data
            )
            unverified_user = db.session.execute(query).scalar()

            if not unverified_user:
                unverified_user = models.UnverifiedUser()
                unverified_user.email = form.email.data
                db.session.add(unverified_user)

            unverified_user.url_code = uuid4()
            unverified_user.valid_until = datetime.now() + LINK_DURATION
            db.session.commit()

            verify_link = (
                f"http://127.0.0.1:5000/auth/verify/{unverified_user.url_code}"
                if app.debug
                else ""
            )  # TODO: Set else condition url for production

            msg = EmailMessage()
            msg["Subject"] = "Confirm Registration"
            msg.set_content(
                "Click on this link to confirm your registration and create "
                f"a new account.\n{verify_link}\nPlease do not share this "
                "link with anyone. Happy Puzzling! :)"
            )

            await utils.send_mail(msg, form.email.data)
            app.logger.debug(f"Sent registration email to {form.email.data}.")

            await flash(
                f"Registration link has been sent to your email ({form.email.data}).",
                "success",
            )
            return redirect(url_for("landing_page"))

        else:
            # TODO: Login Link
            print(f"Emailing link to {form.email.data}")

    # TODO: show validation errors in template
    return await render_template("login.html", form=form)


@auth_bp.route("/v-reg/<uuid:code>", methods=["GET"])
async def verify_registration(code: UUID):
    return await render_template("verify_registration.html")
