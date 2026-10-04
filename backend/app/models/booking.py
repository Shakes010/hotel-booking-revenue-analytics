from datetime import datetime
from . import db

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_reference = db.Column(db.String(30), nullable=False, unique=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guests.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    num_guests = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.Enum('confirmed', 'checked_in', 'checked_out', 'cancelled', name='booking_status'), default='confirmed')
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_status = db.Column(db.Enum('pending', 'paid', 'refunded', 'partially_paid', name='booking_payment_status'), default='pending')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cancellation = db.relationship('Cancellation', backref='booking', uselist=False, lazy=True)
    payments = db.relationship('Payment', backref='booking', lazy=True)

    @property
    def nights_stayed(self):
        if self.check_in_date and self.check_out_date:
            delta = self.check_out_date - self.check_in_date
            return max(delta.days, 1)
        return 1

    def to_dict(self):
        return {
            'id': self.id,
            'booking_reference': self.booking_reference,
            'guest_id': self.guest_id,
            'guest_name': self.guest.full_name if self.guest else None,
            'guest_email': self.guest.email if self.guest else None,
            'guest_phone': self.guest.phone if self.guest else None,
            'room_id': self.room_id,
            'room_number': self.room.room_number if self.room else None,
            'room_type_name': self.room.room_type.type_name if (self.room and self.room.room_type) else None,
            'check_in_date': self.check_in_date.isoformat() if self.check_in_date else None,
            'check_out_date': self.check_out_date.isoformat() if self.check_out_date else None,
            'nights_stayed': self.nights_stayed,
            'num_guests': self.num_guests,
            'status': self.status,
            'total_amount': float(self.total_amount),
            'payment_status': self.payment_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
