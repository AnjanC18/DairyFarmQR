from datetime import datetime, date
from models import db

class FeedInventory(db.Model):
    __tablename__ = 'feed_inventories'

    id = db.Column(db.Integer, primary_key=True)
    feed_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Green Fodder, Dry Fodder, Concentrate, Mineral Mixture, Silage, Other
    current_stock = db.Column(db.Float, default=0.0, nullable=False)
    unit = db.Column(db.String(20), default='kg')
    unit_cost = db.Column(db.Float, default=0.0, nullable=False)
    minimum_threshold = db.Column(db.Float, default=50.0)
    supplier = db.Column(db.String(150), nullable=True)
    last_restocked = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    consumptions = db.relationship('FeedConsumption', backref='feed_item', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def is_low_stock(self):
        return self.current_stock <= (self.minimum_threshold or 0)

    @property
    def stock_value(self):
        return round(self.current_stock * self.unit_cost, 2)

    def __repr__(self):
        return f"<FeedInventory {self.feed_name} Stock:{self.current_stock}{self.unit}>"


class FeedConsumption(db.Model):
    __tablename__ = 'feed_consumptions'

    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('feed_inventories.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    quantity_used = db.Column(db.Float, nullable=False)
    group_or_animal = db.Column(db.String(100), default='All Milking Cattle')
    cost = db.Column(db.Float, default=0.0)
    recorded_by = db.Column(db.String(100), default='Admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FeedConsumption Feed:{self.feed_id} Used:{self.quantity_used}>"
