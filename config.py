# import os
from dotenv import dotenv_values

config = dotenv_values(".env")

CONFIG = {
    "SECRET_KEY": config["SECRET_KEY"],
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "SESSION_TYPE": "filesystem",
    "SQLALCHEMY_DATABASE_URI": config["POSTGRES_URL_NON_POOLING"],
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
}

# CONFIG = {
#     "SECRET_KEY": os.environ.get("SECRET_KEY"),
#     "CACHE_TYPE": "SimpleCache",
#     "CACHE_DEFAULT_TIMEOUT": 300,
#     "SESSION_TYPE": "filesystem",
#     "SQLALCHEMY_DATABASE_URI": os.environ.get("POSTGRES_URL_NON_POOLING"),
#     "SQLALCHEMY_TRACK_MODIFICATIONS": False,
# }