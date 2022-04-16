import json
import random

import pytest

from songs import create_app
from songs import mongo
from config import Config


def gen_ratings(len_):
    i = 0
    while i < len_:
        i += 1
        yield {'value': random.randint(1, 5)}


@pytest.fixture(scope='function')
def app_func(testdata):
    app = create_app(Config)
    app.config.update({
        "TESTING": True,
    })

    mongo.db.songs.delete_many({})
    mongo.db.ratings.delete_many({})
    mongo.db.songs.insert_many([json.loads(val.json()) for val in testdata])
    mongo.db.ratings.insert_many(list(gen_ratings(10)))
    yield app
    mongo.db.songs.delete_many({})
    mongo.db.ratings.delete_many({})


@pytest.fixture(scope='function')
def client_func(app_func):
    yield app_func.test_client()


@pytest.fixture(scope='function')
def songs(app_func):
    yield list(mongo.db.songs.find({}))


@pytest.fixture(scope='function')
def db_ratings(app_func):
    yield list(mongo.db.ratings.find({}))


def test_post_rating_success(client_func, songs):
    song_id = songs[0]['_id']
    response = client_func.post(f'/api/songs/{song_id}/rating', json={
        'song_id': song_id,
        'rating': 3,
    })

    saved = next(mongo.db.ratings.find({'value': 3}))

    assert response.json.get('rating_id') is not None

    assert saved['value'] == 3


def test_post_rating_success_second(client_func, songs):
    song_id = songs[0]['_id']
    response1 = client_func.post(f'/api/songs/{song_id}/rating', json={
        'song_id': song_id,
        'rating': 3,
    })

    response2 = client_func.post(f'/api/songs/{song_id}/rating', json={
        'song_id': song_id,
        'rating': 4,
    })

    saved3 = next(mongo.db.ratings.find({'value': 3}))
    saved4 = next(mongo.db.ratings.find({'value': 4}))

    assert response1.json.get('rating_id') is not None
    assert response2.json.get('rating_id') is not None

    assert saved3['value'] == 3
    assert saved4['value'] == 4


def test_post_rating_failure(client_func):
    response = client_func.post('/api/songs/dummy/ratings', json={})
    assert response.status_code == 404


def calculate_statistics(ratings):
    min_ = possible_max = 5 + 1
    max_ = len_ = sum_ = 0
    for rating in ratings:
        if rating > max_:
            max_ = rating
        if rating < min_:
            min_ = rating

        sum_ += rating
        len_ += 1

    avg = 0
    if len_ != 0:
        avg = sum_ / len_

    if min_ == possible_max:
        min_ = 0

    return {
        'avg': round(avg, 2),
        'min': min_,
        'max': max_,
    }


def test_ratings_statistics(client_func, testdata):
    song = testdata[0]
    db_song = list(mongo.db.songs.aggregate([
        {'$match': {'title': {'$eq': song.title}}},
    ]))[0]
    mongo.db.ratings.update_many(
        {},
        {'$set': {'song_id': db_song['_id']}},
    )
    ratings = list(mongo.db.ratings.find({}))
    response = client_func.get(f'/api/songs/{db_song["_id"]}/statistics')

    assert response.json == {
        'statistics': calculate_statistics(
            map(lambda x: x['value'], ratings)),
    }
