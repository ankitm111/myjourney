from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ankitm111:@localhost/myjourneydb'
db = SQLAlchemy(app)


@app.route('/<username>')
def index(username=None):
    if username is None:
        return "Please log in"
    else:
        return "Hi!! Welcome %s" % username


if __name__ == '__main__':
    app.run()
