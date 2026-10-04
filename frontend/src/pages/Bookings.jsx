import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { Search, Plus, CheckCircle, LogOut, XCircle, Filter, Calendar } from 'lucide-react';

const Bookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Cancel Modal state
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [cancelReason, setCancelReason] = useState('Change of Travel Plans');
  const [cancelFee, setCancelFee] = useState(500);

  useEffect(() => {
    fetchBookings();
  }, [statusFilter]);

  const fetchBookings = async () => {
    setLoading(true);
    try {
      const res = await api.get('/bookings', {
        params: {
          status: statusFilter,
          search: search,
          start_date: startDate,
          end_date: endDate
        }
      });
      setBookings(res.data.bookings);
    } catch (err) {
      console.error("Error fetching bookings:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchBookings();
  };

  const handleCheckIn = async (id, ref) => {
    if (!window.confirm(`Confirm Check-In for booking reference ${ref}?`)) return;
    try {
      await api.post(`/bookings/${id}/check-in`);
      fetchBookings();
    } catch (err) {
      alert(err.response?.data?.error || "Check-in failed");
    }
  };

  const handleCheckOut = async (id, ref) => {
    if (!window.confirm(`Confirm Check-Out for booking reference ${ref}?`)) return;
    try {
      await api.post(`/bookings/${id}/check-out`);
      fetchBookings();
    } catch (err) {
      alert(err.response?.data?.error || "Check-out failed");
    }
  };

  const handleCancelSubmit = async () => {
    if (!selectedBooking) return;
    try {
      await api.post(`/cancellations/process/${selectedBooking.id}`, {
        reason: cancelReason,
        cancellation_fee: cancelFee
      });
      setSelectedBooking(null);
      fetchBookings();
    } catch (err) {
      alert(err.response?.data?.error || "Cancellation failed");
    }
  };

  return (
    <div className="p-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h3 className="fw-bold text-dark mb-1">Bookings & Reservations</h3>
          <p className="text-muted small mb-0">Manage guest reservations, lifecycle check-ins, and cancellations</p>
        </div>
        <Link to="/create-booking" className="btn btn-success d-flex align-items-center gap-2 rounded-pill px-3 fw-semibold">
          <Plus size={18} /> New Reservation
        </Link>
      </div>

      {/* Filter and Search Bar Card */}
      <div className="card card-dashboard mb-4 p-3">
        <form onSubmit={handleSearchSubmit} className="row g-3 align-items-center">
          <div className="col-md-4">
            <label className="form-label text-muted extra-small fw-bold">Search</label>
            <div className="input-group input-group-sm">
              <span className="input-group-text bg-light text-secondary">
                <Search size={16} />
              </span>
              <input
                type="text"
                className="form-control bg-light"
                placeholder="Guest Name or Booking Reference..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>

          <div className="col-md-3">
            <label className="form-label text-muted extra-small fw-bold">Status Filter</label>
            <select
              className="form-select form-select-sm bg-light"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="confirmed">Confirmed</option>
              <option value="checked_in">Checked In</option>
              <option value="checked_out">Checked Out</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div className="col-md-3">
            <label className="form-label text-muted extra-small fw-bold">Check-in Date Range</label>
            <input
              type="date"
              className="form-control form-control-sm bg-light"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>

          <div className="col-md-2 d-flex align-items-end">
            <button type="submit" className="btn btn-primary btn-sm w-100 fw-semibold">
              <Filter size={14} className="me-1" /> Filter
            </button>
          </div>
        </form>
      </div>

      {/* Bookings Table Card */}
      <div className="card card-dashboard overflow-hidden">
        <div className="table-responsive">
          <table className="table table-custom mb-0 align-middle">
            <thead>
              <tr>
                <th>Booking Ref</th>
                <th>Guest</th>
                <th>Room Info</th>
                <th>Check-in / Out</th>
                <th>Nights</th>
                <th>Amount</th>
                <th>Status</th>
                <th className="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="8" className="text-center py-4 text-muted">Loading reservations...</td>
                </tr>
              ) : bookings.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-4 text-muted">No booking records found.</td>
                </tr>
              ) : (
                bookings.map((b) => (
                  <tr key={b.id}>
                    <td><span className="fw-bold text-primary">{b.booking_reference}</span></td>
                    <td>
                      <div className="fw-semibold text-dark">{b.guest_name}</div>
                      <small className="text-muted extra-small">{b.guest_phone}</small>
                    </td>
                    <td>
                      <div>Room {b.room_number}</div>
                      <small className="text-muted extra-small">{b.room_type_name}</small>
                    </td>
                    <td>
                      <small className="d-block text-dark fw-semibold">{b.check_in_date}</small>
                      <small className="text-muted extra-small">to {b.check_out_date}</small>
                    </td>
                    <td>{b.nights_stayed} nts</td>
                    <td className="fw-bold text-success">₹{b.total_amount.toLocaleString()}</td>
                    <td>
                      <span className={`badge ${
                        b.status === 'confirmed' ? 'bg-primary text-white' :
                        b.status === 'checked_in' ? 'bg-info text-dark' :
                        b.status === 'checked_out' ? 'bg-secondary text-white' : 'bg-danger text-white'
                      }`}>
                        {b.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </td>
                    <td className="text-end">
                      <div className="btn-group btn-group-sm">
                        {b.status === 'confirmed' && (
                          <button
                            onClick={() => handleCheckIn(b.id, b.booking_reference)}
                            className="btn btn-outline-info"
                            title="Check In Guest"
                          >
                            <CheckCircle size={14} /> Check-In
                          </button>
                        )}
                        {b.status === 'checked_in' && (
                          <button
                            onClick={() => handleCheckOut(b.id, b.booking_reference)}
                            className="btn btn-outline-warning"
                            title="Check Out Guest"
                          >
                            <LogOut size={14} /> Check-Out
                          </button>
                        )}
                        {b.status === 'confirmed' && (
                          <button
                            onClick={() => setSelectedBooking(b)}
                            className="btn btn-outline-danger"
                            title="Cancel Reservation"
                          >
                            <XCircle size={14} /> Cancel
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Cancellation Modal */}
      {selectedBooking && (
        <div className="modal d-block bg-dark bg-opacity-50" tabIndex="-1">
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header bg-danger text-white">
                <h6 className="modal-title font-weight-bold">Cancel Reservation - {selectedBooking.booking_reference}</h6>
                <button type="button" className="btn-close btn-close-white" onClick={() => setSelectedBooking(null)}></button>
              </div>
              <div className="modal-body">
                <p className="small mb-2">Guest: <strong>{selectedBooking.guest_name}</strong></p>
                <p className="small mb-3">Total Booking Price: <strong className="text-success">₹{selectedBooking.total_amount}</strong></p>

                <div className="mb-3">
                  <label className="form-label extra-small fw-bold">Cancellation Reason</label>
                  <select className="form-select form-select-sm" value={cancelReason} onChange={(e) => setCancelReason(e.target.value)}>
                    <option value="Change of Travel Plans">Change of Travel Plans</option>
                    <option value="Personal Emergency">Personal Emergency</option>
                    <option value="Flight Cancellation">Flight Cancellation</option>
                    <option value="Medical Emergency">Medical Emergency</option>
                    <option value="Work Schedule Shift">Work Schedule Shift</option>
                  </select>
                </div>

                <div className="mb-3">
                  <label className="form-label extra-small fw-bold">Cancellation Fee (₹)</label>
                  <input
                    type="number"
                    className="form-control form-control-sm"
                    value={cancelFee}
                    onChange={(e) => setCancelFee(parseFloat(e.target.value) || 0)}
                  />
                  <small className="text-muted extra-small">Calculated Refund to Guest: ₹{Math.max(0, selectedBooking.total_amount - cancelFee)}</small>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-light btn-sm" onClick={() => setSelectedBooking(null)}>Dismiss</button>
                <button type="button" className="btn btn-danger btn-sm" onClick={handleCancelSubmit}>Confirm Cancellation</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Bookings;
