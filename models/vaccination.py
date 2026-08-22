from datetime import datetime, date
from models import db

class Vaccination(db.Model):
    __tablename__ = 'vaccinations'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id', ondelete='CASCADE'), nullable=False, index=True)
    vaccine_name = db.Column(db.String(120), nullable=False)
    administered_date = db.Column(db.Date, nullable=False, default=date.today)
    next_due_date = db.Column(db.Date, nullable=False)
    veterinarian = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(30), default='Completed')  # 'Completed', 'Upcoming', 'Overdue'
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_overdue(self):
        if self.next_due_date and self.status != 'Completed':
            return self.next_due_date < date.today()
        return False

    @property
    def days_until_due(self):
        if self.next_due_date:
            delta = (self.next_due_date - date.today()).days
            return delta
        return None

    def update_status(self):
        today = date.today()
        if self.next_due_date:
            if self.next_due_date < today and self.status != 'Completed':
                self.status = 'Overdue'
            elif self.next_due_date >= today and self.status != 'Completed':
                self.status = 'Upcoming'

    def __repr__(self):
        return f"<Vaccination Animal:{self.animal_id} Vaccine:{self.vaccine_name}>"
