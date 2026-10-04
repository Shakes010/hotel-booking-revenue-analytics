import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Bookings from './pages/Bookings';
import CreateBooking from './pages/CreateBooking';
import Rooms from './pages/Rooms';
import Guests from './pages/Guests';
import Cancellations from './pages/Cancellations';
import Payments from './pages/Payments';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import Users from './pages/Users';

const MainLayout = ({ children }) => (
  <div className="d-flex flex-column min-vh-100 bg-light">
    <Navbar />
    <div className="d-flex flex-grow-1 overflow-hidden">
      <Sidebar />
      <main className="flex-grow-1 overflow-auto bg-light">
        {children}
      </main>
    </div>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Dashboard />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/bookings"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Bookings />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/create-booking"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <CreateBooking />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/rooms"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Rooms />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/guests"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Guests />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/cancellations"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Cancellations />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/payments"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Payments />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <AnalyticsDashboard />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/users"
            element={
              <ProtectedRoute allowedRoles={['Admin']}>
                <MainLayout>
                  <Users />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
