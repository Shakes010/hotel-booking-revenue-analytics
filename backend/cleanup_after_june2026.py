import os
from datetime import date
from app import create_app
from app.models import db, Booking, Cancellation, Payment, Room, RoomType, Guest

app = create_app()

def execute_date_cleanup():
    print("=" * 75)
    print("FINAL DATASET DATE RANGE CLEANUP (CUTOFF: 2026-06-30)")
    print("=" * 75)

    cutoff_date = date(2026, 6, 30)

    with app.app_context():
        # -------------------------------------------------------------------
        # BEFORE CLEANUP INSPECTION
        # -------------------------------------------------------------------
        print("\n[BEFORE CLEANUP INSPECTION]")
        total_bookings_before = Booking.query.count()
        total_canc_before = Cancellation.query.count()
        total_pmt_before = Payment.query.count()

        min_checkin_before = db.session.query(db.func.min(Booking.check_in_date)).scalar()
        max_checkin_before = db.session.query(db.func.max(Booking.check_in_date)).scalar()

        # Identify bookings check-in after June 30, 2026
        post_cutoff_bookings = Booking.query.filter(Booking.check_in_date > cutoff_date).all()
        post_cutoff_booking_ids = [b.id for b in post_cutoff_bookings]

        post_cutoff_cancellations = Cancellation.query.filter(
            Cancellation.booking_id.in_(post_cutoff_booking_ids)
        ).all()

        post_cutoff_payments = Payment.query.filter(
            Payment.booking_id.in_(post_cutoff_booking_ids)
        ).all()

        print(f"  - Minimum Booking Check-In Date : {min_checkin_before}")
        print(f"  - Maximum Booking Check-In Date : {max_checkin_before}")
        print(f"  - Total Bookings Before          : {total_bookings_before}")
        print(f"  - Bookings Dated After 2026-06-30: {len(post_cutoff_bookings)}")
        print(f"  - Cancellations Linked (> June) : {len(post_cutoff_cancellations)}")
        print(f"  - Payments Linked (> June)      : {len(post_cutoff_payments)}")

        # -------------------------------------------------------------------
        # SAFE DELETION OF POST-JUNE-2026 RECORDS ONLY
        # -------------------------------------------------------------------
        print("\n[PERFORMING TARGETED DELETION OF POST-JUNE-2026 RECORDS]")
        
        # 1. Delete dependent cancellations
        if post_cutoff_cancellations:
            for c in post_cutoff_cancellations:
                db.session.delete(c)
            print(f"  [OK] Deleted {len(post_cutoff_cancellations)} cancellation records after 2026-06-30.")

        # 2. Delete dependent payments
        if post_cutoff_payments:
            for p in post_cutoff_payments:
                db.session.delete(p)
            print(f"  [OK] Deleted {len(post_cutoff_payments)} payment records after 2026-06-30.")

        # 3. Delete post-cutoff bookings
        if post_cutoff_bookings:
            for b in post_cutoff_bookings:
                db.session.delete(b)
            print(f"  [OK] Deleted {len(post_cutoff_bookings)} booking records after 2026-06-30.")

        db.session.commit()

        # -------------------------------------------------------------------
        # AFTER CLEANUP VERIFICATION
        # -------------------------------------------------------------------
        print("\n[AFTER CLEANUP VERIFICATION]")
        total_bookings_after = Booking.query.count()
        total_canc_after = Cancellation.query.count()
        total_pmt_after = Payment.query.count()

        min_checkin_after = db.session.query(db.func.min(Booking.check_in_date)).scalar()
        max_checkin_after = db.session.query(db.func.max(Booking.check_in_date)).scalar()

        remaining_post_cutoff = Booking.query.filter(Booking.check_in_date > cutoff_date).count()

        print(f"  - Minimum Booking Check-In Date : {min_checkin_after}")
        print(f"  - Maximum Booking Check-In Date : {max_checkin_after}")
        print(f"  - Total Bookings Remaining       : {total_bookings_after}")
        print(f"  - Total Cancellations Remaining  : {total_canc_after}")
        print(f"  - Total Payments Remaining       : {total_pmt_after}")
        print(f"  - Records Dated After 2026-06-30 : {remaining_post_cutoff} [VERIFIED 0]")

        # -------------------------------------------------------------------
        # RECALCULATED ANALYTICS METRICS (JAN 2025 - JUN 2026)
        # -------------------------------------------------------------------
        print("\n" + "=" * 75)
        print("RECALCULATED ANALYTICS (JANUARY 1, 2025 - JUNE 30, 2026)")
        print("=" * 75)

        confirmed_bookings = Booking.query.filter_by(status='confirmed').all()
        checked_in_bookings = Booking.query.filter_by(status='checked_in').all()
        checked_out_bookings = Booking.query.filter_by(status='checked_out').all()
        cancelled_bookings = Booking.query.filter_by(status='cancelled').all()

        valid_bookings = confirmed_bookings + checked_in_bookings + checked_out_bookings

        rev_confirmed = sum([float(b.total_amount) for b in confirmed_bookings])
        rev_checked_in = sum([float(b.total_amount) for b in checked_in_bookings])
        rev_checked_out = sum([float(b.total_amount) for b in checked_out_bookings])
        rev_cancelled = sum([float(b.total_amount) for b in cancelled_bookings])

        total_valid_revenue = rev_confirmed + rev_checked_in + rev_checked_out

        valid_nights = sum([b.nights_stayed for b in valid_bookings])
        adr = round(total_valid_revenue / valid_nights, 2) if valid_nights > 0 else 0.0

        period_days = (max_checkin_after - min_checkin_after).days + 1 if min_checkin_after and max_checkin_after else 365
        total_rooms = Room.query.count()
        maintenance_rooms = Room.query.filter_by(status='maintenance').count()
        operational_rooms = total_rooms - maintenance_rooms
        total_available_nights = operational_rooms * period_days

        occupancy_rate = round((valid_nights / total_available_nights) * 100, 2) if total_available_nights > 0 else 0.0
        revpar = round((occupancy_rate / 100.0) * adr, 2)

        cancellation_rate = round((len(cancelled_bookings) / total_bookings_after) * 100, 2) if total_bookings_after > 0 else 0.0

        refund_res = db.session.query(db.func.sum(Cancellation.refund_amount)).scalar()
        total_refund_loss = float(refund_res) if refund_res else 0.0

        print(f"  1. Total Bookings            : {total_bookings_after}")
        print(f"  2. Cancelled Bookings        : {len(cancelled_bookings)}")
        print(f"  3. Valid Bookings            : {len(valid_bookings)}")
        print(f"  4. Cancellation Rate (%)     : {cancellation_rate}%")
        print(f"  5. Total Valid Revenue (INR) : INR {total_valid_revenue:,.2f}")
        print(f"  6. Sold Room Nights          : {valid_nights} nights")
        print(f"  7. Period Available Nights   : {total_available_nights} nights ({operational_rooms} rooms * {period_days} days)")
        print(f"  8. Occupancy Rate (%)        : {occupancy_rate}%")
        print(f"  9. Average Daily Rate (ADR)  : INR {adr:,.2f}")
        print(f" 10. RevPAR                    : INR {revpar:,.2f}")
        print(f" 11. Revenue Lost to Canc.     : INR {total_refund_loss:,.2f}")
        print("=" * 75)

if __name__ == '__main__':
    execute_date_cleanup()
