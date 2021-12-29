from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    token = db.Column(db.String(100), default=None)
    name = db.Column(db.String(1000))
    directory = db.Column(db.String(256))
    regdate = db.Column(db.Date())
    
 