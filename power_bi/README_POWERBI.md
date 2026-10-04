# Power BI Analytics Dashboard Integration Specification
## Hotel Booking & Revenue Analytics System (MCA Project)

### 1. MySQL 8.4 Connection Parameters & Date Range Scope
- **Database Engine**: MySQL 8.4 Server
- **Server / Host**: `localhost:3306` (or `127.0.0.1:3306`)
- **Database Name**: `hotel_analytics_db`
- **Data Connectivity Mode**: **Import Mode**
- **Analytical Date Range**: **January 1, 2025 – June 30, 2026** (18 Months Complete Coverage)

---

### 2. Star Schema Architecture

#### Fact Tables
1. **`FactBookings`**: Transaction core (`id`, `booking_reference`, `guest_id`, `room_id`, `check_in_date`, `check_out_date`, `nights_stayed`, `lead_time_days`, `total_amount`, `status`).
2. **`FactCancellations`**: Financial loss audit (`id`, `booking_id`, `cancelled_at`, `reason`, `cancellation_fee`, `refund_amount`).
3. **`FactPayments`**: Payment transactions (`id`, `booking_id`, `payment_method`, `amount`, `payment_date`, `transaction_id`, `status`).

#### Dimension Tables
1. **`DimDate`**: Dynamic calendar covering `2025-01-01` to `2026-06-30` (`Date`, `Year`, `Month Number`, `Month Name`, `Quarter`, `Year-Month`, `Day`, `Day Name`, `Week Number`, `IsWeekend`).
2. **`DimRoom`**: Inventory (`id`, `room_number`, `room_type_id`, `status`, `floor`).
3. **`DimRoomType`**: Room tiers & base pricing (`id`, `type_name`, `base_price`, `capacity`).
4. **`DimGuest`**: Demographics (`id`, `full_name`, `email`, `phone`, `city`, `country`).

---

### 3. Model Relationships
In Power BI **Model View**, establish the following relationships:

1. **`FactBookings[room_id]`** $\rightarrow$ **`DimRoom[id]`** *(Many-to-One)*
2. **`FactBookings[guest_id]`** $\rightarrow$ **`DimGuest[id]`** *(Many-to-One)*
3. **`FactBookings[check_in_date]`** $\rightarrow$ **`DimDate[Date]`** *(Many-to-One, Active)*
4. **`FactCancellations[booking_id]`** $\rightarrow$ **`FactBookings[id]`** *(One-to-One)*
5. **`FactPayments[booking_id]`** $\rightarrow$ **`FactBookings[id]`** *(Many-to-One)*
6. **`DimRoom[room_type_id]`** $\rightarrow$ **`DimRoomType[id]`** *(Many-to-One)*

---

### 4. Recalculated Final Expanded Dataset Metrics (Jan 2025 - Jun 2026)

| Metric | SQL / Power BI Value |
|---|---|
| **Total Historical Bookings** | `691` |
| **Total Cancellations** | `128` |
| **Valid Bookings Count** | `563` |
| **Cancellation Rate %** | `18.52%` |
| **Total Valid Revenue** | `INR 14,316,500.00` |
| **Sold Room Nights** | `1,951 nights` |
| **Average Daily Rate (ADR)** | `INR 7,338.03` |
| **Occupancy Rate %** | `17.87%` |
| **RevPAR** | `INR 1,311.31` |
| **Revenue Lost to Cancellations** | `INR 2,903,000.00` |
