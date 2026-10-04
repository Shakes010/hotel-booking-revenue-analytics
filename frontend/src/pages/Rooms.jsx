import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { BedDouble, RefreshCw, Filter, ShieldAlert } from 'lucide-react';

const Rooms = () => {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('');

  useEffect(() => {
    fetchRooms();
  }, [filterStatus]);

  const fetchRooms = async () => {
    setLoading(true);
    try {
      const res = await api.get('/rooms', { params: { status: filterStatus } });
      setRooms(res.data.rooms);
    } catch (err) {
      console.error("Error fetching rooms:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (room, newStatus) => {
    if (room.status === 'occupied' && newStatus === 'available') {
      if (!window.confirm(`Room ${room.room_number} is currently occupied by a guest. Change status manually?`)) {
        return;
      }
    }
    try {
      await api.put(`/rooms/${room.id}/status`, { status: newStatus });
      fetchRooms();
    } catch (err) {
      alert(err.response?.data?.error || "Failed to update room status");
    }
  };

  return (
    <div className="p-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h3 className="fw-bold text-dark mb-1">Rooms Inventory & Housekeeping Grid</h3>
          <p className="text-muted small mb-0">Live room status monitoring, pricing tiers, and operational controls</p>
        </div>
        <button onClick={fetchRooms} className="btn btn-outline-primary btn-sm d-flex align-items-center gap-1 rounded-pill px-3">
          <RefreshCw size={14} /> Refresh Grid
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="mb-4 d-flex gap-2">
        {['', 'available', 'occupied', 'cleaning', 'maintenance'].map((st) => (
          <button
            key={st}
            onClick={() => setFilterStatus(st)}
            className={`btn btn-sm rounded-pill text-capitalize px-3 ${
              filterStatus === st ? 'btn-primary' : 'btn-outline-secondary'
            }`}
          >
            {st === '' ? 'All Inventory' : st}
          </button>
        ))}
      </div>

      {/* Rooms Grid Cards */}
      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status"></div>
        </div>
      ) : (
        <div className="row g-3">
          {rooms.map((room) => (
            <div className="col-xl-3 col-md-4 col-sm-6" key={room.id}>
              <div className="card card-dashboard p-3 h-100">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <span className="fs-4 fw-bold text-dark">Room {room.room_number}</span>
                  <span className={`badge ${
                    room.status === 'available' ? 'badge-status-available' :
                    room.status === 'occupied' ? 'badge-status-occupied' :
                    room.status === 'cleaning' ? 'badge-status-cleaning' : 'badge-status-maintenance'
                  }`}>
                    {room.status.toUpperCase()}
                  </span>
                </div>

                <div className="text-muted extra-small mb-3">
                  <div>Type: <strong className="text-dark">{room.room_type_name}</strong></div>
                  <div>Base Rate: <strong className="text-success">₹{room.base_price}/night</strong></div>
                  <div>Floor: <strong className="text-dark">Floor {room.floor}</strong></div>
                </div>

                <div className="border-top pt-2 mt-auto">
                  <label className="text-muted extra-small d-block mb-1">Operational Status:</label>
                  <select
                    className="form-select form-select-sm bg-light"
                    value={room.status}
                    onChange={(e) => handleStatusChange(room, e.target.value)}
                  >
                    <option value="available">Available</option>
                    <option value="occupied">Occupied</option>
                    <option value="cleaning">Cleaning</option>
                    <option value="maintenance">Maintenance</option>
                  </select>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Rooms;
