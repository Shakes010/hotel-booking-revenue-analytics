from datetime import datetime
from . import db

class Guest(db.Model):
    __tablename__ = 'guests'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    id_proof_type = db.Column(db.String(50), default='Aadhaar / Passport')
    id_proof_number = db.Column(db.String(50))
    address = db.Column(db.String(255))
    city = db.Column(db.String(50))
    country = db.Column(db.String(50), default='India')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='guest', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'id_proof_type': self.id_proof_type,
            'id_proof_number': self.id_proof_number,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
