import os
# from dotenv import load_dotenv

# load_dotenv()

CONFIG = {
    "SECRET_KEY": os.getenv("SECRET_KEY"),
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "SESSION_TYPE": "filesystem",
    "SQLALCHEMY_DATABASE_URI": (
        "mysql+pymysql://"
        + os.getenv("MYSQL_USERNAME")
        + ":"
        + os.getenv("MYSQL_PASSWORD")
        + "@"
        + os.getenv("MYSQL_HOST")
        + "/"
        + os.getenv("MYSQL_DATABASE")
    ),
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
}