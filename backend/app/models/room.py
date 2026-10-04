from datetime import datetime
from . import db

class RoomType(db.Model):
    __tablename__ = 'room_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(50), nullable=False, unique=True)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=2)
    description = db.Column(db.Text)
    total_rooms = db.Column(db.Integer, nullable=False, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    rooms = db.relationship('Room', backref='room_type', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'type_name': self.type_name,
            'base_price': float(self.base_price),
            'capacity': self.capacity,
            'description': self.description,
            'total_rooms': self.total_rooms
        }


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_number = db.Column(db.String(20), nullable=False, unique=True)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_types.id'), nullable=False)
    status = db.Column(db.Enum('available', 'occupied', 'maintenance', 'cleaning', name='room_status'), default='available')
    floor = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='room', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'room_number': self.room_number,
            'room_type_id': self.room_type_id,
            'room_type_name': self.room_type.type_name if self.room_type else None,
            'base_price': float(self.room_type.base_price) if self.room_type else 0.0,
            'status': self.status,
            'floor': self.floor
        }
