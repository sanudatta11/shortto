from flask import Flask
from flask.ext.login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
app = Flask(__name__)
application = app
login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

csrf = CSRFProtect(app)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import views
