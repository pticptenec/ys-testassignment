from abc import ABC
from abc import abstractmethod
from types import NoneType
from typing import Optional

from pymongo.database import Database # type: ignore
from pydantic import ValidationError

from songs.models import Song
from songs.models import Rating
from songs.models import MongoObjectId


class Ratings(ABC):
    @abstractmethod
    def post_rating(self, rating: int, song_id: str) -> MongoObjectId:
        raise NotImplementedError

    @abstractmethod
    def statistics(self,
            song_id: Optional[MongoObjectId]) -> dict:
        raise NotImplementedError


class Songs(ABC):
    @abstractmethod
    def all_songs(self, page: int, limit: int) -> list[Song]:
        raise NotImplementedError

    @abstractmethod
    def avg_by_level(self, level: int) -> dict:
        raise NotImplementedError

    @abstractmethod
    def search(self, msg: str) -> list[Song]:
        raise NotImplementedError

    @abstractmethod
    def get_song_by_id(self, song_id: MongoObjectId) -> Optional[Song]:
        raise NotImplementedError


class RatingsRepository(Ratings):
    def __init__(self, db: Database):
        self.db = db

    def post_rating(self, rating: int, song_id: str) -> MongoObjectId:
        rating_id = self.db.ratings.insert_one(
            Rating(value=rating, song_id=MongoObjectId(song_id)).bson()
        )
        return rating_id.inserted_id

    def statistics(self, song_id: Optional[MongoObjectId]) -> dict:
        try:
            return next(self.db.ratings.aggregate([
                {'$match': {'song_id': {'$eq': song_id}}},
                {'$group': {
                    '_id': 0,
                    'avg': {'$avg': '$value'},
                    'min': {'$min': '$value'},
                    'max': {'$max': '$value'},
                }},
            ]))
        except StopIteration:
            return {}


class SongsRepository(Songs):
    def __init__(self, db: Database):
        self.db = db

    def all_songs(self, page: int, limit: int) -> list[Song]:
        """
        For Production level code it's better to not query
        song's ratings_ids list, but I do it for more evident JSON API
        """
        aggr = [
            {'$sort': {'title': 1}},
            {'$skip': (page - 1) * limit},
            {'$limit': limit},
        ]
        return list(map(
            lambda x: Song(**x),
            self.db.songs.aggregate(aggr))
        )

    def avg_by_level(self, level: int) -> dict:
        return next(self.db.songs.aggregate([
            {'$match': {'level': {'$gt': level}}},
            {'$group': {'_id': 0, 'avg': {'$avg': '$difficulty'}}},
        ]))

    def search(self, msg: str) -> list[Song]:
        return list(map(
            lambda data: Song(**data),
            self.db.songs.aggregate([
            {'$match': {'$text': {'$search': msg}}},
            {'$sort': {'score': {'$meta': "textScore"}}},
        ])))

    def get_song_by_id(self, song_id: MongoObjectId) -> Optional[Song]:
        res = self.db.songs.find_one({
            '_id': {'$eq': song_id},
        })
        if res is None:
            return res

        return Song(**res)


class SongsMem(Songs):
    def __init__(self, songs):
        self.songs = songs

    def all_songs(self, page: int, limit: int) -> list[Song]:
        return self.songs

    def avg_by_level(self, level: int) -> dict:
        return NotImplemented

    def get_song_by_id(self, song_id: MongoObjectId) -> Song:
        return next(filter(lambda x: x.id == song_id, self.songs))

    def search(self, msg: str) -> list[Song]:
        return NotImplemented


class RatingsMem(Ratings):
    def __init__(self, ratings):
        self.ratings = ratings

    def post_rating(self, rating: int, song_id: str) -> MongoObjectId:
        return NotImplemented

    def statistics(self, song_id: Optional[MongoObjectId]) -> dict:
        sum_ = 0
        min_ = possible_max = 5 + 1
        max_ = 0
        size = 0
        for rating in filter(lambda x: x.song_id == song_id,
                             self.ratings):
            sum_ += rating.value
            if rating.value > max_:
                max_ = rating.value
            if rating.value < min_:
                min_ = rating.value

            size += 1

        avg = 0.0
        if size != 0:
            avg = sum_ / size

        if min_ == possible_max:
            min_ = 0

        return {
            '_id': 0,
            'avg': avg,
            'min': min_,
            'max': max_,
        }
