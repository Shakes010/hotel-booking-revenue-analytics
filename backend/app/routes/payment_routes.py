import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db, Payment, Booking

payment_bp = Blueprint('payments', __name__, url_prefix='/api/v1/payments')

@payment_bp.route('', methods=['GET'])
@jwt_required()
def get_payments():
    booking_id = request.args.get('booking_id')
    status = request.args.get('status')
    
    query = Payment.query.order_by(Payment.id.desc())
    if booking_id:
        query = query.filter_by(booking_id=booking_id)
    if status:
        query = query.filter_by(status=status)

    payments = query.all()
    return jsonify({'payments': [p.to_dict() for p in payments]}), 200


@payment_bp.route('/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({'error': f'Payment record with ID {payment_id} not found'}), 404
    return jsonify({'payment': payment.to_dict()}), 200


@payment_bp.route('', methods=['POST'])
@jwt_required()
def create_payment():
    data = request.get_json() or {}
    booking_id = data.get('booking_id')
    amount = data.get('amount')
    payment_method = data.get('payment_method', 'upi')

    if not booking_id or amount is None:
        return jsonify({'error': 'booking_id and amount are required'}), 400

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': f'Booking with ID {booking_id} does not exist'}), 404

    if float(amount) <= 0:
        return jsonify({'error': 'Payment amount must be greater than zero'}), 400

    transaction_id = data.get('transaction_id') or f"TXN-{uuid.uuid4().hex[:10].upper()}"

    # Duplicate transaction check
    existing = Payment.query.filter_by(transaction_id=transaction_id).first()
    if existing:
        return jsonify({'error': f'Payment with transaction_id {transaction_id} already recorded'}), 409

    payment = Payment(
        booking_id=booking_id,
        payment_method=payment_method,
        amount=float(amount),
        transaction_id=transaction_id,
        status=data.get('status', 'completed')
    )
    db.session.add(payment)
    db.session.commit()

    return jsonify({'message': 'Payment recorded successfully', 'payment': payment.to_dict()}), 201
