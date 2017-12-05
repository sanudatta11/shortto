import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_restful import Resource,Api

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

class api_auth(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.String(100),nullable=False)
    client_secret = db.Column(db.String(400),nullable=False,unique=True)

    api_calls = db.Column(db.Integer,nullable=False,default=0)


# class make_url_api(Resource):
#     def get(self,jwt_token):


class Client_auth(object):
    def __init__(self,client_id,client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def __str__(self):
        return "Client Id = '%s'" % self.client_id