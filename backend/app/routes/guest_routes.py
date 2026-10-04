from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db, Guest, Booking

guest_bp = Blueprint('guests', __name__, url_prefix='/api/v1/guests')

@guest_bp.route('', methods=['GET'])
@jwt_required()
def get_guests():
    search = request.args.get('search')
    query = Guest.query
    if search:
        query = query.filter(
            (Guest.full_name.ilike(f'%{search}%')) |
            (Guest.email.ilike(f'%{search}%')) |
            (Guest.phone.ilike(f'%{search}%'))
        )
    guests = query.order_by(Guest.id.desc()).all()
    return jsonify({'guests': [g.to_dict() for g in guests]}), 200


@guest_bp.route('/<int:guest_id>', methods=['GET'])
@jwt_required()
def get_guest(guest_id):
    guest = Guest.query.get(guest_id)
    if not guest:
        return jsonify({'error': f'Guest with ID {guest_id} not found'}), 404
    return jsonify({'guest': guest.to_dict()}), 200


@guest_bp.route('', methods=['POST'])
@jwt_required()
def create_guest():
    data = request.get_json() or {}
    full_name = data.get('full_name')
    email = data.get('email')
    phone = data.get('phone')

    if not full_name or not email or not phone:
        return jsonify({'error': 'Full name, email, and phone are required'}), 400

    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Invalid email address format'}), 400

    guest = Guest(
        full_name=full_name.strip(),
        email=email.strip().lower(),
        phone=phone.strip(),
        id_proof_type=data.get('id_proof_type', 'Aadhaar / Passport'),
        id_proof_number=data.get('id_proof_number'),
        address=data.get('address'),
        city=data.get('city'),
        country=data.get('country', 'India')
    )
    db.session.add(guest)
    db.session.commit()

    return jsonify({'message': 'Guest registered successfully', 'guest': guest.to_dict()}), 201


@guest_bp.route('/<int:guest_id>', methods=['PUT'])
@jwt_required()
def update_guest(guest_id):
    guest = Guest.query.get(guest_id)
    if not guest:
        return jsonify({'error': f'Guest with ID {guest_id} not found'}), 404

    data = request.get_json() or {}
    if 'full_name' in data:
        guest.full_name = data['full_name'].strip()
    if 'email' in data:
        if '@' not in data['email']:
            return jsonify({'error': 'Invalid email address format'}), 400
        guest.email = data['email'].strip().lower()
    if 'phone' in data:
        guest.phone = data['phone'].strip()
    if 'address' in data:
        guest.address = data['address']
    if 'city' in data:
        guest.city = data['city']
    if 'id_proof_number' in data:
        guest.id_proof_number = data['id_proof_number']

    db.session.commit()
    return jsonify({'message': 'Guest profile updated successfully', 'guest': guest.to_dict()}), 200


@guest_bp.route('/<int:guest_id>', methods=['DELETE'])
@jwt_required()
def delete_guest(guest_id):
    guest = Guest.query.get(guest_id)
    if not guest:
        return jsonify({'error': f'Guest with ID {guest_id} not found'}), 404

    # Check historical bookings dependency
    booking_count = Booking.query.filter_by(guest_id=guest.id).count()
    if booking_count > 0:
        return jsonify({
            'error': f'Cannot delete guest record. {booking_count} historical booking(s) exist for this guest.',
            'booking_count': booking_count
        }), 409

    db.session.delete(guest)
    db.session.commit()
    return jsonify({'message': 'Guest profile deleted successfully'}), 200
