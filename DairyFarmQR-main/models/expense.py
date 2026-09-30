from datetime import datetime, date
from models import db

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(60), nullable=False)  # Feed, Veterinary & Medical, Maintenance & Repairs, Labor & Wages, Utilities & Electricity, Equipment & Machinery, Fuel & Transport, Miscellaneous
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    paid_to = db.Column(db.String(120), nullable=True)
    payment_method = db.Column(db.String(30), default='Cash')  # Cash, Bank Transfer, UPI, Cheque
    receipt_number = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Expense {self.title} - {self.amount}>"
