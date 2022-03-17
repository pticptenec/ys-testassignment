import os
from dotenv import load_dotenv


load_dotenv('./config.env', override=True)


class DevConfig:
    DEBUG = False
    MONGO_URI = os.getenv('MONGO_URI')

class LoadConfig(DevConfig):
    pass


app_env = os.getenv('FLASK_ENV')
if app_env == 'development':
    Config = DevConfig
elif app_env == 'load':
    Config = LoadConfig
