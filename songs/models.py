from datetime import date
from typing import Optional
from typing import Any

from flask.json import JSONEncoder
from pydantic import BaseModel
from pydantic import Field
from pydantic.json import ENCODERS_BY_TYPE
from bson import ObjectId # type: ignore
from bson import BSON # type: ignore


class MongoObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Any):
        return MongoObjectId(value)


class MongoEncoder(JSONEncoder):
    def default(self, o: Any):
        if isinstance(o, MongoObjectId):
            return str(o)
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, Song):
            return o.dict()
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d')

        return super().default(o)


class Rating(BaseModel):
    id: Optional[MongoObjectId] = Field(None, alias="_id")
    song_id: MongoObjectId
    value: int

    def bson(self) -> BSON:
        res = self.dict()
        if res.get('_id') is None:
            res.pop('_id', None)
        return res


class Song(BaseModel):
    id: Optional[MongoObjectId] = Field(None, alias="_id")
    artist: str
    title: str
    difficulty: float
    level: int
    released: date


ENCODERS_BY_TYPE[MongoObjectId] = str
