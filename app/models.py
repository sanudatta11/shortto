from sqlalchemy.orm import relationship

from app import app
from manage import db, login_manager


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100),nullable=False)
    password = db.Column(db.String(400),nullable=False)

    shorttos = db.relationship('Shortto', backref='User', lazy='dynamic')

    def check_pass(self,password):
        if self.password == password:
            return True
        else:
            return False

    @login_manager.user_loader
    def user_loader(user_id):
        """Given *user_id*, return the associated User object.

        :param unicode user_id: user_id (email) user to retrieve
        """
        return User.query.get(user_id)

class Shortto(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    big_url = db.Column(db.String(500),nullable=False)
    short_url = db.Column(db.String(50),nullable=False,unique=True)

    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    user = db.relationship('User')

    def show_url(self):
        return app.config['BASE_URL'] + self.short_url + '/'