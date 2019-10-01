import os
from flask import Flask
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

if os.environ.get('ENVIRONMENT') != 'DEVELOPEMENT':
    sentry_sdk.init(
        dsn="https://8cfab95e9e164c649ad16f0e9ca70f32@sentry.io/1550025",
        integrations=[FlaskIntegration(),SqlalchemyIntegration()]
    )

app = Flask(__name__)

# LoginManager.login_view = "login"
# LoginManager.login_message = u"Please Log in again!"
# LoginManager.login_message_category = "error"

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = os.urandom(24)  # Change this!
app.config['SECRET_KEY'] = os.urandom(24)  # Change this!

application = app
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
app.config.from_object('config')
db = SQLAlchemy(app)
cors = CORS(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
app.config['CORS_HEADERS'] = 'Content-Type'
from app import views
