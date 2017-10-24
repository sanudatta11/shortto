from app import app
from manage import db

class shortto(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    big_url = db.Column(db.String(500),nullable=False)
    short_url = db.Column(db.String(50),nullable=False,unique=True)

    def show_url(self):
        return app.config['BASE_URL'] + self.short_url + '/'