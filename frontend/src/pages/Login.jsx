import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Hotel, Lock, Mail, ArrowRight } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Authentication failed. Please verify credentials.');
    } finally {
      setSubmitting(false);
    }
  };

  const setDemoCredentials = (role) => {
    if (role === 'admin') {
      setEmail('admin@hotelanalytics.com');
      setPassword('Admin@123');
    } else if (role === 'manager') {
      setEmail('manager@hotelanalytics.com');
      setPassword('Manager@123');
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light p-3">
      <div className="card border-0 shadow-lg rounded-4 overflow-hidden" style={{ maxWidth: '440px', width: '100%' }}>
        <div className="card-body p-4 p-sm-5 bg-white">
          <div className="text-center mb-4">
            <div className="d-inline-flex p-3 rounded-circle bg-primary bg-opacity-10 text-primary mb-3">
              <Hotel size={40} />
            </div>
            <h3 className="fw-bold text-dark">Grand Horizon Hotel</h3>
            <p className="text-muted small">Revenue Analytics & Booking System Portal</p>
          </div>

          {error && <div className="alert alert-danger py-2 small" role="alert">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label text-muted small fw-semibold">Email Address</label>
              <div className="input-group">
                <span className="input-group-text bg-light text-secondary border-end-0">
                  <Mail size={18} />
                </span>
                <input
                  type="email"
                  className="form-control bg-light border-start-0 ps-0"
                  placeholder="admin@hotelanalytics.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="mb-4">
              <label className="form-label text-muted small fw-semibold">Password</label>
              <div className="input-group">
                <span className="input-group-text bg-light text-secondary border-end-0">
                  <Lock size={18} />
                </span>
                <input
                  type="password"
                  className="form-control bg-light border-start-0 ps-0"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary w-100 py-2 d-flex align-items-center justify-content-center gap-2 fw-semibold rounded-3"
              disabled={submitting}
            >
              {submitting ? 'Authenticating...' : 'Sign In to Portal'}
              <ArrowRight size={18} />
            </button>
          </form>

          <div className="mt-4 pt-3 border-top">
            <div className="d-flex gap-2">
              <button
                type="button"
                onClick={() => setDemoCredentials('admin')}
                className="btn btn-outline-primary btn-sm flex-fill extra-small"
              >
                Admin Account
              </button>
              <button
                type="button"
                onClick={() => setDemoCredentials('manager')}
                className="btn btn-outline-secondary btn-sm flex-fill extra-small"
              >
                Manager Account
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
