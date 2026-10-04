from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required
from app.models import db, Room, RoomType, Booking

room_bp = Blueprint('rooms', __name__, url_prefix='/api/v1/rooms')

@room_bp.route('', methods=['GET'])
def get_rooms():
    status_filter = request.args.get('status')
    type_filter = request.args.get('room_type_id')

    query = Room.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if type_filter:
        query = query.filter_by(room_type_id=type_filter)

    rooms = query.all()
    return jsonify({'rooms': [r.to_dict() for r in rooms]}), 200


@room_bp.route('/types', methods=['GET'])
def get_room_types():
    types = RoomType.query.all()
    return jsonify({'room_types': [t.to_dict() for t in types]}), 200


@room_bp.route('/availability', methods=['GET'])
def check_availability():
    check_in_str = request.args.get('check_in')
    check_out_str = request.args.get('check_out')

    if not check_in_str or not check_out_str:
        return jsonify({'error': 'check_in and check_out dates are required (YYYY-MM-DD)'}), 400

    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    if check_out <= check_in:
        return jsonify({'error': 'Check-out date must be after check-in date'}), 400

    # Subquery for booked room IDs during dates
    booked_room_ids = db.session.query(Booking.room_id).filter(
        Booking.status.in_(['confirmed', 'checked_in']),
        Booking.check_in_date < check_out,
        Booking.check_out_date > check_in
    ).subquery()

    available_rooms = Room.query.filter(
        Room.id.notin_(booked_room_ids),
        Room.status != 'maintenance'
    ).all()

    return jsonify({
        'check_in': check_in_str,
        'check_out': check_out_str,
        'available_count': len(available_rooms),
        'rooms': [r.to_dict() for r in available_rooms]
    }), 200


@room_bp.route('/<int:room_id>/status', methods=['PUT'])
@jwt_required()
def update_room_status(room_id):
    room = Room.query.get_or_404(room_id)
    data = request.get_json() or {}
    new_status = data.get('status')

    if new_status not in ['available', 'occupied', 'maintenance', 'cleaning']:
        return jsonify({'error': 'Invalid status'}), 400

    room.status = new_status
    db.session.commit()
    return jsonify({'message': 'Room status updated successfully', 'room': room.to_dict()}), 200
