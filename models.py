from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_deaf = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        """Хеширует пароль и сохраняет его в password_hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверяет правильность введенного пароля."""
        return check_password_hash(self.password_hash, password)

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.String(50), nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_inclusive = db.Column(db.Boolean, default=False)
    
    organizer = db.relationship('User', backref=db.backref('events', lazy=True))

class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='_user_event_uc'),)