import os
WTF_CSRF_ENABLED = True
SECRET_KEY = os.urandom(24)

basedir = os.path.abspath(os.path.dirname(__file__))

COOKIE_VAR = '__shortto_url__'

DEBUG = True
SQLALCHEMY_DATABASE_URI = 'mysql://root:mysqlmysql@shortto.co8zric1dcsi.us-east-1.rds.amazonaws.com:3306/shortto'
# SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/shortto'
BASE_URL = 'https://www.shortto.com/'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
