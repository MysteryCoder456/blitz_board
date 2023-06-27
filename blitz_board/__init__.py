import os

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_socketio import SocketIO
from yagmail import SMTP

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")

csrf = CSRFProtect(app)
db = SQLAlchemy(app)
smtp = SMTP(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
socketio = SocketIO(app)

login_manager = LoginManager(app)
login_manager.login_view = "auth.login"  # type: ignore
login_manager.login_message_category = "info"

from .main import main_bp
from .auth import auth_bp
from .game import game_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(game_bp)


def run():
    socketio.run(app, use_reloader=True)
