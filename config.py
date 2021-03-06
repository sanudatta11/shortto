import os

import datetime

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

SAFE_BROWSING_KEY = os.environ['SAFE_BROWSING_KEY']

SQLALCHEMY_DATABASE_URI = RDS_PROTOCOL+'://'+RDS_USER+':'+RDS_PASS+'@'+RDS_HOST+':'+RDS_PORT+'/'+RDS_DBNAME
# SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/shortto'
if os.environ.get('ENVIRONMENT') == 'DEVELOPEMENT':
    BASE_URL = 'http://localhost:5000/'
else:
    BASE_URL = 'http://shortto.com/'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

SIGNUP_TEMPLATE_ID = "d-636a67c919f34360aadccd1b49ee2c67"
SIGNUP_COMPLETE_ID = "d-e9e3012381a04bd382adc83e5042ca2e"
FORGOT_COMPLETE_ID = "d-6f540c2634e945928f5b6294111bd7ed"
PASSWORD_RESET_SUCCESFULL_ID = "d-2bb9ac40f87542a1a27196aba7774acb"

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
    'tinyarrows.com',
    'bitly.su',
    'bitly.in',
    'bitly.su',
    'shortl.link'
]


# Google Login
if os.environ.get('ENVIRONMENT') == 'DEVELOPEMENT':
    class Auth:
        CLIENT_ID = os.environ['CLIENT_ID']
        CLIENT_SECRET = os.environ['CLIENT_SECRET']
        BASE_URI = BASE_URL + 'checkLogin'
        DASH_URI = BASE_URL + 'dashboard'
        REDIRECT_URI = BASE_URL + 'google/auth'
        AUTH_URI = 'http://accounts.google.com/o/oauth2/auth'
        TOKEN_URI = 'http://accounts.google.com/o/oauth2/token'
        USER_INFO = 'http://www.googleapis.com/userinfo/v2/me'
        RECAPTCHA_SECRET = os.environ['RECAPTCHA_SECRET']
else:
    class Auth:
        CLIENT_ID = os.environ['CLIENT_ID']
        CLIENT_SECRET = os.environ['CLIENT_SECRET']
        BASE_URI = 'https://shortto.com/checkLogin'
        DASH_URI = 'https://shortto.com/dashboard'
        REDIRECT_URI = 'https://shortto.com/google/auth'
        AUTH_URI = 'http://accounts.google.com/o/oauth2/auth'
        TOKEN_URI = 'http://accounts.google.com/o/oauth2/token'
        USER_INFO = 'http://www.googleapis.com/userinfo/v2/me'
        RECAPTCHA_SECRET = os.environ['RECAPTCHA_SECRET']