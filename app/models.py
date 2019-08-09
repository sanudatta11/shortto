import datetime

from flask_login import UserMixin
from app import app,db

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
    archieved = db.Column(db.Boolean,default=False)

    def show_url(self):
        return app.config['BASE_URL'] + self.short_url + '/'

    def generate_qr(self):
        return "https://api.qrserver.com/v1/create-qr-code/?data="+ self.show_url() + "&size=200x200"

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bundle_id = db.Column(db.Integer, db.ForeignKey('bundle.id'))

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True,unique=True, nullable=False)
    username = db.Column(db.String(50), index=True,unique=True)
    firstName = db.Column(db.String(130))
    lastName = db.Column(db.String(130))
    password_hash = db.Column(db.String(128))
    picture = db.Column(db.String(200))
    birthday = db.Column(db.Date)
    personal_phone = db.Column(db.String(20))

    confirmed = db.Column(db.Boolean, default=False)
    confirmationHash = db.Column(db.String(1000))

    # Google Stuff
    google_login = db.Column(db.Boolean,default=False)
    locale = db.Column(db.String(30))
    authenticated = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean,default=False)

    links = db.relationship("Links", backref="user", lazy=True)
    bundles = db.relationship("Bundle", backref="user", lazy=True)
    announcements = db.relationship('Announcement', backref='user', lazy=True)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())


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

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    links = db.relationship('Links', backref='bundle', lazy=True)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

