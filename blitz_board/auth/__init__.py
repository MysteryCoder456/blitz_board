import os
from datetime import timedelta, datetime
from uuid import uuid4, UUID
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields import (
    EmailField,
    StringField,
    SubmitField,
)
from wtforms.validators import Email, Length
from flask_login import current_user, login_required, login_user, logout_user
from PIL import Image

from .. import db, app, smtp
from .models import User, UnverifiedUser, MagicLink

LINK_DURATION = timedelta(hours=2)


class LoginForm(FlaskForm):
    email = EmailField(
        label="Email",
        validators=[Email()],
        description="user@mail.com",
    )
    submit = SubmitField()


class SignUpForm(FlaskForm):
    username = StringField(
        label="Username",
        validators=[Length(min=3, max=30)],
        description="John Doe",
    )
    submit = SubmitField()

    def validate_username(self, username: StringField):
        query = db.select(User).where(User.username == username.data)

        if db.session.scalar(query):
            raise ValidationError("This username is already taken!")


class EditProfileForm(FlaskForm):
    # TODO: add other profile related fields
    new_avatar = FileField(
        label="New Avatar",
        validators=[
            FileAllowed(
                ["png", "jpg", "jpeg"],
                "Please submit a valid PNG/JPEG file!",
            ),
        ],
    )
    submit = SubmitField()

    # TODO: Validation not working here


templates = Path(__file__).parent / "templates"
auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    template_folder=templates,
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        query = db.select(User).where(User.email == form.email.data)
        user = db.session.execute(query).scalar()

        if user is None:  # User has not registered yet
            query = db.select(UnverifiedUser).where(
                UnverifiedUser.email == form.email.data
            )
            unverified_user = db.session.scalar(query)

            if not unverified_user:
                unverified_user = UnverifiedUser()
                unverified_user.email = form.email.data
                db.session.add(unverified_user)

            unverified_user.url_code = uuid4()
            unverified_user.valid_until = datetime.now() + LINK_DURATION
            db.session.commit()

            endpoint = url_for(
                "auth.verify_registration",
                code=unverified_user.url_code.hex,
            )
            verify_prefix = (
                app.config["VERIFY_PREFIX"] or "http://127.0.0.1:5000"
            )
            verify_link = f"{verify_prefix}{endpoint}"

            msg_content = [
                "Click on this link to confirm and create a new account.",
                verify_link,
                "Please do not share this link with anyone. Happy Typing! :)",
            ]
            smtp.send(
                to=form.email.data,
                subject="Confirm Registration",
                contents=msg_content,
            )

            app.logger.debug(f"Sent registration link to {form.email.data}.")
            flash(
                f"Registration link has been sent to your email ({form.email.data}).",
                "success",
            )
            return redirect(url_for("main.home"))

        else:  # User has an account
            query = db.select(MagicLink).where(MagicLink.user == user)
            magic_link = db.session.scalar(query)

            if not magic_link:
                magic_link = MagicLink()
                magic_link.user = user
                db.session.add(magic_link)

            magic_link.url_code = uuid4()
            magic_link.valid_until = datetime.now() + LINK_DURATION
            db.session.commit()

            endpoint = url_for(
                "auth.verify_login",
                code=magic_link.url_code.hex,
            )
            verify_prefix = (
                app.config["VERIFY_PREFIX"] or "http://127.0.0.1:5000"
            )
            verify_link = f"{verify_prefix}{endpoint}"

            msg_content = [
                "Click on this link to log into your account.",
                verify_link,
                "Please do not share this link with anyone. Happy Typing! :)",
            ]
            smtp.send(
                to=form.email.data,
                subject="Confirm Login",
                contents=msg_content,
            )

            app.logger.debug(f"Sent login link to {form.email.data}")
            flash(
                f"Login link has been sent to your email ({form.email.data}).",
                "success",
            )
            return redirect(url_for("main.home"))

    return render_template("login.html", form=form)


@auth_bp.route("/v-reg/<code>", methods=["GET", "POST"])
def verify_registration(code: str):
    query = db.select(UnverifiedUser).where(
        UnverifiedUser.url_code == UUID(code)
    )
    unverified_user = db.one_or_404(query)

    if unverified_user.valid_until < datetime.now():
        flash("Invalid registration link, please try again.", "error")
        return redirect(url_for("auth.login"))

    form = SignUpForm(request.form)

    if form.validate_on_submit():
        new_user = User()
        new_user.username = form.username.data
        new_user.email = unverified_user.email

        db.session.add(new_user)
        db.session.delete(unverified_user)
        db.session.commit()

        login_user(new_user, remember=True, duration=timedelta(days=1))
        flash(
            f"Welcome, {new_user.username}! Your account was created successfully!",
            "success",
        )
        return redirect(url_for("main.home"))

    return render_template("verify_registration.html", form=form)


@auth_bp.route("/v-log/<code>")
def verify_login(code: str):
    query = db.select(MagicLink).where(MagicLink.url_code == UUID(code))
    magic_link = db.one_or_404(query)

    if magic_link.valid_until < datetime.now():
        flash("Invalid login link, please try again.", "error")
        return redirect(url_for("auth.login"))

    login_user(magic_link.user, remember=True, duration=timedelta(days=1))
    flash(f"Welcome back, {magic_link.user}!", "success")

    db.session.delete(magic_link)
    db.session.commit()

    return redirect("/")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out of your account!", "info")
    return redirect(url_for("main.home"))


@auth_bp.route("/profile/<int:user_id>")
def user_profile(user_id: int):
    user: User = db.get_or_404(
        User,
        user_id,
        description="The requested user does not exist!",
    )

    recent_sessions = user.sessions[:10]
    total_game_count = len(user.sessions)

    avg_speed = (
        int(sum([s.speed for s in user.sessions]) / total_game_count)
        if total_game_count
        else 0
    )
    avg_speed_recent = (
        int(sum([s.speed for s in recent_sessions]) / len(recent_sessions))
        if total_game_count
        else 0
    )

    if user.avatar:
        user_pfp = (
            "/" + app.config["UPLOAD_FOLDER"].parts[-1] + f"/{user.avatar}"
        )
    else:
        # Default profile picture
        user_pfp = url_for("static", filename="images/default-pfp.jpg")

    return render_template(
        "user_profile.html",
        user_pfp=user_pfp,
        pencil=url_for("static", filename="images/pencil.png"),
        user=user,
        total_game_count=total_game_count,
        avg_speed=avg_speed,
        avg_speed_recent=avg_speed_recent,
        recent_sessions=recent_sessions,
    )


@auth_bp.route("/profile/avatar", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(request.form)

    if form.validate_on_submit():
        # Change profile picture if file was uploaded
        if file := request.files[form.new_avatar.name]:
            img_name = file.filename
            img_ext = img_name.split(".")[-1]  # type: ignore
            img_filepath: Path = (
                app.config["UPLOAD_FOLDER"]
                / "avatars"
                / f"{uuid4().hex}.{img_ext}"
            )

            # Crop image into box
            image = Image.open(file.stream)
            min_size_half = min(image.size) / 2
            center = tuple(dim / 2 for dim in image.size)
            crop_box = (
                center[0] - min_size_half,
                center[1] - min_size_half,
                center[0] + min_size_half,
                center[1] + min_size_half,
            )
            cropped_image = image.crop(crop_box)  # type: ignore

            # Saving the file
            cropped_image.save(img_filepath, optimize=True)  # type: ignore

            # Delete old avatar if it exists
            if old_avatar := current_user.avatar:  # type: ignore
                os.remove(app.config["UPLOAD_FOLDER"] / old_avatar)

            # Save new avatar filepath to database
            current_user.avatar = "/".join(img_filepath.parts[-2:])
            db.session.commit()

        flash("Profile updated successfully!", "success")
        return redirect(
            url_for(
                "auth.user_profile",
                user_id=current_user.id,  # type: ignore
            )
        )

    return render_template("edit_profile.html", form=form)


# TODO: show avatar in appropriate locations
