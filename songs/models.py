from datetime import date
from typing import Optional

from flask.json import JSONEncoder
from pydantic import BaseModel, Field
from pydantic.json import ENCODERS_BY_TYPE
from bson import ObjectId


class MongoObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return MongoObjectId(v)


class MongoEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, MongoObjectId):
            return str(o)
        if isinstance(o, ObjectId):
            return str(o)
        else:
            return super().default(o)


class Rating(BaseModel):
    id: Optional[MongoObjectId] = Field(None, alias="_id")
    value: int


class Song(BaseModel):
    id: Optional[MongoObjectId] = Field(None, alias="_id")
    artist: str
    title: str
    difficulty: float
    level: int
    released: date
    ratings: Optional[list[int]]


ENCODERS_BY_TYPE[MongoObjectId] = str
