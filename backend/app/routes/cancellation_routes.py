from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Booking, Cancellation

cancellation_bp = Blueprint('cancellations', __name__, url_prefix='/api/v1/cancellations')

@cancellation_bp.route('', methods=['GET'])
@jwt_required()
def get_cancellations():
    cancellations = Cancellation.query.order_by(Cancellation.id.desc()).all()
    return jsonify({'cancellations': [c.to_dict() for c in cancellations]}), 200


@cancellation_bp.route('/process/<int:booking_id>', methods=['POST'])
@jwt_required()
def process_cancellation(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': f'Booking with ID {booking_id} not found'}), 404

    # Strict lifecycle guards
    if booking.status == 'cancelled':
        return jsonify({'error': 'Booking is already cancelled'}), 400
    if booking.status == 'checked_out':
        return jsonify({'error': 'Completed / checked-out bookings cannot be cancelled'}), 400

    data = request.get_json() or {}
    reason = data.get('reason', 'Guest Request')
    cancellation_fee = float(data.get('cancellation_fee', 500.00))

    total_amt = float(booking.total_amount)
    refund_amt = max(0.0, total_amt - cancellation_fee)

    booking.status = 'cancelled'
    booking.payment_status = 'refunded'
    if booking.room:
        booking.room.status = 'available'

    current_user_id_str = get_jwt_identity()
    user_id = int(current_user_id_str) if (current_user_id_str and str(current_user_id_str).isdigit()) else None

    cancellation = Cancellation(
        booking_id=booking.id,
        reason=reason,
        cancellation_fee=cancellation_fee,
        refund_amount=refund_amt,
        processed_by=user_id
    )

    db.session.add(cancellation)
    db.session.commit()

    return jsonify({
        'message': 'Booking cancelled successfully',
        'cancellation': cancellation.to_dict(),
        'booking': booking.to_dict()
    }), 200
