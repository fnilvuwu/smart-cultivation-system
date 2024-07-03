import os
# from dotenv import load_dotenv

# load_dotenv()

CONFIG = {
    "SECRET_KEY": os.getenv("SECRET_KEY"),
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "SESSION_TYPE": "filesystem",
    "SQLALCHEMY_DATABASE_URI": os.getenv("POSTGRES_URL_NON_POOLING"),
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
}
