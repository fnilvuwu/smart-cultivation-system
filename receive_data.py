from flask import Blueprint, request, jsonify
from datetime import datetime
from auth import auth
from rate_limiter import limiter
from socket_io import socketio

from database.model.location import Location
from database.mysql import db, format_database_error

bp = Blueprint("receive_data", __name__)


@bp.route("/receive_data", methods=["GET", "POST"])
@limiter.limit("5 per minute")
@auth.login_required()
def receive_data_from_esp32():
    if request.method == "POST":
        input_data = request.get_json()
        tracker_id = input_data["tracker_id"]
        lat = input_data["lat"]
        lon = input_data["lon"]
        timestamp = input_data["timestamp"]

        try:
            location = Location(tracker_id, lat, lon, timestamp)
            db.session.add(location)
            db.session.commit()
            return (
                jsonify(
                    {
                        "status": {
                            "code": 201,
                            "message": "Data received and saved successfully",
                        },
                        "data": {
                            "tracker_id": tracker_id,
                            "lat": lat,
                            "lon": lon,
                            "timestamp": timestamp,
                        },
                    }
                ),
                201,
            )
        except Exception as e:
            db.session.rollback()
            error_msg = format_database_error(e)
            return (
                jsonify(
                    {
                        "status": {"code": 500, "message": error_msg},
                        "data": None,
                    }
                ),
                500,
            )
    else:
        return (
            jsonify(
                {"status": {"code": 405, "message": "Method not allowed"}, "data": None}
            ),
            405,
        )


@bp.route("/broadcast", methods=["POST"])
def broadcast():
    if request.method == "POST":
        input_data = request.get_json()
        message = input_data["message"]
        socketio.emit('new_broadcast', message)
        return jsonify({
            "status": {
                "code": 200,
                "message": "Success broadcasting new messae",
            },
            "data": None,
        }), 200
