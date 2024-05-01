from flask import Blueprint, render_template, jsonify


bp = Blueprint("errors", __name__)


@bp.app_errorhandler(400)
def bad_request(error):
    return render_template("pages/errors/400.html"), 400


@bp.app_errorhandler(404)
def not_found(error):
    return render_template("pages/errors/404.html"), 404


@bp.app_errorhandler(405)
def method_not_allowed(error):
    return render_template("pages/errors/405.html"), 405


@bp.app_errorhandler(429)
def rate_limit_exceeded(error):
    return render_template("pages/errors/429.html"), 429


@bp.app_errorhandler(429)
def rate_limit_exceeded_json(error):
    return jsonify({
        "status": {
            "code": 429,
            "message": "Rate limit exceeded. Please try again later."
        },
        "data": None
    }), 429


@bp.app_errorhandler(500)
def internal_server_error(error):
    return render_template("pages/errors/500.html"), 500
