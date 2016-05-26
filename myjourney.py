from flask import Flask, jsonify, abort, request, g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask.ext.httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/myjourneydb'
app.config['SECRET_KEY'] = 'sapkit111'
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

import database_models

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

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


@app.route('/myjourney/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')}) 


@app.route('/myjourney/adduser', methods=['POST'])
def adduser():
    if not request.json or not 'user_id' in request.json or not 'user_name' in request.json or not 'password' in request.json:
        abort(400)

    user = database_models.users.query.filter_by(user_id=request.json['user_id']).first()
    if user is not None:
        # existing user
        abort(400)

    content = request.json
    newuser = database_models.users(content['user_id'], content['user_name'], content.get('email', ''), content.get('phone', ''))
    newuser.hash_password(content['password'])

    db.session.add(newuser)
    db.session.commit()
    u = database_models.users.query.filter_by(user_id=content['user_id']).first()
    return jsonify({'success' : u.id}), 201


@app.route('/myjourney/addjourney', methods=['POST'])
@auth.login_required
def addjourney():
    if not request.json or not 'name' in request.json:
        abort(400)

    content = request.json
    if not database_models.users.query.filter_by(user_id=g.user.user_id).first():
        abort(400)

    journey = database_models.journeys(content['name'], g.user.id, content.get('description', ''))
    db.session.add(journey)
    db.session.commit()
    journey = database_models.journeys.query.filter_by(user_id=g.user.id, journey_name=content['name']).first()
    return jsonify({'success' : journey.journey_id}), 201


@app.route('/myjourney/addpoint/<int:journey_id>', methods=['POST'])
@auth.login_required
def addpoint(journey_id):
    content = request.json
    if not request.json or not 'latitude' in content or not 'longitude' in content:
        abort(400)

    point = database_models.points(content.get('name', ''), content.get('story', ''), journey_id, content['latitude'], content['longitude'], datetime.now()) 
    db.session.add(point)
    db.session.commit()
    return jsonify({'success' : True}), 201


@app.route('/myjourney/getalljourneys', methods=['GET'])
@auth.login_required
def getalljourneys():
    journeys = g.user.journeys
    return jsonify({'journeys' : [j.serialize for j in journeys.all()]}), 201


if __name__ == '__main__':
    app.run()
