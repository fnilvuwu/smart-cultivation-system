import os
# from dotenv import load_dotenv

# load_dotenv()

CONFIG = {
    "SECRET_KEY": os.getenv("SECRET_KEY"),
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "SESSION_TYPE": "filesystem",
    "SQLALCHEMY_DATABASE_URI": (
        "postgresql://"
        + os.getenv("POSTGRES_USER")
        + ":"
        + os.getenv("POSTGRES_PASSWORD")
        + "@"
        + os.getenv("POSTGRES_HOST")
        + "/"
        + os.getenv("POSTGRES_DATABASE")
    ),
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
}
