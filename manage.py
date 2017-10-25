#!/usr/bin/env python
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app import app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db

login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

migrate = Migrate(app, db)
manager = Manager(app)

db = SQLAlchemy(app)

# migrations
manager.add_command('db', MigrateCommand)

@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


if __name__ == '__main__':
    manager.run()
