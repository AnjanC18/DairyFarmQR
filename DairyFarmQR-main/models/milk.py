from datetime import datetime, date
from models import db

class MilkProduction(db.Model):
    __tablename__ = 'milk_productions'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id', ondelete='CASCADE'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    session = db.Column(db.String(20), nullable=False)  # 'Morning', 'Evening', 'Afternoon'
    quantity_liters = db.Column(db.Float, nullable=False)
    fat_percentage = db.Column(db.Float, default=4.0)
    snf_percentage = db.Column(db.Float, default=8.5)
    rate_per_liter = db.Column(db.Float, default=40.0)
    total_amount = db.Column(db.Float, default=0.0)
    recorded_by = db.Column(db.String(100), default='Admin')
    remarks = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def calculate_total(self):
        if self.quantity_liters and self.rate_per_liter:
            self.total_amount = round(self.quantity_liters * self.rate_per_liter, 2)
        else:
            self.total_amount = 0.0

    def __repr__(self):
        return f"<MilkRecord Animal:{self.animal_id} Date:{self.date} Qty:{self.quantity_liters}L>"
