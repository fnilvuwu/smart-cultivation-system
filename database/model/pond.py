from datetime import datetime
from database.mysql import db
from database.model.association_tables import employee_ponds


class Pond(db.Model):
    __tablename__ = "ponds"

    pond_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pond_name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    water_qualities = db.relationship("WaterQuality", backref="pond", lazy=True)
    fish_data = db.relationship("FishData", back_populates="pond", lazy=True)
    metrics = db.relationship("FishPondMetrics", backref="pond", lazy=True)
    employees = db.relationship(
        "Employee", secondary=employee_ponds, back_populates="ponds"
    )

    def __init__(self, pond_name, owner_id, location=None):
        self.pond_name = pond_name
        self.owner_id = owner_id
        self.location = location

    def to_dict(self):
        return {
            "pond_id": self.pond_id,
            "pond_name": self.pond_name,
            "location": self.location,
            "creation_date": self.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
            "owner_id": self.owner_id,
        }

class WaterQuality(db.Model):
    __tablename__ = "water_qualities"

    water_quality_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pond_id = db.Column(db.Integer, db.ForeignKey("ponds.pond_id"), nullable=False)
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)  # Make date optional
    pH = db.Column(db.Float, nullable=False)
    turbidity = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    nitrate = db.Column(db.Float, nullable=False)
    ammonia = db.Column(db.Float, nullable=False)  # Add ammonia
    dissolved_oxygen = db.Column(db.Float, nullable=False)  # Add dissolved oxygen
    quality_grade = db.Column(db.String(10), nullable=False)
    recorded_by = db.Column(
        db.Integer, db.ForeignKey("employees.employee_id"), nullable=False
    )

    recorded_by_employee = db.relationship('Employee', back_populates='water_quality_records')

    def __init__(self, pond_id, pH, turbidity, temperature, nitrate, ammonia, dissolved_oxygen, employee_id, date=None):
        self.pond_id = pond_id
        self.pH = pH
        self.turbidity = turbidity
        self.temperature = temperature
        self.nitrate = nitrate
        self.ammonia = ammonia
        self.dissolved_oxygen = dissolved_oxygen
        self.recorded_by = employee_id
        self.date = date or datetime.now().replace(microsecond=0)  # Use current time if date is None
        # Use get_quality_grade method to set the quality_grade
        self.quality_grade = self.get_quality_grade()

    def get_quality_grade(self):
        """
        Determine the water quality grade (category) based on the water parameters.
        This is the method to populate the `quality_grade` field.
        """
        from predict import get_quality_grade
        return get_quality_grade(
            self.temperature, 
            self.turbidity, 
            self.dissolved_oxygen, 
            self.pH, 
            self.ammonia, 
            self.nitrate
        )

class FishData(db.Model):
    __tablename__ = "fish_data"

    fish_data_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pond_id = db.Column(db.Integer, db.ForeignKey("ponds.pond_id"), nullable=False)
    recorded_by = db.Column(
        db.Integer, db.ForeignKey("employees.employee_id"), nullable=False
    )
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)  # Make date optional
    fish_weight = db.Column(db.Float, nullable=False)
    fish_height = db.Column(db.Float, nullable=False)
    fish_population = db.Column(db.Integer, nullable=False)

    pond = db.relationship('Pond', back_populates='fish_data')
    recorded_by_employee = db.relationship('Employee', back_populates='fish_data_records')

    def __init__(self, pond_id, fish_weight, fish_height, fish_population, employee_id, date=None):
        self.pond_id = pond_id
        self.fish_weight = fish_weight
        self.fish_height = fish_height
        self.fish_population = fish_population
        self.recorded_by = employee_id
        self.date = date or datetime.now().replace(microsecond=0)  # Use current time if date is None

    def to_dict(self):
        return {
            "fish_data_id": self.fish_data_id,
            "pond_id": self.pond_id,
            "recorded_by": self.recorded_by,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),
            "fish_weight": self.fish_weight,
            "fish_height": self.fish_height,
            "fish_population": self.fish_population,
        }


class FishPondMetrics(db.Model):
    __tablename__ = "fish_pond_metrics"

    metric_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pond_id = db.Column(db.Integer, db.ForeignKey("ponds.pond_id"), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_fish_weight = db.Column(db.Float, nullable=False)
    average_fish_weight = db.Column(db.Float, nullable=False)
    average_fish_height = db.Column(db.Float, nullable=False)
    total_population = db.Column(db.Integer, nullable=False)

    def __init__(
        self,
        pond_id,
        total_fish_weight,
        average_fish_weight,
        average_fish_height,
        total_population,
        date=None,
    ):
        self.pond_id = pond_id
        self.total_fish_weight = total_fish_weight
        self.average_fish_weight = average_fish_weight
        self.average_fish_height = average_fish_height
        self.total_population = total_population
        self.date = date if date else datetime.utcnow()

    def to_dict(self):
        return {
            "metric_id": self.metric_id,
            "pond_id": self.pond_id,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),
            "total_fish_weight": self.total_fish_weight,
            "average_fish_weight": self.average_fish_weight,
            "average_fish_height": self.average_fish_height,
            "total_population": self.total_population,
        }
