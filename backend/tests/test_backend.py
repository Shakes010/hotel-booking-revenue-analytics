import unittest
import json
from datetime import datetime, timedelta
from app import create_app
from app.models import db, User, Role, Room, RoomType, Guest, Booking, Cancellation, Payment

class BackendTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        with cls.app.app_context():
            db.create_all()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def get_jwt_token(self, email='admin@hotelanalytics.com', password='Admin@123'):
        res = self.client.post('/api/v1/auth/login', json={
            'email': email,
            'password': password
        })
        data = json.loads(res.data)
        return data.get('access_token')

    # 1. Auth & Login Tests
    def test_01_valid_login(self):
        res = self.client.post('/api/v1/auth/login', json={
            'email': 'admin@hotelanalytics.com',
            'password': 'Admin@123'
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('access_token', data)
        self.assertEqual(data['user']['email'], 'admin@hotelanalytics.com')

    def test_02_invalid_login(self):
        res = self.client.post('/api/v1/auth/login', json={
            'email': 'admin@hotelanalytics.com',
            'password': 'WrongPassword123'
        })
        self.assertEqual(res.status_code, 401)
        data = json.loads(res.data)
        self.assertIn('error', data)

    def test_03_jwt_validation_and_me(self):
        token = self.get_jwt_token()
        headers = {'Authorization': f'Bearer {token}'}
        res = self.client.get('/api/v1/auth/me', headers=headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['user']['email'], 'admin@hotelanalytics.com')

    def test_04_unauthorized_access(self):
        res = self.client.get('/api/v1/auth/me')
        self.assertEqual(res.status_code, 401)

    # 2. Guest Management Tests
    def test_05_create_and_get_guest(self):
        token = self.get_jwt_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create guest
        guest_payload = {
            'full_name': 'UnitTest Guest',
            'email': 'unittest.guest@example.com',
            'phone': '9988776655',
            'city': 'Delhi'
        }
        res = self.client.post('/api/v1/guests', json=guest_payload, headers=headers)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        guest_id = data['guest']['id']

        # Get guest
        res_get = self.client.get(f'/api/v1/guests/{guest_id}', headers=headers)
        self.assertEqual(res_get.status_code, 200)
        self.assertEqual(json.loads(res_get.data)['guest']['full_name'], 'UnitTest Guest')

    def test_06_delete_guest_dependency_check(self):
        token = self.get_jwt_token()
        headers = {'Authorization': f'Bearer {token}'}

        # Pick guest with existing bookings
        booking = Booking.query.first()
        if booking:
            res = self.client.delete(f'/api/v1/guests/{booking.guest_id}', headers=headers)
            self.assertEqual(res.status_code, 409)
            self.assertIn('Cannot delete guest record', json.loads(res.data)['error'])

    # 3. Room Inventory Tests
    def test_07_room_filtering_and_availability(self):
        token = self.get_jwt_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        res = self.client.get('/api/v1/rooms', headers=headers)
        self.assertEqual(res.status_code, 200)
        
        res_avail = self.client.get('/api/v1/rooms/availability?check_in=2027-01-01&check_out=2027-01-05', headers=headers)
        self.assertEqual(res_avail.status_code, 200)

    # 4. Booking & Workflow Tests
    def test_08_booking_lifecycle_and_validation(self):
        token = self.get_jwt_token()
        headers = {'Authorization': f'Bearer {token}'}

        guest = Guest.query.first()
        room = Room.query.filter_by(status='available').first()
        self.assertIsNotNone(guest)
        self.assertIsNotNone(room)

        # Booking creation test
        check_in = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
        check_out = (datetime.now() + timedelta(days=63)).strftime('%Y-%m-%d')

        payload = {
            'guest_id': guest.id,
            'room_id': room.id,
            'check_in_date': check_in,
            'check_out_date': check_out,
            'num_guests': 1,
            'payment_method': 'credit_card'
        }
        res = self.client.post('/api/v1/bookings', json=payload, headers=headers)
        self.assertEqual(res.status_code, 201)
        booking = json.loads(res.data)['booking']
        booking_id = booking['id']

        # Overlapping booking attempt test (must return 409 Conflict)
        res_conflict = self.client.post('/api/v1/bookings', json=payload, headers=headers)
        self.assertEqual(res_conflict.status_code, 409)

        # Workflow: Check-In
        res_checkin = self.client.post(f'/api/v1/bookings/{booking_id}/check-in', headers=headers)
        self.assertEqual(res_checkin.status_code, 200)
        self.assertEqual(json.loads(res_checkin.data)['booking']['status'], 'checked_in')

        # Invalid Transition: Check-in again (must return 400 Bad Request)
        res_recheckin = self.client.post(f'/api/v1/bookings/{booking_id}/check-in', headers=headers)
        self.assertEqual(res_recheckin.status_code, 400)

        # Workflow: Check-Out
        res_checkout = self.client.post(f'/api/v1/bookings/{booking_id}/check-out', headers=headers)
        self.assertEqual(res_checkout.status_code, 200)
        self.assertEqual(json.loads(res_checkout.data)['booking']['status'], 'checked_out')

        # Invalid Transition: Cancel checked-out booking (must return 400 Bad Request)
        res_cancel = self.client.post(f'/api/v1/cancellations/process/{booking_id}', json={'reason': 'Test'}, headers=headers)
        self.assertEqual(res_cancel.status_code, 400)

    def test_09_cancellation_workflow(self):
        token = self.get_jwt_token()
        headers = {'Authorization': f'Bearer {token}'}

        guest = Guest.query.first()
        room = Room.query.filter_by(status='available').first()
        
        check_in = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        check_out = (datetime.now() + timedelta(days=92)).strftime('%Y-%m-%d')

        payload = {
            'guest_id': guest.id,
            'room_id': room.id,
            'check_in_date': check_in,
            'check_out_date': check_out,
            'num_guests': 1
        }
        res = self.client.post('/api/v1/bookings', json=payload, headers=headers)
        booking_id = json.loads(res.data)['booking']['id']

        # Process cancellation
        res_cancel = self.client.post(f'/api/v1/cancellations/process/{booking_id}', json={
            'reason': 'Flight Delayed',
            'cancellation_fee': 500
        }, headers=headers)
        self.assertEqual(res_cancel.status_code, 200)
        self.assertEqual(json.loads(res_cancel.data)['booking']['status'], 'cancelled')

        # Persistence check
        canc_obj = Cancellation.query.filter_by(booking_id=booking_id).first()
        self.assertIsNotNone(canc_obj)
        self.assertEqual(float(canc_obj.cancellation_fee), 500.0)

    # 5. Payment Tests
    def test_10_payment_endpoints(self):
        token = self.get_jwt_token()
        headers = {'Authorization': f'Bearer {token}'}

        res = self.client.get('/api/v1/payments', headers=headers)
        self.assertEqual(res.status_code, 200)
        payments = json.loads(res.data)['payments']
        self.assertGreater(len(payments), 0)

    # 6. Analytics API Calculation Tests
    def test_11_analytics_kpi_calculations(self):
        res = self.client.get('/api/v1/analytics/summary')
        self.assertEqual(res.status_code, 200)
        kpis = json.loads(res.data)['kpis']

        self.assertGreater(kpis['total_revenue'], 0)
        self.assertGreater(kpis['total_bookings'], 0)
        self.assertGreater(kpis['adr'], 0)
        self.assertGreaterEqual(kpis['cancellation_rate'], 0)
        self.assertGreaterEqual(kpis['occupancy_rate'], 0)

if __name__ == '__main__':
    unittest.main()
