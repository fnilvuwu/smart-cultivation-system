from flask import Blueprint, render_template
from rate_limiter import limiter
from cache import cache


bp = Blueprint("index", __name__)


@bp.route("/")
@limiter.limit("5 per day")
@cache.cached(timeout=60)
def index():
    return render_template("pages/index.html")
