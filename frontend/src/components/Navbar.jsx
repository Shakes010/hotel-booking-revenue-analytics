import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { LogOut, User as UserIcon, Hotel, Shield } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useContext(AuthContext);

  return (
    <header className="app-header px-4 py-2 sticky-top">
      <div className="container-fluid d-flex justify-content-between align-items-center">
        <div className="d-flex align-items-center gap-3">
          <div className="p-2 bg-primary bg-opacity-10 text-primary rounded-3">
            <Hotel size={24} />
          </div>
          <div>
            <h5 className="brand-title mb-0">Grand Horizon Hotel</h5>
            <small className="text-muted extra-small">Booking & Revenue Analytics Management System</small>
          </div>
        </div>

        <div className="d-flex align-items-center gap-3">
          {user && (
            <>
              <div className="d-flex align-items-center gap-2 bg-light border px-3 py-1 rounded-pill">
                <UserIcon size={16} className="text-primary" />
                <span className="text-dark fw-semibold small">{user.full_name}</span>
                <span className="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-25 rounded-pill text-uppercase px-2">
                  <Shield size={12} className="me-1" />
                  {user.role_name}
                </span>
              </div>
              <button
                onClick={logout}
                className="btn btn-outline-danger btn-sm rounded-pill px-3 d-flex align-items-center gap-1"
                title="Sign out of system"
              >
                <LogOut size={15} /> Logout
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
