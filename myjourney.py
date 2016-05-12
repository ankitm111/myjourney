from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ankitm111:@localhost/myjourneydb'
db = SQLAlchemy(app)


####################################### MODELS ##########################################

class users(db.Model):
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
        self.journeys = []


class journeys(db.Model):
    journey_id = db.Column(db.Integer, primary_key=True)    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    journey_name = db.Column(db.String(40))
    journey_description = db.Column(db.String(100))
    points = db.relationship('Points', backref='journey', lazy='dynamic')

    def __init__(self, name, description):
        self.journey_name = name
        self.journey_description = description
        self.points = []


class points(db.Model):
    point_id = db.Column(db.Integer, primary_key=True)
    journey_id = db.Column(db.Integer, db.ForeignKey('journeys.journey_id'))
    point_name = db.Column(db.String(20))
    point_story = db.Column(db.String(50))
#    point_lat_long = db.Column(Geometry('POINT'))
    point_latitude = db.Column(db.Float)
    point_longitude = db.Column(db.Float)
    point_datetime = db.Column(db.DateTime)
    images = db.relationship('Images', backref='point', lazy='dynamic')

    def __init__(self, name, story, latitude, longitude):
        self.point_name = name
        self.point_story = story
#        self.point_lat_long = "POINT(latitude, longitude)"
        self.latitude = latitude
        self.longitude = longitude
        self.images = []


class images(db.Model):
    point_image_id = db.Column(db.Integer, primary_key=True)
    point_id = db.Column(db.Integer, db.ForeignKey('points.point_id'))
    point_image_file = db.Column(db.String(50))

######################################################################################

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/<username>')
def index(username=None):
    if username is None:
        return "Please log in"
    else:
        return "Hi!! Welcome %s" % username

@app.route('/myjourney/api/v1.0/adduser', methods=['POST'])
def adduser():
    print(request.json)
    if not request.json or not 'user_id' in request.json or not 'user_name' in request.json:
        abort(400)
    
    content = request.json
    newuser = users(content['user_id'], content['user_name'], content.get('email', ''),
                    content.get('phone', ''))
    db.session.add(newuser)
    db.session.commit()
    return 201

if __name__ == '__main__':
    app.run()
