import json

import pytest

from songs import create_app
from songs import mongo
from config import Config


@pytest.fixture(scope='session')
def app():
    app = create_app(Config)
    app.config.update({
        "TESTING": True,
    })
    
    data = load_testdata()
    mongo.db.songs.insert_many([json.loads(val.json()) for val in data])
    yield app
    # mongo.db.songs.delete_many()


@pytest.fixture(scope='session')
def client(app):
    yield app.test_client()
