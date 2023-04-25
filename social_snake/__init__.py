import os
from dotenv import load_dotenv
from quart import Quart, render_template
from quart_sqlalchemy import SQLAlchemy

load_dotenv()

app = Quart(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")

db = SQLAlchemy(app)

from . import models
from .auth import auth_bp

app.register_blueprint(auth_bp)


@app.route("/")
async def landing_page():
    return await render_template("landing.html")


def run():
    app.run(debug=True)
