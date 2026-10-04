import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { CreditCard, Plus, Search, RefreshCw, CheckCircle2 } from 'lucide-react';

const Payments = () => {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchBookingId, setSearchBookingId] = useState('');

  // New Payment Modal state
  const [showModal, setShowModal] = useState(false);
  const [newPayment, setNewPayment] = useState({
    booking_id: '',
    amount: '',
    payment_method: 'upi',
    transaction_id: ''
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    setLoading(true);
    try {
      const res = await api.get('/payments', {
        params: { booking_id: searchBookingId }
      });
      setPayments(res.data.payments);
    } catch (err) {
      console.error("Error fetching payments:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRecordPayment = async (e) => {
    e.preventDefault();
    if (!newPayment.booking_id || !newPayment.amount) {
      alert("Please enter both Booking ID and Amount.");
      return;
    }
    setSubmitting(true);
    try {
      await api.post('/payments', newPayment);
      setShowModal(false);
      setNewPayment({ booking_id: '', amount: '', payment_method: 'upi', transaction_id: '' });
      fetchPayments();
    } catch (err) {
      alert(err.response?.data?.error || "Failed to record payment transaction.");
    } finally {
      setSubmitting(false);
    }
  };

  const totalCollected = payments.reduce((acc, p) => p.status === 'completed' ? acc + p.amount : acc, 0);

  return (
    <div className="p-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h3 className="fw-bold text-dark mb-1">Payments & Transactions Audit</h3>
          <p className="text-muted small mb-0">Monitor payment transaction ledgers, payment methods, and financial records</p>
        </div>
        <div className="d-flex gap-2">
          <button onClick={fetchPayments} className="btn btn-outline-primary btn-sm d-flex align-items-center gap-1 rounded-pill px-3">
            <RefreshCw size={14} /> Refresh
          </button>
          <button onClick={() => setShowModal(true)} className="btn btn-success btn-sm d-flex align-items-center gap-1 rounded-pill px-3 fw-semibold">
            <Plus size={16} /> Record Payment
          </button>
        </div>
      </div>

      {/* Summary Banner Card */}
      <div className="row g-3 mb-4">
        <div className="col-md-6">
          <div className="card card-dashboard p-3">
            <span className="text-muted extra-small fw-bold text-uppercase">Total Processed Payments</span>
            <h3 className="fw-bold text-success mb-0 mt-1">₹{totalCollected.toLocaleString()}</h3>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card card-dashboard p-3">
            <span className="text-muted extra-small fw-bold text-uppercase">Total Transaction Count</span>
            <h3 className="fw-bold text-primary mb-0 mt-1">{payments.length} Transactions</h3>
          </div>
        </div>
      </div>

      {/* Payments Table Card */}
      <div className="card card-dashboard overflow-hidden">
        <div className="table-responsive">
          <table className="table table-custom mb-0 align-middle">
            <thead>
              <tr>
                <th>Transaction ID</th>
                <th>Booking ID</th>
                <th>Amount</th>
                <th>Payment Method</th>
                <th>Status</th>
                <th>Transaction Date</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="6" className="text-center py-4 text-muted">Loading transaction ledgers...</td>
                </tr>
              ) : payments.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center py-4 text-muted">No payment records found.</td>
                </tr>
              ) : (
                payments.map((p) => (
                  <tr key={p.id}>
                    <td><span className="font-monospace text-primary fw-semibold">{p.transaction_id}</span></td>
                    <td><span className="badge bg-light text-dark border">Booking #{p.booking_id}</span></td>
                    <td className="fw-bold text-success">₹{p.amount.toLocaleString()}</td>
                    <td><span className="text-uppercase extra-small fw-bold text-dark">{p.payment_method.replace('_', ' ')}</span></td>
                    <td>
                      <span className={`badge ${p.status === 'completed' ? 'bg-success text-white' : 'bg-warning text-dark'}`}>
                        {p.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="text-muted extra-small">{p.payment_date}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Record Payment Modal */}
      {showModal && (
        <div className="modal d-block bg-dark bg-opacity-50" tabIndex="-1">
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <form onSubmit={handleRecordPayment}>
                <div className="modal-header bg-success text-white">
                  <h6 className="modal-title font-weight-bold">Record Manual Payment Transaction</h6>
                  <button type="button" className="btn-close btn-close-white" onClick={() => setShowModal(false)}></button>
                </div>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label extra-small fw-bold">Booking ID</label>
                    <input
                      type="number"
                      className="form-control form-control-sm"
                      placeholder="e.g. 1"
                      value={newPayment.booking_id}
                      onChange={(e) => setNewPayment({ ...newPayment, booking_id: e.target.value })}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label extra-small fw-bold">Payment Amount (₹)</label>
                    <input
                      type="number"
                      className="form-control form-control-sm"
                      placeholder="4500"
                      value={newPayment.amount}
                      onChange={(e) => setNewPayment({ ...newPayment, amount: e.target.value })}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label extra-small fw-bold">Payment Method</label>
                    <select
                      className="form-select form-select-sm"
                      value={newPayment.payment_method}
                      onChange={(e) => setNewPayment({ ...newPayment, payment_method: e.target.value })}
                    >
                      <option value="upi">UPI / QR Code</option>
                      <option value="credit_card">Credit Card</option>
                      <option value="debit_card">Debit Card</option>
                      <option value="net_banking">Net Banking</option>
                      <option value="cash">Cash Payment</option>
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label extra-small fw-bold">Transaction Reference ID (Optional)</label>
                    <input
                      type="text"
                      className="form-control form-control-sm"
                      placeholder="e.g. TXN-12345678"
                      value={newPayment.transaction_id}
                      onChange={(e) => setNewPayment({ ...newPayment, transaction_id: e.target.value })}
                    />
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-light btn-sm" onClick={() => setShowModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-success btn-sm" disabled={submitting}>
                    {submitting ? 'Saving...' : 'Record Payment'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Payments;
