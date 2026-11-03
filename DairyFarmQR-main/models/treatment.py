from datetime import datetime, date
from models import db

class MedicalTreatment(db.Model):
    __tablename__ = 'medical_treatments'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id', ondelete='CASCADE'), nullable=False, index=True)
    diagnosis = db.Column(db.String(120), nullable=False)  # e.g. 'Clinical Mastitis', 'Subclinical Mastitis', 'Milk Fever', 'Bloat', 'Foot Rot'
    symptoms = db.Column(db.Text, nullable=True)
    treatment_given = db.Column(db.String(255), nullable=False)  # e.g. Antibiotics, Anti-inflammatory, Intramammary tubes
    administered_date = db.Column(db.Date, nullable=False, default=date.today)
    veterinarian = db.Column(db.String(100), nullable=True)
    withdrawal_period_days = db.Column(db.Integer, default=3)  # Milk withholding period in days
    status = db.Column(db.String(50), default='Under Treatment')  # 'Under Treatment', 'Recovered', 'Follow-up Needed'
    cost = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_in_withdrawal(self):
        """Returns True if the milk withdrawal period is currently active."""
        if not self.administered_date or not self.withdrawal_period_days:
            return False
        days_passed = (date.today() - self.administered_date).days
        return 0 <= days_passed < self.withdrawal_period_days

    @property
    def withdrawal_days_remaining(self):
        if not self.administered_date or not self.withdrawal_period_days:
            return 0
        days_passed = (date.today() - self.administered_date).days
        rem = self.withdrawal_period_days - days_passed
        return max(0, rem)

    def __repr__(self):
        return f"<MedicalTreatment Animal:{self.animal_id} Diagnosis:{self.diagnosis} Status:{self.status}>"
