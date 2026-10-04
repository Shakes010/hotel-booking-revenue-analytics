from datetime import date
from app import create_app
from app.models import db, Booking, Cancellation, Payment

app = create_app()

def cleanup_leftovers():
    cutoff_date = date(2026, 6, 30)
    with app.app_context():
        post_cutoff_bookings = Booking.query.filter(Booking.check_in_date > cutoff_date).all()
        post_cutoff_booking_ids = [b.id for b in post_cutoff_bookings]

        if post_cutoff_booking_ids:
            Cancellation.query.filter(Cancellation.booking_id.in_(post_cutoff_booking_ids)).delete(synchronize_session=False)
            Payment.query.filter(Payment.booking_id.in_(post_cutoff_booking_ids)).delete(synchronize_session=False)
            Booking.query.filter(Booking.id.in_(post_cutoff_booking_ids)).delete(synchronize_session=False)
            db.session.commit()
            print(f"[OK] Purged {len(post_cutoff_booking_ids)} post-June-2026 leftover test bookings.")
        else:
            print("[OK] No post-June-2026 records found.")

if __name__ == '__main__':
    cleanup_leftovers()
