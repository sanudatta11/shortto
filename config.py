import os
WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@localhost:3306/shortto'
BASE_URL = 'https://shortto.com/'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
