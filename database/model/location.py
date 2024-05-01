from database.mysql import db
from database.model.tracker import Tracker
from datetime import datetime

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracker_id = db.Column(db.Integer, db.ForeignKey("tracker.id"), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    tracker = db.relationship("Tracker", backref="locations")

    def __init__(self, tracker_id, lat, lon, timestamp):
        self.tracker_id = tracker_id
        self.lat = lat
        self.lon = lon
        self.timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "id": self.id,
            "tracker_id": self.tracker_id,
            "lat": self.lat,
            "lon": self.lon,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
