from typing import Optional

from flask import Blueprint
from flask import request
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound

from songs import mongo
from songs.repository import Songs
from songs.repository import Ratings
from songs.repository import SongsRepository
from songs.repository import RatingsRepository
from songs.models import MongoObjectId


bp = Blueprint('api', __name__, url_prefix='/api')


def parse_page(page: Optional[str]) -> int:
    if page is None:
        return 1
    try:
        res = int(page)
    except ValueError:
        raise BadRequest from ValueError

    if res < 0:
        raise BadRequest

    return res


ITEMS_PER_PAGE = 3

@bp.route('/songs', methods=['GET'])
def get_songs():
    page = request.args.get('page')
    page = parse_page(page)
    return {
        'songs': SongsRepository(mongo.db).all_songs(page, ITEMS_PER_PAGE)
    }


def parse_level(level: Optional[str]) -> int:
    if level is None:
        return 0

    try:
        res = int(level)
    except ValueError:
        raise BadRequest from ValueError

    return res


@bp.route('/songs/avg-difficulty', methods=['GET'])
def get_songs_avg_difficulty() -> dict:
    level_arg = request.args.get('level')
    level = parse_level(level_arg)
    try:
        avg = SongsRepository(mongo.db).avg_by_level(level)
        del avg['_id']
        avg['avg'] = round(avg['avg'], 2)
    except StopIteration:
        avg = {'avg': None}
    return avg


def parse_message(message: Optional[str]) -> str:
    if message is None:
        raise BadRequest

    if message == '':
        raise BadRequest

    return message


@bp.route('/songs/search', methods=['GET'])
def get_songs_search() -> dict:
    message = request.args.get('message')
    message = parse_message(message)
    results = SongsRepository(mongo.db).search(message.lower())
    return {
        'result': results,
    }


RATING_MIN = 1
RATING_MAX = 5


def parse_rating(rating: Optional[str]) -> int:
    if rating is None:
        raise BadRequest

    try:
        res = int(rating)
    except ValueError:
        raise BadRequest from ValueError

    if RATING_MIN <= res <= RATING_MAX:
        return res

    raise BadRequest


@bp.route('/songs/<string:song_id>/rating', methods=['POST'])
def post_song_rating(song_id: str) -> dict:
    rating_arg = request.json.get('rating') # type: ignore
    rating = parse_rating(rating_arg)
    rating_id = RatingsRepository(mongo.db).post_rating(rating)
    status = SongsRepository(mongo.db).append_rating(song_id, rating_id)
    return {
        'result': status,
    }


def calculate_statistics(song_repo: Songs,
        ratings_repo: Ratings,
        song_id: str
    ) -> dict:
    song_id = MongoObjectId(song_id)
    song = song_repo.get_song_by_id(song_id)
    if song is None:
        raise NotFound
    if song.ratings_ids is None:
        raise BadRequest

    stat = ratings_repo.statistics(song.ratings_ids)
    del stat['_id']
    stat['avg'] = round(stat['avg'], 2)
    return stat


@bp.route('/songs/<string:song_id>/statistics', methods=['GET'])
def get_song_statistics(song_id: str) -> dict:
    stat = calculate_statistics(
        SongsRepository(mongo.db),
        RatingsRepository(mongo.db),
        song_id,
    )
    return {
        'statistics': stat,
    }
