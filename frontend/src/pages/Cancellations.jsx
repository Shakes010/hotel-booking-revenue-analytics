import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { CalendarX, RefreshCw } from 'lucide-react';

const Cancellations = () => {
  const [cancellations, setCancellations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCancellations();
  }, []);

  const fetchCancellations = async () => {
    setLoading(true);
    try {
      const res = await api.get('/cancellations');
      setCancellations(res.data.cancellations);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const totalRefunds = cancellations.reduce((acc, c) => acc + c.refund_amount, 0);
  const totalFees = cancellations.reduce((acc, c) => acc + c.cancellation_fee, 0);

  return (
    <div className="p-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h3 className="fw-bold text-dark mb-1">Cancellations & Financial Loss Audit</h3>
          <p className="text-muted small mb-0">Financial impact monitoring of cancelled reservations, fees, and guest refunds</p>
        </div>
        <button onClick={fetchCancellations} className="btn btn-outline-primary btn-sm d-flex align-items-center gap-1 rounded-pill px-3">
          <RefreshCw size={14} /> Refresh Log
        </button>
      </div>

      {/* Loss Summary Cards */}
      <div className="row g-3 mb-4">
        <div className="col-md-6">
          <div className="card card-dashboard p-3">
            <span className="text-muted extra-small fw-bold text-uppercase">Total Revenue Refunded to Guests</span>
            <h3 className="fw-bold text-danger mt-1 mb-0">₹{totalRefunds.toLocaleString()}</h3>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card card-dashboard p-3">
            <span className="text-muted extra-small fw-bold text-uppercase">Total Cancellation Fees Retained</span>
            <h3 className="fw-bold text-success mt-1 mb-0">₹{totalFees.toLocaleString()}</h3>
          </div>
        </div>
      </div>

      {/* Cancellations Audit Table */}
      <div className="card card-dashboard overflow-hidden">
        <div className="table-responsive">
          <table className="table table-custom mb-0 align-middle">
            <thead>
              <tr>
                <th>Booking Ref</th>
                <th>Guest Name</th>
                <th>Cancellation Reason</th>
                <th>Fee Retained</th>
                <th>Refund Amount</th>
                <th>Cancelled On</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="6" className="text-center py-4 text-muted">Loading cancellation logs...</td>
                </tr>
              ) : cancellations.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center py-4 text-muted">No cancellation records logged.</td>
                </tr>
              ) : (
                cancellations.map((c) => (
                  <tr key={c.id}>
                    <td><span className="fw-semibold text-primary">{c.booking_reference}</span></td>
                    <td><span className="text-dark fw-semibold">{c.guest_name}</span></td>
                    <td><span className="badge bg-warning bg-opacity-10 text-warning border border-warning border-opacity-25">{c.reason}</span></td>
                    <td className="text-success fw-semibold">₹{c.cancellation_fee.toLocaleString()}</td>
                    <td className="text-danger fw-semibold">₹{c.refund_amount.toLocaleString()}</td>
                    <td className="text-muted extra-small">{c.cancelled_at}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Cancellations;
