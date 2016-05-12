from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#ankitm111:@
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/myjourneydb'
db = SQLAlchemy(app)

import database_models

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/<username>')
def index(username=None):
    if username is None:
        return "Please log in"
    else:
        return "Hi!! Welcome %s" % username

@app.route('/myjourney/adduser', methods=['POST'])
def adduser():
    print(request.json)
    if not request.json or not 'user_id' in request.json or not 'user_name' in request.json:
        abort(400)
    
    content = request.json
    newuser = database_models.users(content['user_id'], content['user_name'], content.get('email', ''),
                                    content.get('phone', ''))
    db.session.add(newuser)
    db.session.commit()
    u = database_models.users.query.filter_by(user_id=content['user_id']).first()
    print(type(u))
    print(u.id)
    return jsonify({'success' : u.id}), 201

@app.route('/myjourney/addjourney/<user_id>', methods=['POST'])
def addjourney(user_id):
    content = request.json
    if not request.json or not 'name' in request.json:
        abort(400)

    journey = database_models.journeys(request.json['name'], user_id, request.json.get('description', ''))
    db.session.add(journey)
    db.session.commit()
    return jsonify({'success' : True}), 201

@app.route('/myjourney/addpoint/<int:journey_id>', methods=['POST'])
def addpoint(journey_id):
    content = request.json
    return jsonify({'success' : True}), 201




if __name__ == '__main__':
    app.run()
