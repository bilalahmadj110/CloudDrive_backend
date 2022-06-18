from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    token = db.Column(db.String(4000), default=None)
    name = db.Column(db.String(1000))
    directory = db.Column(db.String(256))
    regdate = db.Column(db.Date())
    is_admin = db.Column(db.Boolean, default=False)
    has_access = db.Column(db.Integer, default=0)
    
    # serialize the user object to JSON
    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "directory": self.directory,
            "regdate": self.regdate,
            "is_admin": self.is_admin,
            "access": self.has_access
        }
    
 