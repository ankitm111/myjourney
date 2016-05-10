from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from myjourney import db


# This table will hold data for user
class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    user_id = db.Column(db.String(30), unique=True)
    name = db.Column(db.String(40))
    email = db.Column(db.String(40), unique=True)
    phone = db.Column(db.String(11))
    journeys = db.relationship('Journeys', backref='user', lazy='dynamic')

    def __init__(self, user_id, name, email, phone):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone


class journeys(db.Model):
    journey_id = db.Column(db.Integer, primary_key=True)    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    journey_name = db.Column(db.String(40))
    journey_description = db.Column(db.String(100))
    points = db.relationship('Points', backref='journey', lazy='dynamic')

    def __init__(self, name, description):
        self.journey_name = name
        self.journey_description = description


class points(db.Model):
    point_id = db.Column(db.Integer, primary_key=True)
    journey_id = db.Column(db.Integer, db.ForeignKey('journeys.journey_id'))
    point_name = db.Column(db.String(20))
    point_story = db.Column(db.String(50))
    point_latitude = db.Column(db.Float)
    point_longitude = db.Column(db.Float)
    images = db.relationship('Images', backref='point', lazy='dynamic')

    def __init__(self, name, story, latitude, longitude):
        self.point_name = name
        self.point_story = story
        self.point_latitude = latitude
        self.point_longitude = longitude 


class images(db.Model):
    point_image_id = db.Column(db.Integer, primary_key=True)
    point_id = db.Column(db.Integer, db.ForeignKey('points.point_id'))
    point_image_file = db.Column(db.String(50))
