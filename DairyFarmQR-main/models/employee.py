from datetime import datetime, date
from models import db

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    salary = db.Column(db.Float, default=0.0, nullable=False)
    joining_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(30), default='Active')  # 'Active', 'On Leave', 'Inactive'
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Employee {self.name} ({self.role})>"
