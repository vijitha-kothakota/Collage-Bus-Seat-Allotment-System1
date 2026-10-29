# 🚌 College Bus Seat Allotment & Live Tracking System
**B.Tech Mini Project &bull; Ananthalakshmi Institute of Technology & Sciences (ALTS)**

A full-stack web application built with **Python Flask**, **SQLite**, **Leaflet.js**, and **Bootstrap 5**. Designed for college transportation management, interactive 2×2 bus seat reservation with yearly database locking, digital QR-code bus passes, live GPS tracking from drivers' mobile phones, and automatic proximity arrival alerts.

---

## 🌟 Key Features

### 1. Student Portal
- **Registration & Login**: Student ID strictly formatted as **10 characters mixed with letters and numbers** (e.g. `23B91A0501`). Password as per student's choice.
- **Year-Based Shift Schedules**:
  - 🎓 **1st Year (Freshers)**: Morning Pickup at **8:30 AM** &bull; Evening Return at **5:00 PM**.
  - 🎓 **2nd, 3rd & 4th Years**: Morning Pickup at **7:30 AM** &bull; Evening Return at **4:00 PM**.
- **Interactive Visual Seat Selection**: Real-time visual bus cabin layout (DRIVER at front, 2×2 rows, central aisle).
  - 🟢 **Available** (Green)
  - 🔴 **Occupied & Locked** (Red)
  - 🔵 **Selected** (Blue)
- **Yearly Seat Locking**: Once a seat is booked and paid for an academic year (e.g., 2026–27), database-level unique constraints prevent any other student from booking that seat.
- **Simulated Bus Fee Payment**: Instant demo gateway supporting UPI, Debit/Credit Card, and Net Banking.
- **Digital Bus Pass**: Printable pass containing student photo placeholder, route, seat number, verified college stamp, and a verifiable **QR Code** generated with Python's `qrcode` library.
- **Live Bus Tracking & Proximity Alerts**:
  - Live OpenStreetMap powered by Leaflet.js.
  - Real-time bus marker movement polled every 3 seconds.
  - Dynamic calculation of distance to student's boarding stop using the Haversine formula.
  - **🚨 Approaching Stop Proximity Alert**: Triggers an alert banner and audio chime sound when the bus is within 1.2 km of the student's stop!

### 2. Driver Console (Mobile-Optimized)
- Responsive mobile UI designed specifically for smartphone browsers.
- Big touch-friendly **START TRIP** and **END TRIP** buttons.
- Utilizes the browser's **HTML5 Geolocation API** (`navigator.geolocation.watchPosition`) to transmit real-time latitude, longitude, accuracy, and speed to the Flask backend (`POST /api/bus-location`).
- **Lab / Presentation Mode**: Toggle to simulate movement along route stops for indoor classroom demonstrations.

### 3. Transport Administration Panel
- **8 KPI Metric Cards**: Total Students, Total Buses, Total Seats, Allocated Seats, Available Seats, Paid Fees, Pending Fees, and Active Trips.
- **Fleet Management**: Add buses, configure capacity (default 40 seats), and assign routes.
- **Route & Stop Management**: Add routes and boarding points with GPS coordinates and scheduled pickup times.
- **Student Database Registry**: Search, filter, add, or remove student records.
- **Seat Allocations & Payments Audit**: Real-time ledger of transactions and ability to release seats.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.11, Flask 3.1, Flask-SQLAlchemy, Flask-Login, Werkzeug |
| **Database** | SQLite (`database/bus.db`) |
| **Frontend** | HTML5, CSS3, JavaScript (ES6), Bootstrap 5.3, Bootstrap Icons |
| **Mapping & GPS** | Leaflet.js, OpenStreetMap, HTML5 Geolocation API, Web Audio API |
| **QR Code** | Python `qrcode` & `Pillow` |

---

## 📂 Project Directory Structure

```text
college_bus/
│
├── app.py                     # Main Flask Application & API Routes
├── config.py                  # Database & App Configuration
├── requirements.txt           # Python Dependencies
├── seed.py                    # Initial Sample Data Population
├── test_app.py                # Automated Unit & Integration Tests
├── utils.py                   # Role Decorators, QR Generator & Haversine Distance
│
├── models/                    # SQLAlchemy Database Models
│   ├── __init__.py
│   ├── user.py                # User & Flask-Login Auth
│   ├── student.py             # Student Model & Shift Timings
│   ├── driver.py              # Driver Model & Bus Link
│   ├── bus.py                 # Bus Model & Capacity
│   ├── route.py               # Route Model & Distance
│   ├── boarding_point.py      # GPS Stops & Pickup Times
│   ├── seat.py                # Bus Seat Model
│   ├── allocation.py          # Seat Allocation & Year Locking Constraint
│   ├── payment.py             # Demo Payment Transactions
│   ├── bus_pass.py            # Digital Bus Pass & QR Reference
│   └── bus_location.py        # Real-time GPS Telemetry
│
├── templates/                 # Jinja2 HTML Templates
│   ├── base.html              # Layout, Navbar & College Logo
│   ├── login.html             # Login Page with 1-Click Credentials
│   ├── register.html          # Registration with 10-Char ID Validation
│   │
│   ├── student/
│   │   ├── dashboard.html     # Student Dashboard & Timetable
│   │   ├── buses.html         # Bus & Route Selection
│   │   ├── seats.html         # Interactive 2x2 Seat Layout
│   │   ├── payment.html       # Demo Payment Gateway
│   │   ├── bus_pass.html      # Printable QR Bus Pass
│   │   └── track_bus.html     # Live Map & Proximity Alerts
│   │
│   ├── driver/
│   │   └── dashboard.html     # Mobile GPS Transmitter Console
│   │
│   └── admin/
│       ├── dashboard.html     # 8 KPI Metric Cards & Fleet Overview
│       ├── buses.html         # Add & Manage Buses
│       ├── routes.html        # Add Routes & Boarding Points
│       ├── students.html      # Searchable Student Database
│       ├── allocations.html   # Seat Lock Audit
│       └── payments.html      # Fee Transaction Ledger
│
├── static/
│   ├── css/
│   │   └── style.css          # Background Bus Styling & Glassmorphism
│   ├── js/
│   │   ├── main.js            # Tooltips & Alert Dismissal
│   │   ├── seats.js           # Visual Seat Selection Interaction
│   │   ├── tracking.js        # Leaflet Polling, Chime & Alerts
│   │   └── driver_gps.js      # HTML5 Geolocation Watcher & Simulator
│   ├── images/
│   │   ├── college_bus_bg.png # Website Background Image
│   │   └── alts_logo.png      # Transparent ALTS College Emblem
│   └── qr_codes/              # Generated QR Code PNG Images
│
└── database/
    └── bus.db                 # SQLite Relational Database
```

---

## 🚀 How to Run the Project

### Step 1: Open Terminal in Project Directory
```powershell
cd "C:\Users\Lenovo\.gemini\antigravity\scratch\college_bus"
```

### Step 2: Activate the Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### Step 3: Run the Flask Server
```powershell
python app.py
```

The application will start on:
- **Local PC**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Mobile Phone on Wi-Fi**: `http://<YOUR_LOCAL_IP>:5000` (e.g., `http://10.217.158.170:5000`)

---

## 🔑 Demo Login Accounts (1-Click Fill on Login Page)

| Role | Username / Identifier | Password | Details |
|---|---|---|---|
| **Student** | `23B91A0501` | `student123` | **Vijitha** &bull; 1st Year (8:30 AM - 5:00 PM) |
| **Student 2** | `23B91A0502` | `student123` | **Rahul Sharma** &bull; 3rd Year (7:30 AM - 4:00 PM) |
| **Driver** | `driver_ramesh` | `driver123` | **Ramesh Kumar** &bull; Bus BUS-05 |
| **Admin** | `admin` | `admin123` | **College Administrator** |

---

## 📱 Testing Mobile GPS Tracking from an Android Phone

1. Ensure your laptop/PC and your Android phone are connected to the **same Wi-Fi network**.
2. On your phone's browser (e.g. Chrome), navigate to:
   ```text
   http://10.217.158.170:5000
   ```
3. Tap **Driver Login** (or click the quick fill button for **Ramesh Kumar**).
4. Tap the large green **START TRIP** button.
5. When Android prompts: *"Allow this website to access your location?"*, tap **Allow**.
6. On your PC/laptop, open [http://127.0.0.1:5000](http://127.0.0.1:5000), log in as student **Vijitha**, and click **Track My Bus**.
7. Watch the bus marker update in real time on the OpenStreetMap as the driver moves!
8. When the bus approaches within 1.2 km of the student's stop, notice the **Approaching Bus Alert Banner** and audio chime!

---

## 🧪 Running Automated Unit Tests
To verify all 13 phases, seat locking constraints, student ID validations, and APIs:
```powershell
.\venv\Scripts\python.exe -m unittest test_app.py -v
```
All 5 test suites will run and report: `Ran 5 tests in ... OK`.
