from datetime import date
from flask import Blueprint, jsonify
from sqlalchemy import func, extract
from flask_jwt_extended import jwt_required
from app.models import db, Booking, Room, RoomType, Cancellation, Payment

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/v1/analytics')

@analytics_bp.route('/summary', methods=['GET'])
def get_summary_kpis():
    today = date.today()

    # 1. Total Revenue (Valid status: confirmed, checked_in, checked_out)
    revenue_res = db.session.query(func.sum(Booking.total_amount)).filter(
        Booking.status.in_(['confirmed', 'checked_in', 'checked_out'])
    ).scalar()
    total_revenue = float(revenue_res) if revenue_res else 0.0

    # 2. Total Bookings
    total_bookings = Booking.query.count()

    # 3. Total Cancellations & Cancellation Rate
    total_cancellations = Booking.query.filter_by(status='cancelled').count()
    cancellation_rate = round((total_cancellations / total_bookings * 100), 2) if total_bookings > 0 else 0.0

    # 4. Rooms Count & Inventory Status
    total_rooms = Room.query.count()
    occupied_rooms = Room.query.filter_by(status='occupied').count()
    available_rooms = Room.query.filter_by(status='available').count()
    maintenance_rooms = Room.query.filter_by(status='maintenance').count()
    operational_rooms = total_rooms - maintenance_rooms
    current_occupancy_rate = round((occupied_rooms / operational_rooms * 100), 2) if operational_rooms > 0 else 0.0

    # 5. Today's Check-ins & Check-outs
    todays_check_ins = Booking.query.filter_by(check_in_date=today).count()
    todays_check_outs = Booking.query.filter_by(check_out_date=today).count()

    # 6. Total Refund Loss & Retained Fees
    refund_res = db.session.query(func.sum(Cancellation.refund_amount)).scalar()
    total_refund_loss = float(refund_res) if refund_res else 0.0

    # 7. Average Daily Rate (ADR) = Total Valid Room Revenue / Sold Room Nights
    valid_bookings = Booking.query.filter(Booking.status.in_(['confirmed', 'checked_in', 'checked_out'])).all()
    total_nights = sum([b.nights_stayed for b in valid_bookings])
    adr = round(total_revenue / total_nights, 2) if total_nights > 0 else 0.0

    # 8. Historical Period Occupancy Rate (%) = (Occupied Room Nights / Available Room Nights) * 100
    earliest_date = db.session.query(func.min(Booking.check_in_date)).scalar()
    latest_date = db.session.query(func.max(Booking.check_in_date)).scalar()
    period_days = (latest_date - earliest_date).days + 1 if (earliest_date and latest_date) else 365
    total_available_room_nights = operational_rooms * period_days
    historical_occupancy_rate = round((total_nights / total_available_room_nights * 100), 2) if total_available_room_nights > 0 else 0.0

    # 9. RevPAR (Revenue Per Available Room)
    revpar = round((historical_occupancy_rate / 100.0) * adr, 2)

    return jsonify({
        'kpis': {
            'total_revenue': total_revenue,
            'total_bookings': total_bookings,
            'total_cancellations': total_cancellations,
            'cancellation_rate': cancellation_rate,
            'total_rooms': total_rooms,
            'available_rooms': available_rooms,
            'occupied_rooms': occupied_rooms,
            'maintenance_rooms': maintenance_rooms,
            'current_occupancy_rate': current_occupancy_rate,
            'occupancy_rate': historical_occupancy_rate,  # Main historical period occupancy %
            'todays_check_ins': todays_check_ins,
            'todays_check_outs': todays_check_outs,
            'total_refund_loss': total_refund_loss,
            'adr': adr,
            'revpar': revpar,
            'total_nights_stayed': total_nights,
            'total_available_nights': total_available_room_nights
        }
    }), 200


@analytics_bp.route('/revenue-by-type', methods=['GET'])
def get_revenue_by_room_type():
    results = db.session.query(
        RoomType.type_name,
        func.sum(Booking.total_amount).label('total_revenue'),
        func.count(Booking.id).label('booking_count')
    ).join(Room, Room.room_type_id == RoomType.id)\
     .join(Booking, Booking.room_id == Room.id)\
     .filter(Booking.status.in_(['confirmed', 'checked_in', 'checked_out']))\
     .group_by(RoomType.type_name)\
     .all()

    data = [
        {
            'room_type': type_name,
            'total_revenue': float(total_revenue),
            'booking_count': booking_count
        }
        for type_name, total_revenue, booking_count in results
    ]
    return jsonify({'revenue_by_room_type': data}), 200


@analytics_bp.route('/monthly-trend', methods=['GET'])
def get_monthly_trend():
    results = db.session.query(
        extract('year', Booking.check_in_date).label('year'),
        extract('month', Booking.check_in_date).label('month'),
        func.sum(Booking.total_amount).label('monthly_revenue'),
        func.count(Booking.id).label('total_bookings')
    ).filter(Booking.status.in_(['confirmed', 'checked_in', 'checked_out']))\
     .group_by('year', 'month')\
     .order_by('year', 'month')\
     .all()

    month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    data = [
        {
            'year': int(year),
            'month': int(month),
            'label': f"{month_names[int(month)]} {int(year)}",
            'monthly_revenue': float(monthly_revenue),
            'total_bookings': int(total_bookings)
        }
        for year, month, monthly_revenue, total_bookings in results
    ]
    return jsonify({'monthly_trend': data}), 200
