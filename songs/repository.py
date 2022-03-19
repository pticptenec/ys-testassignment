import json
from abc import ABC, abstractmethod

from pymongo.database import Database

from songs import models


class Songs(ABC):
    @abstractmethod
    def all_songs(self, page: int) -> list[models.Song]:
        raise NotImplementedError

    @abstractmethod
    def avg_by_level(self, level: float) -> list[models.Song]:
        raise NotImplementedError


class SongsRepository(Songs):
    def __init__(self, db: Database):
        self.db = db

    def all_songs(self, page: int, limit: int) -> list[models.Song]:
        aggr = [
            {'$sort': {'title': 1}},
            {'$skip': (page - 1) * limit},
            {'$limit': limit},
        ]
        return list(self.db.songs.aggregate(aggr))

    def avg_by_level(self, level):
        return next(self.db.songs.aggregate([
            {'$match': {'level': {'$gt': level}}},
            {'$group': {'_id': 0, 'avg': {'$avg': '$level'}}},
        ]))

    def search(self, msg):
        return list(self.db.songs.aggregate([
            {'$match': {'$text': {'$search': msg}}},
            # do not change order of two dicts below, MongoDB:4.4 bug
            {'$project': {'title': 1, '_id': 0, 'artist': 1}},
            {'$sort': {'score': {'$meta': "textScore"}}},
        ]))

    def post_rating(self, song_id, rating):
        mobj_id = models.MongoObjectId(song_id)
        objects = list(self.db.songs.find({'_id': mobj_id}))
        if len(objects) != 1:
            return False

        song = models.Song(**objects[0])
        if song.ratings is None:
            song.ratings = []

        song.ratings.append(rating)
        self.db.songs.update_one({
            '_id': mobj_id,
        }, {
            '$set': json.loads(song.json()),
        })
        return True

    def song_rating(self, song_id):
        mobj_id = models.MongoObjectId(song_id)
        return []
