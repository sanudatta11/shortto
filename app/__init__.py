from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
application = app
app = Flask(__name__)
csrf = CSRFProtect(app)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import views
