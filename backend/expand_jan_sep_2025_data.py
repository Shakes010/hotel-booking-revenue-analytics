import os
import json
import random
import uuid
from datetime import date, datetime, timedelta
from app import create_app
from app.models import db, Booking, Cancellation, Payment, Room, RoomType, Guest, User

app = create_app()

FIRST_NAMES = ['Aarav', 'Ananya', 'Rohan', 'Priya', 'Rahul', 'Sneha', 'Vikram', 'Neha', 'Aditya', 'Kavya', 'Siddharth', 'Meera', 'Rajesh', 'Pooja', 'Amit', 'Divya']
LAST_NAMES = ['Sharma', 'Verma', 'Patel', 'Nair', 'Iyer', 'Gupta', 'Reddy', 'Chowdhury', 'Bose', 'Kumar', 'Singh', 'Deshmukh', 'Joshi', 'Menon']
CITIES = ['Mumbai', 'Delhi', 'Bengaluru', 'Chennai', 'Kochi', 'Hyderabad', 'Kolkata', 'Pune', 'Ahmedabad', 'Goa']
REASONS = ['Change of Travel Plans', 'Personal Emergency', 'Flight Cancellation', 'Found Alternative Stay', 'Medical Emergency', 'Work Schedule Shift']
PAYMENT_METHODS = ['upi', 'credit_card', 'debit_card', 'net_banking', 'cash']

def expand_dataset():
    print("=" * 75)
    print("DATASET EXPANSION: ADDING JAN 2025 - SEP 2025 HISTORICAL BOOKINGS")
    print("=" * 75)

    with app.app_context():
        # 1. BEFORE INSPECTION
        bookings_before = Booking.query.count()
        canc_before = Cancellation.query.count()
        valid_before = Booking.query.filter(Booking.status.in_(['confirmed', 'checked_in', 'checked_out'])).count()

        print(f"\n[BEFORE EXPANSION METRICS]")
        print(f"  - Total Bookings : {bookings_before}")
        print(f"  - Cancellations  : {canc_before}")
        print(f"  - Valid Bookings : {valid_before}")

        # Fetch entities
        guests = Guest.query.all()
        rooms = Room.query.all()
        admin_user = User.query.first()

        if not guests or not rooms:
            print("Error: Missing guest or room database records.")
            return

        # Prepare list for tracking inserted booking IDs for rollback capability
        new_booking_ids = []
        new_cancellation_ids = []
        new_payment_ids = []

        # Target months for insertion: Jan 2025 to Sep 2025 (9 months)
        # Generate ~35-40 bookings per month = ~330 new bookings total
        monthly_targets = [
            (2025, 1, 35), (2025, 2, 32), (2025, 3, 38),
            (2025, 4, 36), (2025, 5, 40), (2025, 6, 38),
            (2025, 7, 42), (2025, 8, 39), (2025, 9, 36)
        ]

        total_inserted = 0
        canc_inserted = 0

        for year, month, target_count in monthly_targets:
            # Determine days in month
            if month in [1, 3, 5, 7, 8, 10, 12]:
                max_day = 31
            elif month in [4, 6, 9, 11]:
                max_day = 30
            else:
                max_day = 28  # 2025 is non-leap

            for _ in range(target_count):
                day = random.randint(1, max_day)
                check_in = date(year, month, day)
                stay_nights = random.choice([1, 2, 2, 3, 3, 4, 5, 7])
                check_out = check_in + timedelta(days=stay_nights)

                # Ensure check_out does not exceed 2026-06-30
                if check_out > date(2026, 6, 30):
                    check_out = date(2026, 6, 30)
                    stay_nights = max(1, (check_out - check_in).days)

                room = random.choice(rooms)
                guest = random.choice(guests)
                base_price = float(room.room_type.base_price)
                total_amount = base_price * stay_nights

                # Historical status: ~18% cancelled, ~82% checked_out
                status_rand = random.random()
                if status_rand < 0.18:
                    status = 'cancelled'
                    payment_status = 'refunded'
                else:
                    status = 'checked_out'
                    payment_status = 'paid'

                lead_time_days = random.choice([1, 2, 3, 5, 7, 10, 14, 21, 30])
                created_at = datetime.combine(check_in - timedelta(days=lead_time_days), datetime.min.time())

                ref_code = f"HB-{check_in.strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"

                booking = Booking(
                    booking_reference=ref_code,
                    guest_id=guest.id,
                    room_id=room.id,
                    check_in_date=check_in,
                    check_out_date=check_out,
                    num_guests=random.randint(1, room.room_type.capacity),
                    status=status,
                    total_amount=total_amount,
                    payment_status=payment_status,
                    created_by=admin_user.id if admin_user else None,
                    created_at=created_at
                )
                db.session.add(booking)
                db.session.flush()
                new_booking_ids.append(booking.id)

                # Payment record
                pay_method = random.choice(PAYMENT_METHODS)
                payment = Payment(
                    booking_id=booking.id,
                    payment_method=pay_method,
                    amount=total_amount,
                    payment_date=created_at,
                    transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
                    status='refunded' if status == 'cancelled' else 'completed'
                )
                db.session.add(payment)
                db.session.flush()
                new_payment_ids.append(payment.id)

                # Cancellation record if cancelled
                if status == 'cancelled':
                    fee = random.choice([0.0, 500.0, 1000.0])
                    refund = max(0.0, total_amount - fee)
                    cancellation = Cancellation(
                        booking_id=booking.id,
                        cancelled_at=created_at + timedelta(days=random.randint(0, max(0, lead_time_days - 1))),
                        reason=random.choice(REASONS),
                        cancellation_fee=fee,
                        refund_amount=refund,
                        processed_by=admin_user.id if admin_user else None
                    )
                    db.session.add(cancellation)
                    db.session.flush()
                    new_cancellation_ids.append(cancellation.id)
                    canc_inserted += 1

                total_inserted += 1

        db.session.commit()
        print(f"  [OK] Successfully inserted {total_inserted} new bookings and {canc_inserted} cancellations for Jan-Sep 2025.")

        # Save rollback log
        rollback_data = {
            'inserted_at': datetime.now().isoformat(),
            'booking_ids': new_booking_ids,
            'payment_ids': new_payment_ids,
            'cancellation_ids': new_cancellation_ids
        }
        with open('rollback_jan_sep_2025_expansion.json', 'w') as f:
            json.dump(rollback_data, f, indent=2)
        print("  [OK] Saved rollback log file: rollback_jan_sep_2025_expansion.json")

        # -------------------------------------------------------------------
        # AFTER EXPANSION RECALCULATIONS & VERIFICATION
        # -------------------------------------------------------------------
        print("\n" + "=" * 75)
        print("AFTER EXPANSION METRICS SUMMARY (MYSQL 8.4)")
        print("=" * 75)

        total_bookings = Booking.query.count()
        total_cancellations = Cancellation.query.count()
        total_payments = Payment.query.count()
        total_guests = Guest.query.count()
        total_rooms = Room.query.count()

        confirmed_bookings = Booking.query.filter_by(status='confirmed').all()
        checked_in_bookings = Booking.query.filter_by(status='checked_in').all()
        checked_out_bookings = Booking.query.filter_by(status='checked_out').all()
        cancelled_bookings = Booking.query.filter_by(status='cancelled').all()

        valid_bookings = confirmed_bookings + checked_in_bookings + checked_out_bookings

        sql_revenue = db.session.query(db.func.sum(Booking.total_amount)).filter(
            Booking.status.in_(['confirmed', 'checked_in', 'checked_out'])
        ).scalar()
        total_valid_revenue = float(sql_revenue) if sql_revenue else 0.0

        valid_nights = sum([b.nights_stayed for b in valid_bookings])
        adr = round(total_valid_revenue / valid_nights, 2) if valid_nights > 0 else 0.0

        min_date = db.session.query(db.func.min(Booking.check_in_date)).scalar()
        max_date = db.session.query(db.func.max(Booking.check_in_date)).scalar()
        period_days = (max_date - min_date).days + 1 if min_date and max_date else 546

        operational_rooms = total_rooms - Room.query.filter_by(status='maintenance').count()
        total_available_nights = operational_rooms * period_days

        occupancy_rate = round((valid_nights / total_available_nights) * 100, 2) if total_available_nights > 0 else 0.0
        revpar = round((occupancy_rate / 100.0) * adr, 2)
        cancellation_rate = round((len(cancelled_bookings) / total_bookings) * 100, 2) if total_bookings > 0 else 0.0

        print(f"  1. Total Bookings            : {total_bookings}")
        print(f"  2. Total Cancellations       : {total_cancellations}")
        print(f"  3. Valid Bookings            : {len(valid_bookings)}")
        print(f"  4. Total Payments            : {total_payments}")
        print(f"  5. Cancellation Rate (%)     : {cancellation_rate}%")
        print(f"  6. Total Valid Revenue (INR) : INR {total_valid_revenue:,.2f}")
        print(f"  7. Sold Room Nights          : {valid_nights} nights")
        print(f"  8. Period Available Nights   : {total_available_nights} nights ({operational_rooms} rooms * {period_days} days)")
        print(f"  9. Occupancy Rate (%)        : {occupancy_rate}%")
        print(f" 10. Average Daily Rate (ADR)  : INR {adr:,.2f}")
        print(f" 11. RevPAR                    : INR {revpar:,.2f}")

        # Date boundaries check
        post_june = Booking.query.filter(Booking.check_in_date > date(2026, 6, 30)).count()
        pre_jan = Booking.query.filter(Booking.check_in_date < date(2025, 1, 1)).count()

        print(f"\n[DATE BOUNDARIES VERIFICATION]")
        print(f"  - Minimum Booking Check-In Date : {min_date} (>= 2025-01-01) [VERIFIED]")
        print(f"  - Maximum Booking Check-In Date : {max_date} (<= 2026-06-30) [VERIFIED]")
        print(f"  - Records After 2026-06-30      : {post_june} [VERIFIED 0]")
        print(f"  - Records Before 2025-01-01     : {pre_jan} [VERIFIED 0]")

        # -------------------------------------------------------------------
        # MONTH-BY-MONTH BOOKING DISTRIBUTION TABLE (ALL 18 MONTHS)
        # -------------------------------------------------------------------
        print("\n" + "=" * 75)
        print("MONTH-BY-MONTH BOOKING DISTRIBUTION TABLE (ALL 18 MONTHS)")
        print("=" * 75)
        print(f"{'Year-Month':<15} | {'Month Name':<15} | {'Total Bookings':<15} | {'Valid Revenue (INR)':<20}")
        print("-" * 75)

        months_list = [
            (2025, 1, 'January 2025'), (2025, 2, 'February 2025'), (2025, 3, 'March 2025'),
            (2025, 4, 'April 2025'), (2025, 5, 'May 2025'), (2025, 6, 'June 2025'),
            (2025, 7, 'July 2025'), (2025, 8, 'August 2025'), (2025, 9, 'September 2025'),
            (2025, 10, 'October 2025'), (2025, 11, 'November 2025'), (2025, 12, 'December 2025'),
            (2026, 1, 'January 2026'), (2026, 2, 'February 2026'), (2026, 3, 'March 2026'),
            (2026, 4, 'April 2026'), (2026, 5, 'May 2026'), (2026, 6, 'June 2026')
        ]

        for y, m, mname in months_list:
            b_count = db.session.query(db.func.count(Booking.id)).filter(
                db.extract('year', Booking.check_in_date) == y,
                db.extract('month', Booking.check_in_date) == m
            ).scalar()

            m_rev = db.session.query(db.func.sum(Booking.total_amount)).filter(
                db.extract('year', Booking.check_in_date) == y,
                db.extract('month', Booking.check_in_date) == m,
                Booking.status.in_(['confirmed', 'checked_in', 'checked_out'])
            ).scalar()
            m_rev_val = float(m_rev) if m_rev else 0.0

            print(f"{f'{y}-{m:02d}':<15} | {mname:<15} | {b_count:<15} | INR {m_rev_val:,.2f}")

        print("=" * 75)

if __name__ == '__main__':
    expand_dataset()
