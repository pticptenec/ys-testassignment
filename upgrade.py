from dotenv import load_dotenv

load_dotenv('config.env', override=True)

from config import *


if Config is DevConfig:
    import testdb
