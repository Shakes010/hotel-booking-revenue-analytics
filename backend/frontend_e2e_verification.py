import urllib.request
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000/api/v1'

def make_request(endpoint, method='GET', payload=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode('utf-8') if payload else None
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

def run_e2e_test():
    print("=" * 70)
    print("END-TO-END WORKFLOW INTEGRATION TEST")
    print("=" * 70)

    # 1. Login
    print("\n1. Testing Login (POST /auth/login)...")
    status, res = make_request('/auth/login', 'POST', {'email': 'admin@hotelanalytics.com', 'password': 'Admin@123'})
    assert status == 200, f"Login failed: {res}"
    token = res['access_token']
    print(f"   [OK] Logged in as: {res['user']['full_name']} ({res['user']['role_name']})")

    # 2. Create Guest
    print("\n2. Testing Guest Creation (POST /guests)...")
    guest_payload = {
        'full_name': 'E2E Workflow Guest',
        'email': f'e2e_guest_{datetime.now().strftime("%H%M%S")}@example.com',
        'phone': '9876543210',
        'city': 'Bengaluru',
        'id_proof_type': 'Aadhaar Card'
    }
    status, res = make_request('/guests', 'POST', guest_payload, token)
    assert status == 201, f"Guest creation failed: {res}"
    guest_id = res['guest']['id']
    print(f"   [OK] Guest Created: ID #{guest_id} - {res['guest']['full_name']}")

    # 3. Check Room Availability
    print("\n3. Testing Room Availability Query (GET /rooms/availability)...")
    check_in = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
    check_out = (datetime.now() + timedelta(days=13)).strftime('%Y-%m-%d')
    status, res = make_request(f'/rooms/availability?check_in={check_in}&check_out={check_out}', 'GET', token=token)
    assert status == 200, f"Availability query failed: {res}"
    available_rooms = res['rooms']
    assert len(available_rooms) > 0, "No available rooms found"
    
    # Pick room with capacity >= 2 (e.g. Deluxe Double)
    target_room = next((r for r in available_rooms if 'Double' in r['room_type_name'] or 'Suite' in r['room_type_name']), available_rooms[0])
    print(f"   [OK] Found {len(available_rooms)} available rooms. Selected Room #{target_room['room_number']} ({target_room['room_type_name']} | INR {target_room['base_price']}/night)")

    # 4. Create Booking
    print("\n4. Testing Booking Creation (POST /bookings)...")
    booking_payload = {
        'guest_id': guest_id,
        'room_id': target_room['id'],
        'check_in_date': check_in,
        'check_out_date': check_out,
        'num_guests': 2,
        'payment_method': 'upi'
    }
    status, res = make_request('/bookings', 'POST', booking_payload, token)
    assert status == 201, f"Booking creation failed: {res}"
    booking = res['booking']
    booking_id = booking['id']
    print(f"   [OK] Booking Created: Ref #{booking['booking_reference']} | Total: INR {booking['total_amount']}")

    # 5. Check-In
    print("\n5. Testing Check-In (POST /bookings/<id>/check-in)...")
    status, res = make_request(f'/bookings/{booking_id}/check-in', 'POST', token=token)
    assert status == 200, f"Check-in failed: {res}"
    assert res['booking']['status'] == 'checked_in', "Status did not update to checked_in"
    print(f"   [OK] Guest Checked-In successfully. Status: {res['booking']['status']}")

    # 6. Record Payment
    print("\n6. Testing Record Payment (POST /payments)...")
    pay_payload = {
        'booking_id': booking_id,
        'amount': booking['total_amount'],
        'payment_method': 'upi',
        'transaction_id': f'TXN-E2E-{datetime.now().strftime("%H%M%S")}'
    }
    status, res = make_request('/payments', 'POST', pay_payload, token)
    assert status == 201, f"Payment failed: {res}"
    print(f"   [OK] Payment Recorded: TXN #{res['payment']['transaction_id']} | INR {res['payment']['amount']}")

    # 7. Check-Out
    print("\n7. Testing Check-Out (POST /bookings/<id>/check-out)...")
    status, res = make_request(f'/bookings/{booking_id}/check-out', 'POST', token=token)
    assert status == 200, f"Check-out failed: {res}"
    assert res['booking']['status'] == 'checked_out', "Status did not update to checked_out"
    print(f"   [OK] Guest Checked-Out successfully. Status: {res['booking']['status']}")

    # 8. Test Cancellation Workflow
    print("\n8. Testing Cancellation Workflow (Create Booking -> Cancel -> Verify)...")
    c_check_in = (datetime.now() + timedelta(days=20)).strftime('%Y-%m-%d')
    c_check_out = (datetime.now() + timedelta(days=22)).strftime('%Y-%m-%d')
    status, res = make_request('/bookings', 'POST', {
        'guest_id': guest_id,
        'room_id': target_room['id'],
        'check_in_date': c_check_in,
        'check_out_date': c_check_out,
        'num_guests': 2
    }, token)
    c_booking_id = res['booking']['id']
    
    status, res = make_request(f'/cancellations/process/{c_booking_id}', 'POST', {
        'reason': 'Change of Plans',
        'cancellation_fee': 500
    }, token)
    assert status == 200, f"Cancellation failed: {res}"
    assert res['booking']['status'] == 'cancelled', "Status did not update to cancelled"
    print(f"   [OK] Booking Cancelled: Fee INR {res['cancellation']['cancellation_fee']} | Refund INR {res['cancellation']['refund_amount']}")

    print("\n" + "=" * 70)
    print("ALL END-TO-END WORKFLOW TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == '__main__':
    run_e2e_test()
