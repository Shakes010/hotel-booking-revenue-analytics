import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Search, Plus, Mail, Phone, MapPin, Edit, Trash2, UserPlus } from 'lucide-react';

const Guests = () => {
  const [guests, setGuests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  
  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingGuest, setEditingGuest] = useState(null);
  const [guestForm, setGuestForm] = useState({
    full_name: '', email: '', phone: '', address: '', city: 'Mumbai', id_proof_type: 'Aadhaar Card', id_proof_number: ''
  });

  useEffect(() => {
    fetchGuests();
  }, []);

  const fetchGuests = async () => {
    setLoading(true);
    try {
      const res = await api.get('/guests', { params: { search } });
      setGuests(res.data.guests);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchGuests();
  };

  const openCreateModal = () => {
    setEditingGuest(null);
    setGuestForm({ full_name: '', email: '', phone: '', address: '', city: 'Mumbai', id_proof_type: 'Aadhaar Card', id_proof_number: '' });
    setShowModal(true);
  };

  const openEditModal = (guest) => {
    setEditingGuest(guest);
    setGuestForm({
      full_name: guest.full_name,
      email: guest.email,
      phone: guest.phone,
      address: guest.address || '',
      city: guest.city || 'Mumbai',
      id_proof_type: guest.id_proof_type || 'Aadhaar Card',
      id_proof_number: guest.id_proof_number || ''
    });
    setShowModal(true);
  };

  const handleSaveGuest = async (e) => {
    e.preventDefault();
    try {
      if (editingGuest) {
        await api.put(`/guests/${editingGuest.id}`, guestForm);
      } else {
        await api.post('/guests', guestForm);
      }
      setShowModal(false);
      fetchGuests();
    } catch (err) {
      alert(err.response?.data?.error || "Failed to save guest profile");
    }
  };

  const handleDeleteGuest = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete guest profile for ${name}?`)) return;
    try {
      await api.delete(`/guests/${id}`);
      fetchGuests();
    } catch (err) {
      if (err.response?.status === 409) {
        alert("This guest profile cannot be deleted because historical booking records depend on it.");
      } else {
        alert(err.response?.data?.error || "Failed to delete guest");
      }
    }
  };

  return (
    <div className="p-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h3 className="fw-bold text-dark mb-1">Guests Directory</h3>
          <p className="text-muted small mb-0">Customer contact information, address details, and ID verification records</p>
        </div>
        <button onClick={openCreateModal} className="btn btn-primary d-flex align-items-center gap-2 rounded-pill px-3 fw-semibold">
          <UserPlus size={18} /> Register Guest
        </button>
      </div>

      <div className="card card-dashboard mb-4 p-3">
        <form onSubmit={handleSearchSubmit} className="row g-3">
          <div className="col-md-9">
            <div className="input-group input-group-sm">
              <span className="input-group-text bg-light text-secondary">
                <Search size={16} />
              </span>
              <input
                type="text"
                className="form-control bg-light"
                placeholder="Search by Guest Name, Email Address, or Phone Number..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>
          <div className="col-md-3">
            <button type="submit" className="btn btn-primary btn-sm w-100 fw-semibold">Search Directory</button>
          </div>
        </form>
      </div>

      <div className="card card-dashboard overflow-hidden">
        <div className="table-responsive">
          <table className="table table-custom mb-0 align-middle">
            <thead>
              <tr>
                <th>ID</th>
                <th>Full Name</th>
                <th>Contact Info</th>
                <th>City & Address</th>
                <th>ID Proof</th>
                <th className="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="6" className="text-center py-4 text-muted">Loading guest directory...</td>
                </tr>
              ) : guests.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center py-4 text-muted">No guest records found.</td>
                </tr>
              ) : (
                guests.map((g) => (
                  <tr key={g.id}>
                    <td><span className="text-muted extra-small">#GST-{g.id}</span></td>
                    <td><span className="fw-semibold text-dark">{g.full_name}</span></td>
                    <td>
                      <div><Mail size={14} className="me-1 text-primary" /> {g.email}</div>
                      <small className="text-muted extra-small"><Phone size={14} className="me-1 text-success" /> {g.phone}</small>
                    </td>
                    <td>
                      <div><MapPin size={14} className="me-1 text-warning" /> {g.city}, {g.country}</div>
                      <small className="text-muted extra-small">{g.address}</small>
                    </td>
                    <td>
                      <span className="badge bg-light text-dark border">{g.id_proof_type}</span>
                      <div className="extra-small text-muted mt-1">{g.id_proof_number || 'Verified'}</div>
                    </td>
                    <td className="text-end">
                      <div className="btn-group btn-group-sm">
                        <button onClick={() => openEditModal(g)} className="btn btn-outline-secondary" title="Edit Profile">
                          <Edit size={14} />
                        </button>
                        <button onClick={() => handleDeleteGuest(g.id, g.full_name)} className="btn btn-outline-danger" title="Delete Profile">
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Guest Create / Edit Modal */}
      {showModal && (
        <div className="modal d-block bg-dark bg-opacity-50" tabIndex="-1">
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <form onSubmit={handleSaveGuest}>
                <div className="modal-header bg-primary text-white">
                  <h6 className="modal-title font-weight-bold">{editingGuest ? 'Edit Guest Profile' : 'Register New Guest'}</h6>
                  <button type="button" className="btn-close btn-close-white" onClick={() => setShowModal(false)}></button>
                </div>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label extra-small fw-bold">Full Name</label>
                    <input
                      type="text"
                      className="form-control form-control-sm"
                      value={guestForm.full_name}
                      onChange={(e) => setGuestForm({ ...guestForm, full_name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label extra-small fw-bold">Email Address</label>
                    <input
                      type="email"
                      className="form-control form-control-sm"
                      value={guestForm.email}
                      onChange={(e) => setGuestForm({ ...guestForm, email: e.target.value })}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label extra-small fw-bold">Phone Number</label>
                    <input
                      type="text"
                      className="form-control form-control-sm"
                      value={guestForm.phone}
                      onChange={(e) => setGuestForm({ ...guestForm, phone: e.target.value })}
                      required
                    />
                  </div>
                  <div className="row g-2 mb-3">
                    <div className="col-md-6">
                      <label className="form-label extra-small fw-bold">City</label>
                      <input
                        type="text"
                        className="form-control form-control-sm"
                        value={guestForm.city}
                        onChange={(e) => setGuestForm({ ...guestForm, city: e.target.value })}
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label extra-small fw-bold">ID Proof Type</label>
                      <select
                        className="form-select form-select-sm"
                        value={guestForm.id_proof_type}
                        onChange={(e) => setGuestForm({ ...guestForm, id_proof_type: e.target.value })}
                      >
                        <option value="Aadhaar Card">Aadhaar Card</option>
                        <option value="Passport">Passport</option>
                        <option value="Driving License">Driving License</option>
                        <option value="Voter ID">Voter ID</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-light btn-sm" onClick={() => setShowModal(false)}>Cancel</button>
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

export default Guests;
