import os
import random, string
from datetime import datetime
from myjourney import db, app
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from werkzeug.security import generate_password_hash, check_password_hash

def randomiamgename(length=20):
   return ''.join(random.choice(string.lowercase) for i in range(length))
 
class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    user_id = db.Column(db.String(30), unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(40))
    email = db.Column(db.String(40), unique=True)
    phone = db.Column(db.String(11))
    journeys = db.relationship('journeys', backref='user', lazy='dynamic')

    def __init__(self, user_id, password_hash, name, email, phone):
        self.user_id = user_id
        self.password_hash = password_hash
        self.name = name
        self.email = email
        self.phone = phone
        self.journeys = []

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration = 60000):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'user_id': self.user_id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = users.query.filter_by(user_id=data['user_id']).first()
        return user


class journeys(db.Model):
    journey_id = db.Column(db.Integer, primary_key=True)    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    journey_name = db.Column(db.String(40), unique=True)
    journey_description = db.Column(db.String(100))
    journey_datetime = db.Column(db.DateTime)
    points = db.relationship('points', backref='journey', lazy='dynamic')

    def __init__(self, name, user_id, description, datetime):
        self.journey_name = name
        self.user_id = user_id
        self.journey_description = description
        self.journey_datetime = datetime
        self.points = []

    @property
    def serialize(self):
        return {
            'name': self.journey_name, 
            'description': self.journey_description,
            'points' : [p.serialize for p in self.points.all()]
        }


class points(db.Model):
    point_id = db.Column(db.Integer, primary_key=True)
    journey_id = db.Column(db.Integer, db.ForeignKey('journeys.journey_id'))
    point_name = db.Column(db.String(20))
    point_story = db.Column(db.String(50))
    point_latitude = db.Column(db.Float)
    point_longitude = db.Column(db.Float)
    point_datetime = db.Column(db.DateTime)
    images = db.relationship('images', backref='point', lazy='dynamic')

    def __init__(self, name, journey_id, story, latitude, longitude, datetime):
        self.point_name = name
        self.journey_id = journey_id
        self.point_story = story
        self.latitude = latitude
        self.longitude = longitude
        self.point_datetime = datetime
        self.images = []

    @property
    def serialize(self):
        return {
            'name': self.point_name, 
            'story': self.point_story,
            'latitude' : self.point_latitude,
            'longitude' : self.point_longitude,
            'datetime' : self.point_datetime,
            'images' : [i.serialize for i in self.images.all()]
        }


class images(db.Model):
    point_image_id = db.Column(db.Integer, primary_key=True)
    point_id = db.Column(db.Integer, db.ForeignKey('points.point_id'))
    point_image_file = db.Column(db.String(50))

    def __init__(self, point_id, image):
        self.point_id = point_id
        self.point_image_file = os.path.join(g.user.name, self.point.journey.journey_name, randomiamgename(), '.png')
        with open(self.point_image_file, 'w') as f:
            f.write(image)

    @property
    def serialize(self):
        return {
            'image_file' : self.point_image_file
        }
