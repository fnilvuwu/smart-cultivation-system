from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["600 per day", "150 per hour"],
    storage_uri="memory://",
)


def init_rate_limiter(app):
    limiter.init_app(app)
