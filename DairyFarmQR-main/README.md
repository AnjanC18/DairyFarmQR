# 🐄 Smart Dairy Farm Management System with AI & Predictive Analytics

> **A Comprehensive Full-Stack Dairy Enterprise Web Application with Machine Learning Forecasting, Anomaly Detection, Mastitis Risk Analysis, QR Code Ear Tagging, 3-Tier Role-Based Access Control (RBAC), and Food Safety Milk Withholding Management.**
> 
> *Academic Minor/Major Project & Production Reference Implementation*

---

## 🌟 System Highlights & Key Features

### 🤖 1. Artificial Intelligence & Machine Learning Subsystem (`services/ai_engine.py`)
The system features 6 production-ready AI/ML intelligence capabilities accessible via the **AI Intelligence Hub (`/ai-insights`)** and dedicated REST APIs:

1. **Milk Yield Forecasting (7 to 14 Days Ahead)**:
   - **Algorithms**: scikit-learn `RandomForestRegressor` and `GradientBoostingRegressor` with autoregressive lag features (lag 1, lag 2, lag 7, rolling 7-day mean, and milking session split).
   - **Inputs**: Historical yields, days in milk (lactation curve), breed, session (Morning/Evening), weight, and age.
   - **Visual Output**: Interactive Chart.js forecast line on both the **Reports** (`/reports`) and **Cattle Dossier** (`/animals/<id>`) pages with a 95% Confidence Interval envelope (expanding uncertainty cone).
2. **Early Illness Anomaly Detection**:
   - **Algorithms**: Rolling 7-day dynamic z-scores ($Z \le -1.8$) combined with `IsolationForest` multi-dimensional outlier scoring.
   - **Output**: Instant alert banners on the **Dashboard** and **Milk Production Register**:
     > *"DF-102 gave 38% less than her 7-day average. Check her health."*
   - Includes actionable veterinary directives (California Mastitis Test, rectal temperature, quarter isolation).
3. **Mastitis Risk Prediction Radar (0–100% Risk Index)**:
   - **Algorithms**: Calibrated multi-factor Logistic Regression & Random Forest Risk Classifier.
   - **Inputs**: Yield drop percentage, Solids-Not-Fat (SNF) deficit below the 8.5% epithelial barrier threshold, fat instability, lactation stage, and historical treatments.
   - **Output**: Calibrated risk gauge (High Risk $\ge 70\%$, Moderate Risk $40-69\%$, Low Risk $<40\%$) with clinical diagnostic reasoning.
4. **Cull and Keep Herd Recommendation**:
   - **Algorithms**: scikit-learn `KMeans` unsupervised clustering ($k=3$) coupled with a composite Economic Margin Index ($Score = Revenue_{milk} - Cost_{feed} - Cost_{vet} - Penalty_{age}$).
   - **Tiers**: Ranks every cattle into **High Profit (Keep & Breed)**, **Average Profit (Maintain & Monitor)**, and **Low Profit (Cull Candidate)**.
5. **Precision Feed Optimization & Warehouse Stockout Countdown**:
   - **Algorithms**: `scipy.optimize.linprog` (Linear Programming) solving least-cost feed formulations subject to ICAR/NRC nutritional constraints (Dry Matter, Crude Protein CP, Total Digestible Nutrients TDN).
   - **Stockout Countdown**: Dynamic daily consumption burn rates ($kg/day$) against warehouse inventory, predicting exact depletion dates and recommended 30-day buffer reorders.
6. **Expense & Profit Financial Horizon (Next 30 Days)**:
   - **Algorithms**: Autoregressive linear trend projection with weekly seasonality weighting across Feed, Labor, Utilities, Veterinary, and Maintenance expenses.
   - **Output**: 30-day forward-looking financial trajectory chart, projected gross milk revenues (₹), projected operational costs (₹), and forecasted net profit margin (₹).

---

### 🏥 2. Veterinary Medical Treatments & Milk Withholding Safety (`routes/treatment.py`)
- **Clinical Treatment Logging**: Records diagnosis, clinical symptoms, administered drugs/antibiotics, attending veterinarian, and treatment costs.
- **Mandatory Milk Withdrawal Food Safety Enforcement**: Tracks required withdrawal days (e.g., 3–7 days for penicillin/oxytetracycline). Cattle in active withdrawal are flagged with prominent warning badges across the **Milk Register**, **Cattle Dossier**, and **Treatment Log** to prevent antibiotic residues in bulk milk tanks.
- **Lifecycle Tracking**: Cases transition cleanly from `Active Treatment` to `Observation` to `Completed / Cured`.

---

### 🥛 3. Milk Production & Session Batch Entry (`routes/milk.py`)
- Session-level milking records: Morning, Evening, and Afternoon.
- Milk quality parameters (Fat %, SNF %) with auto-rate and total revenue calculation (₹).
- **Session Batch Entry Grid (`/milk/quick-entry`)**: High-speed spreadsheet-style entry for recording the entire herd in under 2 minutes.

---

### 🏷️ 4. Digital QR Ear Tags & Live Camera Scanner (`routes/qr.py`)
- Automated generation of high-resolution QR tags embedded with cattle IDs (`static/qr_codes/`).
- Real-time webcam and smartphone camera QR scanner powered by `html5-qrcode` (`/scan-qr`) with asynchronous JSON lookup.
- 1-click printable QR tags for physical cattle ear attachment.

---

### 🌾 5. Feed Inventory & Ration Allocation (`routes/feed.py`)
- Warehouse inventory tracking across 5 feed categories: Green Fodder, Dry Fodder, Concentrates, Mineral Mixture, and Silage.
- Automated low-stock thresholds with restocking cost logs.
- Daily consumption logger that automatically deducts warehouse quantities.

---

### 💉 6. Vaccination & Preventive Immunization (`routes/vaccination.py`)
- Immunization scheduling for FMD, Brucellosis, Blackleg, Hemorrhagic Septicemia, Anthrax, and Deworming.
- Color-coded urgency alerts (`Overdue`, `Upcoming`, `Completed`).
- 1-click booster advance action.

---

### 🔐 7. 3-Tier Role-Based Access Control (RBAC) & Security (`routes/auth.py`)
- **Strict Admin-Only Account Provisioning**: Public registration is disabled to prevent unauthorized access. Only authenticated Farm Administrators can create, assign roles, activate/deactivate, or delete user accounts.
- **Role Tiering**:
  - 🔴 **Administrator (`admin`)**: Unrestricted operational, user management, and financial control.
  - 🔵 **Farm Manager (`manager`)**: Herd lifecycle, health records, feed restocking, expense logging, and analytics.
  - 🟢 **Farm Staff (`staff`)**: Barn-level daily milk logging, QR tag scanning, and feeding entries.

---

## 📊 Role & Permission Matrix

| Feature / Module | 🔴 Administrator (`admin`) | 🔵 Farm Manager (`manager`) | 🟢 Farm Staff (`staff`) |
| :--- | :---: | :---: | :---: |
| **User Logins & Provisioning** | ✅ Full Access | ❌ Restricted | ❌ Restricted |
| **AI Intelligence Hub (`/ai-insights`)** | ✅ Full Access | ✅ Full Access | 👁️ View Forecasts |
| **Cattle Records & QR Codes** | ✅ Full Access | ✅ Full Access | 👁️ View & Scan |
| **Milk Production & Batch Entry** | ✅ Full Access | ✅ Full Access | ✅ Daily Entry |
| **Veterinary Treatments & Withdrawal** | ✅ Full Access | ✅ Full Access | 👁️ View Only |
| **Feed Inventory & LP Ration** | ✅ Full Access | ✅ Full Access | ✅ Log Feeding |
| **Vaccinations & Booster Schedules** | ✅ Full Access | ✅ Full Access | ✅ Mark Done |
| **Staff Roster & Payroll** | ✅ Full Access | ✅ Manage Staff | ❌ Restricted |
| **Operational Expense Ledger** | ✅ Full Access | ✅ Log Expenses | ❌ Restricted |
| **Executive Reports & Financials** | ✅ Full Access | ✅ Full Access | 👁️ View Only |

---

## 🛠️ Technology Stack

### Backend & Machine Learning
- **Python 3.10+ / 3.14**
- **Flask 3.x** (Application Factory, Blueprints)
- **SQLAlchemy ORM** (Relational Data Mapping)
- **scikit-learn 1.4+** (Random Forest, Gradient Boosting, Isolation Forest, K-Means Clustering, Logistic Regression)
- **SciPy 1.12+** (`scipy.optimize.linprog` for Linear Programming Feed Formulation)
- **NumPy 1.26+** (Vectorized numerical computations, statistical z-scores)
- **Flask-Login** (Session Authentication & RBAC protection)
- **Flask-WTF & WTForms** (CSRF Protection & form validation)
- **qrcode & Pillow (PIL)** (High-resolution QR code rendering)
- **PyMySQL** (MySQL production connector)

### Frontend & User Experience
- **HTML5 & Vanilla CSS3** (Custom responsive design with modern glassmorphism, cards, and transitions)
- **Bootstrap 5.3.3**
- **Chart.js 4.4** (Dynamic multi-series canvas charting with confidence bands)
- **html5-qrcode** (Client-side HTML5 camera stream QR matrix reader)
- **FontAwesome 6.5** (Agricultural and system icons)

### Database Engines
- **SQLite (`dairy.db`)**: Zero-configuration default with auto-seed demo data on first boot.
- **MySQL (`database/dairy.sql`)**: Enterprise production schema with foreign key cascades and connection pooling.

---

## 📁 Project Structure

```text
DairyFarmQR-main/
│
├── app.py                      # App entry point & database initialization
├── config.py                   # Environment & Database Configuration
├── requirements.txt            # Python dependencies (Flask, scikit-learn, scipy, etc.)
├── run.bat                     # 1-Click Windows execution script
├── test_app.py                 # Automated unit and integration test suite (17 tests)
├── PROJECT_EXPLANATION.txt     # In-depth architectural, viva, and technical guide
├── README.md                   # Comprehensive system overview
│
├── database/
│   └── dairy.sql               # MySQL Schema DDL and sample seed data
│
├── services/
│   └── ai_engine.py            # DairyAIEngine: Forecasting, Anomalies, Mastitis, Cull/Keep, LP Feed
│
├── models/
│   ├── __init__.py             # SQLAlchemy instance
│   ├── user.py                 # User authentication & RBAC models
│   ├── animal.py               # Cattle lifecycle and health models
│   ├── milk.py                 # Milk production & session models
│   ├── treatment.py            # Veterinary medical treatments & milk withdrawal
│   ├── feed.py                 # Feed inventory & consumption models
│   ├── vaccination.py          # Vaccination & health timeline models
│   ├── employee.py             # Staff workforce models
│   └── expense.py              # Operational expense models
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Login, profile, admin user management & role control
│   ├── main.py                 # Overview dashboard & alert banners
│   ├── ai.py                   # AI Intelligence Hub & REST API endpoints
│   ├── treatment.py            # Veterinary treatment logs & withdrawal tracking
│   ├── animal.py               # Cattle CRUD & profile views
│   ├── milk.py                 # Milk production registers & batch entry
│   ├── feed.py                 # Inventory, LP rations, & consumption
│   ├── vaccination.py          # Immunization schedules & booster triggers
│   ├── employee.py             # Staff directory & payroll
│   ├── expense.py              # Expense tracking
│   ├── report.py               # Financial & production analytics + forecasts
│   └── qr.py                   # QR scanner & tag downloads
│
├── utils/
│   ├── __init__.py
│   └── qr_helper.py            # High-resolution QR code generator
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom UI stylesheets & glassmorphic tokens
│   ├── js/
│   │   └── script.js           # Client-side scripts & calculations
│   └── qr_codes/               # Generated QR code image files
│
└── templates/
    ├── layout.html             # Master layout with responsive sidebar & role navigation
    ├── login.html              # Sign-in portal
    ├── dashboard.html          # Main KPI dashboard, illness warnings, & stock alerts
    ├── ai_insights.html        # 6-Tab AI Intelligence command center
    ├── treatments.html         # Veterinary medical treatments & milk withholding
    ├── animals.html            # Cattle list & filter pills
    ├── add_animal.html         # Cattle registration form
    ├── edit_animal.html        # Cattle edit form
    ├── animal_detail.html      # Cattle dossier, individual AI forecast, & mastitis radar
    ├── milk_production.html    # Daily milk production register & anomaly flash alerts
    ├── quick_milk_entry.html   # Milking session batch entry grid
    ├── feed.html               # Feed inventory cards, stockout countdown, & LP ration card
    ├── vaccination.html        # Vaccination schedule & overdue badges
    ├── employees.html          # Staff roster & payroll
    ├── expenses.html           # Expense ledger
    ├── reports.html            # Reports with 14-day forecast line & financial projections
    └── scan_qr.html            # Live camera QR scanner
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14 installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Server
* **Option A**: Double-click `run.bat`
* **Option B**: Run from terminal:
  ```bash
  python app.py
  ```

Open your browser and visit: **`http://localhost:5000`**

---

## 🔑 Default Credentials

| Username | Password | Role | Description |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | **Administrator** | Full system, user creation, financial, and AI access |
| `manager` | `manager123` | **Farm Manager** | Cattle, feed, treatments, expenses, and analytics |
| `staff` | `staff123` | **Farm Staff** | Daily milk entry, feed logging, QR scanner |

---

## 📡 REST API Reference

| Endpoint | Method | Role | Description |
| :--- | :--- | :--- | :--- |
| `/api/ai/forecast?days=14&animal_id=2` | `GET` | Authenticated | 7–14 day milk forecast with 95% confidence intervals |
| `/api/ai/anomalies` | `GET` | Authenticated | Rolling z-score illness and yield crash alerts |
| `/api/ai/mastitis-risk` | `GET` | Authenticated | Multi-factor calibrated 0–100% mastitis risk ratings |
| `/api/ai/cull-keep` | `GET` | Authenticated | K-Means clustering and economic profitability tiers |
| `/api/ai/feed/ration?weight=480&yield=14` | `GET` | Authenticated | Linear programming least-cost ration formulation |
| `/api/ai/financial-forecast` | `GET` | Authenticated | 30-day forward expense, revenue, and net profit |
| `/api/qr/lookup/<tag_number>` | `GET` | Authenticated | JSON cattle lookup for live camera QR scanner |
| `/api/animals/search?q=<query>` | `GET` | Authenticated | Autocomplete cattle search |

---

## 🧪 Automated Testing & Verification

The project includes an automated test suite verifying all routes, RBAC security, QR code rendering, veterinary treatments, and all 6 AI modules:

```bash
python -m unittest test_app.py
```

**Test Results**:
```text
Ran 17 tests in 4.609s
OK
[PASSED] Feature 1: AI Milk Yield Forecasting (7 to 14 days, herd & individual) verified.
[PASSED] Feature 2: AI Anomaly Detection (Early Illness Warning) with exact alert text verified.
[PASSED] Feature 3: AI Mastitis Risk Prediction verified (Top Risk: DF-101 at 93.1%).
[PASSED] Feature 4: Cull and Keep K-Means Clustering & Economic Ranking verified.
[PASSED] Feature 5: Feed LP Optimization & Stock Depletion verified.
[PASSED] Feature 6: Next Month Financial Forecasting verified.
[PASSED] Medical Treatment log & milk withdrawal workflow verified.
[PASSED] AI Web Hub (/ai-insights), Reports Forecast Line, and all 6 REST API endpoints verified.
```

---

## 📄 License
This project is licensed under the MIT License - open for educational and non-commercial project use.
