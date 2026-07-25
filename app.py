# ============================================================
# GSE OEE MAINTENANCE MANAGEMENT SYSTEM
# Air Tanzania Company Limited (ATCL)
# Developer: Aura Deonatus Nyamwelo
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import joblib
import json
import sqlite3
import os
from datetime import datetime, date, timedelta
from fpdf import FPDF
import io
import hashlib

# ─────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GSE OEE Management System - Air Tanzania",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f0f4f8; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #003580 0%, #001f4d 100%);
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    [data-testid="stSidebar"] .stRadio label { color: #ffffff !important; }

    .main-header {
        background: linear-gradient(90deg, #003580 0%, #0055b3 60%, #c9972c 100%);
        padding: 18px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .main-header h1 { color:white; font-size:26px; font-weight:700; margin:0; }
    .main-header p  { color:#d4e4ff; font-size:13px; margin:4px 0 0 0; }

    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-top: 4px solid #003580;
    }
    .metric-card h3 { color:#003580; font-size:28px; margin:0; font-weight:700; }
    .metric-card p  { color:#666; font-size:13px; margin:6px 0 0 0; }

    .gold-card {
        background: linear-gradient(135deg, #c9972c, #e8b84b);
        border-radius: 12px;
        padding: 18px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(201,151,44,0.3);
    }
    .gold-card h3 { font-size:26px; margin:0; font-weight:700; }
    .gold-card p  { font-size:13px; margin:4px 0 0 0; opacity:0.9; }

    .red-card {
        background: linear-gradient(135deg, #c0392b, #e74c3c);
        border-radius: 12px;
        padding: 18px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(192,57,43,0.3);
    }
    .red-card h3 { font-size:26px; margin:0; font-weight:700; }
    .red-card p  { font-size:13px; margin:4px 0 0 0; opacity:0.9; }

    .section-header {
        background: #003580;
        color: white;
        padding: 10px 18px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        margin: 16px 0 12px 0;
    }

    .badge-verypoor { background:#7b0000; color:white; padding:5px 14px; border-radius:20px; font-size:13px; font-weight:600; }
    .badge-poor     { background:#c0392b; color:white; padding:5px 14px; border-radius:20px; font-size:13px; font-weight:600; }
    .badge-moderate { background:#e67e22; color:white; padding:5px 14px; border-radius:20px; font-size:13px; font-weight:600; }
    .badge-good     { background:#2980b9; color:white; padding:5px 14px; border-radius:20px; font-size:13px; font-weight:600; }
    .badge-verygood { background:#1a7a1a; color:white; padding:5px 14px; border-radius:20px; font-size:13px; font-weight:600; }

    .badge-critical { background:#7b0000; color:white; padding:3px 10px; border-radius:14px; font-size:11px; font-weight:600; }
    .badge-high     { background:#c0392b; color:white; padding:3px 10px; border-radius:14px; font-size:11px; font-weight:600; }
    .badge-medium   { background:#e67e22; color:white; padding:3px 10px; border-radius:14px; font-size:11px; font-weight:600; }
    .badge-low      { background:#2980b9; color:white; padding:3px 10px; border-radius:14px; font-size:11px; font-weight:600; }

    .badge-open        { background:#c0392b; color:white; padding:3px 10px; border-radius:14px; font-size:11px; font-weight:600; }
    .badge-inprogress  { background:#e67e22; color:white; padding:3px 10px; border-radius:14px; font-size:11px; font-weight:600; }
    .badge-completed   { background:#1a7a1a; color:white; padding:3px 10px; border-radius:14px; font-size:11px; font-weight:600; }
    .badge-onhold      { background:#7f8c8d; color:white; padding:3px 10px; border-radius:14px; font-size:11px; font-weight:600; }

    .stButton > button {
        background: linear-gradient(90deg, #003580, #0055b3);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #c9972c, #e8b84b);
        transform: translateY(-1px);
    }

    .info-box {
        background: #e8f0fe;
        border-left: 4px solid #003580;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
        font-size: 14px;
        color: #1a1a2e;
    }

    .alert-box {
        background: #fdecea;
        border-left: 4px solid #c0392b;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
        font-size: 14px;
        color: #1a1a2e;
    }

    .warn-box {
        background: #fff6e5;
        border-left: 4px solid #e67e22;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
        font-size: 14px;
        color: #1a1a2e;
    }

    .ok-box {
        background: #eaf7ea;
        border-left: 4px solid #1a7a1a;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
        font-size: 14px;
        color: #1a1a2e;
    }

    .user-info-bar {
        background: white;
        border-radius: 8px;
        padding: 8px 16px;
        margin-bottom: 16px;
        border-left: 4px solid #c9972c;
        font-size: 13px;
        color: #333;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    }

    .oee-band-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        margin-top: 10px;
    }
    .oee-band-table th {
        background: #003580;
        color: white;
        padding: 8px 12px;
        text-align: left;
    }
    .oee-band-table td {
        padding: 7px 12px;
        border-bottom: 1px solid #e0e0e0;
    }
    .oee-band-table tr:nth-child(even) td { background: #f5f8ff; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# OEE CALIBRATION  (unchanged from original system)
# ─────────────────────────────────────────────
OEE_BANDS = {
    1: (0,  20,  "Very Poor"),
    2: (20, 40,  "Poor"),
    3: (40, 60,  "Moderate"),
    4: (60, 80,  "Good"),
    5: (80, 100, "Very Good"),
}

def calibrate_oee(raw_scores_dict, raw_oee):
    mean_score = np.mean(list(raw_scores_dict.values()))

    if   mean_score < 1.5: band_min, band_max = 0,  20
    elif mean_score < 2.5: band_min, band_max = 20, 40
    elif mean_score < 3.5: band_min, band_max = 40, 60
    elif mean_score < 4.5: band_min, band_max = 60, 80
    else:                  band_min, band_max = 80, 100

    raw_clipped    = max(0.0, min(100.0, raw_oee))
    relative_pos   = raw_clipped / 100.0
    calibrated_oee = band_min + relative_pos * (band_max - band_min)

    score_variation = (mean_score - int(mean_score)) * (band_max - band_min) * 0.3
    calibrated_oee  = calibrated_oee + score_variation
    calibrated_oee  = max(band_min, min(band_max - 0.01, calibrated_oee))

    return round(calibrated_oee, 2), band_min, band_max

def get_oee_status(oee):
    if   oee < 20: return "Very Poor"
    elif oee < 40: return "Poor"
    elif oee < 60: return "Moderate"
    elif oee < 80: return "Good"
    else:          return "Very Good"

def get_implementation_label(oee):
    if   oee < 20: return "Implementation Very Poor"
    elif oee < 40: return "Implementation Poor"
    elif oee < 60: return "Implementation Moderate"
    elif oee < 80: return "Implementation Good"
    else:          return "Implementation Very Good"

# ─────────────────────────────────────────────
# USER ACCOUNTS
# ─────────────────────────────────────────────
def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

USERS = {
    "admin": {
        "password": hash_pw("Admin@2024"),
        "name":     "System Administrator",
        "role":     "admin",
        "position": "System Administrator",
    },
    "manager1": {
        "password": hash_pw("Manager@2024"),
        "name":     "Maintenance Manager",
        "role":     "manager",
        "position": "Maintenance Manager - ATCL",
    },
    "engineer1": {
        "password": hash_pw("Engineer@2024"),
        "name":     "Maintenance Engineer",
        "role":     "manager",
        "position": "Maintenance Engineer - ATCL",
    },
    "tech1": {
        "password": hash_pw("Tech@2024"),
        "name":     "GSE Technician",
        "role":     "technician",
        "position": "GSE Technician - ATCL",
    },
    "tech2": {
        "password": hash_pw("Tech2@2024"),
        "name":     "Ground Handling Staff",
        "role":     "technician",
        "position": "Ground Handling Staff - ATCL",
    },
}

# Pages available per role (Trend Analysis & Admin Dashboard removed)
ROLE_PAGES = {
    "admin": [
        "Home",
        "OEE Prediction",
        "Objective OEE Calculator",
        "Asset Registry",
        "Spare Parts Inventory",
        "Work Orders",
        "Failure Log (RCA/FMEA)",
        "PM Scheduler",
        "Bulk CSV Upload",
        "Alerts & Notifications",
    ],
    "manager": [
        "Home",
        "OEE Prediction",
        "Objective OEE Calculator",
        "Asset Registry",
        "Spare Parts Inventory",
        "Work Orders",
        "Failure Log (RCA/FMEA)",
        "PM Scheduler",
        "Bulk CSV Upload",
        "Alerts & Notifications",
    ],
    "technician": [
        "Home",
        "OEE Prediction",
        "Objective OEE Calculator",
        "Work Orders",
        "Failure Log (RCA/FMEA)",
        "PM Scheduler",
        "Alerts & Notifications",
    ],
}

def login(username, password):
    username = username.strip().lower()
    if username in USERS:
        if USERS[username]["password"] == hash_pw(password):
            return True, USERS[username]
    return False, None

def logout():
    for key in ['authenticated', 'user', 'username']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def init_session():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'user'          not in st.session_state:
        st.session_state['user']          = None
    if 'username'      not in st.session_state:
        st.session_state['username']      = None

# ─────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────
def show_login_page():

    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:

        if os.path.exists('atcl_logo.png'):
            st.image('atcl_logo.png', use_container_width=True)
        else:
            st.markdown("""
            <div style='text-align:center; padding:10px 0;'>
                <h2 style='color:#003580; font-weight:800;'>Air Tanzania</h2>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style='background:white; border-radius:16px;
                    box-shadow:0 8px 32px rgba(0,53,128,0.15);
                    overflow:hidden; margin-top:10px;'>
            <div style='background:linear-gradient(90deg,#003580 0%,#0055b3 70%,#c9972c 100%);
                        padding:24px 30px; text-align:center;'>
                <h2 style='color:white; font-size:20px; font-weight:700; margin:0;'>
                    GSE OEE Management System
                </h2>
                <p style='color:#d4e4ff; font-size:12px; margin:6px 0 0 0;'>
                    Air Tanzania Company Limited (ATCL)<br>
                    Authorized Personnel Only
                </p>
            </div>
            <div style='height:4px;
                        background:linear-gradient(90deg,#c9972c,#e8b84b);'>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<h4 style='color:#003580; margin:0 0 12px 0;'>Sign In</h4>",
            unsafe_allow_html=True
        )

        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        login_btn = st.button("Login", use_container_width=True)

        if login_btn:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                success, user_data = login(username, password)
                if success:
                    st.session_state['authenticated'] = True
                    st.session_state['user']          = user_data
                    st.session_state['username']      = username.strip().lower()
                    st.success(
                        "Welcome, " + user_data['name'] + "! Redirecting..."
                    )
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        st.markdown("---")
        st.markdown("""
        <div style='font-size:12px; color:#888; line-height:2.2;'>
            <b>Demo Credentials:</b><br>
            Admin      : admin / Admin@2024<br>
            Manager    : manager1 / Manager@2024<br>
            Technician : tech1 / Tech@2024
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style='font-size:11px; color:#aaa; margin-top:14px; text-align:center;'>
            M.Eng. Dissertation - Aura Deonatus Nyamwelo<br>
            Dar es Salaam Institute of Technology (DIT) 2024
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
FEATURE_LABELS = {
    'Unplanned_Breakdowns':            'Unplanned Breakdowns',
    'Preventive_Maintenance_Schedule': 'Preventive Maintenance Schedule',
    'Spare_Parts_Availability':        'Spare Parts Availability',
    'Maintenance_Errors_and_Rework':   'Maintenance Errors and Rework',
    'CMMS':                            'CMMS Availability',
    'Maintenance_Budget':              'Maintenance Budget',
    'Technician_Competency':           'Technician Competency',
    'Maintenance_History_Records':     'Maintenance History Records',
}

GSE_TYPES = [
    "Ground Power Unit (GPU)",
    "Pushback Tractor",
    "Belt Loader",
    "Air Start Unit (ASU)",
    "Passenger Stairs",
    "Catering Truck",
    "Baggage Tractor",
    "Refueling Truck",
    "Service Vehicle",
]

ASSET_STATUSES   = ["Active", "Under Maintenance", "Standby", "Retired"]
WO_TASK_TYPES    = ["Preventive", "Corrective", "Predictive", "Inspection"]
WO_PRIORITIES    = ["Low", "Medium", "High", "Critical"]
WO_STATUSES      = ["Open", "In Progress", "Completed", "On Hold"]
PM_FREQUENCIES   = ["Daily", "Weekly", "Monthly", "Quarterly", "Annually"]
SEVERITY_LEVELS  = ["Low", "Medium", "High", "Critical"]

LANGUAGES = {
    "English": {
        "predict_btn":    "Predict OEE",
        "download_btn":   "Download PDF Report",
        "oee_label":      "Predicted OEE",
        "status_label":   "Implementation Status",
        "rec_label":      "Recommendation",
        "select_gse":     "Select GSE Equipment Type",
        "current_scores": "Current Maintenance Scores",
    },
    "Kiswahili": {
        "predict_btn":    "Tabiri OEE",
        "download_btn":   "Pakua Ripoti ya PDF",
        "oee_label":      "OEE Inayotabiriwa",
        "status_label":   "Hali ya Utekelezaji",
        "rec_label":      "Mapendekezo",
        "select_gse":     "Chagua Aina ya GSE",
        "current_scores": "Alama za Sasa za Matengenezo",
    }
}

RECOMMENDATIONS = {
    "Very Poor": "Implementation Very Poor. Immediate and comprehensive overhaul of all maintenance systems is required. All 8 factors are critically underperforming.",
    "Poor":      "Implementation Poor. Major improvement needed. Prioritize CMMS deployment, spare parts supply chain, and technician training urgently.",
    "Moderate":  "Implementation Moderate. Strengthen Preventive Maintenance scheduling and Maintenance History documentation to move into the Good band.",
    "Good":      "Implementation Good. Fine-tune Unplanned Breakdown response and CMMS utilization to reach Very Good world-class performance.",
    "Very Good": "Implementation Very Good. World-class OEE achieved. Maintain current practices and continue monitoring all 8 maintenance factors.",
}

RECOMMENDATIONS_SW = {
    "Very Poor": "Utekelezaji Mbaya Sana. Marekebisho ya haraka na ya kina ya mifumo yote ya matengenezo inahitajika.",
    "Poor":      "Utekelezaji Mbaya. Uboreshaji mkubwa unahitajika. Toa kipaumbele kwa CMMS, vipuri, na mafunzo ya mafundi.",
    "Moderate":  "Utekelezaji wa Wastani. Imarisha Ratiba ya Matengenezo ya Kuzuia na uhifadhi wa historia ya matengenezo.",
    "Good":      "Utekelezaji Mzuri. Boresha mwitikio wa hitilafu na matumizi ya CMMS kufikia utendaji wa kiwango cha dunia.",
    "Very Good": "Utekelezaji Mzuri Sana. OEE ya kiwango cha dunia imepatikana. Endelea na mazoea ya sasa.",
}

# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
DB_FILE = 'oee_predictions.db'

def get_conn():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # OEE (regression/RF model) prediction records
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            username TEXT,
            role TEXT,
            gse_type TEXT,
            asset_code TEXT,
            unplanned_breakdowns INTEGER,
            preventive_maintenance INTEGER,
            spare_parts INTEGER,
            maintenance_errors INTEGER,
            cmms INTEGER,
            maintenance_budget INTEGER,
            technician_competency INTEGER,
            history_records INTEGER,
            mean_score REAL,
            predicted_oee REAL,
            oee_band_min REAL,
            oee_band_max REAL,
            status TEXT,
            implementation_label TEXT,
            language TEXT
        )
    ''')

    # 1. Asset / Equipment Registry
    c.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_code TEXT UNIQUE,
            gse_type TEXT,
            model_serial TEXT,
            location TEXT,
            commission_date TEXT,
            status TEXT,
            created_by TEXT,
            last_updated TEXT
        )
    ''')

    # 2. Spare Parts Inventory
    c.execute('''
        CREATE TABLE IF NOT EXISTS spare_parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_code TEXT UNIQUE,
            part_name TEXT,
            category TEXT,
            quantity_in_stock INTEGER,
            minimum_stock_level INTEGER,
            reorder_point INTEGER,
            unit_cost REAL,
            supplier TEXT,
            lead_time_days INTEGER,
            last_restocked TEXT
        )
    ''')

    # 3. Work Orders
    c.execute('''
        CREATE TABLE IF NOT EXISTS work_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wo_number TEXT,
            asset_code TEXT,
            title TEXT,
            description TEXT,
            task_type TEXT,
            priority TEXT,
            assigned_to TEXT,
            status TEXT,
            created_date TEXT,
            due_date TEXT,
            completed_date TEXT
        )
    ''')

    # 4. Failure Logs / RCA-FMEA
    c.execute('''
        CREATE TABLE IF NOT EXISTS failure_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_code TEXT,
            failure_date TEXT,
            failure_mode TEXT,
            root_cause TEXT,
            failure_effect TEXT,
            severity TEXT,
            downtime_hours REAL,
            corrective_action TEXT,
            reported_by TEXT
        )
    ''')

    # 5. Preventive Maintenance Scheduler
    c.execute('''
        CREATE TABLE IF NOT EXISTS pm_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_code TEXT,
            task_name TEXT,
            frequency TEXT,
            last_done_date TEXT,
            next_due_date TEXT,
            status TEXT,
            times_completed INTEGER,
            times_overdue INTEGER
        )
    ''')

    # 6. Objective OEE (Availability x Performance x Quality)
    c.execute('''
        CREATE TABLE IF NOT EXISTS objective_oee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            asset_code TEXT,
            operating_time REAL,
            planned_time REAL,
            ideal_rate REAL,
            actual_output REAL,
            total_ops REAL,
            good_ops REAL,
            availability REAL,
            performance REAL,
            quality REAL,
            oee REAL,
            username TEXT
        )
    ''')

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
# DATABASE MIGRATION (safe, non-destructive)
# Ensures old databases created with the previous
# version of the app get any new columns added,
# without deleting existing records.
# ─────────────────────────────────────────────
def migrate_db():
    conn = get_conn()
    c = conn.cursor()

    def add_column_if_missing(table, column, col_type):
        c.execute(f"PRAGMA table_info({table})")
        existing_cols = [row[1] for row in c.fetchall()]
        if column not in existing_cols:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")

    # predictions table may be missing asset_code from older app versions
    add_column_if_missing("predictions", "asset_code", "TEXT")

    conn.commit()
    conn.close()

# ---- Predictions ----
def save_prediction(username, role, gse_type, asset_code, scores,
                    mean_score, oee, band_min, band_max,
                    status, impl_label, lang):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        INSERT INTO predictions (
            timestamp, username, role, gse_type, asset_code,
            unplanned_breakdowns, preventive_maintenance,
            spare_parts, maintenance_errors, cmms,
            maintenance_budget, technician_competency,
            history_records, mean_score, predicted_oee,
            oee_band_min, oee_band_max, status,
            implementation_label, language
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        username, role, gse_type, asset_code,
        scores['Unplanned_Breakdowns'],
        scores['Preventive_Maintenance_Schedule'],
        scores['Spare_Parts_Availability'],
        scores['Maintenance_Errors_and_Rework'],
        scores['CMMS'],
        scores['Maintenance_Budget'],
        scores['Technician_Competency'],
        scores['Maintenance_History_Records'],
        round(mean_score, 2),
        round(oee, 2),
        band_min, band_max,
        status, impl_label, lang
    ))
    conn.commit()
    conn.close()

def load_predictions():
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM predictions ORDER BY timestamp DESC", conn
    )
    conn.close()
    return df

# ---- Assets ----
def add_asset(asset_code, gse_type, model_serial, location,
             commission_date, status, created_by):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        INSERT INTO assets (asset_code, gse_type, model_serial, location,
                            commission_date, status, created_by, last_updated)
        VALUES (?,?,?,?,?,?,?,?)
    ''', (asset_code, gse_type, model_serial, location,
          str(commission_date), status, created_by,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_assets():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM assets ORDER BY id DESC", conn)
    conn.close()
    return df

def update_asset_status(asset_code, new_status):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''UPDATE assets SET status=?, last_updated=? WHERE asset_code=?''',
              (new_status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), asset_code))
    conn.commit()
    conn.close()

def delete_asset(asset_code):
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM assets WHERE asset_code=?', (asset_code,))
    conn.commit()
    conn.close()

# ---- Spare Parts ----
def add_spare_part(part_code, part_name, category, qty, min_stock,
                   reorder_point, unit_cost, supplier, lead_time):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        INSERT INTO spare_parts (part_code, part_name, category,
                                 quantity_in_stock, minimum_stock_level,
                                 reorder_point, unit_cost, supplier,
                                 lead_time_days, last_restocked)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    ''', (part_code, part_name, category, qty, min_stock, reorder_point,
          unit_cost, supplier, lead_time,
          datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def get_spare_parts():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM spare_parts ORDER BY id DESC", conn)
    conn.close()
    return df

def update_spare_part_stock(part_code, new_qty):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''UPDATE spare_parts SET quantity_in_stock=?, last_restocked=?
                WHERE part_code=?''',
              (new_qty, datetime.now().strftime("%Y-%m-%d"), part_code))
    conn.commit()
    conn.close()

def delete_spare_part(part_code):
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM spare_parts WHERE part_code=?', (part_code,))
    conn.commit()
    conn.close()

# ---- Work Orders ----
def add_work_order(asset_code, title, description, task_type, priority,
                   assigned_to, due_date):
    conn = get_conn()
    c = conn.cursor()
    wo_number = "WO-" + datetime.now().strftime("%Y%m%d%H%M%S")
    c.execute('''
        INSERT INTO work_orders (wo_number, asset_code, title, description,
                                 task_type, priority, assigned_to, status,
                                 created_date, due_date, completed_date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    ''', (wo_number, asset_code, title, description, task_type, priority,
          assigned_to, "Open", datetime.now().strftime("%Y-%m-%d"),
          str(due_date), None))
    conn.commit()
    conn.close()
    return wo_number

def get_work_orders():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM work_orders ORDER BY id DESC", conn)
    conn.close()
    return df

def update_work_order_status(wo_number, new_status):
    conn = get_conn()
    c = conn.cursor()
    completed_date = (datetime.now().strftime("%Y-%m-%d")
                      if new_status == "Completed" else None)
    c.execute('''UPDATE work_orders SET status=?, completed_date=?
                WHERE wo_number=?''', (new_status, completed_date, wo_number))
    conn.commit()
    conn.close()

# ---- Failure Logs (RCA / FMEA) ----
def add_failure_log(asset_code, failure_date, failure_mode, root_cause,
                    failure_effect, severity, downtime_hours,
                    corrective_action, reported_by):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        INSERT INTO failure_logs (asset_code, failure_date, failure_mode,
                                  root_cause, failure_effect, severity,
                                  downtime_hours, corrective_action, reported_by)
        VALUES (?,?,?,?,?,?,?,?,?)
    ''', (asset_code, str(failure_date), failure_mode, root_cause,
          failure_effect, severity, downtime_hours, corrective_action,
          reported_by))
    conn.commit()
    conn.close()

def get_failure_logs():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM failure_logs ORDER BY id DESC", conn)
    conn.close()
    return df

# ---- PM Scheduler ----
def compute_next_due(frequency, from_date):
    days_map = {
        "Daily": 1, "Weekly": 7, "Monthly": 30,
        "Quarterly": 90, "Annually": 365
    }
    return from_date + timedelta(days=days_map.get(frequency, 30))

def add_pm_task(asset_code, task_name, frequency, last_done_date):
    conn = get_conn()
    c = conn.cursor()
    next_due = compute_next_due(frequency, last_done_date)
    c.execute('''
        INSERT INTO pm_schedule (asset_code, task_name, frequency,
                                 last_done_date, next_due_date, status,
                                 times_completed, times_overdue)
        VALUES (?,?,?,?,?,?,?,?)
    ''', (asset_code, task_name, frequency, str(last_done_date),
          str(next_due), "Scheduled", 0, 0))
    conn.commit()
    conn.close()

def get_pm_tasks():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM pm_schedule ORDER BY id DESC", conn)
    conn.close()
    return df

def mark_pm_completed(pm_id, frequency):
    today = date.today()
    next_due = compute_next_due(frequency, today)
    conn = get_conn()
    c = conn.cursor()
    c.execute('''UPDATE pm_schedule
                SET last_done_date=?, next_due_date=?, status=?,
                    times_completed = times_completed + 1
                WHERE id=?''',
              (str(today), str(next_due), "Scheduled", pm_id))
    conn.commit()
    conn.close()

def pm_compliance_rate():
    df = get_pm_tasks()
    if df.empty:
        return 0.0
    today = date.today()
    df['next_due_date'] = pd.to_datetime(df['next_due_date']).dt.date
    overdue = df[df['next_due_date'] < today]
    on_time = len(df) - len(overdue)
    return round((on_time / len(df)) * 100, 1)

# ---- Objective OEE (A x P x Q) ----
def add_objective_oee(asset_code, operating_time, planned_time, ideal_rate,
                      actual_output, total_ops, good_ops,
                      availability, performance, quality, oee, username):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        INSERT INTO objective_oee (timestamp, asset_code, operating_time,
                                   planned_time, ideal_rate, actual_output,
                                   total_ops, good_ops, availability,
                                   performance, quality, oee, username)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), asset_code,
          operating_time, planned_time, ideal_rate, actual_output,
          total_ops, good_ops, availability, performance, quality, oee,
          username))
    conn.commit()
    conn.close()

def get_objective_oee():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM objective_oee ORDER BY id DESC", conn)
    conn.close()
    return df

# ─────────────────────────────────────────────
# LOAD MODEL  (same original model files, unchanged)
# ─────────────────────────────────────────────
@st.cache_resource
def load_model():
    model    = joblib.load('gse_oee_model/rf_model.pkl')
    features = joblib.load('gse_oee_model/feature_columns.pkl')
    with open('gse_oee_model/model_metadata.json') as f:
        meta = json.load(f)
    fi_df = pd.read_csv('gse_oee_model/feature_importance.csv')
    return model, features, meta, fi_df

# ─────────────────────────────────────────────
# PREDICTION WITH CALIBRATION (unchanged logic)
# ─────────────────────────────────────────────
def predict_oee_calibrated(model, features, scores_dict):
    inp        = pd.DataFrame([scores_dict])[features]
    tree_preds = np.array([t.predict(inp)[0] for t in model.estimators_])
    raw_oee    = float(np.mean(tree_preds))

    cal_oee, band_min, band_max = calibrate_oee(scores_dict, raw_oee)

    raw_lower = float(np.percentile(tree_preds, 5))
    raw_upper = float(np.percentile(tree_preds, 95))

    cal_lower, _, _ = calibrate_oee(scores_dict, raw_lower)
    cal_upper, _, _ = calibrate_oee(scores_dict, raw_upper)

    cal_lower  = max(band_min,        min(cal_lower, cal_oee))
    cal_upper  = min(band_max - 0.01, max(cal_upper, cal_oee))
    mean_score = np.mean(list(scores_dict.values()))

    return (
        round(cal_oee,   2),
        round(cal_lower, 2),
        round(cal_upper, 2),
        band_min,
        band_max,
        round(mean_score, 2)
    )

# ─────────────────────────────────────────────
# GAUGE CHART
# ─────────────────────────────────────────────
def gauge_chart(oee, lower, upper, title="Predicted OEE"):
    status = get_oee_status(oee)
    color_map = {
        "Very Poor": "#7b0000",
        "Poor":      "#c0392b",
        "Moderate":  "#e67e22",
        "Good":      "#2980b9",
        "Very Good": "#1a7a1a",
    }
    needle_color = color_map.get(status, "#003580")

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=oee,
        delta={
            'reference': 80,
            'increasing': {'color': '#1a7a1a'},
            'decreasing': {'color': '#c0392b'}
        },
        title={
            'text': (
                "<b>" + title + "</b><br>"
                "<span style='font-size:12px;color:#555;'>"
                "90% CI: " + str(lower) + "% - " + str(upper) + "%</span><br>"
                "<span style='font-size:13px;color:" + needle_color +
                ";font-weight:600;'>" + get_implementation_label(oee) +
                "</span>"
            ),
            'font': {'size': 15}
        },
        number={
            'suffix': "%",
            'font': {'size': 42, 'color': needle_color}
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickvals': [0, 20, 40, 60, 80, 100],
                'ticktext': ['0', '20', '40', '60', '80', '100'],
                'tickwidth': 1,
                'tickcolor': "#333",
                'tickfont': {'size': 11}
            },
            'bar': {'color': needle_color, 'thickness': 0.28},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e0e0e0",
            'steps': [
                {'range': [0,  20], 'color': '#ffcccc'},
                {'range': [20, 40], 'color': '#fde8e8'},
                {'range': [40, 60], 'color': '#fff3e0'},
                {'range': [60, 80], 'color': '#e8f0fe'},
                {'range': [80,100], 'color': '#c8e6c9'},
            ],
            'threshold': {
                'line': {'color': "#003580", 'width': 3},
                'thickness': 0.8,
                'value': 80
            }
        }
    ))
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=80, b=10),
        paper_bgcolor='white',
        font={'family': 'Arial'}
    )
    return fig

# ─────────────────────────────────────────────
# PRIORITY TABLE
# ─────────────────────────────────────────────
def priority_table(fi_df, scores_dict):
    rows = []
    for _, row in fi_df.iterrows():
        col   = row['Variable']
        label = FEATURE_LABELS.get(col, col)
        score = scores_dict.get(col, 3)
        imp   = row['Importance (%)']
        gap   = 5 - score
        rows.append({
            'Factor':         label,
            'Your Score':     score,
            'Max Score':      5,
            'Gap':            gap,
            'Importance (%)': round(imp, 2),
            'Priority Score': round(imp * gap, 2)
        })
    df_p = pd.DataFrame(rows).sort_values(
        'Priority Score', ascending=False
    ).reset_index(drop=True)
    df_p.index += 1
    return df_p

# ─────────────────────────────────────────────
# PDF GENERATION (OEE Prediction Report)
# ─────────────────────────────────────────────
def generate_pdf(username, role, gse_type, scores,
                 oee, lower, upper, band_min, band_max,
                 mean_score, status, impl_label, rec, fi_df):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_fill_color(0, 53, 128)
    pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, 8)
    pdf.cell(190, 10, 'AIR TANZANIA COMPANY LIMITED (ATCL)', align='C')
    pdf.set_font('Helvetica', '', 11)
    pdf.set_xy(10, 20)
    pdf.cell(190, 8, 'GSE OEE Maintenance Management Report', align='C')

    pdf.set_fill_color(201, 151, 44)
    pdf.rect(0, 35, 210, 3, 'F')

    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_xy(10, 42)
    pdf.cell(90, 6,
             'Generated: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    pdf.set_xy(110, 42)
    pdf.cell(90, 6, 'Equipment: ' + gse_type)
    pdf.set_xy(10, 48)
    pdf.cell(90, 6, 'User: ' + username + ' (' + role.title() + ')')
    pdf.set_xy(110, 48)
    pdf.cell(90, 6, 'Prepared by: Aura Deonatus Nyamwelo')
    pdf.line(10, 56, 200, 56)

    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_fill_color(0, 53, 128)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, 60)
    pdf.cell(190, 8, ' OEE PREDICTION RESULT', fill=True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_xy(10, 72)
    pdf.cell(70, 12, 'OEE: ' + str(round(oee, 2)) + '%')

    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_xy(85, 72)
    pdf.cell(115, 8, 'Status: ' + impl_label)

    pdf.set_font('Helvetica', '', 11)
    pdf.set_xy(85, 80)
    pdf.cell(115, 6,
             'OEE Band: ' + str(band_min) + '% - ' + str(band_max) + '%')

    pdf.set_xy(10, 84)
    pdf.cell(75, 6,
             'Mean Score: ' + str(round(mean_score, 2)) + ' / 5.00')

    pdf.set_xy(85, 86)
    pdf.cell(115, 6,
             '90% CI: ' + str(round(lower, 1)) + '% - ' +
             str(round(upper, 1)) + '%')

    pdf.set_xy(10, 90)
    gap_to_wc = round(max(0, 80.0 - oee), 2)
    pdf.cell(180, 6,
             'Gap to World-class (80%+): ' + str(gap_to_wc) + '%')

    pdf.set_fill_color(232, 240, 254)
    pdf.set_xy(10, 98)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(190, 6, ' OEE Calibration Scale Reference', fill=True)

    pdf.set_font('Helvetica', '', 9)
    scale_data = [
        ('All scores = 1', '0% - 20%',   'Very Poor'),
        ('All scores = 2', '20% - 40%',  'Poor'),
        ('All scores = 3', '40% - 60%',  'Moderate'),
        ('All scores = 4', '60% - 80%',  'Good'),
        ('All scores = 5', '80% - 100%', 'Very Good'),
    ]
    y_s = 105
    for score_label, band, status_l in scale_data:
        pdf.set_xy(15, y_s)
        pdf.cell(60, 5, score_label)
        pdf.cell(45, 5, '->  ' + band)
        pdf.cell(50, 5, '(' + status_l + ')')
        y_s += 5

    rec_clean = rec
    for emoji in ['🔴', '🟠', '🟡', '🔵', '✅']:
        rec_clean = rec_clean.replace(emoji, '').strip()

    pdf.set_fill_color(232, 240, 254)
    pdf.set_xy(10, y_s + 3)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(190, 7, ' Recommendation', fill=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_xy(10, y_s + 11)
    pdf.multi_cell(190, 6, rec_clean)

    y = y_s + 32
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_fill_color(0, 53, 128)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, y)
    pdf.cell(190, 7, ' INPUT MAINTENANCE FACTOR SCORES', fill=True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(220, 230, 245)
    pdf.set_xy(10, y + 8)
    pdf.cell(120, 6, 'Maintenance Factor', fill=True, border=1)
    pdf.cell(35,  6, 'Score (1-5)',        fill=True, border=1, align='C')
    pdf.cell(35,  6, 'OEE Band',           fill=True, border=1, align='C')

    pdf.set_font('Helvetica', '', 10)
    y += 14
    for col, label in FEATURE_LABELS.items():
        sc      = scores[col]
        b_label = OEE_BANDS[sc][2]
        pdf.set_xy(10, y)
        pdf.set_fill_color(245, 248, 255)
        pdf.cell(120, 6, label,    fill=True, border=1)
        pdf.cell(35,  6, str(sc),  fill=True, border=1, align='C')
        pdf.cell(35,  6, b_label,  fill=True, border=1, align='C')
        y += 6

    y += 5
    if y > 240:
        pdf.add_page()
        y = 20

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_fill_color(0, 53, 128)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, y)
    pdf.cell(190, 7, ' TOP MAINTENANCE PRIORITIES', fill=True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(220, 230, 245)
    y += 8
    pdf.set_xy(10, y)
    pdf.cell(10,  6, '#',              fill=True, border=1, align='C')
    pdf.cell(110, 6, 'Factor',         fill=True, border=1)
    pdf.cell(35,  6, 'Importance (%)', fill=True, border=1, align='C')
    pdf.cell(35,  6, 'Score Gap',      fill=True, border=1, align='C')

    p_df = priority_table(fi_df, scores)
    pdf.set_font('Helvetica', '', 10)
    for i, row in p_df.head(5).iterrows():
        y += 6
        pdf.set_xy(10, y)
        pdf.cell(10,  6, str(i),                           border=1, align='C')
        pdf.cell(110, 6, row['Factor'],                    border=1)
        pdf.cell(35,  6, str(row['Importance (%)']) + '%', border=1, align='C')
        pdf.cell(35,  6, str(row['Gap']),                  border=1, align='C')

    pdf.set_fill_color(0, 53, 128)
    pdf.rect(0, 282, 210, 15, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_xy(10, 285)
    pdf.cell(
        190, 6,
        'Air Tanzania GSE OEE System  |  M.Eng. Dissertation - DIT  |  Confidential',
        align='C'
    )
    return pdf.output()

# ─────────────────────────────────────────────
# ALERT HELPERS
# ─────────────────────────────────────────────
def get_alerts():
    """Aggregate all system alerts: overdue PM, low stock, overdue WOs, low OEE."""
    alerts = {"overdue_pm": pd.DataFrame(), "low_stock": pd.DataFrame(),
              "overdue_wo": pd.DataFrame(), "low_oee": pd.DataFrame()}
    today = date.today()

    pm_df = get_pm_tasks()
    if not pm_df.empty:
        pm_df['next_due_date'] = pd.to_datetime(pm_df['next_due_date']).dt.date
        alerts["overdue_pm"] = pm_df[pm_df['next_due_date'] < today]

    sp_df = get_spare_parts()
    if not sp_df.empty:
        alerts["low_stock"] = sp_df[
            sp_df['quantity_in_stock'] <= sp_df['reorder_point']
        ]

    wo_df = get_work_orders()
    if not wo_df.empty:
        wo_df['due_date_parsed'] = pd.to_datetime(
            wo_df['due_date'], errors='coerce'
        ).dt.date
        alerts["overdue_wo"] = wo_df[
            (wo_df['due_date_parsed'] < today) &
            (wo_df['status'] != 'Completed')
        ]

    pred_df = load_predictions()
    if not pred_df.empty:
        alerts["low_oee"] = pred_df[pred_df['predicted_oee'] < 40].head(10)

    return alerts

# ─────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────
def main():
    init_session()
    init_db()
    migrate_db()          # ensures old databases get any new columns safely

    if not st.session_state['authenticated']:
        show_login_page()
        return

    model, features, meta, fi_df = load_model()
    user     = st.session_state['user']
    username = st.session_state['username']
    role     = user['role']

    # ── SIDEBAR ──────────────────────────────
    with st.sidebar:
        if os.path.exists('atcl_logo.png'):
            st.image('atcl_logo.png', width=160)
        st.markdown("---")

        role_color = {
            "admin":      "#c9972c",
            "manager":    "#2980b9",
            "technician": "#27ae60"
        }.get(role, "#666")

        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.1); border-radius:8px;
                    padding:10px 12px; margin-bottom:10px;'>
            <div style='font-size:13px; font-weight:600;'>
                User: {user['name']}
            </div>
            <div style='font-size:11px; opacity:0.8;'>{user['position']}</div>
            <div style='margin-top:6px;'>
                <span style='background:{role_color}; color:white;
                             padding:2px 10px; border-radius:10px;
                             font-size:11px; font-weight:600;'>
                    {role.upper()}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        lang = st.radio("Language / Lugha", ["English", "Kiswahili"])
        L    = LANGUAGES[lang]
        st.markdown("---")

        allowed_pages = ROLE_PAGES[role]
        page = st.radio("Navigation", allowed_pages)
        st.markdown("---")

        if st.button("Logout", use_container_width=True):
            logout()

        st.markdown("---")
        st.markdown("""
        <div style='font-size:11px; color:#aac4ff; line-height:1.8;'>
            <b>OEE Scale:</b><br>
            0-20%   : Very Poor<br>
            20-40%  : Poor<br>
            40-60%  : Moderate<br>
            60-80%  : Good<br>
            80-100% : Very Good
        </div>
        """, unsafe_allow_html=True)

    # ── HEADER ───────────────────────────────
    st.markdown("""
    <div class="main-header">
        <h1>GSE Overall Equipment Effectiveness (OEE) Management System</h1>
        <p>Air Tanzania Company Limited (ATCL) - Ground Support Equipment
        Maintenance Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="user-info-bar">
        User: <b>{user['name']}</b> &nbsp;|&nbsp;
        {user['position']} &nbsp;|&nbsp;
        Role: <b style='color:#003580;'>{role.title()}</b> &nbsp;|&nbsp;
        {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
    """, unsafe_allow_html=True)

    # Quick alert banner (visible on every page)
    alerts = get_alerts()
    total_alerts = (len(alerts["overdue_pm"]) + len(alerts["low_stock"]) +
                    len(alerts["overdue_wo"]) + len(alerts["low_oee"]))
    if total_alerts > 0:
        st.markdown(
            "<div class='alert-box'>⚠ <b>" + str(total_alerts) +
            " active alert(s)</b> require attention. "
            "See <b>Alerts &amp; Notifications</b> for details.</div>",
            unsafe_allow_html=True
        )

    # ════════════════════════════════════════
    # PAGE: HOME
    # ════════════════════════════════════════
    if page == "Home":
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""<div class="metric-card">
                <h3>80%+</h3><p>World-class OEE Target</p>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card">
                <h3>{meta['oee_benchmark']['estimated_current_atcl']}%</h3>
                <p>Estimated Current ATCL OEE</p>
            </div>""", unsafe_allow_html=True)
        with col3:
            gap = round(
                80.0 - meta['oee_benchmark']['estimated_current_atcl'], 1
            )
            st.markdown(f"""<div class="gold-card">
                <h3>{gap}%</h3><p>OEE Gap to World-class</p>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div class="red-card">
                <h3>{total_alerts}</h3>
                <p>Active System Alerts</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        col_a, col_b = st.columns([1.2, 1])

        with col_a:
            st.markdown(
                '<div class="section-header">About This System</div>',
                unsafe_allow_html=True
            )
            st.markdown("""
            <div class="info-box">
            This system was developed as part of an M.Eng. (Maintenance Management)
            dissertation at the <b>Dar es Salaam Institute of Technology (DIT)</b>.
            It applies a <b>Random Forest Regression model</b> to predict and improve
            the Overall Equipment Effectiveness (OEE) of Aircraft Ground Support
            Equipment (GSE) at <b>Air Tanzania Company Limited (ATCL)</b>.
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            **System Modules:**
            - OEE Prediction (8-factor Random Forest model)
            - Objective OEE Calculator (Availability x Performance x Quality)
            - Asset / Equipment Registry
            - Spare Parts Inventory Management
            - Work Order Management
            - Failure Log & RCA / FMEA
            - Preventive Maintenance Scheduler
            - Bulk CSV Upload for fleet-wide assessment
            - Alerts & Notifications
            - Available in English and Kiswahili, with role-based access
            """)

        with col_b:
            st.markdown(
                '<div class="section-header">OEE Calibration Scale</div>',
                unsafe_allow_html=True
            )
            st.markdown("""
            <table class="oee-band-table">
                <tr>
                    <th>Input Scores</th>
                    <th>OEE Band</th>
                    <th>Implementation Status</th>
                </tr>
                <tr><td>All scores = 1</td>
                    <td>0% - 20%</td><td>Very Poor</td></tr>
                <tr><td>All scores = 2</td>
                    <td>20% - 40%</td><td>Poor</td></tr>
                <tr><td>All scores = 3</td>
                    <td>40% - 60%</td><td>Moderate</td></tr>
                <tr><td>All scores = 4</td>
                    <td>60% - 80%</td><td>Good</td></tr>
                <tr><td>All scores = 5</td>
                    <td>80% - 100%</td><td>Very Good</td></tr>
            </table>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.latex(r"OEE = Availability \times Performance \times Quality")

            pm_rate = pm_compliance_rate()
            st.markdown(
                "<div class='info-box'><b>Current PM Compliance Rate:</b> " +
                str(pm_rate) + "%</div>", unsafe_allow_html=True
            )

    # ════════════════════════════════════════
    # PAGE: OEE PREDICTION (horizontal, manual entry)
    # ════════════════════════════════════════
    elif page == "OEE Prediction":
        st.markdown(
            '<div class="section-header">'
            'OEE Prediction Tool - Objective 2</div>',
            unsafe_allow_html=True
        )

        with st.expander("OEE Score Interpretation Guide", expanded=False):
            st.markdown("""
            | Score Entered | OEE Output Band | Implementation Status |
            |---|---|---|
            | All 1s | 0% - 20% | Very Poor |
            | All 2s | 20% - 40% | Poor |
            | All 3s | 40% - 60% | Moderate |
            | All 4s | 60% - 80% | Good |
            | All 5s | 80% - 100% | Very Good |

            Mixed scores produce OEE in the band corresponding to their mean.
            """)

        col_gse, col_asset = st.columns(2)
        with col_gse:
            gse_type = st.selectbox(L['select_gse'], GSE_TYPES)
        with col_asset:
            asset_df = get_assets()
            asset_options = ["Not Linked / Unknown"] + (
                asset_df['asset_code'].tolist() if not asset_df.empty else []
            )
            asset_code = st.selectbox("Link to Registered Asset (optional)",
                                      asset_options)

        st.markdown(
            "**" + L['current_scores'] + "**"
            " *(Enter a value from 1 to 5 for each factor - "
            "1 = Strongly Disagree, 5 = Strongly Agree)*"
        )

        # Horizontal layout: 4 factors per row, manual number entry
        feature_items = list(FEATURE_LABELS.items())
        scores = {}

        row1 = st.columns(4)
        for i in range(4):
            col_key, col_label = feature_items[i]
            with row1[i]:
                scores[col_key] = st.number_input(
                    col_label, min_value=1, max_value=5, value=3, step=1,
                    key="pred_" + col_key
                )

        row2 = st.columns(4)
        for i in range(4, 8):
            col_key, col_label = feature_items[i]
            with row2[i - 4]:
                scores[col_key] = st.number_input(
                    col_label, min_value=1, max_value=5, value=3, step=1,
                    key="pred_" + col_key
                )

        mean_display = round(np.mean(list(scores.values())), 2)
        col_m1, col_m2 = st.columns([3, 1])
        with col_m1:
            st.info("Mean score: " + str(mean_display) + " / 5.00")
        with col_m2:
            predict_clicked = st.button(
                L['predict_btn'], use_container_width=True
            )

        st.markdown("---")

        if predict_clicked:
            oee, lower, upper, band_min, band_max, mean_sc = \
                predict_oee_calibrated(model, features, scores)
            status     = get_oee_status(oee)
            impl_label = get_implementation_label(oee)
            rec        = (RECOMMENDATIONS_SW[status]
                          if lang == "Kiswahili"
                          else RECOMMENDATIONS[status])

            save_prediction(
                username, role, gse_type, asset_code, scores,
                mean_sc, oee, band_min, band_max,
                status, impl_label, lang
            )

            col_out1, col_out2 = st.columns([1, 1.2])

            with col_out1:
                st.plotly_chart(
                    gauge_chart(oee, lower, upper, L['oee_label']),
                    use_container_width=True
                )
                badge_map = {
                    "Very Poor": "badge-verypoor",
                    "Poor":      "badge-poor",
                    "Moderate":  "badge-moderate",
                    "Good":      "badge-good",
                    "Very Good": "badge-verygood",
                }
                st.markdown(
                    "<center><span class='" + badge_map[status] + "'>"
                    + impl_label + "</span></center>",
                    unsafe_allow_html=True
                )

            with col_out2:
                c1, c2, c3 = st.columns(3)
                c1.metric("OEE Band",
                          str(band_min) + "% - " + str(band_max) + "%")
                c2.metric("Mean Input Score",
                          str(mean_sc) + " / 5.00")
                c3.metric("Gap to Very Good (80%)",
                          str(round(max(0, 80.0 - oee), 2)) + "%")

                st.markdown(
                    "<div class='info-box'><b>" + L['rec_label'] +
                    ":</b> " + rec + "</div>",
                    unsafe_allow_html=True
                )

                st.markdown("**Maintenance Priority Action Plan**")
                p_df = priority_table(fi_df, scores)
                st.dataframe(
                    p_df[['Factor', 'Your Score', 'Gap',
                           'Importance (%)', 'Priority Score']],
                    use_container_width=True
                )

                pdf_bytes = generate_pdf(
                    username, role, gse_type, scores,
                    oee, lower, upper, band_min, band_max,
                    mean_sc, status, impl_label, rec, fi_df
                )
                st.download_button(
                    label=L['download_btn'],
                    data=bytes(pdf_bytes),
                    file_name=(
                        "OEE_Report_" +
                        gse_type.replace(' ', '_') + "_" +
                        datetime.now().strftime('%Y%m%d_%H%M%S') + ".pdf"
                    ),
                    mime='application/pdf',
                    use_container_width=True
                )
        else:
            st.markdown("""
            <div style='text-align:center; padding:50px 20px; color:#666;'>
                <h3>Enter maintenance scores above and click Predict OEE</h3>
                <p>1 = 0-20% | 2 = 20-40% | 3 = 40-60% |
                4 = 60-80% | 5 = 80-100%</p>
            </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════
    # PAGE: OBJECTIVE OEE CALCULATOR (A x P x Q)
    # ════════════════════════════════════════
    elif page == "Objective OEE Calculator":
        st.markdown(
            '<div class="section-header">'
            'Objective OEE Calculator (Availability x Performance x Quality)'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown("""<div class="info-box">
        This module computes OEE directly from operational data (Section 2.6
        of the model), independent of the subjective 1-5 ratings used in the
        Prediction module. Use it to cross-validate the predicted OEE
        against measured operational performance.
        </div>""", unsafe_allow_html=True)

        asset_df = get_assets()
        asset_options = ["Not Linked / Unknown"] + (
            asset_df['asset_code'].tolist() if not asset_df.empty else []
        )
        asset_code = st.selectbox("Select Equipment", asset_options)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Availability Inputs**")
            operating_time = st.number_input(
                "Operating Time (hours)", min_value=0.0, value=20.0, step=0.5
            )
            planned_time = st.number_input(
                "Planned Production Time (hours)",
                min_value=0.01, value=24.0, step=0.5
            )
            st.markdown("**Performance Inputs**")
            ideal_rate = st.number_input(
                "Ideal Rate (units/hour)", min_value=0.01, value=10.0, step=0.5
            )
            actual_output = st.number_input(
                "Actual Output (units)", min_value=0.0, value=180.0, step=1.0
            )
        with col2:
            st.markdown("**Quality Inputs**")
            total_ops = st.number_input(
                "Total Operations / Cycles", min_value=0.01, value=200.0, step=1.0
            )
            good_ops = st.number_input(
                "Acceptable / Good Operations", min_value=0.0, value=190.0, step=1.0
            )

        calc_clicked = st.button(
            "Calculate Objective OEE", use_container_width=True
        )

        if calc_clicked:
            availability = min(100.0, (operating_time / planned_time) * 100)
            performance  = min(100.0,
                (actual_output / (ideal_rate * operating_time)) * 100
                if operating_time > 0 else 0
            )
            quality = min(100.0, (good_ops / total_ops) * 100)
            oee_obj = round(
                (availability / 100) * (performance / 100) *
                (quality / 100) * 100, 2
            )

            add_objective_oee(
                asset_code, operating_time, planned_time, ideal_rate,
                actual_output, total_ops, good_ops,
                round(availability, 2), round(performance, 2),
                round(quality, 2), oee_obj, username
            )

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Availability", str(round(availability, 2)) + "%")
            c2.metric("Performance",  str(round(performance, 2)) + "%")
            c3.metric("Quality",      str(round(quality, 2)) + "%")
            c4.metric("Objective OEE", str(oee_obj) + "%")

            st.plotly_chart(
                gauge_chart(oee_obj, oee_obj, oee_obj, "Measured (Objective) OEE"),
                use_container_width=True
            )

            # Cross-check against latest prediction for this asset
            pred_df = load_predictions()
            if not pred_df.empty and asset_code != "Not Linked / Unknown":
                match = pred_df[pred_df['asset_code'] == asset_code]
                if not match.empty:
                    latest_pred = match.iloc[0]['predicted_oee']
                    diff = round(oee_obj - latest_pred, 2)
                    st.markdown(
                        "<div class='info-box'>Latest predicted OEE "
                        "for this asset: <b>" + str(latest_pred) + "%</b> "
                        "&nbsp;|&nbsp; Difference from measured OEE: <b>" +
                        str(diff) + " points</b></div>",
                        unsafe_allow_html=True
                    )

        st.markdown("---")
        st.markdown("**Objective OEE Calculation History**")
        obj_df = get_objective_oee()
        if obj_df.empty:
            st.info("No objective OEE calculations recorded yet.")
        else:
            st.dataframe(obj_df, use_container_width=True)

    # ════════════════════════════════════════
    # PAGE: ASSET REGISTRY
    # ════════════════════════════════════════
    elif page == "Asset Registry":
        st.markdown(
            '<div class="section-header">GSE Asset / Equipment Registry</div>',
            unsafe_allow_html=True
        )

        with st.expander("Register New Asset", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                asset_code_new = st.text_input("Asset Code (unique)",
                                               placeholder="e.g. GPU-001")
                gse_type_new   = st.selectbox("GSE Type", GSE_TYPES,
                                              key="asset_gse_type")
                model_serial   = st.text_input("Model / Serial Number")
            with c2:
                location_new   = st.text_input("Location / Station",
                                               placeholder="e.g. JNIA Apron 3")
                commission_dt  = st.date_input("Commissioning Date")
                status_new     = st.selectbox("Status", ASSET_STATUSES)

            if st.button("Add Asset to Registry"):
                if not asset_code_new:
                    st.error("Asset Code is required.")
                else:
                    try:
                        add_asset(asset_code_new, gse_type_new, model_serial,
                                  location_new, commission_dt, status_new,
                                  username)
                        st.success(
                            "Asset " + asset_code_new + " registered successfully."
                        )
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Asset code already exists.")

        st.markdown("**Registered Assets**")
        asset_df = get_assets()
        if asset_df.empty:
            st.info("No assets registered yet.")
        else:
            st.dataframe(asset_df, use_container_width=True)

            st.markdown("**Update Asset Status**")
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                sel_asset = st.selectbox(
                    "Select Asset", asset_df['asset_code'].tolist()
                )
            with c2:
                sel_status = st.selectbox("New Status", ASSET_STATUSES)
            with c3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Update Status"):
                    update_asset_status(sel_asset, sel_status)
                    st.success("Status updated.")
                    st.rerun()

            if role in ("admin", "manager"):
                with st.expander("Remove Asset"):
                    del_asset = st.selectbox(
                        "Select Asset to Remove",
                        asset_df['asset_code'].tolist(), key="del_asset"
                    )
                    if st.button("Delete Asset", type="secondary"):
                        delete_asset(del_asset)
                        st.warning("Asset removed.")
                        st.rerun()

    # ════════════════════════════════════════
    # PAGE: SPARE PARTS INVENTORY
    # ════════════════════════════════════════
    elif page == "Spare Parts Inventory":
        st.markdown(
            '<div class="section-header">Spare Parts Inventory Management</div>',
            unsafe_allow_html=True
        )
        st.markdown("""<div class="info-box">
        Linked to CMMS: tracks minimum stock levels, reorder points, and
        supplier lead times, as recommended for Spare Parts Availability
        (Section 4.2.2.4 of the dissertation).
        </div>""", unsafe_allow_html=True)

        with st.expander("Add New Spare Part", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                part_code = st.text_input("Part Code", placeholder="e.g. SP-001")
                part_name = st.text_input("Part Name")
                category  = st.text_input("Category",
                                          placeholder="e.g. Hydraulic, Electrical")
            with c2:
                qty        = st.number_input("Quantity in Stock",
                                             min_value=0, value=10, step=1)
                min_stock  = st.number_input("Minimum Stock Level",
                                             min_value=0, value=5, step=1)
                reorder_pt = st.number_input("Reorder Point",
                                             min_value=0, value=8, step=1)
            with c3:
                unit_cost  = st.number_input("Unit Cost (TZS)",
                                             min_value=0.0, value=50000.0, step=1000.0)
                supplier   = st.text_input("Supplier")
                lead_time  = st.number_input("Lead Time (days)",
                                             min_value=0, value=14, step=1)

            if st.button("Add Spare Part"):
                if not part_code or not part_name:
                    st.error("Part Code and Part Name are required.")
                else:
                    try:
                        add_spare_part(part_code, part_name, category, qty,
                                      min_stock, reorder_pt, unit_cost,
                                      supplier, lead_time)
                        st.success("Spare part added successfully.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Part code already exists.")

        st.markdown("**Current Inventory**")
        sp_df = get_spare_parts()
        if sp_df.empty:
            st.info("No spare parts recorded yet.")
        else:
            def highlight_low(row):
                if row['quantity_in_stock'] <= row['reorder_point']:
                    return ['background-color:#fdecea'] * len(row)
                return [''] * len(row)

            st.dataframe(
                sp_df.style.apply(highlight_low, axis=1),
                use_container_width=True
            )

            low_stock = sp_df[sp_df['quantity_in_stock'] <= sp_df['reorder_point']]
            if not low_stock.empty:
                st.markdown(
                    "<div class='alert-box'>⚠ " + str(len(low_stock)) +
                    " part(s) at or below reorder point.</div>",
                    unsafe_allow_html=True
                )

            st.markdown("**Update Stock Quantity**")
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                sel_part = st.selectbox(
                    "Select Part", sp_df['part_code'].tolist()
                )
            with c2:
                new_qty = st.number_input(
                    "New Quantity", min_value=0, value=0, step=1
                )
            with c3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Update Stock"):
                    update_spare_part_stock(sel_part, new_qty)
                    st.success("Stock updated.")
                    st.rerun()

            if role in ("admin", "manager"):
                with st.expander("Remove Spare Part"):
                    del_part = st.selectbox(
                        "Select Part to Remove",
                        sp_df['part_code'].tolist(), key="del_part"
                    )
                    if st.button("Delete Part", type="secondary"):
                        delete_spare_part(del_part)
                        st.warning("Part removed.")
                        st.rerun()

    # ════════════════════════════════════════
    # PAGE: WORK ORDERS
    # ════════════════════════════════════════
    elif page == "Work Orders":
        st.markdown(
            '<div class="section-header">Work Order Management</div>',
            unsafe_allow_html=True
        )

        with st.expander("Create New Work Order", expanded=False):
            asset_df = get_assets()
            asset_options = (asset_df['asset_code'].tolist()
                            if not asset_df.empty else ["No assets registered"])
            c1, c2 = st.columns(2)
            with c1:
                wo_asset = st.selectbox("Equipment (Asset Code)", asset_options)
                wo_title = st.text_input("Work Order Title")
                wo_type  = st.selectbox("Task Type", WO_TASK_TYPES)
            with c2:
                wo_priority = st.selectbox("Priority", WO_PRIORITIES)
                wo_assigned = st.text_input("Assigned To")
                wo_due      = st.date_input("Due Date")
            wo_desc = st.text_area("Description")

            if st.button("Create Work Order"):
                if not wo_title:
                    st.error("Work Order Title is required.")
                else:
                    wo_num = add_work_order(wo_asset, wo_title, wo_desc,
                                            wo_type, wo_priority,
                                            wo_assigned, wo_due)
                    st.success("Work Order " + wo_num + " created.")
                    st.rerun()

        st.markdown("**All Work Orders**")
        wo_df = get_work_orders()
        if wo_df.empty:
            st.info("No work orders recorded yet.")
        else:
            st.dataframe(wo_df, use_container_width=True)

            st.markdown("**Update Work Order Status**")
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                sel_wo = st.selectbox(
                    "Select Work Order", wo_df['wo_number'].tolist()
                )
            with c2:
                sel_wo_status = st.selectbox("New Status", WO_STATUSES)
            with c3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Update WO Status"):
                    update_work_order_status(sel_wo, sel_wo_status)
                    st.success("Work order status updated.")
                    st.rerun()

    # ════════════════════════════════════════
    # PAGE: FAILURE LOG (RCA / FMEA)
    # ════════════════════════════════════════
    elif page == "Failure Log (RCA/FMEA)":
        st.markdown(
            '<div class="section-header">'
            'Failure Log &amp; Root Cause Analysis (RCA / FMEA)</div>',
            unsafe_allow_html=True
        )
        st.markdown("""<div class="info-box">
        Structured breakdown reporting recommended in Section 4.2.2.5 to
        ground the Unplanned Breakdowns (UB) and Maintenance Errors and
        Rework (MER) ratings in actual failure data.
        </div>""", unsafe_allow_html=True)

        with st.expander("Log New Failure / Breakdown", expanded=False):
            asset_df = get_assets()
            asset_options = (asset_df['asset_code'].tolist()
                            if not asset_df.empty else ["No assets registered"])
            c1, c2 = st.columns(2)
            with c1:
                f_asset = st.selectbox("Equipment (Asset Code)", asset_options,
                                       key="fail_asset")
                f_date  = st.date_input("Failure Date")
                f_severity = st.selectbox("Severity", SEVERITY_LEVELS)
            with c2:
                f_downtime = st.number_input("Downtime (hours)",
                                             min_value=0.0, value=2.0, step=0.5)
                f_reported = st.text_input("Reported By")

            f_mode   = st.text_input("Failure Mode",
                                     placeholder="e.g. Hydraulic leak, Engine stall")
            f_cause  = st.text_area("Root Cause (RCA)",
                                    placeholder="Why did the failure occur?")
            f_effect = st.text_area("Failure Effect (FMEA)",
                                    placeholder="What was the operational impact?")
            f_action = st.text_area("Corrective Action Taken")

            if st.button("Log Failure"):
                if not f_mode:
                    st.error("Failure Mode is required.")
                else:
                    add_failure_log(f_asset, f_date, f_mode, f_cause, f_effect,
                                    f_severity, f_downtime, f_action, f_reported)
                    st.success("Failure logged successfully.")
                    st.rerun()

        st.markdown("**Failure History**")
        fl_df = get_failure_logs()
        if fl_df.empty:
            st.info("No failures logged yet.")
        else:
            st.dataframe(fl_df, use_container_width=True)

            c1, c2 = st.columns(2)
            with c1:
                sev_counts = fl_df['severity'].value_counts().reset_index()
                sev_counts.columns = ['Severity', 'Count']
                fig_sev = px.pie(
                    sev_counts, values='Count', names='Severity',
                    title='Failures by Severity',
                    color_discrete_map={
                        'Critical': '#7b0000', 'High': '#c0392b',
                        'Medium': '#e67e22', 'Low': '#2980b9'
                    }
                )
                st.plotly_chart(fig_sev, use_container_width=True)
            with c2:
                asset_counts = fl_df['asset_code'].value_counts().reset_index()
                asset_counts.columns = ['Asset', 'Failure Count']
                fig_asset = px.bar(
                    asset_counts.head(10), x='Asset', y='Failure Count',
                    title='Top Assets by Failure Frequency',
                    color_discrete_sequence=['#003580']
                )
                fig_asset.update_layout(
                    plot_bgcolor='white', paper_bgcolor='white'
                )
                st.plotly_chart(fig_asset, use_container_width=True)

            st.metric("Total Downtime Logged",
                      str(round(fl_df['downtime_hours'].sum(), 1)) + " hours")

    # ════════════════════════════════════════
    # PAGE: PM SCHEDULER
    # ════════════════════════════════════════
    elif page == "PM Scheduler":
        st.markdown(
            '<div class="section-header">Preventive Maintenance Scheduler</div>',
            unsafe_allow_html=True
        )
        st.markdown("""<div class="info-box">
        Converts the Preventive Maintenance Schedule (PMS) factor from a
        static rating into a live, trackable operational metric with
        due-date alerts and compliance tracking.
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Overall PM Compliance Rate", str(pm_compliance_rate()) + "%")
        with c2:
            pm_df_check = get_pm_tasks()
            overdue_ct = 0
            if not pm_df_check.empty:
                today = date.today()
                pm_df_check['next_due_date'] = pd.to_datetime(
                    pm_df_check['next_due_date']
                ).dt.date
                overdue_ct = len(pm_df_check[pm_df_check['next_due_date'] < today])
            st.metric("Overdue PM Tasks", overdue_ct)

        with st.expander("Schedule New PM Task", expanded=False):
            asset_df = get_assets()
            asset_options = (asset_df['asset_code'].tolist()
                            if not asset_df.empty else ["No assets registered"])
            c1, c2, c3 = st.columns(3)
            with c1:
                pm_asset = st.selectbox("Equipment (Asset Code)", asset_options,
                                        key="pm_asset")
            with c2:
                pm_task_name = st.text_input(
                    "Task Name", placeholder="e.g. Oil change, Inspection"
                )
            with c3:
                pm_freq = st.selectbox("Frequency", PM_FREQUENCIES)

            pm_last_done = st.date_input("Last Done Date", value=date.today())

            if st.button("Add PM Task"):
                if not pm_task_name:
                    st.error("Task Name is required.")
                else:
                    add_pm_task(pm_asset, pm_task_name, pm_freq, pm_last_done)
                    st.success("PM task scheduled successfully.")
                    st.rerun()

        st.markdown("**Scheduled PM Tasks**")
        pm_df = get_pm_tasks()
        if pm_df.empty:
            st.info("No PM tasks scheduled yet.")
        else:
            today = date.today()
            pm_df['next_due_date'] = pd.to_datetime(pm_df['next_due_date']).dt.date
            pm_df['Overdue'] = pm_df['next_due_date'] < today

            def highlight_overdue(row):
                if row['Overdue']:
                    return ['background-color:#fdecea'] * len(row)
                return [''] * len(row)

            st.dataframe(
                pm_df.style.apply(highlight_overdue, axis=1),
                use_container_width=True
            )

            st.markdown("**Mark Task as Completed**")
            c1, c2 = st.columns([3, 1])
            with c1:
                pm_options = (pm_df['task_name'] + " | " +
                             pm_df['asset_code'] + " (ID:" +
                             pm_df['id'].astype(str) + ")").tolist()
                sel_pm = st.selectbox("Select PM Task", pm_options)
                sel_pm_id = int(sel_pm.split("ID:")[1].replace(")", ""))
            with c2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Mark Completed"):
                    row_match = pm_df[pm_df['id'] == sel_pm_id].iloc[0]
                    mark_pm_completed(sel_pm_id, row_match['frequency'])
                    st.success("PM task marked as completed. Next due date recalculated.")
                    st.rerun()

    # ════════════════════════════════════════
    # PAGE: BULK CSV UPLOAD
    # ════════════════════════════════════════
    elif page == "Bulk CSV Upload":
        st.markdown(
            '<div class="section-header">Bulk GSE Assessment Upload</div>',
            unsafe_allow_html=True
        )
        st.markdown("""<div class="info-box">
        Upload a CSV with columns for all 8 factors (Likert 1-5).
        Each row = one GSE unit. OEE output follows the calibration scale.
        </div>""", unsafe_allow_html=True)

        tmpl = pd.DataFrame(
            columns=['GSE_Type'] + list(FEATURE_LABELS.keys())
        )
        tmpl.loc[0] = ['Ground Power Unit (GPU)'] + [3] * 8
        tmpl.loc[1] = ['Pushback Tractor']         + [4] * 8
        st.download_button(
            "Download CSV Template",
            data=tmpl.to_csv(index=False),
            file_name="GSE_Template.csv",
            mime='text/csv'
        )

        uploaded = st.file_uploader("Upload CSV", type=['csv'])
        if uploaded:
            up_df = pd.read_csv(uploaded)
            st.markdown("**Uploaded Data Preview:**")
            st.dataframe(up_df.head(), use_container_width=True)

            missing = [c for c in FEATURE_LABELS if c not in up_df.columns]
            if missing:
                st.error("Missing columns: " + str(missing))
            else:
                results = []
                for _, row in up_df.iterrows():
                    s = {c: int(row[c]) for c in FEATURE_LABELS}
                    o, lo, hi, bmin, bmax, ms = predict_oee_calibrated(
                        model, features, s
                    )
                    results.append({
                        'GSE_Type':      row.get('GSE_Type', 'Unknown'),
                        'Mean_Score':    ms,
                        'Predicted_OEE': o,
                        'OEE_Band':      str(bmin) + "% - " + str(bmax) + "%",
                        'Lower_CI':      lo,
                        'Upper_CI':      hi,
                        'Status':        get_implementation_label(o),
                        'Gap_to_80':     round(max(0, 80 - o), 2)
                    })

                res_df = pd.DataFrame(results)
                st.success(
                    str(len(res_df)) + " GSE units processed successfully."
                )
                st.dataframe(
                    res_df.style.background_gradient(
                        subset=['Predicted_OEE'],
                        cmap='RdYlGn', vmin=0, vmax=100
                    ),
                    use_container_width=True
                )

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res_df.to_excel(writer, index=False,
                                    sheet_name='OEE Results')
                    up_df.to_excel(writer, index=False,
                                   sheet_name='Input Data')
                st.download_button(
                    "Download Results",
                    data=output.getvalue(),
                    file_name="Bulk_OEE_" +
                               datetime.now().strftime('%Y%m%d_%H%M%S') +
                               ".xlsx",
                    mime='application/vnd.openxmlformats-officedocument'
                         '.spreadsheetml.sheet'
                )

    # ════════════════════════════════════════
    # PAGE: ALERTS & NOTIFICATIONS
    # ════════════════════════════════════════
    elif page == "Alerts & Notifications":
        st.markdown(
            '<div class="section-header">Alerts &amp; Notifications</div>',
            unsafe_allow_html=True
        )
        st.markdown("""<div class="info-box">
        Consolidated real-time alerts drawn from the Spare Parts, PM
        Scheduler, Work Order, and OEE Prediction modules, operationalising
        the system's decision-support function.
        </div>""", unsafe_allow_html=True)

        alerts = get_alerts()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Overdue PM Tasks", len(alerts["overdue_pm"]))
        c2.metric("Low Stock Parts", len(alerts["low_stock"]))
        c3.metric("Overdue Work Orders", len(alerts["overdue_wo"]))
        c4.metric("Recent Low OEE Predictions (<40%)", len(alerts["low_oee"]))

        st.markdown("---")

        st.markdown("**⏰ Overdue Preventive Maintenance Tasks**")
        if alerts["overdue_pm"].empty:
            st.markdown(
                "<div class='ok-box'>No overdue PM tasks.</div>",
                unsafe_allow_html=True
            )
        else:
            st.dataframe(
                alerts["overdue_pm"][
                    ['asset_code', 'task_name', 'frequency',
                     'next_due_date', 'status']
                ], use_container_width=True
            )

        st.markdown("**📦 Spare Parts Below Reorder Point**")
        if alerts["low_stock"].empty:
            st.markdown(
                "<div class='ok-box'>No low-stock alerts.</div>",
                unsafe_allow_html=True
            )
        else:
            st.dataframe(
                alerts["low_stock"][
                    ['part_code', 'part_name', 'quantity_in_stock',
                     'reorder_point', 'supplier', 'lead_time_days']
                ], use_container_width=True
            )

        st.markdown("**🛠 Overdue Work Orders**")
        if alerts["overdue_wo"].empty:
            st.markdown(
                "<div class='ok-box'>No overdue work orders.</div>",
                unsafe_allow_html=True
            )
        else:
            st.dataframe(
                alerts["overdue_wo"][
                    ['wo_number', 'asset_code', 'title', 'priority',
                     'assigned_to', 'due_date', 'status']
                ], use_container_width=True
            )

        st.markdown("**📉 Recent Low OEE Predictions (Below 40%)**")
        if alerts["low_oee"].empty:
            st.markdown(
                "<div class='ok-box'>No recent low-OEE predictions.</div>",
                unsafe_allow_html=True
            )
        else:
            st.dataframe(
                alerts["low_oee"][
                    ['timestamp', 'gse_type', 'asset_code',
                     'predicted_oee', 'status']
                ], use_container_width=True
            )

# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()