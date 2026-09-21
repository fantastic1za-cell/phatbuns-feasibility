import os
import shutil
import urllib.parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import streamlit as st

# ReportLab Imports for PDF Generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ==========================================
# STREAMLIT PAGE CONFIG & BRAND STYLING
# ==========================================
st.set_page_config(
    page_title="Phatbuns Feasibility Engine",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Responsive CSS for Mobile Ergonomics
st.markdown("""
<style>
.stApp {
    background-color: #111111;
    color: #FFFFFF;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.brand-banner {
    background: linear-gradient(135deg, #1f1f1f 0%, #0a0a0a 100%);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    border: 1px solid #333;
    text-align: center;
}
.brand-title {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: 800;
    margin: 0;
    letter-spacing: 0.5px;
}
.brand-subtitle {
    color: #FFD1B3;
    font-size: 13px;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

# Top Brand Banner
st.markdown("""
<div class="brand-banner">
    <div class="brand-title">PHATBUNS SOUTH AFRICA</div>
    <div class="brand-subtitle">Commercial Feasibility & Location Intelligence Engine</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# STORE MODEL DEFINITIONS & DEFAULTS
# ==========================================
STORE_MODELS = {
    "Kiosk Model": {
        "size_range": "20 - 60 sqm",
        "turnkey_capital": 850000.0,
        "working_capital": 250000.0,
    },
    "Express Model": {
        "size_range": "40 - 90 sqm",
        "turnkey_capital": 2500000.0,
        "working_capital": 450000.0,
    },
    "Full Sit-Down Model": {
        "size_range": "100 - 160 sqm",
        "turnkey_capital": 3250000.0,
        "working_capital": 700000.0,
    },
    "Multi-Brand Kitchen Model": {
        "size_range": "100 - 160 sqm",
        "turnkey_capital": 3250000.0,
        "working_capital": 700000.0,
    },
}

# ==========================================
# SECTION 1: SITE & LEASE SPECIFICATION
# ==========================================
st.header("1. Site & Lease Specification")

col1, col2 = st.columns(2)
with col1:
    location_name = st.text_input("Location Name", value="The Glen Shopping Centre")
with col2:
    shop_code = st.text_input("Shop / Unit Code", value="Shop M12C")

suburb_node = st.text_input("Suburb / Node", value="Oakdene, Johannesburg South")

st.divider()

# Store Model Selection
st.subheader("Store Model Type")
selected_model = st.radio(
    "Select Model Type",
    options=list(STORE_MODELS.keys()),
    index=3,
    horizontal=True
)

# Fetch Model Specifics
model_data = STORE_MODELS.get(selected_model, STORE_MODELS["Multi-Brand Kitchen Model"])

# Size Guidance Alert
st.info(f"📐 **Recommended Size Range:** {model_data['size_range']}")

st.divider()

# ==========================================
# SECTION 2: COMMERCIAL CAPITAL REQUIREMENTS
# ==========================================
st.subheader("2. Commercial Capital Requirements")

col_cap, col_wc = st.columns(2)

with col_cap:
    turnkey_capital = st.number_input(
        "Total Turnkey Capital (Excl. VAT)",
        value=model_data["turnkey_capital"],
        step=50000.0,
        format="%.2f",
        help="Estimated baseline turnkey capital based on selected model."
    )

with col_wc:
    working_capital = st.number_input(
        "Suggested Working Capital Requirement",
        value=model_data["working_capital"],
        step=25000.0,
        format="%.2f",
        help="Recommended liquidity reserve."
    )

st.warning(
    "**Commercial Terms & Legal Notes:**\n"
    "* All capital amounts are **exclusive of VAT** and working capital requirements.\n"
    "* Excludes rental deposits required by landlords.\n"
    "* Includes Franchise Fee, architectural/submission plans, and complete turnkey buildout.\n"
    "* Store size and site specs are subject to final landlord proposals.\n"
    "* **Franchise Agreement Term:** 5 Years (renewable at a fee to be determined). "
    "Requires a complete store refresh once every 5 years."
)

st.divider()

# ==========================================
# MASTER RIGHTS HOLDER CONTACT FOOTER
# ==========================================
st.subheader("Master Rights Holder Contact Information")
st.markdown("""
**Master Rights Holder – South Africa**  
📧 **Email:** nisaar@fantastic1.com | fantastic1za@gmail.com  
💬 **WhatsApp:** +27 82 786 7712  
📲 **Mobile:** +27 68 710 1939 | +27 68 727 4731  
""")
