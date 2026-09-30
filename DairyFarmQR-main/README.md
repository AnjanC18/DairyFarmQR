# 🐄 Smart Dairy Farm Management System

> **A Comprehensive Full-Stack Web Application with Daily Milk Production Monitoring, Cattle Health Tracking, QR Code Tagging, 3-Tier Role-Based Security, and Financial Analytics.**
> 
> *Built for MCA Minor Project*

---

## 🌟 Key Features

- **🥛 Daily Milk Production Monitoring**:
  - Track Morning, Evening, and Afternoon milking yields.
  - Quality metrics logging (Fat %, SNF %) and auto-rate calculation (₹).
  - Fast session batch entry grid for recording multiple cattle simultaneously.

- **🏷️ Digital Cattle Ear Tag & QR System**:
  - Automated generation of high-resolution QR codes with cattle tag labels.
  - Real-time webcam/mobile camera QR scanner powered by `html5-qrcode` with instant profile lookup.
  - Printable QR tags for physical cattle identification.

- **🌾 Feed & Ration Inventory**:
  - Stock level tracking across fodder categories (Green, Dry, Concentrates, Mineral Mixture, Silage).
  - Minimum stock threshold warnings and restock alerts.
  - Daily feed consumption logger with automatic inventory deduction and cost calculation.

- **💉 Health & Vaccination Scheduling**:
  - Track immunization records for FMD, Brucellosis, Blackleg, HS, Anthrax, and Deworming.
  - Color-coded alerts for `Overdue`, `Upcoming`, and `Completed` schedules.
  - One-click administration action to advance booster schedules.

- **👥 Farm Workforce & Payroll**:
  - Employee directory (milkers, caretakers, supervisors, veterinarians).
  - Monthly payroll and staff status monitoring.

- **🧾 Operational Expense Ledger**:
  - Categorized cost tracking for Feed, Veterinary, Maintenance, Utilities, and Labor.
  - Real-time expense breakdown cards.

- **📊 Visual Analytics & Reports (Chart.js)**:
  - 7-Day milk production curves (Morning vs Evening).
  - Cattle status and health distribution charts.
  - Daily revenue vs operating expense trend comparison.
  - Top 5 milk-producing cattle leaderboard.
  - Print-ready format for presentations and documentation.

- **🔐 3-Tier Role-Based Access Control (RBAC) & Security**:
  - **Admin-Only Account Provisioning**: Public registration is disabled to maintain strict farm data security. Only authenticated Farm Administrators can create, assign roles, activate/deactivate, or delete user logins.
  - **Tiered Role Architecture**:
    - 🔴 **Administrator (`admin`)**: Full system, user management, financial, and operational control.
    - 🔵 **Farm Manager (`manager`)**: Herd oversight, batch milk recording, feed restocking, and health schedules.
    - 🟢 **Farm Staff (`staff`)**: Barn-level daily milk logging, QR tag scanning, and feed ration entries.

---

## 📊 Role & Permission Matrix

| Feature / Module | 🔴 Administrator (`admin`) | 🔵 Farm Manager (`manager`) | 🟢 Farm Staff (`staff`) |
| :--- | :---: | :---: | :---: |
| **User & Login Creation** | ✅ Full Access | ❌ Restricted | ❌ Restricted |
| **Cattle Records & QR Codes** | ✅ Full Access | ✅ Full Access | 👁️ View & Scan |
| **Milk Yield & Batch Entry** | ✅ Full Access | ✅ Full Access | ✅ Daily Entry |
| **Feed Stock & Daily Ration** | ✅ Full Access | ✅ Full Access | ✅ Log Rations |
| **Vaccinations & Health** | ✅ Full Access | ✅ Full Access | ✅ Mark Done |
| **Staff & Payroll Records** | ✅ Full Access | ✅ Manage Staff | ❌ Restricted |
| **Expense & Cost Tracking** | ✅ Full Access | ✅ Log Expenses | ❌ Restricted |
| **Analytics & Export Reports** | ✅ Full Access | ✅ Full Access | 👁️ View Only |

---

## 🛠️ Technology Stack

### Frontend
- **HTML5 & CSS3** (Vanilla CSS with modern glassmorphism & responsive sidebar design)
- **Bootstrap 5.3.3**
- **JavaScript (ES6+)**
- **Jinja2 Templates**
- **Chart.js 4.4**
- **FontAwesome 6.5**
- **html5-qrcode**

### Backend
- **Python 3.10+ / 3.14**
- **Flask 3.x**
- **Flask-SQLAlchemy 3.x** (ORM)
- **Flask-Login** (Authentication & Role Management)
- **Flask-WTF**
- **qrcode & Pillow (PIL)** (QR Code Generation)
- **PyMySQL** (MySQL Connector)

### Database
- **MySQL** (Default production schema in `database/dairy.sql`)
- **SQLite** (Auto-fallback for zero-setup local development)

---

## 📁 Project Structure

```text
Smart-Dairy-Farm/
│
├── app.py                      # Application entry point & auto-seed initialization
├── config.py                   # Environment & Database Configuration
├── requirements.txt            # Python dependencies
├── test_app.py                 # Automated unit and integration test suite
├── .gitignore
├── README.md
│
├── .vscode/
│   ├── launch.json             # 1-click VS Code Run & Debug configuration
│   └── settings.json           # Python import path resolver
│
├── database/
│   └── dairy.sql               # MySQL Schema DDL and sample seed data
│
├── models/
│   ├── __init__.py             # SQLAlchemy instance
│   ├── user.py                 # User authentication & RBAC models
│   ├── animal.py               # Cattle lifecycle and health models
│   ├── milk.py                 # Milk production & session models
│   ├── feed.py                 # Feed inventory & consumption models
│   ├── vaccination.py          # Vaccination & health timeline models
│   ├── employee.py             # Staff workforce models
│   └── expense.py              # Operational expense models
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Login, profile, admin user management & role control
│   ├── main.py                 # Overview dashboard
│   ├── animal.py               # Cattle CRUD & profile views
│   ├── milk.py                 # Milk production registers & batch entry
│   ├── feed.py                 # Inventory & consumption
│   ├── vaccination.py          # Immunization schedule
│   ├── employee.py             # Staff directory
│   ├── expense.py              # Expense tracking
│   ├── report.py               # Financial & production analytics
│   └── qr.py                   # QR scanner & tag downloads
│
├── utils/
│   ├── __init__.py
│   └── qr_helper.py            # High-resolution QR code generator
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom UI stylesheets
│   ├── js/
│   │   └── script.js           # Client-side scripts & calculations
│   ├── images/
│   └── qr_codes/               # Generated QR code image files
│
└── templates/
    ├── layout.html             # Master layout with responsive sidebar & role navigation
    ├── login.html              # Sign-in page
    ├── users.html              # Admin user management & login creation portal
    ├── register.html           # Admin create new user login page
    ├── profile.html            # User account settings
    ├── dashboard.html          # Main KPI dashboard & charts
    ├── animals.html            # Cattle list & filter pills
    ├── add_animal.html         # Cattle registration form
    ├── edit_animal.html        # Cattle edit form
    ├── animal_detail.html      # Individual cattle profile & QR badge
    ├── milk_production.html    # Daily milk production register
    ├── quick_milk_entry.html   # Milking session batch entry grid
    ├── feed.html               # Feed inventory cards & consumption logger
    ├── vaccination.html        # Vaccination schedule & overdue badges
    ├── employees.html          # Staff roster & payroll
    ├── expenses.html           # Expense ledger
    ├── reports.html            # Date-filtered analytics & print views
    └── scan_qr.html            # Live camera QR scanner
```

---

## ⚡ Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/AnjanC18/DairyFarm.git
cd DairyFarm
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux / macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup (Optional MySQL)
- By default, the application runs on **SQLite** out-of-the-box with pre-populated demo data.
- To connect to **MySQL**, import `database/dairy.sql` into MySQL Workbench and set environment variable:
  ```bash
  set USE_MYSQL=true
  set DB_USER=root
  set DB_PASSWORD=your_password
  set DB_HOST=localhost
  set DB_NAME=dairy_farm
  ```

### 5. Run the Application
```bash
python app.py
```

Open your browser and visit: **`http://localhost:5000`**

---

## 🔑 Default Credentials

- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `Administrator` (Full Access)

> **Note**: To create logins for Farm Managers or Farm Staff, sign in as `admin` and navigate to **"User Logins & Access"** in the sidebar.

---

## 🧪 Running Tests

Execute the automated test suite covering all routes, authentication, RBAC security, and QR endpoints:
```bash
python test_app.py
```

---

## 📄 License
This project is licensed under the MIT License - open for educational and non-commercial project use.
