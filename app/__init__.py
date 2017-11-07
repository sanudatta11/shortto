from flask import Flask

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
application = app
login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

app.config.from_object('config')
db = SQLAlchemy(app)

from app import views
