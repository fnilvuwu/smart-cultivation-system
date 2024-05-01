from database.mysql import db


class Tracker(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    asset_img_url = db.Column(db.String(255), nullable=True)
    tracker_img_url = db.Column(db.String(255), nullable=True)

    def __init__(self, name, description, asset_img_url, tracker_img_url):
        self.name = name
        self.description = description
        self.asset_img_url = asset_img_url,
        self.tracker_img_url = tracker_img_url,
