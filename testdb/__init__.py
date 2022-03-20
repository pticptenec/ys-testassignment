import os
from pymongo import MongoClient
from pymongo import TEXT


client = MongoClient(os.getenv('MONGO_URI'))

songs_db = client['songs_db']
songs = songs_db['songs']
songs.drop_indexes()
songs.insert_one({"artist": "The Yousicians","title": "Lycanthropic Metamorphosis","difficulty": 14.6,"level":13,"released": "2016-10-26"})
songs.create_index([('artist', TEXT), ('title', TEXT)])
songs.delete_many({})
