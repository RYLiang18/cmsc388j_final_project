from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager
from . import config
from .utils import current_time
import base64


@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()


class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    following = db.ListField(db.ReferenceField("self"))

    # Returns unique string identifying our object
    def get_id(self):
        return self.username


class Photo(db.Document):
    poster = db.ReferenceField(User, required=True)
    image = db.ImageField(required=True)
    date = db.StringField(required=True)
    caption = db.StringField(required=True, min_length=1, max_length=100)

    def get_id(self):
        return "{}-{}".format(poster,date)

class Comment(db.Document):
    commenter = db.ReferenceField(User, required=True)
    photo = db.ReferenceField(Photo, required=True)
    date = db.StringField(required=True)
    caption = db.StringField(required=True, min_length=1, max_length=100)
