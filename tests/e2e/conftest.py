import json
import os
from pathlib import Path

import pytest

from songs import create_app
from songs import mongo
from songs import models
from config import Config


testdatadir = os.path.join(os.path.dirname(__file__), 'testdata')


@pytest.fixture(scope='session')
def testdata():
    yield load_testdata()


def load_testdata():
    data = []
    with open(Path(testdatadir) / 'songs.json', 'rt', encoding='utf-8') as f:
        for line in f:
            data.append(models.Song(**json.loads(line)))

    return data


@pytest.fixture(scope='session')
def app(testdata):
    app = create_app(Config)
    app.config.update({
        "TESTING": True,
    })

    mongo.db.songs.delete_many({})
    mongo.db.songs.insert_many([json.loads(val.json(exclude={'id'})) for val in testdata])
    yield app
    mongo.db.songs.delete_many({})
    mongo.db.ratings.delete_many({})


@pytest.fixture(scope='session')
def client(app):
    yield app.test_client()


@pytest.fixture(scope='session')
def app_only():
    app = create_app(Config)
    app.config.update({
        "TESTING": True,
    })
    yield app


@pytest.fixture(scope='session')
def insert_testdata(app_only, testdata):
    mongo.db.songs.insert_many([json.loads(val.json(exclude={'id'})) for val in testdata])
    yield


POPULATE_OPT = '--populate'


def pytest_addoption(parser):
    parser.addoption(POPULATE_OPT, default=None)


def pytest_collection_modifyitems(config, items):
    mark = 'run_only_from_cmd'
    if config.getoption(POPULATE_OPT):
        mark_skipped(
            filter(
                lambda x: True if mark not in x.keywords else False,
                items
            )
        )
        return
 
    mark_skipped(
            filter(
                lambda x: True if mark in x.keywords else False,
                items
            )
        )
    return


def mark_skipped(items):
    skip = pytest.mark.skip(reason='manual tests, population only')
    for item in items:
        item.add_marker(skip)
