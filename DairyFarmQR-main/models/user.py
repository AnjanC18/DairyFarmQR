from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    plain_password = db.Column(db.String(100), nullable=True)  # Admin credential viewer
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='staff')  # 'admin', 'manager', 'staff'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username=None, email=None, full_name=None, role='staff', is_active=True, plain_password=None, password_hash=None, **kwargs):
        super().__init__(**kwargs)
        if username is not None:
            self.username = username
        if email is not None:
            self.email = email
        if full_name is not None:
            self.full_name = full_name
        if role is not None:
            self.role = role
        self.is_active = is_active
        if plain_password is not None:
            self.plain_password = plain_password
        if password_hash is not None:
            self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.plain_password = password

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_manager(self):
        return self.role in ('admin', 'manager')

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
