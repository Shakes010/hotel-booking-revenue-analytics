import React, { useContext } from 'react';
import { NavLink } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import {
  LayoutDashboard,
  CalendarCheck,
  PlusCircle,
  BedDouble,
  Users,
  XCircle,
  CreditCard,
  BarChart3,
  UserCheck
} from 'lucide-react';

const Sidebar = () => {
  const { user } = useContext(AuthContext);
  const role = user?.role_name || '';

  return (
    <aside className="sidebar text-white p-3 vh-100" style={{ width: '250px' }}>
      <div className="px-2 mb-3">
        <small className="text-slate-400 text-uppercase fw-bold extra-small letter-spacing-1">Operations</small>
      </div>

      <ul className="nav nav-pills flex-column mb-auto gap-1">
        <li className="nav-item">
          <NavLink to="/dashboard" className={({ isActive }) => `nav-link d-flex align-items-center gap-3 ${isActive ? 'active' : ''}`}>
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </NavLink>
        </li>

        <li className="nav-item">
          <NavLink to="/bookings" className={({ isActive }) => `nav-link d-flex align-items-center gap-3 ${isActive ? 'active' : ''}`}>
            <CalendarCheck size={18} />
            <span>Bookings</span>
          </NavLink>
        </li>

        <li className="nav-item">
          <NavLink to="/create-booking" className={({ isActive }) => `nav-link d-flex align-items-center gap-3 ${isActive ? 'active' : ''}`}>
            <PlusCircle size={18} />
            <span>New Reservation</span>
          </NavLink>
        </li>

        <li className="nav-item">
          <NavLink to="/rooms" className={({ isActive }) => `nav-link d-flex align-items-center gap-3 ${isActive ? 'active' : ''}`}>
            <BedDouble size={18} />
            <span>Rooms & Inventory</span>
          </NavLink>
        </li>

        <li className="nav-item">
          <NavLink to="/guests" className={({ isActive }) => `nav-link d-flex align-items-center gap-3 ${isActive ? 'active' : ''}`}>
            <Users size={18} />
            <span>Guests Directory</span>
          </NavLink>
        </li>

        <li className="nav-item">
          <NavLink to="/cancellations" className={({ isActive }) => `nav-link d-flex align-items-center gap-3 ${isActive ? 'active' : ''}`}>
            <XCircle size={18} />
            <span>Cancellations</span>
          </NavLink>
        </li>

        <li className="nav-item">
          <NavLink to="/payments" className={({ isActive }) => `nav-link d-flex align-items-center gap-3 ${isActive ? 'active' : ''}`}>
            <CreditCard size={18} />
            <span>Payments</span>
          </NavLink>
        </li>
      </ul>

      <hr className="border-slate-700 my-3" />

      <div className="px-2 mb-2">
        <small className="text-slate-400 text-uppercase fw-bold extra-small letter-spacing-1">Intelligence</small>
      </div>

      <ul className="nav nav-pills flex-column gap-1">
        <li className="nav-item">
          <NavLink to="/analytics" className={({ isActive }) => `nav-link d-flex align-items-center gap-3 ${isActive ? 'active' : ''}`}>
            <BarChart3 size={18} />
            <span>Power BI Analytics</span>
          </NavLink>
        </li>

        {/* User Management visible for Admin only */}
        {role === 'Admin' && (
          <li className="nav-item mt-2">
            <NavLink to="/users" className={({ isActive }) => `nav-link d-flex align-items-center gap-3 ${isActive ? 'active' : ''}`}>
              <UserCheck size={18} />
              <span>Staff Accounts</span>
            </NavLink>
          </li>
        )}
      </ul>
    </aside>
  );
};

export default Sidebar;
