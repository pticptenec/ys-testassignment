from abc import ABC, abstractmethod

from flask_pymongo import PyMongo
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
            # {'$sort': {'score': {'$meta': "textScore"}}},
            # {'$project': {'title': 1, '_id': 0, 'artist': 1}},
        ]))
        # return list(self.db.songs.find(filter={'$text': {'$search': msg}}))
