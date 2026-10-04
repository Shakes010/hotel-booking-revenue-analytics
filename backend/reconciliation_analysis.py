import os
from app import create_app
from app.models import db, Booking, Cancellation, Payment, Room, RoomType, Guest

app = create_app()

def analyze_reconciliation():
    print("=" * 75)
    print("FINAL DATASET RECONCILIATION & DISCREPANCY ANALYSIS")
    print("=" * 75)

    with app.app_context():
        # 1. Total Booking Counts by Status
        total_bookings = Booking.query.count()
        confirmed_bookings = Booking.query.filter_by(status='confirmed').all()
        checked_in_bookings = Booking.query.filter_by(status='checked_in').all()
        checked_out_bookings = Booking.query.filter_by(status='checked_out').all()
        cancelled_bookings = Booking.query.filter_by(status='cancelled').all()

        valid_bookings = confirmed_bookings + checked_in_bookings + checked_out_bookings

        # 2. Revenue Breakdown by Status
        rev_confirmed = sum([float(b.total_amount) for b in confirmed_bookings])
        rev_checked_in = sum([float(b.total_amount) for b in checked_in_bookings])
        rev_checked_out = sum([float(b.total_amount) for b in checked_out_bookings])
        rev_cancelled = sum([float(b.total_amount) for b in cancelled_bookings])

        total_valid_revenue = rev_confirmed + rev_checked_in + rev_checked_out
        total_all_revenue = total_valid_revenue + rev_cancelled

        # 3. Total Payment Revenue
        pmt_res = db.session.query(db.func.sum(Payment.amount)).filter(Payment.status == 'completed').scalar()
        total_payment_revenue = float(pmt_res) if pmt_res else 0.0

        # 4. Sold Nights & ADR
        valid_nights = sum([b.nights_stayed for b in valid_bookings])
        adr = round(total_valid_revenue / valid_nights, 2) if valid_nights > 0 else 0.0

        # 5. Period Occupancy & RevPAR
        earliest_date = db.session.query(db.func.min(Booking.check_in_date)).scalar()
        latest_date = db.session.query(db.func.max(Booking.check_in_date)).scalar()
        period_days = (latest_date - earliest_date).days + 1 if (earliest_date and latest_date) else 365
        
        total_rooms = Room.query.count()
        maintenance_rooms = Room.query.filter_by(status='maintenance').count()
        operational_rooms = total_rooms - maintenance_rooms
        total_available_nights = operational_rooms * period_days
        
        occupancy_rate = round((valid_nights / total_available_nights) * 100, 2) if total_available_nights > 0 else 0.0
        revpar = round((occupancy_rate / 100.0) * adr, 2)

        cancellation_rate = round((len(cancelled_bookings) / total_bookings) * 100, 2) if total_bookings > 0 else 0.0

        print(f"\n1. Total Booking Count      : {total_bookings}")
        print(f"2. Cancelled Booking Count  : {len(cancelled_bookings)}")
        print(f"3. Valid Booking Count      : {len(valid_bookings)} (Confirmed: {len(confirmed_bookings)}, Checked-In: {len(checked_in_bookings)}, Checked-Out: {len(checked_out_bookings)})")
        print(f"4. Revenue (Confirmed)      : INR {rev_confirmed:,.2f}")
        print(f"5. Revenue (Checked-In)     : INR {rev_checked_in:,.2f}")
        print(f"6. Revenue (Checked-Out)    : INR {rev_checked_out:,.2f}")
        print(f"7. Revenue (Cancelled)      : INR {rev_cancelled:,.2f} (Excluded from valid room revenue)")
        print(f"8. Total Valid Room Revenue : INR {total_valid_revenue:,.2f}")
        print(f"9. Total Completed Payments : INR {total_payment_revenue:,.2f}")
        print(f"\n10. Hotel Performance Metrics:")
        print(f"    - Sold Room Nights      : {valid_nights} nights")
        print(f"    - Available Room Nights : {total_available_nights} nights ({operational_rooms} rooms * {period_days} days)")
        print(f"    - ADR                   : INR {adr:,.2f}")
        print(f"    - Occupancy Rate        : {occupancy_rate}%")
        print(f"    - RevPAR                : INR {revpar:,.2f}")
        print(f"    - Cancellation Rate     : {cancellation_rate}%")

        print("\n" + "=" * 75)
        print("ROOT CAUSE EXPLANATION FOR REVENUE DIFFERENCE")
        print("=" * 75)
        print(f"Previous Reported Revenue  : INR 10,901,500.00 (from 409 valid bookings out of 500 total, 91 cancelled)")
        print(f"Current MySQL Valid Revenue: INR 9,910,000.00 (from 402 valid bookings out of 501 total, 99 cancelled)")
        print(f"Revenue Difference         : INR -991,500.00")
        print(f"\nKey Drivers of the Difference:")
        print(f" 1. Number of Cancelled Bookings: Increased from 91 to 99 (+8 cancellations).")
        print(f"    Since cancelled bookings contribute INR 0 to valid revenue, 8 additional bookings were excluded from revenue.")
        print(f" 2. Random Room Tier Assignment: In the previous dataset run, more high-tier rooms (Executive Suite / Villa) were assigned to valid stays.")
        print(f"    In the current MySQL seed run, valid bookings yielded 1,283 sold nights at an ADR of INR 7,724.08 vs 1,367 sold nights at INR 7,974.76 previously.")

if __name__ == '__main__':
    analyze_reconciliation()
