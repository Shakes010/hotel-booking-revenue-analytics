import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { UserCheck, Shield, Mail, Phone, Lock } from 'lucide-react';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await api.get('/auth/me'); // Active profile info
      // Demo mock roster display of staff accounts
      setUsers([
        { id: 1, full_name: 'Admin Manager', email: 'admin@hotelanalytics.com', role_name: 'Admin', phone: '9876543210', status: 'active' },
        { id: 2, full_name: 'Revenue Manager', email: 'manager@hotelanalytics.com', role_name: 'Hotel Manager', phone: '9876543211', status: 'active' },
        { id: 3, full_name: 'Front Desk Officer', email: 'receptionist@hotelanalytics.com', role_name: 'Receptionist', phone: '9876543212', status: 'active' }
      ]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h3 className="fw-bold text-dark mb-1">Staff Accounts & System Roles</h3>
          <p className="text-muted small mb-0">Admin Management Portal - User Access Control & Security Policies</p>
        </div>
      </div>

      <div className="card card-dashboard overflow-hidden">
        <div className="table-responsive">
          <table className="table table-custom mb-0 align-middle">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Full Name</th>
                <th>Email Address</th>
                <th>System Role</th>
                <th>Phone Number</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td><span className="text-muted extra-small">#USR-{u.id}</span></td>
                  <td><span className="fw-semibold text-dark">{u.full_name}</span></td>
                  <td><Mail size={14} className="me-1 text-primary" /> {u.email}</td>
                  <td>
                    <span className="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-25 rounded-pill px-3">
                      <Shield size={12} className="me-1" /> {u.role_name}
                    </span>
                  </td>
                  <td><Phone size={14} className="me-1 text-success" /> {u.phone}</td>
                  <td><span className="badge bg-success text-white">ACTIVE</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Users;
