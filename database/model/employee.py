from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database.mysql import db
from database.model.association_tables import employee_ponds
from database.model.pond import WaterQuality
from database.model.pond import FishData

class Employee(UserMixin, db.Model):
    __tablename__ = 'employees'
    
    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    employee_email = db.Column(db.String(255), unique=True, nullable=False)
    employee_name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    role = db.Column(db.String(50), nullable=False, default='employee')

    user = db.relationship('User', back_populates='employees')
    ponds = db.relationship('Pond', secondary=employee_ponds, back_populates='employees')
    fish_data_records = db.relationship('FishData', back_populates='recorded_by_employee')
    water_quality_records = db.relationship('WaterQuality', back_populates='recorded_by_employee')

    def __init__(self, user_id, employee_name, employee_email, password):
        self.user_id = user_id
        self.employee_name = employee_name
        self.employee_email = employee_email
        self.password_hash = generate_password_hash(password)
        self.role = 'employee'

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Return string id for flask-login."""
        return f'E{self.employee_id}'

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_role(self):
        """Return role for authorization checks."""
        return self.role
