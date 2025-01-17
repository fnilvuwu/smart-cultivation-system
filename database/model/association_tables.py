from database.mysql import db

# Association Table Definition
employee_ponds = db.Table('employee_ponds',
    db.Column('employee_id', db.Integer, db.ForeignKey('employees.employee_id'), primary_key=True),
    db.Column('pond_id', db.Integer, db.ForeignKey('ponds.pond_id'), primary_key=True)
)
