from flask import Blueprint
from flask import request
from werkzeug.exceptions import BadRequest

from songs import mongo
from songs import repository


bp = Blueprint('api', __name__, url_prefix='/api')


def parse_page(page):
    if page is None:
        return 1
    try:
        res = int(page)
    except ValueError:
        raise BadRequest
    
    if res < 0:
        raise BadRequest

    return res


items_per_page = 3
@bp.route('/songs', methods=['GET'])
def get_songs():
    page = request.args.get('page')
    page = parse_page(page)
    return {
        'songs': repository.SongsRepository(mongo.db).all_songs(page, items_per_page)
    }


def parse_level(level):
    if level is None:
        return 0
    
    try:
        res = int(level)
    except ValueError:
        raise BadRequest

    return res


@bp.route('/songs/avg-difficulty', methods=['GET'])
def get_songs_avg_difficulty():
    level = request.args.get('level')
    level = parse_level(level)
    try:
        avg = repository.SongsRepository(mongo.db).avg_by_level(level)
    except StopIteration:
        avg = {'avg': None}
    return {
        'avg': avg
    }


def parse_message(message):
    if message is None:
        raise BadRequest

    return str(message)


@bp.route('/songs/search', methods=['GET'])
def get_songs_search():
    message = request.args.get('message')
    message = parse_message(message)
    results = repository.SongsRepository(mongo.db).search(message.lower())
    return {
        'result': results,
    }


def parse_rating(rating):
    if rating is None:
        raise BadRequest
    
    try:
        res = int(rating)
    except ValueError:
        raise BadRequest

    if 1 <= res <= 5:
        return res
    raise BadRequest


@bp.route('/songs/<string:song_id>/rating', methods=['POST'])
def post_song_rating(song_id):
    rating = request.json.get('rating')
    rating = parse_rating(rating)
    res = repository.SongsRepository(mongo.db).post_rating(song_id, rating)
    return {
        'result': res
    }


@bp.route('/songs/<string:song_id>/statistics', methods=['GET'])
def get_song_statistics(song_id):
    return {
        'statistics': repository.SongsRepository(mongo.db).song_rating(song_id),
    }
