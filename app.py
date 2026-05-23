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
from datetime import datetime
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
# OEE CALIBRATION
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

ROLE_PAGES = {
    "admin": [
        "Home",
        "OEE Prediction",
        "Trend Analysis",
        "Bulk CSV Upload",
        "Admin Dashboard",
    ],
    "manager": [
        "Home",
        "OEE Prediction",
        "Trend Analysis",
        "Bulk CSV Upload",
    ],
    "technician": [
        "Home",
        "OEE Prediction",
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
# LOGIN PAGE — UPDATED WITH LOGO
# ─────────────────────────────────────────────
def show_login_page():

    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:

        # Air Tanzania logo above the login box
        if os.path.exists('atcl_logo.png'):
            st.image('atcl_logo.png', use_container_width=True)
        else:
            st.markdown("""
            <div style='text-align:center; padding:10px 0;'>
                <h2 style='color:#003580; font-weight:800;'>Air Tanzania</h2>
            </div>
            """, unsafe_allow_html=True)

        # Login card with blue/gold header
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

        # Login form
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
def init_db():
    conn = sqlite3.connect('oee_predictions.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            username TEXT,
            role TEXT,
            gse_type TEXT,
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
    conn.commit()
    conn.close()

def save_prediction(username, role, gse_type, scores,
                    mean_score, oee, band_min, band_max,
                    status, impl_label, lang):
    conn = sqlite3.connect('oee_predictions.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO predictions (
            timestamp, username, role, gse_type,
            unplanned_breakdowns, preventive_maintenance,
            spare_parts, maintenance_errors, cmms,
            maintenance_budget, technician_competency,
            history_records, mean_score, predicted_oee,
            oee_band_min, oee_band_max, status,
            implementation_label, language
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        username, role, gse_type,
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
    conn = sqlite3.connect('oee_predictions.db')
    df = pd.read_sql_query(
        "SELECT * FROM predictions ORDER BY timestamp DESC", conn
    )
    conn.close()
    return df

# ─────────────────────────────────────────────
# LOAD MODEL
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
# PREDICTION WITH CALIBRATION
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
# PDF GENERATION
# ─────────────────────────────────────────────
def generate_pdf(username, role, gse_type, scores,
                 oee, lower, upper, band_min, band_max,
                 mean_score, status, impl_label, rec, fi_df):
    pdf = FPDF()
    pdf.add_page()

    # Blue header
    pdf.set_fill_color(0, 53, 128)
    pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, 8)
    pdf.cell(190, 10, 'AIR TANZANIA COMPANY LIMITED (ATCL)', align='C')
    pdf.set_font('Helvetica', '', 11)
    pdf.set_xy(10, 20)
    pdf.cell(190, 8, 'GSE OEE Maintenance Management Report', align='C')

    # Gold line
    pdf.set_fill_color(201, 151, 44)
    pdf.rect(0, 35, 210, 3, 'F')

    # Metadata
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

    # OEE result header
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_fill_color(0, 53, 128)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, 60)
    pdf.cell(190, 8, ' OEE PREDICTION RESULT', fill=True)

    # OEE values
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

    # Scale reference
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

    # Recommendation — strip emojis for PDF safety
    rec_clean = rec
    for emoji in ['🔴','🟠','🟡','🔵','✅']:
        rec_clean = rec_clean.replace(emoji, '').strip()

    pdf.set_fill_color(232, 240, 254)
    pdf.set_xy(10, y_s + 3)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(190, 7, ' Recommendation', fill=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_xy(10, y_s + 11)
    pdf.multi_cell(190, 6, rec_clean)

    # Input scores table
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

    # Priority table
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

    # Footer
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
# MAIN APPLICATION
# ─────────────────────────────────────────────
def main():
    init_session()
    init_db()

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
            st.markdown(f"""<div class="metric-card">
                <h3>{meta['n_features']}</h3>
                <p>Significant Maintenance Factors</p>
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
            **System Capabilities:**
            - Predict OEE from 8 key maintenance factors
            - Track OEE trends over time
            - Batch-process multiple GSE assessments
            - Generate downloadable PDF maintenance reports
            - Available in English and Kiswahili
            - Role-based access control
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

    # ════════════════════════════════════════
    # PAGE: OEE PREDICTION
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

        col_inp, col_out = st.columns([1, 1.2])

        with col_inp:
            gse_type = st.selectbox(L['select_gse'], GSE_TYPES)
            st.markdown(
                "**" + L['current_scores'] + "**"
                " *(1 = Strongly Disagree, 5 = Strongly Agree)*"
            )
            scores = {}
            for col, label in FEATURE_LABELS.items():
                scores[col] = st.slider(label, 1, 5, 3, key="pred_" + col)

            mean_display = round(np.mean(list(scores.values())), 2)
            st.info("Mean score: " + str(mean_display) + " / 5.00")
            predict_clicked = st.button(
                L['predict_btn'], use_container_width=True
            )

        with col_out:
            if predict_clicked:
                oee, lower, upper, band_min, band_max, mean_sc = \
                    predict_oee_calibrated(model, features, scores)
                status     = get_oee_status(oee)
                impl_label = get_implementation_label(oee)
                rec        = (RECOMMENDATIONS_SW[status]
                              if lang == "Kiswahili"
                              else RECOMMENDATIONS[status])

                save_prediction(
                    username, role, gse_type, scores,
                    mean_sc, oee, band_min, band_max,
                    status, impl_label, lang
                )

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
                st.markdown("<br>", unsafe_allow_html=True)

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
                    <h3>Set maintenance scores and click Predict</h3>
                    <p>1 = 0-20% | 2 = 20-40% | 3 = 40-60% |
                    4 = 60-80% | 5 = 80-100%</p>
                </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════
    # PAGE: TREND ANALYSIS
    # ════════════════════════════════════════
    elif page == "Trend Analysis":
        st.markdown(
            '<div class="section-header">OEE Trend Analysis</div>',
            unsafe_allow_html=True
        )
        pred_df = load_predictions()

        if pred_df.empty:
            st.info(
                "No predictions recorded yet. "
                "Use OEE Prediction to generate records."
            )
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Predictions", len(pred_df))
            c2.metric("Mean OEE",
                      str(round(pred_df['predicted_oee'].mean(), 2)) + "%")
            c3.metric("Best OEE",
                      str(round(pred_df['predicted_oee'].max(), 2)) + "%")
            c4.metric("Latest OEE",
                      str(round(pred_df['predicted_oee'].iloc[0], 2)) + "%")

            pred_asc = pred_df.sort_values('timestamp')
            fig_t = go.Figure()
            fig_t.add_trace(go.Scatter(
                x=pred_asc['timestamp'],
                y=pred_asc['predicted_oee'],
                mode='lines+markers',
                name='OEE',
                line=dict(color='#003580', width=2),
                marker=dict(size=8, color='#c9972c')
            ))
            for y_val, lbl, color in [
                (80, 'Very Good (80%)', 'green'),
                (60, 'Good (60%)',      '#2980b9'),
                (40, 'Moderate (40%)', 'orange'),
                (20, 'Poor (20%)',     'red'),
            ]:
                fig_t.add_hline(
                    y=y_val, line_dash="dash", line_color=color,
                    annotation_text=lbl, annotation_position="right"
                )
            fig_t.update_layout(
                title='OEE Trend Over Time',
                yaxis=dict(range=[0, 100]),
                height=420,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            st.plotly_chart(fig_t, use_container_width=True)

            gse_avg = (
                pred_df.groupby('gse_type')['predicted_oee']
                .mean().reset_index()
            )
            fig_g = px.bar(
                gse_avg, x='gse_type', y='predicted_oee',
                title='Average OEE by GSE Type',
                color='predicted_oee',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100]
            )
            fig_g.update_layout(
                height=350, xaxis_tickangle=-30,
                plot_bgcolor='white', paper_bgcolor='white'
            )
            st.plotly_chart(fig_g, use_container_width=True)

            st.markdown("**All Prediction Records**")
            st.dataframe(pred_df, use_container_width=True)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                pred_df.to_excel(writer, index=False,
                                 sheet_name='OEE Predictions')
            st.download_button(
                "Download as Excel",
                data=output.getvalue(),
                file_name="OEE_Trend_" +
                           datetime.now().strftime('%Y%m%d') + ".xlsx",
                mime='application/vnd.openxmlformats-officedocument'
                     '.spreadsheetml.sheet'
            )

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
    # PAGE: ADMIN DASHBOARD
    # ════════════════════════════════════════
    elif page == "Admin Dashboard":
        if role != "admin":
            st.markdown("""
            <div style='text-align:center; padding:60px 20px; color:#c0392b;'>
                <h2>Access Denied</h2>
                <p>This page is restricted to system administrators only.</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="section-header">'
                'Admin Dashboard - System Monitoring</div>',
                unsafe_allow_html=True
            )
            pred_df = load_predictions()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Predictions", len(pred_df))
            c2.metric(
                "Mean OEE",
                str(round(pred_df['predicted_oee'].mean(), 2)) + "%"
                if not pred_df.empty else "N/A"
            )
            c3.metric(
                "Very Good Count",
                len(pred_df[pred_df['status'] == 'Very Good'])
                if not pred_df.empty else 0
            )
            c4.metric(
                "Very Poor Count",
                len(pred_df[pred_df['status'] == 'Very Poor'])
                if not pred_df.empty else 0
            )

            if not pred_df.empty:
                col_a, col_b = st.columns(2)

                with col_a:
                    sc = pred_df['status'].value_counts().reset_index()
                    sc.columns = ['Status', 'Count']
                    fig_s = px.pie(
                        sc, values='Count', names='Status',
                        title='Implementation Status Distribution',
                        color_discrete_map={
                            'Very Good': '#1a7a1a',
                            'Good':      '#2980b9',
                            'Moderate':  '#e67e22',
                            'Poor':      '#c0392b',
                            'Very Poor': '#7b0000'
                        }
                    )
                    st.plotly_chart(fig_s, use_container_width=True)

                with col_b:
                    if 'username' in pred_df.columns:
                        uc = pred_df['username'].value_counts().reset_index()
                        uc.columns = ['User', 'Count']
                        fig_u = px.bar(
                            uc, x='User', y='Count',
                            title='Predictions by User',
                            color_discrete_sequence=['#003580']
                        )
                        fig_u.update_layout(
                            plot_bgcolor='white', paper_bgcolor='white'
                        )
                        st.plotly_chart(fig_u, use_container_width=True)

                st.markdown("**All System Records**")
                st.dataframe(pred_df, use_container_width=True)

                st.markdown("**System Information**")
                st.json({
                    "model_version":   meta['version'],
                    "trained_on":      meta['trained_on'],
                    "author":          meta['author'],
                    "institution":     meta['institution'],
                    "db_file":         "oee_predictions.db",
                    "system_time":     datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "active_accounts": len(USERS),
                    "total_records":   len(pred_df)
                })
            else:
                st.info("No records in the database yet.")

# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()