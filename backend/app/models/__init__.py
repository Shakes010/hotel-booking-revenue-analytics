from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import Role, User
from .room import RoomType, Room
from .guest import Guest
from .booking import Booking
from .cancellation import Cancellation
from .payment import Payment

__all__ = ['db', 'Role', 'User', 'RoomType', 'Room', 'Guest', 'Booking', 'Cancellation', 'Payment']
