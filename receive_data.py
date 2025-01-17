from flask import Blueprint, request, jsonify
from datetime import datetime
from auth import auth
from rate_limiter import limiter
from socket_io import socketio

from database.model.pond import WaterQuality, FishData, FishPondMetrics
from database.mysql import db, format_database_error

bp = Blueprint("receive_data", __name__)

@bp.route("/receive_data", methods=["GET", "POST"])
@limiter.limit("5 per minute")
@auth.login_required()
def receive_data_from_esp32():
    if request.method == "POST":
        input_data = request.get_json()
        pond_id = input_data["pond_id"]
        pH = input_data["pH"]
        turbidity = input_data["turbidity"]
        temperature = input_data["temperature"]
        nitrate = input_data["nitrate"]
        fish_weight = input_data["fish_weight"]
        fish_height = input_data["fish_height"]
        fish_population = input_data["fish_population"]
        total_fish_weight = input_data["total_fish_weight"]
        average_fish_weight = input_data["average_fish_weight"]
        average_fish_height = input_data["average_fish_height"]
        total_population = input_data["total_population"]
        timestamp = input_data["timestamp"]

        try:
            water_quality = WaterQuality(pond_id, pH, turbidity, temperature, nitrate, timestamp)
            fish_data = FishData(pond_id, fish_weight, fish_height, fish_population, timestamp)
            metrics = FishPondMetrics(pond_id, total_fish_weight, average_fish_weight, average_fish_height, total_population, timestamp)
            
            db.session.add(water_quality)
            db.session.add(fish_data)
            db.session.add(metrics)
            db.session.commit()

            return (
                jsonify(
                    {
                        "status": {
                            "code": 201,
                            "message": "Data received and saved successfully",
                        },
                        "data": {
                            "pond_id": pond_id,
                            "pH": pH,
                            "turbidity": turbidity,
                            "temperature": temperature,
                            "nitrate": nitrate,
                            "fish_weight": fish_weight,
                            "fish_height": fish_height,
                            "fish_population": fish_population,
                            "total_fish_weight": total_fish_weight,
                            "average_fish_weight": average_fish_weight,
                            "average_fish_height": average_fish_height,
                            "total_population": total_population,
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
                "message": "Success broadcasting new message",
            },
            "data": None,
        }), 200
