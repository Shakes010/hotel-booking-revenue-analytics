import React, { useEffect, useState } from 'react';
import api from '../services/api';
import {
  IndianRupee,
  BedDouble,
  CalendarX,
  TrendingUp,
  CalendarCheck,
  CheckCircle,
  LogOut,
  RefreshCw,
  Building
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  CartesianGrid,
  Legend
} from 'recharts';

const COLORS = ['#2563eb', '#0ea5e9', '#f59e0b', '#ef4444', '#10b981'];

const Dashboard = () => {
  const [kpis, setKpis] = useState(null);
  const [revenueByType, setRevenueByType] = useState([]);
  const [monthlyTrend, setMonthlyTrend] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [kpiRes, typeRes, trendRes] = await Promise.all([
        api.get('/analytics/summary'),
        api.get('/analytics/revenue-by-type'),
        api.get('/analytics/monthly-trend')
      ]);
      setKpis(kpiRes.data.kpis);
      setRevenueByType(typeRes.data.revenue_by_room_type);
      setMonthlyTrend(trendRes.data.monthly_trend);
    } catch (err) {
      console.error("Error loading dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center vh-50">
        <div className="spinner-border text-primary" role="status"></div>
      </div>
    );
  }

  // Derive booking status distribution for Pie Chart
  const statusDistribution = [
    { name: 'Confirmed / Checked-Out', value: (kpis?.total_bookings || 0) - (kpis?.total_cancellations || 0) },
    { name: 'Cancelled', value: kpis?.total_cancellations || 0 }
  ];

  return (
    <div className="p-4">
      {/* Header Bar */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h3 className="fw-bold text-dark mb-1">Executive Revenue Dashboard</h3>
          <p className="text-muted small mb-0">Real-time Operational Performance & Business Intelligence Overview</p>
        </div>
        <button onClick={fetchDashboardData} className="btn btn-outline-primary btn-sm d-flex align-items-center gap-1 rounded-pill px-3">
          <RefreshCw size={14} /> Refresh Data
        </button>
      </div>

      {/* Row 1: Primary Financial & Operational KPI Cards */}
      <div className="row g-3 mb-4">
        <div className="col-xl-3 col-md-6">
          <div className="card card-dashboard p-3">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted extra-small fw-bold text-uppercase">Total Revenue</span>
                <h3 className="fw-bold text-success mb-0 mt-1">₹{kpis?.total_revenue?.toLocaleString() || '0'}</h3>
                <small className="text-muted extra-small">Valid Bookings</small>
              </div>
              <div className="kpi-icon-box bg-success bg-opacity-10 text-success">
                <IndianRupee size={24} />
              </div>
            </div>
          </div>
        </div>

        <div className="col-xl-3 col-md-6">
          <div className="card card-dashboard p-3">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted extra-small fw-bold text-uppercase">Total Reservations</span>
                <h3 className="fw-bold text-primary mb-0 mt-1">{kpis?.total_bookings || 0}</h3>
                <small className="text-muted extra-small">Past 12 Months</small>
              </div>
              <div className="kpi-icon-box bg-primary bg-opacity-10 text-primary">
                <CalendarCheck size={24} />
              </div>
            </div>
          </div>
        </div>

        <div className="col-xl-3 col-md-6">
          <div className="card card-dashboard p-3">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted extra-small fw-bold text-uppercase">Occupancy Rate</span>
                <h3 className="fw-bold text-info mb-0 mt-1">{kpis?.occupancy_rate || 0}%</h3>
                <small className="text-muted extra-small">Period Capacity</small>
              </div>
              <div className="kpi-icon-box bg-info bg-opacity-10 text-info">
                <BedDouble size={24} />
              </div>
            </div>
          </div>
        </div>

        <div className="col-xl-3 col-md-6">
          <div className="card card-dashboard p-3">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted extra-small fw-bold text-uppercase">Cancellation Rate</span>
                <h3 className="fw-bold text-danger mb-0 mt-1">{kpis?.cancellation_rate || 0}%</h3>
                <small className="text-muted extra-small">{kpis?.total_cancellations || 0} Cancelled</small>
              </div>
              <div className="kpi-icon-box bg-danger bg-opacity-10 text-danger">
                <CalendarX size={24} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: Secondary Performance KPIs */}
      <div className="row g-3 mb-4">
        <div className="col-md-3">
          <div className="card card-dashboard p-3">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <span className="text-muted extra-small fw-bold">ADR (Avg Daily Rate)</span>
                <h5 className="fw-bold text-dark mt-1 mb-0">₹{kpis?.adr?.toLocaleString() || 0}</h5>
              </div>
              <TrendingUp size={20} className="text-primary" />
            </div>
          </div>
        </div>

        <div className="col-md-3">
          <div className="card card-dashboard p-3">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <span className="text-muted extra-small fw-bold">RevPAR</span>
                <h5 className="fw-bold text-dark mt-1 mb-0">₹{kpis?.revpar?.toLocaleString() || 0}</h5>
              </div>
              <IndianRupee size={20} className="text-warning" />
            </div>
          </div>
        </div>

        <div className="col-md-3">
          <div className="card card-dashboard p-3">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <span className="text-muted extra-small fw-bold">Available / Occupied Rooms</span>
                <h5 className="fw-bold text-dark mt-1 mb-0">{kpis?.available_rooms || 0} / {kpis?.occupied_rooms || 0}</h5>
              </div>
              <Building size={20} className="text-success" />
            </div>
          </div>
        </div>

        <div className="col-md-3">
          <div className="card card-dashboard p-3">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <span className="text-muted extra-small fw-bold">Today's Check-ins / Outs</span>
                <h5 className="fw-bold text-dark mt-1 mb-0">{kpis?.todays_check_ins || 0} / {kpis?.todays_check_outs || 0}</h5>
              </div>
              <CheckCircle size={20} className="text-info" />
            </div>
          </div>
        </div>
      </div>

      {/* Row 3: Recharts Charts Grid */}
      <div className="row g-4 mb-4">
        {/* 1. Monthly Revenue Trend (Line/Area Chart) */}
        <div className="col-lg-8">
          <div className="card card-dashboard p-3 h-100">
            <h6 className="fw-bold text-dark mb-3">Monthly Revenue Trend (₹)</h6>
            <div style={{ width: '100%', height: 280 }}>
              <ResponsiveContainer>
                <AreaChart data={monthlyTrend}>
                  <defs>
                    <linearGradient id="colorRevLight" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563eb" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="label" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#cbd5e1', color: '#0f172a' }} />
                  <Area type="monotone" dataKey="monthly_revenue" stroke="#2563eb" strokeWidth={2} fillOpacity={1} fill="url(#colorRevLight)" name="Revenue (₹)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* 2. Revenue Share by Room Type (Bar Chart) */}
        <div className="col-lg-4">
          <div className="card card-dashboard p-3 h-100">
            <h6 className="fw-bold text-dark mb-3">Revenue by Room Category</h6>
            <div style={{ width: '100%', height: 280 }}>
              <ResponsiveContainer>
                <BarChart data={revenueByType} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis type="number" stroke="#64748b" fontSize={10} />
                  <YAxis type="category" dataKey="room_type" stroke="#64748b" fontSize={10} width={100} />
                  <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#cbd5e1', color: '#0f172a' }} />
                  <Bar dataKey="total_revenue" fill="#0ea5e9" name="Revenue (₹)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Row 4: Monthly Booking Trend & Status Breakdown */}
      <div className="row g-4">
        {/* 3. Monthly Booking Volume Trend (Line Chart) */}
        <div className="col-lg-8">
          <div className="card card-dashboard p-3 h-100">
            <h6 className="fw-bold text-dark mb-3">Monthly Reservation Volume</h6>
            <div style={{ width: '100%', height: 260 }}>
              <ResponsiveContainer>
                <LineChart data={monthlyTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="label" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#cbd5e1', color: '#0f172a' }} />
                  <Line type="monotone" dataKey="total_bookings" stroke="#10b981" strokeWidth={2.5} name="Total Bookings" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* 4. Booking Status Distribution (Donut Chart) */}
        <div className="col-lg-4">
          <div className="card card-dashboard p-3 h-100">
            <h6 className="fw-bold text-dark mb-3">Booking Status Distribution</h6>
            <div style={{ width: '100%', height: 260 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={statusDistribution}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={4}
                    label
                  >
                    <Cell fill="#10b981" />
                    <Cell fill="#ef4444" />
                  </Pie>
                  <Tooltip />
                  <Legend verticalAlign="bottom" height={36} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
