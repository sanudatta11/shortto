import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_restful import Resource,Api
from flask_login import UserMixin
from app import app
from app import db, login_manager

class Links(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    big_url = db.Column(db.String(1000),nullable=False)
    short_url = db.Column(db.String(50),nullable=False,unique=True)

    description = db.Column(db.String(20))

    clicks = db.Column(db.Integer,nullable=False,default=0)

    password_protect = db.Column(db.Boolean,default=False)
    password_hash = db.Column(db.String(250))

    expiration = db.Column(db.Boolean,default=False)
    expiration_date = db.Column(db.DateTime)

    def show_url(self):
        return app.config['BASE_URL'] + self.short_url + '/'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bundle_id = db.Column(db.Integer, db.ForeignKey('bundle.id'))

class api_auth(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.String(100),nullable=False)
    client_secret = db.Column(db.String(400),nullable=False,unique=True)

    api_calls = db.Column(db.Integer,nullable=False,default=0)

class Client_auth(object):
    def __init__(self,client_id,client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def __str__(self):
        return "Client Id = '%s'" % self.client_id

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True,unique=True, nullable=False)
    
    firstName = db.Column(db.String(130))
    lastName = db.Column(db.String(130))

    password_hash = db.Column(db.String(128))
    picture = db.Column(db.String(200))

    birthday = db.Column(db.Date)
    personal_phone = db.Column(db.String(20))

    # Google Stuff
    google_login = db.Column(db.Boolean,default=False)
    locale = db.Column(db.String(30))

    authenticated = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    admin = db.Column(db.Boolean,default=False)

    links = db.relationship("Links", backref="user", lazy=True)

    announcements = db.relationship('Announcement', backref='user', lazy=True)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500),nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

class Bundle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    archieved = db.Column(db.Boolean,default=False)
    links = db.relationship('Links', backref='bundle', lazy=True)

