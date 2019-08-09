import os

import datetime
WTF_CSRF_ENABLED = True

basedir = os.path.abspath(os.path.dirname(__file__))

COOKIE_VAR = '__shortto_url__'
JWT_HEADER_NAME = 'Auth'
JWT_EXPIRATION_DELTA = datetime.timedelta(minutes=15)
JWT_NOT_BEFORE_DELTA = datetime.timedelta(seconds=1)
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
RDS_PROTOCOL = 'mysql'
RDS_USER = os.environ['RDS_USER']
RDS_PASS = os.environ['RDS_PASS']
RDS_PORT = '3306'
RDS_HOST = os.environ['RDS_HOST']
RDS_DBNAME = 'shortto'
BCRYPT_LOG_ROUNDS = 12

SQLALCHEMY_DATABASE_URI = RDS_PROTOCOL+'://'+RDS_USER+':'+RDS_PASS+'@'+RDS_HOST+':'+RDS_PORT+'/'+RDS_DBNAME
# SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/shortto'
if os.environ.get('ENVIRONMENT') == 'DEVELOPEMENT':
    BASE_URL = 'http://localhost:5000/'
else:
    BASE_URL = 'https://www.shortto.com/'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

SIGNUP_TEMPLATE_ID = "d-636a67c919f34360aadccd1b49ee2c67"

blacklist = [
    'shortto.com',
    'tinyurl.com',
    'goo.gl',
    'is.gd',
    'bit.ly',
    'bit.do',
    't.co',
    'lnkd.in',
    'db.tt',
    'qr.ae',
    'adf.ly',
    'cur.lv',
    'ow.ly',
    'ity.im',
    'q.gs',
    'po.st',
    'bc.bc',
    'twitthis.com',
    'u.to',
    'j.mp',
    'buzurl.com',
    'cutt.es',
    'u.bb',
    'urls.org',
    'x.co',
    'prettylinkpro.com',
    'scrnch.me',
    'filoops.info',
    'vzturl.com'
    'qr.net',
    'oneurl.com',
    'tweez.me',
    'v.gd',
    'tr.im',
    'link.zip.net',
    'tinyarrows.com'
]


# Google Login

class Auth:
    CLIENT_ID = os.environ['CLIENT_ID']
    CLIENT_SECRET = os.environ['CLIENT_SECRET']
    BASE_URI = 'http://localhost:5000/checkLogin'
    DASH_URI = 'http://localhost:5000/dashboard'
    REDIRECT_URI = 'http://localhost:5000/google/auth'
    AUTH_URI = 'http://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'http://accounts.google.com/o/oauth2/token'
    USER_INFO = 'http://www.googleapis.com/userinfo/v2/me'
    RECAPTCHA_SECRET = os.environ['RECAPTCHA_SECRET']