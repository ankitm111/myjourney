from flask import Flask, jsonify, abort, request, g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/myjourneydb'
app.config['SECRET_KEY'] = 'sapkit111'
db = SQLAlchemy(app)

import database_models

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

"""
@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = database_models.users.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = database_models.users.query.filter_by(user_id=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True
"""

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Access token missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            g.user = database_models.users.query.filter_by(user_id=data['user_id']).first()
        except:
            return jsonify({'message': 'Access token invalid'}), 401
    
        return f(*args, **kwargs)

    return decorated


@app.route('/myjourney/token', methods=['GET'])
def get_auth_token():
#    token = g.user.generate_auth_token()
#    return jsonify({'token': token.decode('ascii')}) 
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = database_models.users.query.filter_by(user_id=auth.username).first()
    
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if check_password_hash(user.password_hash, auth.password):
        token = jwt.encode({'user_id': user.user_id, 'exp': datetime.utcnow() + timedelta(minutes=60)}, app.config['SECRET_KEY'])
    return jsonify({"token": token.decode("UTF-8")})


    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})


@app.route('/myjourney/adduser', methods=['POST'])
def adduser():
    if not request.json or not 'user_id' in request.json or not 'user_name' in request.json or not 'password' in request.json:
        abort(400)

    user = database_models.users.query.filter_by(user_id=request.json['user_id']).first()
    if user is not None:
        # existing user
        abort(400)

    content = request.json
    hashed_password = generate_password_hash(content['password'], method='sha256')
    newuser = database_models.users(content['user_id'], hashed_password, content['user_name'], content.get('email', ''), content.get('phone', ''))
    db.session.add(newuser)
    db.session.commit()
    u = database_models.users.query.filter_by(user_id=content['user_id']).first()
    return jsonify({'success' : u.id}), 201


@app.route('/myjourney/addjourney', methods=['POST'])
@token_required
def addjourney():
    if not request.json or not 'name' in request.json:
        abort(400)

    content = request.json
    if not database_models.users.query.filter_by(user_id=g.user.id).first():
        abort(400)

    journey = database_models.journeys(content['name'], g.user.id, content.get('description', ''))
    db.session.add(journey)
    db.session.commit()
    journey = database_models.journeys.query.filter_by(user_id=g.user.id, journey_name=content['name']).first()
    return jsonify({'success' : journey.journey_id}), 201


@app.route('/myjourney/addpoint', methods=['POST'])
@token_required
def addpoint():
    content = request.json
    if not content or not 'journey_name' in content or not 'latitude' in content or not 'point_name' in content or not 'longitude' in content or not 'datetime' in content:
        abort(400)

    journey = database_models.journeys.query.filter_by(user_id=g.user.id, journey_name=content['journey_name']).first()
    if journey is None:
        abort(400)

    point = database_models.points(content['point_name'], journey.journey_id, content.get('story', ''), content['latitude'], content['longitude'], datetime) 
    db.session.add(point)
    db.session.commit()
    return jsonify({'success' : True}), 201


@app.route('/myjourney/addimage', methods=['POST'])
@token_required
def addimage():
    content = request.json
    if not content or not 'point_name' in content or not 'image' in content:
        abort(400)

    point = database_models.points.query.filter_by(user_id=g.user.id, point_name=content['point_name']) 
    image = database_models.images(point.point_id, image)
    db.session.add(image)
    db.session.commit()
    return jsonify({'success' : True}), 201


@app.route('/myjourney/getalljourneys', methods=['GET'])
@token_required
def getalljourneys():
    journeys = g.user.journeys
    return jsonify({'journeys' : [j.serialize for j in journeys.all()]}), 201


@app.route('/myjourney/getjourneynames', methods=['GET'])
@token_required
def getjourneynames():
    journeys = g.user.journeys
    return jsonify({'journeys' : [j.journey_name for j in journeys.all()]}), 201


@app.route('/myjourney/getjourneydetails/<journey_name>', methods=['GET'])
@token_required
def getjourneydetails(journey_name):
    j = None
    for journey in g.user.journeys:
        if journey.journey_name == journey_name:
            j = journey
    if j:
        return jsonify({'journey' : j.serialize}), 201
    else:
        abort(400)


@app.route('/myjourney/getimagesforpoint', methods=['GET'])
@token_required
def getimagesforpoint():
    content = request.json
    if not content or not 'point_name' in content or not journey_name in content:
        abort(400)
    
    journey = database_models.journeys.query.filter_by(user_id=g.user.id, journey_name=journey_name)
    if journey:
        point = database_models.points.query.filter_by(journey_id=journey.journey_id, point_name=point_name)
        if point:
            images = database_models.images.query.filter_by(point_id=point.point_id)
            return jsonify({'images' : [i.serialize for i in images.all()]}), 201
        else:
            abort(400)
    else:
        abort(400)


@app.route('/myjourney/getimage', methods=['GET'])
@token_required
def getimage():
    content = request.json
    if not content or not 'image_filename' in content:
        abort(400)

    try:
        with open(content['image_filename'], 'r') as f:
            image = f.read()
    except:
        abort(400)

    return jsonify({'image' : image}), 201


if __name__ == '__main__':
    app.run()
