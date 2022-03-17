from flask import Flask
from flask_pymongo import PyMongo


mongo = PyMongo()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    from songs.models import MongoEncoder
    app.json_encoder = MongoEncoder

    mongo.init_app(app)

    from songs.routes import bp
    app.register_blueprint(bp)

    return app
