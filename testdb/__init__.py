import os
from pymongo import MongoClient


client = MongoClient(os.getenv('MONGO_URI'))

songs_db = client['songs_db']
songs = songs_db['songs']
songs.create_index({'artist': 'text', 'title': 'text'})
