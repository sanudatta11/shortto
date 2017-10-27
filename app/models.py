import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app import app
from app import db, login_manager

class Shortto(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    big_url = db.Column(db.String(500),nullable=False)
    short_url = db.Column(db.String(50),nullable=False,unique=True)

    # user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    # user = db.relationship('User')

    clicks = db.Column(db.Integer,nullable=False,default=0)

    def show_url(self):
        return app.config['BASE_URL'] + self.short_url + '/'