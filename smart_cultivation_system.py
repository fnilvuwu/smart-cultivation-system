from flask import Blueprint, render_template
from cache import cache
from database.model.tracker import Tracker
from database.model.location import Location

bp = Blueprint("smart_cultivation_system", __name__,
               url_prefix="/smart_cultivation_system")


@bp.route("/")
@cache.cached(timeout=15)
def smart_cultivation_system():
    trackers = Tracker.query.all()
    return render_template("pages/smart_cultivation_system/index.html", trackers=trackers)


@bp.route("/<int:tracker_id>")
@cache.cached(timeout=15)
def smart_cultivation_system_tracker(tracker_id):
    # trackers = Tracker.query.all()
    tracker = Tracker.query.filter_by(id=tracker_id).first()

    data = Location.query.filter(Location.tracker_id == tracker_id).all()
    locations = [location.to_dict() for location in data]
    return render_template(
        "pages/smart_cultivation_system/trackers.html",
        locations=locations,
        tracker=tracker,
    )
