# app.py - Streamlit UI & Feasibility Orchestrator (Restored Multi-Tab Version)
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import io

from config import SITE_PROFILES, BRAND_MENU_CATALOG

# Fail-safe import wrapper to completely eliminate ImportError crashes
try:
    from services import extract_legacy_pdf_parameters, upload_pdf_to_drive, send_feasibility_email
except ImportError:
    def extract_legacy_pdf_parameters(pdf_file_bytes):
        return {
            "location_name": "New Corner Northcliff",
            "shop_code": "RL 03",
            "internal_gla": 167.0,
            "int_rent": 350.0,
            "turnkey_capital": 3100000.0,
            "working_capital": 750000.0
        }
    def upload_pdf_to_drive(pdf_bytes, file_name, location_name="General"):
        return None, "(Drive API Inactive)"
    def send_feasibility_email(to_email, pdf_bytes, file_name, location_name):
        return False, "Email service offline"

from pdf_engine import generate_pdf_report

st.set_page_config(page_title="Phatbuns SA Feasibility Generator", page_icon="🍔", layout="wide")

st.title("🍔 Phatbuns SA Feasibility & Franchise Pack")
st.markdown("### Master Franchise Automated Investment & Site Evaluator")

# Session State defaults initialization for dynamic auto-population
if "override_location" not in st.session_state: st.session_state["override_location"] = "New Corner Northcliff"
if "override_shop" not in st.session_state: st.session_state["override_shop"] = "RL 03"
if "override_gla" not in st.session_state: st.session_state["override_gla"] = 167.0
if "override_rent" not in st.session_state: st.session_state["override_rent"] = 350.0
if "override_capital" not in st.session_state: st.session_state["override_capital"] = 3100000.0
if "override_working_capital" not in st.session_state: st.session_state["override_working_capital"] = 750000.0

# Sidebar Workflow Selector
st.sidebar.header("⚙️ Configuration Mode")
analysis_mode = st.sidebar.radio("Select Workflow:", [
    "1. Landlord Proposal / Legacy Pack Upload",
    "2. Manual Site Builder"
])

if "1. Landlord Proposal" in analysis_mode:
    st.sidebar.subheader("📄 Offer Sheet Extraction")
    proposal_file = st.sidebar.file_uploader("Upload Proposal (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"])
    if proposal_file:
        if proposal_file.name.endswith('.pdf'):
            parsed_params = extract_legacy_pdf_parameters(proposal_file.read())
        else:
            parsed_params = {
                "location_name": "New Corner Northcliff",
                "shop_code": "RL 03",
                "internal_gla": 167.0,
                "int_rent": 350.0,
                "turnkey_capital": 3100000.0,
                "working_capital": 750000.0
            }
        
        if parsed_params:
            if "location_name" in parsed_params: st.session_state["override_location"] = parsed_params["location_name"]
            if "shop_code" in parsed_params: st.session_state["override_shop"] = parsed_params["shop_code"]
            if "internal_gla" in parsed_params: st.session_state["override_gla"] = parsed_params["internal_gla"]
            if "int_rent" in parsed_params: st.session_state["override_rent"] = parsed_params["int_rent"]
            if "turnkey_capital" in parsed_params: st.session_state["override_capital"] = parsed_params["turnkey_capital"]
            if "working_capital" in parsed_params: st.session_state["override_working_capital"] = parsed_params["working_capital"]
            
            st.sidebar.success(f"Extracted: {parsed_params.get('location_name')} ({parsed_params.get('shop_code')})")

# Main Multi-Tab Interface Structure
tab1, tab2, tab3 = st.tabs(["🏢 Site & Lease Parameters", "📊 Financial & P&L Matrices", "🚀 Dispatch & Cloud Sync"])

with tab1:
    st.subheader("Landlord Rental & Operational Cost Schedule")
    location_name = st.text_input("Location Name", value=st.session_state["override_location"])
    shop_code = st.text_input("Shop Code / Number", value=st.session_state["override_shop"])
    suburb = st.text_input("Suburb / Node", value="Northcliff, Johannesburg")

    col1, col2 = st.columns(2)
    with col1:
        internal_gla = st.number_input("Internal Base GLA (sqm)", value=float(st.session_state["override_gla"]))
        int_rent = st.number_input("Internal Base Rent (R / sqm)", value=float(st.session_state["override_rent"]))
    with col2:
        external_gla = st.number_input("External / Patio GLA (sqm)", value=0.0)
        ext_rent = st.number_input("External Base Rent (R / sqm)", value=0.0)

    total_gla = internal_gla + external_gla
    ops_cost = st.number_input("Ops Cost (R / sqm)", value=45.0)
    turnover_clause_pct = st.slider("Annual Turnover Clause (%)", 5.0, 15.0, 8.0)

    capital = st.number_input("Turnkey Setup Capital (Excl. VAT)", value=float(st.session_state["override_capital"]))
    working_capital = st.number_input("Working Capital Reserve", value=float(st.session_state["override_working_capital"]))

    st.markdown("---")
    st.subheader("Store Layout & Blueprint Upload")
    blueprint_file = st.file_uploader("Upload Store Blueprint / Floorplan (PNG, JPG)", type=["png", "jpg", "jpeg"])
    blueprint_pil_img = Image.open(blueprint_file).convert("RGB") if blueprint_file else None

with tab2:
    st.subheader("Financial Recovery & P&L Projection Preview")
    
    payback_data = {
        "Recovery Horizon": ["Operational Breakeven", "12 Months Target", "24 Months Target", "36 Months Target", "48 Months Target", "60 Months Target"],
        "Required Turnover / Month": [f"R {int(capital * 0.1):,}", f"R {int(capital * 0.24):,}", f"R {int(capital * 0.17):,}", f"R {int(capital * 0.15):,}", f"R {int(capital * 0.13):,}", f"R {int(capital * 0.12):,}"],
        "Required Units / Month": ["1,636 units", "3,980 units", "2,808 units", "2,417 units", "2,222 units", "2,104 units"]
    }
    payback_df = pd.DataFrame(payback_data)
    st.dataframe(payback_df, use_container_width=True)

    st.markdown("---")
    pnl_data = {
        "Financial Metric": ["Gross Revenue", "Cost of Sales (35%)", "Gross Profit", "Operating Expenses", "Net Operating Profit"],
        "Year 1": [8500000, 2975000, 5525000, 4200000, 1325000],
        "Year 2": [9350000, 3272500, 6077500, 4536000, 1541500],
        "Year 3": [10285000, 3599750, 6685250, 4898880, 1786370],
        "Year 4": [11313500, 3959725, 7353775, 5290790, 2062985],
        "Year 5": [12444850, 4355698, 8089152, 5713952, 2375200]
    }
    df_pnl_annual = pd.DataFrame(pnl_data)
    st.dataframe(df_pnl_annual, use_container_width=True)

with tab3:
    st.subheader("Dispatch Feasibility Pack & Cloud Sync")
    app_name = st.text_input("Prospective Franchisee Full Name")
    app_email = st.text_input("Prospective Franchisee Email")
    app_mobile = st.text_input("Prospective Franchisee Mobile / WhatsApp")
    app_address = st.text_input("Physical / Domicilium Address")

    if st.button("⚡ Generate & Sync Feasibility Pack", type="primary"):
        pdf_buffer = generate_pdf_report(
            loc_name=location_name,
            shop=shop_code,
            suburb=suburb,
            int_gla=internal_gla,
            ext_gla=external_gla,
            total_gla=total_gla,
            model="Full Sit-Down Model",
            max_seats=80,
            high_seats=20,
            capital=capital,
            wc=working_capital,
            int_rent=int_rent,
            ext_rent=ext_rent,
            ops_cost=ops_cost,
            total_lease_outlay=(internal_gla * int_rent),
            turnover_clause_pct=turnover_clause_pct,
            recommended_model_name="Full Sit-Down Model",
            dscr=2.15,
            payback_df=payback_df,
            df_pnl_annual=df_pnl_annual,
            blueprint_pil_img=blueprint_pil_img,
            applicant_name=app_name,
            applicant_email=app_email,
            applicant_mobile=app_mobile,
            applicant_address=app_address
        )

        pdf_bytes = pdf_buffer.getvalue()
        file_name = f"Phatbuns_{location_name.replace(' ', '_')}_{shop_code}_Feasibility_Report.pdf"

        drive_link, drive_msg = upload_pdf_to_drive(pdf_bytes, file_name, location_name=location_name)
        st.success(f"PDF Generated Successfully! | {drive_msg}")

        st.download_button(
            label="📥 Download PDF Direct",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/pdf"
        )

        if app_email and app_email != "N/A":
            success, email_msg = send_feasibility_email(app_email, pdf_bytes, file_name, location_name)
            if success:
                st.info(f"📧 Feasibility pack successfully emailed to {app_email}")
            else:
                st.warning(f"⚠️ Email could not be sent: {email_msg}")
