import pytest
from werkzeug.exceptions import BadRequest
from pydantic import ValidationError

from songs.routes import parse_page
from songs.routes import parse_level
from songs.routes import parse_rating
from songs.routes import calculate_statistics
from songs.models import MongoObjectId
from songs.models import Rating
from songs.models import Song
from songs.routes import ITEMS_PER_PAGE
from songs.routes import RATING_MAX
from songs.routes import RATING_MIN
from songs.repository import RatingsMem
from songs.repository import SongsMem


def test_constants():
    assert ITEMS_PER_PAGE == 3
    assert RATING_MAX == 5
    assert RATING_MIN == 1


def test_parse_page():
    val = '1'
    assert 1 == parse_page(val)

    val = '-1'
    with pytest.raises(BadRequest):
        parse_page(val)

    val = 'no'
    with pytest.raises(BadRequest):
        parse_page(val)

    assert 1 == parse_page(None)


def test_model_song_validation():
    data = {
        'dum': 1,
        'no': 2,
    }
    with pytest.raises(ValidationError):
        Song(**data)

    data = {
        'artist': 'John',
        'title': 'Song',
        'difficulty': 12.3,
        'level': 5,
        'released': '2022-01-01'
    }
    assert isinstance(Song(**data), Song)


def test_parse_level():
    assert 0 == parse_level(None)

    with pytest.raises(BadRequest):
        parse_level('no')

    with pytest.raises(BadRequest):
        parse_level('1.2')

    assert -1 == parse_level('-1')
    assert 1 == parse_level('1')


def test_parse_raiting():
    with pytest.raises(BadRequest):
        parse_rating(None)

    with pytest.raises(BadRequest):
        parse_rating('1.2')

    with pytest.raises(BadRequest):
        parse_rating('two')

    with pytest.raises(BadRequest):
        parse_rating('6')

    with pytest.raises(BadRequest):
        parse_rating('-1')


def test_calculate_statistics(testdata):
    song_index = 3
    songs = testdata
    songs[song_index].id = MongoObjectId(b'123456789123')
    repo_songs = SongsMem(songs)
    ratings = [Rating(**d) for d in [{
        '_id': b'abcdefghijkl',
        'song_id': MongoObjectId(b'123456789122'),
        'value': 4,
    }, {
        '_id': b'bcdefghijkla',
        'song_id': MongoObjectId(b'123456789121'),
        'value': 4,
    }, {
        '_id': b'cdefghijklab',
        'song_id': MongoObjectId(b'123456789123'),
        'value': 3,
    }]]
    repo_ratings = RatingsMem(ratings)

    stat = calculate_statistics(repo_songs, repo_ratings, MongoObjectId(b'123456789123'))
    assert stat == {
        'avg': round(3.0),
        'min': 3,
        'max': 3,
    }
