from datetime import datetime, date
from models import db

class Animal(db.Model):
    __tablename__ = 'animals'

    id = db.Column(db.Integer, primary_key=True)
    tag_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=True)
    species = db.Column(db.String(50), default='Cow')  # Cow, Buffalo, Goat, Other
    breed = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), default='Female')
    dob = db.Column(db.Date, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    milking_status = db.Column(db.String(50), default='Milking')  # Milking, Dry, Pregnant, Sick, Calf, Sold
    health_status = db.Column(db.String(50), default='Healthy')   # Healthy, Under Treatment, Quarantined, Critical
    qr_code_image = db.Column(db.String(255), nullable=True)
    entry_date = db.Column(db.Date, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    milk_records = db.relationship('MilkProduction', backref='animal', lazy='dynamic', cascade='all, delete-orphan')
    vaccinations = db.relationship('Vaccination', backref='animal', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def display_name(self):
        return f"{self.tag_number} ({self.name})" if self.name else self.tag_number

    @property
    def age(self):
        if not self.dob:
            return "N/A"
        today = date.today()
        years = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        months = (today.year - self.dob.year) * 12 + today.month - self.dob.month
        if years >= 1:
            rem_months = months % 12
            return f"{years} yr {rem_months} mo" if rem_months else f"{years} yrs"
        return f"{months} months" if months > 0 else "< 1 month"

    @property
    def total_milk(self):
        records = self.milk_records.all()
        return round(sum(r.quantity_liters for r in records), 2) if records else 0.0

    @property
    def today_milk(self):
        records = self.milk_records.filter_by(date=date.today()).all()
        return round(sum(r.quantity_liters for r in records), 2) if records else 0.0

    def __repr__(self):
        return f"<Animal {self.tag_number} - {self.breed}>"
