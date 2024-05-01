from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from auth import auth
from rate_limiter import limiter
from database.model.tracker import Tracker
from database.mysql import db, format_database_error
from form.form_insert import InsertTrackerForm

bp = Blueprint("mysql", __name__, url_prefix="/tracker")


@bp.route("/insert/", methods=["POST", "GET"])
def insert_data():
    form = InsertTrackerForm()

    if form.validate_on_submit():
        name = form.name.data
        desc = form.description.data
        asset_img_url = form.asset_img_url.data
        tracker_img_url = form.tracker_img_url.data

        tracker = Tracker(
            name=name,
            description=desc,
            asset_img_url=asset_img_url,
            tracker_img_url=tracker_img_url,
        )
        db.session.add(tracker)
        db.session.commit()

        return redirect(url_for("smart_cultivation_system.smart_cultivation_system"))
    return render_template(
        "pages/smart_cultivation_system/insert_tracker.html", form=form
    )


@bp.route("/api/insert/", methods=["POST", "GET"])
@limiter.limit("5 per minute")
@auth.login_required()
def insert_data_api():
    if request.method == "POST":
        name = request.form.get("name")
        desc = request.form.get("description")
        asset_img_url = request.form.get("asset_img_url")
        tracker_img_url = request.form.get("tracker_img_url")

        if not any([name, asset_img_url, tracker_img_url]):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            tracker = Tracker(
                name=name,
                description=desc,
                asset_img_url=asset_img_url,
                tracker_img_url=tracker_img_url,
            )
            db.session.add(tracker)
            db.session.commit()
            return (
                jsonify(
                    {
                        "status": {
                            "code": 201,
                            "message": "tracker created successfully",
                        },
                        "tracker": {
                            "id": tracker.id,
                            "name": name,
                            "description": desc,
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
