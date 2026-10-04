from datetime import datetime
from . import db

class Cancellation(db.Model):
    __tablename__ = 'cancellations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, unique=True)
    cancelled_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(255))
    cancellation_fee = db.Column(db.Numeric(10, 2), default=0.00)
    refund_amount = db.Column(db.Numeric(10, 2), default=0.00)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'booking_reference': self.booking.booking_reference if self.booking else None,
            'guest_name': self.booking.guest.full_name if (self.booking and self.booking.guest) else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'reason': self.reason,
            'cancellation_fee': float(self.cancellation_fee),
            'refund_amount': float(self.refund_amount)
        }
