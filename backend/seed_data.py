import random
import uuid
from datetime import datetime, timedelta
from app import create_app
from app.models import db, Role, User, RoomType, Room, Guest, Booking, Cancellation, Payment
from run import init_db_defaults

app = create_app()

FIRST_NAMES = ['Aarav', 'Ananya', 'Rohan', 'Priya', 'Rahul', 'Sneha', 'Vikram', 'Neha', 'Aditya', 'Kavya', 'Siddharth', 'Meera', 'Rajesh', 'Pooja', 'Amit', 'Divya']
LAST_NAMES = ['Sharma', 'Verma', 'Patel', 'Nair', 'Iyer', 'Gupta', 'Reddy', 'Chowdhury', 'Bose', 'Kumar', 'Singh', 'Deshmukh', 'Joshi', 'Menon']
CITIES = ['Mumbai', 'Delhi', 'Bengaluru', 'Chennai', 'Kochi', 'Hyderabad', 'Kolkata', 'Pune', 'Ahmedabad', 'Goa']
REASONS = ['Change of Travel Plans', 'Personal Emergency', 'Flight Cancellation', 'Found Alternative Stay', 'Medical Emergency', 'Work Schedule Shift']
PAYMENT_METHODS = ['upi', 'credit_card', 'debit_card', 'net_banking', 'cash']

def generate_mock_data(total_bookings=500):
    with app.app_context():
        # Ensure database tables and base inventory exist
        db.create_all()
        init_db_defaults()

        print(f"Starting seed data generation for {total_bookings} records...")
        
        room_types = RoomType.query.all()
        rooms = Room.query.all()
        admin_user = User.query.first()

        # 1. Generate Guests
        guests = []
        for i in range(120):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            guest = Guest(
                full_name=f"{fn} {ln}",
                email=f"{fn.lower()}.{ln.lower()}{random.randint(100,999)}@gmail.com",
                phone=f"98{random.randint(10000000, 99999999)}",
                id_proof_type='Aadhaar Card',
                id_proof_number=f"{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                address=f"Flat {random.randint(101,909)}, MG Road",
                city=random.choice(CITIES),
                country='India'
            )
            guests.append(guest)
        db.session.add_all(guests)
        db.session.commit()
        print(f"[OK] Generated {len(guests)} guest profiles.")

        # Refresh guests list
        guests = Guest.query.all()

        # 2. Generate Bookings across past 365 days
        start_date = datetime.now() - timedelta(days=365)
        created_bookings = 0
        cancellation_count = 0

        for i in range(total_bookings):
            # Pick random check-in date
            days_offset = random.randint(0, 360)
            check_in = start_date + timedelta(days=days_offset)
            stay_nights = random.choice([1, 2, 2, 3, 3, 4, 5, 7])
            check_out = check_in + timedelta(days=stay_nights)

            # Pick room and guest
            room = random.choice(rooms)
            guest = random.choice(guests)
            base_price = float(room.room_type.base_price)
            total_amount = base_price * stay_nights

            # Status logic (18% cancelled, 70% checked_out, 12% checked_in / confirmed)
            status_rand = random.random()
            if status_rand < 0.18:
                status = 'cancelled'
                payment_status = 'refunded'
            elif status_rand < 0.88:
                status = 'checked_out'
                payment_status = 'paid'
            else:
                status = 'confirmed'
                payment_status = 'paid'

            lead_time_days = random.choice([1, 2, 3, 5, 7, 10, 14, 21, 30])
            booking_created_at = check_in - timedelta(days=lead_time_days)

            ref_code = f"HB-{check_in.strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"

            booking = Booking(
                booking_reference=ref_code,
                guest_id=guest.id,
                room_id=room.id,
                check_in_date=check_in.date(),
                check_out_date=check_out.date(),
                num_guests=random.randint(1, room.room_type.capacity),
                status=status,
                total_amount=total_amount,
                payment_status=payment_status,
                created_by=admin_user.id if admin_user else None,
                created_at=booking_created_at
            )
            db.session.add(booking)
            db.session.flush()

            # Create payment record
            pay_method = random.choice(PAYMENT_METHODS)
            payment = Payment(
                booking_id=booking.id,
                payment_method=pay_method,
                amount=total_amount,
                payment_date=booking_created_at,
                transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
                status='refunded' if status == 'cancelled' else 'completed'
            )
            db.session.add(payment)

            # Create cancellation record if cancelled
            if status == 'cancelled':
                fee = random.choice([0.0, 500.0, 1000.0])
                refund = max(0.0, total_amount - fee)
                cancellation = Cancellation(
                    booking_id=booking.id,
                    cancelled_at=booking_created_at + timedelta(days=random.randint(0, max(0, lead_time_days - 1))),
                    reason=random.choice(REASONS),
                    cancellation_fee=fee,
                    refund_amount=refund,
                    processed_by=admin_user.id if admin_user else None
                )
                db.session.add(cancellation)
                cancellation_count += 1

            created_bookings += 1

        db.session.commit()
        print(f"[OK] Successfully seeded {created_bookings} bookings with {cancellation_count} cancellations.")

if __name__ == '__main__':
    generate_mock_data(500)
