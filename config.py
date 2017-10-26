import os
WTF_CSRF_ENABLED = True
SECRET_KEY = os.urandom(24)

basedir = os.path.abspath(os.path.dirname(__file__))

class Auth:
    CLIENT_ID = ('568243403925-9vklgmkda7incj0c141n1epoc8ao5lmm.apps.googleusercontent.com')
    CLIENT_SECRET = 'hsj4bztvZAruIkxvD2LODgjt'
    REDIRECT_URI = 'https://localhost:5000/success'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'


class Config:
    APP_NAME = "OAuth Test"
    SECRET_KEY = SECRET_KEY

DEBUG = True
SQLALCHEMY_DATABASE_URI = 'mysql://root:mysqlmysql@shortto.co8zric1dcsi.us-east-1.rds.amazonaws.com:3306/shortto'
BASE_URL = 'https://shortto.com/'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
