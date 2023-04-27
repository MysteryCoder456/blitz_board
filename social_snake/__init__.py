import os
from dotenv import load_dotenv
from quart import Quart, render_template
from quart_sqlalchemy import SQLAlchemy
from quart_wtf.csrf import (
    CSRFProtect,
    DEFAULT_SUBMIT_METHODS,
    DEFAULT_CSRF_FIELD_NAME,
)

load_dotenv()

app = Quart(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")

# Dumb CSRF config without which I get weird errors
app.config["WTF_CSRF_ENABLED"] = True
app.config["WTF_CSRF_CHECK_DEFAULT"] = True
app.config["WTF_CSRF_METHODS"] = DEFAULT_SUBMIT_METHODS
app.config["WTF_CSRF_FIELD_NAME"] = DEFAULT_CSRF_FIELD_NAME

csrf = CSRFProtect(app)
db = SQLAlchemy(app)

from . import models
from .auth import auth_bp

app.register_blueprint(auth_bp)


@app.route("/")
async def landing_page():
    return await render_template("landing.html")


def run():
    app.run(debug=True)
