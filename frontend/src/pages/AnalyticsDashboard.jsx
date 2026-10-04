import React, { useState } from 'react';
import { BarChart3, Calculator, Code, ExternalLink, Database, Layers } from 'lucide-react';

const AnalyticsDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="p-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h3 className="fw-bold text-dark mb-1">Power BI Business Intelligence Hub</h3>
          <p className="text-muted small mb-0">Academic Demonstration - Star Schema Data Warehouse & DAX Analytics Integration</p>
        </div>
        <a
          href="file:///C:/Users/AbelMathewBose/OneDrive/Desktop/Hotel-Booking-Revenue-Analytics/power_bi/README_POWERBI.md"
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-warning text-dark fw-semibold btn-sm d-flex align-items-center gap-1 rounded-pill px-3"
        >
          <ExternalLink size={15} /> Power BI Guide & Specs
        </a>
      </div>

      {/* Tabs */}
      <ul className="nav nav-tabs border-bottom mb-4">
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'overview' ? 'active font-weight-bold text-primary border-primary border-bottom-0' : 'text-muted'}`}
            onClick={() => setActiveTab('overview')}
          >
            <BarChart3 size={16} className="me-2" /> Star Schema & Architecture
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'dax' ? 'active font-weight-bold text-primary border-primary border-bottom-0' : 'text-muted'}`}
            onClick={() => setActiveTab('dax')}
          >
            <Calculator size={16} className="me-2" /> DAX Measures Reference
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'embed' ? 'active font-weight-bold text-primary border-primary border-bottom-0' : 'text-muted'}`}
            onClick={() => setActiveTab('embed')}
          >
            <Code size={16} className="me-2" /> Power BI Integration Canvas
          </button>
        </li>
      </ul>

      {activeTab === 'overview' && (
        <div className="row g-4">
          <div className="col-md-6">
            <div className="card card-dashboard p-4 h-100">
              <h5 className="fw-bold text-primary mb-3">Star Schema Data Model Architecture</h5>
              <p className="text-muted small">
                The MySQL database connects directly into Microsoft Power BI using a Star Schema layout for fast analytical aggregation:
              </p>
              <div className="list-group list-group-flush border-top extra-small">
                <div className="list-group-item bg-transparent py-2">
                  <strong className="text-dark">FactBookings Table:</strong> Primary transaction fact table (Revenue, Nights Stayed, Lead Time).
                </div>
                <div className="list-group-item bg-transparent py-2">
                  <strong className="text-dark">FactCancellations Table:</strong> Financial loss and refund facts.
                </div>
                <div className="list-group-item bg-transparent py-2">
                  <strong className="text-dark">DimDate Table:</strong> Dynamic calendar dimension supporting YTD, MoM, and YoY DAX time intelligence.
                </div>
                <div className="list-group-item bg-transparent py-2">
                  <strong className="text-dark">DimRoom & DimGuest Tables:</strong> Categorical attributes, price tiers, and customer demographics.
                </div>
              </div>
            </div>
          </div>

          <div className="col-md-6">
            <div className="card card-dashboard p-4 h-100">
              <h5 className="fw-bold text-success mb-3">Core DAX Formulas & Analytics Metrics</h5>
              <div className="mb-3">
                <h6 className="fw-bold text-dark extra-small text-uppercase">1. Occupancy Rate (%)</h6>
                <code className="text-primary d-block bg-light p-2 rounded extra-small mb-1 border">Occupancy Rate = (Occupied Room Nights / Available Room Nights) * 100</code>
                <small className="text-muted extra-small">Measures historical room capacity utilization.</small>
              </div>
              <div className="mb-3">
                <h6 className="fw-bold text-dark extra-small text-uppercase">2. ADR (Average Daily Rate)</h6>
                <code className="text-warning-emphasis d-block bg-light p-2 rounded extra-small mb-1 border">ADR = Total Valid Revenue / Sold Room Nights</code>
                <small className="text-muted extra-small">Calculates average revenue per occupied room.</small>
              </div>
              <div>
                <h6 className="fw-bold text-dark extra-small text-uppercase">3. RevPAR (Revenue Per Available Room)</h6>
                <code className="text-success d-block bg-light p-2 rounded extra-small mb-1 border">RevPAR = (Occupancy Rate % / 100) * ADR</code>
                <small className="text-muted extra-small">Blends occupancy and rate performance into a single core metric.</small>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'dax' && (
        <div className="card card-dashboard p-4">
          <h5 className="fw-bold text-dark mb-3">Power BI DAX Formulas Reference Library</h5>
          <pre className="bg-dark text-success p-3 rounded overflow-auto font-monospace extra-small" style={{ maxHeight: '450px' }}>
{`// 1. Total Revenue ($ / ₹)
Total Revenue = 
CALCULATE(
    SUM(FactBookings[total_amount]),
    FactBookings[status] IN {"confirmed", "checked_in", "checked_out"}
)

// 2. Cancellation Rate (%)
Cancellation Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(FactBookings), FactBookings[status] = "cancelled"),
    COUNTROWS(FactBookings),
    0
) * 100

// 3. Occupancy Rate (%)
Occupancy Rate % = 
DIVIDE(
    SUM(FactBookings[nights_stayed]),
    DISTINCTCOUNT(DimRoom[id]) * COUNTROWS(DimDate),
    0
) * 100

// 4. ADR (Average Daily Rate)
ADR = DIVIDE([Total Revenue], SUM(FactBookings[nights_stayed]), 0)

// 5. RevPAR (Revenue Per Available Room)
RevPAR = ([Occupancy Rate %] / 100) * [ADR]`}
          </pre>
        </div>
      )}

      {activeTab === 'embed' && (
        <div className="card card-dashboard p-4 text-center py-5">
          <BarChart3 size={48} className="text-primary mb-3 mx-auto" />
          <h5 className="fw-bold text-dark">Power BI Integration Container</h5>
          <p className="text-muted col-md-8 mx-auto small mb-4">
            Connect Power BI Desktop to MySQL database <code>hotel_analytics_db</code> using the setup guide. Once published to Power BI Service, paste the embed iframe code below to load the interactive dashboard canvas directly inside React.
          </p>
          <div className="p-3 bg-light rounded border text-start font-monospace extra-small col-md-10 mx-auto">
            &lt;iframe title="Hotel Revenue Analytics" width="100%" height="600" src="YOUR_POWERBI_EMBED_URL" frameborder="0" allowFullScreen="true"&gt;&lt;/iframe&gt;
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;
