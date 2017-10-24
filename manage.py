#!/usr/bin/env python
from flask.ext.sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app import app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db

login_manager = LoginManager()

login_manager.init_app(app)
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