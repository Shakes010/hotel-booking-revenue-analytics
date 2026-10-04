import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Calendar, UserPlus, Check, BedDouble, CreditCard, Info } from 'lucide-react';

const CreateBooking = () => {
  const navigate = useNavigate();
  const [guests, setGuests] = useState([]);
  const [selectedGuestId, setSelectedGuestId] = useState('');
  const [checkIn, setCheckIn] = useState('');
  const [checkOut, setCheckOut] = useState('');
  const [numGuests, setNumGuests] = useState(1);
  const [availableRooms, setAvailableRooms] = useState([]);
  const [selectedRoomId, setSelectedRoomId] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('upi');

  const [loadingRooms, setLoadingRooms] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Quick guest registration state
  const [showNewGuestModal, setShowNewGuestModal] = useState(false);
  const [newGuest, setNewGuest] = useState({ full_name: '', email: '', phone: '', address: '', city: 'Mumbai' });

  useEffect(() => {
    fetchGuests();
  }, []);

  const fetchGuests = async () => {
    try {
      const res = await api.get('/guests');
      setGuests(res.data.guests);
      if (res.data.guests.length > 0) {
        setSelectedGuestId(res.data.guests[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCheckAvailability = async () => {
    if (!checkIn || !checkOut) {
      setError('Please select both Check-in and Check-out dates.');
      return;
    }
    if (new Date(checkOut) <= new Date(checkIn)) {
      setError('Check-out date must be strictly after Check-in date.');
      return;
    }
    setError('');
    setLoadingRooms(true);
    try {
      const res = await api.get(`/rooms/availability?check_in=${checkIn}&check_out=${checkOut}`);
      setAvailableRooms(res.data.rooms);
      if (res.data.rooms.length > 0) {
        setSelectedRoomId(res.data.rooms[0].id);
      } else {
        setSelectedRoomId('');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to check room availability');
    } finally {
      setLoadingRooms(false);
    }
  };

  const handleCreateGuest = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/guests', newGuest);
      const created = res.data.guest;
      setGuests([created, ...guests]);
      setSelectedGuestId(created.id);
      setShowNewGuestModal(false);
      setNewGuest({ full_name: '', email: '', phone: '', address: '', city: 'Mumbai' });
    } catch (err) {
      alert(err.response?.data?.error || "Failed to register new guest");
    }
  };

  const handleSubmitBooking = async (e) => {
    e.preventDefault();
    if (!selectedGuestId || !selectedRoomId || !checkIn || !checkOut) {
      setError("Please select guest, room, and valid reservation dates.");
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await api.post('/bookings', {
        guest_id: parseInt(selectedGuestId),
        room_id: parseInt(selectedRoomId),
        check_in_date: checkIn,
        check_out_date: checkOut,
        num_guests: parseInt(numGuests),
        payment_method: paymentMethod
      });
      navigate('/bookings');
    } catch (err) {
      setError(err.response?.data?.error || "Failed to process reservation");
    } finally {
      setSubmitting(false);
    }
  };

  const currentRoom = availableRooms.find(r => r.id === parseInt(selectedRoomId));
  const stayNights = (checkIn && checkOut) ? Math.max(1, (new Date(checkOut) - new Date(checkIn)) / (1000 * 60 * 60 * 24)) : 0;
  const estimatedTotal = currentRoom ? currentRoom.base_price * stayNights : 0;

  return (
    <div className="p-4" style={{ maxWidth: '900px', margin: '0 auto' }}>
      <h3 className="fw-bold text-dark mb-1">Create New Reservation</h3>
      <p className="text-muted small mb-4">Book available room inventory with real-time date conflict verification</p>

      {error && <div className="alert alert-danger py-2 extra-small">{error}</div>}

      <form onSubmit={handleSubmitBooking} className="card card-dashboard p-4">
        {/* Step 1: Select Guest */}
        <div className="mb-4">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <label className="form-label fw-bold text-primary mb-0">1. Select Guest</label>
            <button
              type="button"
              className="btn btn-outline-primary btn-sm d-flex align-items-center gap-1 extra-small"
              onClick={() => setShowNewGuestModal(true)}
            >
              <UserPlus size={14} /> Add New Guest
            </button>
          </div>
          <select
            className="form-select"
            value={selectedGuestId}
            onChange={(e) => setSelectedGuestId(e.target.value)}
            required
          >
            {guests.map((g) => (
              <option key={g.id} value={g.id}>
                {g.full_name} ({g.email} | {g.phone})
              </option>
            ))}
          </select>
        </div>

        {/* Step 2: Reservation Dates & Search */}
        <div className="mb-4">
          <label className="form-label fw-bold text-primary mb-2">2. Dates & Availability Query</label>
          <div className="row g-3">
            <div className="col-md-4">
              <label className="form-label text-muted extra-small fw-bold">Check-in Date</label>
              <input
                type="date"
                className="form-control"
                value={checkIn}
                onChange={(e) => setCheckIn(e.target.value)}
                required
              />
            </div>
            <div className="col-md-4">
              <label className="form-label text-muted extra-small fw-bold">Check-out Date</label>
              <input
                type="date"
                className="form-control"
                value={checkOut}
                onChange={(e) => setCheckOut(e.target.value)}
                required
              />
            </div>
            <div className="col-md-2">
              <label className="form-label text-muted extra-small fw-bold">Guests Count</label>
              <input
                type="number"
                min="1"
                max="6"
                className="form-control"
                value={numGuests}
                onChange={(e) => setNumGuests(e.target.value)}
              />
            </div>
            <div className="col-md-2 d-flex align-items-end">
              <button
                type="button"
                className="btn btn-primary w-100 fw-semibold"
                onClick={handleCheckAvailability}
                disabled={loadingRooms}
              >
                {loadingRooms ? 'Searching...' : 'Check'}
              </button>
            </div>
          </div>
        </div>

        {/* Step 3: Room Selection Grid */}
        {availableRooms.length > 0 && (
          <div className="mb-4">
            <label className="form-label fw-bold text-primary mb-2">3. Select Available Room ({availableRooms.length} available)</label>
            <div className="row g-2">
              {availableRooms.map((r) => (
                <div className="col-md-6" key={r.id}>
                  <div
                    className={`card p-3 border ${
                      parseInt(selectedRoomId) === r.id ? 'border-primary bg-primary bg-opacity-10' : 'border-light-subtle bg-light'
                    }`}
                    onClick={() => setSelectedRoomId(r.id)}
                    style={{ cursor: 'pointer' }}
                  >
                    <div className="d-flex justify-content-between align-items-center">
                      <div>
                        <h6 className="fw-bold mb-0 text-dark">Room {r.room_number}</h6>
                        <small className="text-muted extra-small">{r.room_type_name} (Floor {r.floor})</small>
                      </div>
                      <div className="text-end">
                        <span className="fw-bold text-success">₹{r.base_price}/night</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 4: Payment Method */}
        <div className="mb-4">
          <label className="form-label fw-bold text-primary mb-2">4. Select Payment Method</label>
          <div className="d-flex gap-3">
            {['upi', 'credit_card', 'debit_card', 'cash'].map((method) => (
              <label key={method} className="form-check-label border p-2 rounded flex-fill text-center cursor-pointer bg-light">
                <input
                  type="radio"
                  name="paymentMethod"
                  value={method}
                  checked={paymentMethod === method}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  className="form-check-input me-2"
                />
                <span className="text-uppercase extra-small fw-bold text-dark">{method.replace('_', ' ')}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Dynamic Pricing Summary Box */}
        {currentRoom && (
          <div className="alert alert-info d-flex justify-content-between align-items-center mb-4">
            <div>
              <span className="d-block text-dark font-weight-bold">Summary: {stayNights} Night(s) Stay</span>
              <small className="text-muted">Room {currentRoom.room_number} ({currentRoom.room_type_name})</small>
            </div>
            <div className="text-end">
              <h4 className="fw-bold text-success mb-0">Total: ₹{estimatedTotal.toLocaleString()}</h4>
            </div>
          </div>
        )}

        <button
          type="submit"
          className="btn btn-success py-2 fw-bold text-uppercase d-flex align-items-center justify-content-center gap-2"
          disabled={submitting || !selectedRoomId}
        >
          <Check size={18} /> {submitting ? 'Creating Reservation...' : 'Confirm & Save Booking'}
        </button>
      </form>

      {/* New Guest Modal */}
      {showNewGuestModal && (
        <div className="modal d-block bg-dark bg-opacity-50" tabIndex="-1">
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <form onSubmit={handleCreateGuest}>
                <div className="modal-header bg-primary text-white">
                  <h6 className="modal-title font-weight-bold">Register New Guest Profile</h6>
                  <button type="button" className="btn-close btn-close-white" onClick={() => setShowNewGuestModal(false)}></button>
                </div>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label extra-small fw-bold">Full Name</label>
                    <input
                      type="text"
                      className="form-control form-control-sm"
                      value={newGuest.full_name}
                      onChange={(e) => setNewGuest({ ...newGuest, full_name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label extra-small fw-bold">Email Address</label>
                    <input
                      type="email"
                      className="form-control form-control-sm"
                      value={newGuest.email}
                      onChange={(e) => setNewGuest({ ...newGuest, email: e.target.value })}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label extra-small fw-bold">Phone Number</label>
                    <input
                      type="text"
                      className="form-control form-control-sm"
                      value={newGuest.phone}
                      onChange={(e) => setNewGuest({ ...newGuest, phone: e.target.value })}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label extra-small fw-bold">City</label>
                    <input
                      type="text"
                      className="form-control form-control-sm"
                      value={newGuest.city}
                      onChange={(e) => setNewGuest({ ...newGuest, city: e.target.value })}
                    />
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-light btn-sm" onClick={() => setShowNewGuestModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary btn-sm">Save Guest</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CreateBooking;
