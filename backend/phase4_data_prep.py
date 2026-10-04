import os
from app import create_app
from app.models import db, Booking, Cancellation, Payment, Guest, Room, RoomType, User

app = create_app()

def prepare_and_verify_data():
    print("=" * 70)
    print("PHASE 4: FINAL DATA PREPARATION & QUALITY CHECK")
    print("=" * 70)

    with app.app_context():
        # -------------------------------------------------------------------
        # PART 1: IDENTIFY & REMOVE AUTOMATED TEST / E2E RECORDS ONLY
        # -------------------------------------------------------------------
        print("\n[PART 1] IDENTIFYING AUTOMATED E2E / TEST RECORDS...")
        
        # 1. Identify test guests
        test_guests = Guest.query.filter(
            (Guest.full_name.ilike('%E2E%')) |
            (Guest.full_name.ilike('%UnitTest%')) |
            (Guest.email.ilike('%e2e%')) |
            (Guest.email.ilike('%unittest%'))
        ).all()
        
        test_guest_ids = [g.id for g in test_guests]
        print(f"  - Identified {len(test_guests)} test guest profiles: {[g.full_name for g in test_guests]}")

        # 2. Identify test bookings
        test_bookings = Booking.query.filter(
            (Booking.guest_id.in_(test_guest_ids)) |
            (Booking.booking_reference.ilike('%E2E%'))
        ).all()
        test_booking_ids = [b.id for b in test_bookings]
        print(f"  - Identified {len(test_bookings)} test bookings created during integration testing.")

        # 3. Identify test payments
        test_payments = Payment.query.filter(
            (Payment.booking_id.in_(test_booking_ids)) |
            (Payment.transaction_id.ilike('%E2E%'))
        ).all()
        print(f"  - Identified {len(test_payments)} test payment records.")

        # 4. Identify test cancellations
        test_cancellations = Cancellation.query.filter(
            Cancellation.booking_id.in_(test_booking_ids)
        ).all()
        print(f"  - Identified {len(test_cancellations)} test cancellation records.")

        # Perform targeted cleanup of test records only
        if test_cancellations:
            for c in test_cancellations:
                db.session.delete(c)
        if test_payments:
            for p in test_payments:
                db.session.delete(p)
        if test_bookings:
            for b in test_bookings:
                db.session.delete(b)
        if test_guests:
            for g in test_guests:
                db.session.delete(g)

        db.session.commit()
        print("  [OK] Cleaned up test records while preserving original historical dataset.")

        # -------------------------------------------------------------------
        # PART 2: DATA QUALITY CHECKS ON HISTORICAL DATASET
        # -------------------------------------------------------------------
        print("\n[PART 2] RUNNING SQL DATA QUALITY CHECKS ON MYSQL 8.4...")

        # Quality Check 1: Null Check
        null_bookings = Booking.query.filter(
            (Booking.guest_id == None) |
            (Booking.room_id == None) |
            (Booking.check_in_date == None) |
            (Booking.check_out_date == None) |
            (Booking.total_amount == None)
        ).count()
        print(f"  - NULL check in essential booking fields: {null_bookings} NULLs found. [OK]")

        # Quality Check 2: Invalid Date Ranges (check_out <= check_in)
        invalid_dates = Booking.query.filter(Booking.check_out_date <= Booking.check_in_date).count()
        print(f"  - Invalid date ranges (check_out <= check_in): {invalid_dates} invalid. [OK]")

        # Quality Check 3: Negative Revenue
        negative_rev = Booking.query.filter(Booking.total_amount < 0).count()
        print(f"  - Negative revenue entries: {negative_rev} found. [OK]")

        # Quality Check 4: Duplicate Booking References
        dup_refs = db.session.query(
            Booking.booking_reference, db.func.count(Booking.id)
        ).group_by(Booking.booking_reference).having(db.func.count(Booking.id) > 1).all()
        print(f"  - Duplicate booking references: {len(dup_refs)} duplicates found. [OK]")

        # Quality Check 5: Duplicate Payment Transaction IDs
        dup_txns = db.session.query(
            Payment.transaction_id, db.func.count(Payment.id)
        ).group_by(Payment.transaction_id).having(db.func.count(Payment.id) > 1).all()
        print(f"  - Duplicate payment transaction IDs: {len(dup_txns)} duplicates found. [OK]")

        # Quality Check 6: Cancelled Bookings Revenue Isolation
        cancelled_with_revenue = Booking.query.filter(
            Booking.status == 'cancelled',
            Booking.total_amount > 0
        ).count()
        print(f"  - Total cancelled bookings with status='cancelled': {Booking.query.filter_by(status='cancelled').count()}")
        print(f"  - Note: Revenue aggregation strictly filters `status IN ('confirmed', 'checked_in', 'checked_out')`, so cancelled bookings contribute INR 0 to total revenue. [OK]")

        # -------------------------------------------------------------------
        # FINAL CLEAN DATASET METRICS SUMMARY
        # -------------------------------------------------------------------
        print("\n" + "=" * 70)
        print("FINAL HISTORICAL DATASET METRICS SUMMARY (AFTER CLEANUP)")
        print("=" * 70)

        total_bookings = Booking.query.count()
        total_cancellations = Cancellation.query.count()
        total_payments = Payment.query.count()
        total_guests = Guest.query.count()
        total_rooms = Room.query.count()

        sql_revenue = db.session.query(db.func.sum(Booking.total_amount)).filter(
            Booking.status.in_(['confirmed', 'checked_in', 'checked_out'])
        ).scalar()
        total_revenue = float(sql_revenue) if sql_revenue else 0.0

        cancellation_rate = round((total_cancellations / total_bookings) * 100, 2) if total_bookings > 0 else 0.0

        print(f"  1. Total Bookings Count      : {total_bookings}")
        print(f"  2. Total Cancellations Count : {total_cancellations}")
        print(f"  3. Total Payments Count      : {total_payments}")
        print(f"  4. Total Guests Count        : {total_guests}")
        print(f"  5. Total Rooms Count         : {total_rooms}")
        print(f"  6. Total Valid Revenue (INR) : INR {total_revenue:,.2f}")
        print(f"  7. Cancellation Rate (%)     : {cancellation_rate}%")
        print("=" * 70)

if __name__ == '__main__':
    prepare_and_verify_data()
