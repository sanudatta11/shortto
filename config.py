import os

import datetime

WTF_CSRF_ENABLED = True
SECRET_KEY = os.urandom(24)

basedir = os.path.abspath(os.path.dirname(__file__))

COOKIE_VAR = '__shortto_url__'
JWT_HEADER_NAME = 'Auth'
JWT_EXPIRATION_DELTA = datetime.timedelta(minutes=15)
JWT_NOT_BEFORE_DELTA = datetime.timedelta(seconds=1)
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'mysql://root:y125zmZ75DO8n5k@shortto.co8zric1dcsi.us-east-1.rds.amazonaws.com:3306/shortto'
# SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/shortto'
BASE_URL = 'https://www.shortto.com/'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

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