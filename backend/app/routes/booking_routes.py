import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Booking, Room, Guest, Cancellation, Payment, User

booking_bp = Blueprint('bookings', __name__, url_prefix='/api/v1/bookings')

def generate_booking_ref():
    return f"HB-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"

@booking_bp.route('', methods=['GET'])
@jwt_required()
def get_bookings():
    status = request.args.get('status')
    search = request.args.get('search')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Booking.query.order_by(Booking.id.desc())
    
    if status:
        query = query.filter_by(status=status)

    if start_date:
        try:
            sd = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Booking.check_in_date >= sd)
        except ValueError:
            pass

    if end_date:
        try:
            ed = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Booking.check_out_date <= ed)
        except ValueError:
            pass

    if search:
        query = query.join(Guest).filter(
            (Guest.full_name.ilike(f'%{search}%')) |
            (Booking.booking_reference.ilike(f'%{search}%'))
        )

    bookings = query.all()
    return jsonify({'bookings': [b.to_dict() for b in bookings]}), 200


@booking_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': f'Booking with ID {booking_id} not found'}), 404
    return jsonify({'booking': booking.to_dict()}), 200


@booking_bp.route('', methods=['POST'])
@jwt_required()
def create_booking():
    data = request.get_json() or {}
    guest_id = data.get('guest_id')
    room_id = data.get('room_id')
    check_in_str = data.get('check_in_date')
    check_out_str = data.get('check_out_date')
    num_guests = data.get('num_guests', 1)
    payment_method = data.get('payment_method', 'upi')

    # Validation 1: Required fields
    if not guest_id or not room_id or not check_in_str or not check_out_str:
        return jsonify({'error': 'guest_id, room_id, check_in_date, and check_out_date are required'}), 400

    # Validation 2: Guest & Room exist
    guest = Guest.query.get(guest_id)
    if not guest:
        return jsonify({'error': f'Guest with ID {guest_id} does not exist'}), 404

    room = Room.query.get(room_id)
    if not room:
        return jsonify({'error': f'Room with ID {room_id} does not exist'}), 404

    # Validation 3: Room maintenance check
    if room.status == 'maintenance':
        return jsonify({'error': f'Room {room.room_number} is under maintenance and cannot be booked.'}), 400

    # Validation 4: Date parsing & logic
    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    if check_out <= check_in:
        return jsonify({'error': 'Check-out date must be strictly after check-in date'}), 400

    # Validation 5: Room capacity check
    if room.room_type and num_guests > room.room_type.capacity:
        return jsonify({'error': f'Guest count ({num_guests}) exceeds room capacity ({room.room_type.capacity})'}), 400

    # Validation 6: Overlapping date reservation conflict check
    conflict = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.status.in_(['confirmed', 'checked_in']),
        Booking.check_in_date < check_out,
        Booking.check_out_date > check_in
    ).first()

    if conflict:
        return jsonify({'error': f'Room {room.room_number} is already booked for the selected date range ({conflict.booking_reference})'}), 409

    # Pricing calculation
    nights = (check_out - check_in).days
    total_amount = float(room.room_type.base_price) * nights

    current_user_id_str = get_jwt_identity()
    user_id = int(current_user_id_str) if (current_user_id_str and str(current_user_id_str).isdigit()) else None

    booking = Booking(
        booking_reference=generate_booking_ref(),
        guest_id=guest_id,
        room_id=room_id,
        check_in_date=check_in,
        check_out_date=check_out,
        num_guests=num_guests,
        status='confirmed',
        total_amount=total_amount,
        payment_status='paid',
        created_by=user_id
    )

    db.session.add(booking)
    db.session.flush()

    # Automatically log initial payment transaction
    payment = Payment(
        booking_id=booking.id,
        payment_method=payment_method,
        amount=total_amount,
        transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
        status='completed'
    )
    db.session.add(payment)
    db.session.commit()

    return jsonify({
        'message': 'Booking created successfully',
        'booking': booking.to_dict()
    }), 201


@booking_bp.route('/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': f'Booking with ID {booking_id} not found'}), 404

    if booking.status in ['checked_out', 'cancelled']:
        return jsonify({'error': f'Cannot modify a booking with status {booking.status}'}), 400

    data = request.get_json() or {}
    if 'num_guests' in data:
        booking.num_guests = data['num_guests']

    db.session.commit()
    return jsonify({'message': 'Booking updated successfully', 'booking': booking.to_dict()}), 200


@booking_bp.route('/<int:booking_id>/check-in', methods=['POST'])
@jwt_required()
def check_in_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': f'Booking with ID {booking_id} not found'}), 404

    # Strict lifecycle state transition guard
    if booking.status == 'checked_in':
        return jsonify({'error': 'Guest is already checked in.'}), 400
    if booking.status == 'checked_out':
        return jsonify({'error': 'Cannot check in a booking that has already been checked out.'}), 400
    if booking.status == 'cancelled':
        return jsonify({'error': 'Cannot check in a cancelled booking.'}), 400
    if booking.status != 'confirmed':
        return jsonify({'error': f'Invalid status transition from {booking.status} to checked_in.'}), 400

    booking.status = 'checked_in'
    if booking.room:
        booking.room.status = 'occupied'
    db.session.commit()

    return jsonify({'message': 'Guest checked in successfully', 'booking': booking.to_dict()}), 200


@booking_bp.route('/<int:booking_id>/check-out', methods=['POST'])
@jwt_required()
def check_out_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': f'Booking with ID {booking_id} not found'}), 404

    # Strict lifecycle state transition guard
    if booking.status == 'checked_out':
        return jsonify({'error': 'Booking is already checked out.'}), 400
    if booking.status == 'cancelled':
        return jsonify({'error': 'Cannot check out a cancelled booking.'}), 400
    if booking.status != 'checked_in':
        return jsonify({'error': 'Guest must be checked in before checking out.'}), 400

    booking.status = 'checked_out'
    if booking.room:
        booking.room.status = 'available'
    db.session.commit()

    return jsonify({'message': 'Guest checked out successfully', 'booking': booking.to_dict()}), 200
