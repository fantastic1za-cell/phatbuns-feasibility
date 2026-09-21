import math
import os
import shutil
import sqlite3
import urllib.parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import streamlit as st
import pandas as pd

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

# Custom Dark Mode Styling
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
    <div class="brand-subtitle">Commercial Feasibility, Location Intelligence & Onboarding Framework</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE INITIALIZATION (SQLite)
# ==========================================
DB_FILE = "phatbuns_franchisees.db"

def init_db():
    """Creates the local SQLite database and franchisee pipeline table automatically if not present."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS franchisee_pipeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            entity_name TEXT,
            id_or_passport TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile TEXT NOT NULL,
            preferred_site TEXT NOT NULL,
            store_model TEXT NOT NULL,
            capital_available REAL NOT NULL,
            unencumbered_cash_pct REAL NOT NULL,
            admin_fee_paid INTEGER DEFAULT 0,
            ndnca_signed INTEGER DEFAULT 0,
            popia_consent INTEGER DEFAULT 0,
            application_status TEXT DEFAULT 'Initial Inquiry',
            ceo_approval TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_investor_lead(data):
    """Saves a new investor/franchisee application into the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO franchisee_pipeline (
            full_name, entity_name, id_or_passport, email, mobile,
            preferred_site, store_model, capital_available, unencumbered_cash_pct,
            admin_fee_paid, ndnca_signed, popia_consent
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['full_name'], data['entity_name'], data['id_or_passport'],
        data['email'], data['mobile'], data['preferred_site'],
        data['store_model'], data['capital_available'], data['unencumbered_cash_pct'],
        data['admin_fee_paid'], data['ndnca_signed'], data['popia_consent']
    ))
    conn.commit()
    conn.close()

def get_pipeline_dataframe():
    """Retrieves all registered applicants from the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM franchisee_pipeline ORDER BY id DESC", conn)
    conn.close()
    return df

# ==========================================
# PRE-DEFINED RETAIL NODE LOOKUP REGISTRY
# ==========================================
LOCATION_LOOKUP = {
    "Loftus Park, Pretoria": "Arcadia, Pretoria East",
    "The Glen Shopping Centre": "Oakdene, Johannesburg South",
    "Sandton City Shopping Centre": "Sandton Central, Johannesburg",
    "Rosebank Mall": "Rosebank, Johannesburg",
    "Menlyn Park Shopping Centre": "Menlyn, Pretoria East",
    "Mall of Africa": "Waterfall City, Midrand",
    "Clearwater Mall": "Strubensvallei, Roodepoort",
    "Eastgate Shopping Centre": "Bedfordview, Ekurhuleni",
    "Gateway Theatre of Shopping": "Umhlanga, Durban",
    "V&A Waterfront": "Green Point, Cape Town",
    "Custom / Other Site...": ""
}

if "suburb_val" not in st.session_state:
    st.session_state["suburb_val"] = LOCATION_LOOKUP["The Glen Shopping Centre"]

def update_suburb_from_lookup():
    selected_loc = st.session_state.get("selected_location_key")
    if selected_loc in LOCATION_LOOKUP and selected_loc != "Custom / Other Site...":
        st.session_state["suburb_val"] = LOCATION_LOOKUP[selected_loc]

# ==========================================
# STORE MODEL RULES & FINANCIAL DEFAULTS
# ==========================================
STORE_MODELS = {
    "Kiosk Model": {
        "size_range": "20 - 60 sqm",
        "turnkey_capital": 850000.0,
        "working_capital": 250000.0,
        "est_monthly_turnover": 350000.0,
        "foh_pct": 0.20,
    },
    "Express Model": {
        "size_range": "40 - 90 sqm",
        "turnkey_capital": 2500000.0,
        "working_capital": 450000.0,
        "est_monthly_turnover": 650000.0,
        "foh_pct": 0.60,
    },
    "Full Sit-Down Model": {
        "size_range": "100 - 160 sqm",
        "turnkey_capital": 3250000.0,
        "working_capital": 700000.0,
        "est_monthly_turnover": 950000.0,
        "foh_pct": 0.60,
    },
    "Multi-Brand Kitchen Model": {
        "size_range": "100 - 160 sqm",
        "turnkey_capital": 3250000.0,
        "working_capital": 700000.0,
        "est_monthly_turnover": 1100000.0,
        "foh_pct": 0.40,
    },
}

# ==========================================
# NAVIGATION TABS
# ==========================================
tab1, tab2 = st.tabs(["📊 Feasibility Engine", "📋 Investor & Franchisee Registry"])

with tab1:
    # ==========================================
    # SECTION 1: SITE & LEASE SPECIFICATION
    # ==========================================
    st.header("1. Site & Lease Specification")

    col1, col2 = st.columns(2)
    with col1:
        selected_location = st.selectbox(
            "Select Commercial Location",
            options=list(LOCATION_LOOKUP.keys()),
            index=1,
            key="selected_location_key",
            on_change=update_suburb_from_lookup
        )
        
        if selected_location == "Custom / Other Site...":
            location_name = st.text_input("Enter Custom Location Name", value="Loftus Park, Pretoria")
        else:
            location_name = selected_location

    with col2:
        shop_code = st.text_input("Shop / Unit Code", value="Shop C01")

    col_suburb, col_dummy = st.columns(2)
    with col_suburb:
        suburb_node = st.text_input("Suburb / Node (Auto-Populated)", key="suburb_val")

    # Internal vs. External Space Allocation
    st.subheader("Space Allocation (GLA Breakdown)")
    col_int_gla, col_ext_gla = st.columns(2)
    with col_int_gla:
        internal_gla = st.number_input("Internal Area (sqm)", value=100.0, step=5.0)
    with col_ext_gla:
        external_gla = st.number_input("External / Patio Area (sqm)", value=20.0, step=5.0)

    total_gla = internal_gla + external_gla
    st.caption(f"📐 **Total Combined Store Footprint:** {total_gla:.1f} sqm ({internal_gla:.1f} sqm Internal + {external_gla:.1f} sqm External)")

    st.divider()

    # Store Model Selection
    st.subheader("Store Model Type")
    selected_model = st.radio(
        "Select Model Type",
        options=list(STORE_MODELS.keys()),
        index=3,
        horizontal=True
    )

    model_data = STORE_MODELS.get(selected_model, STORE_MODELS["Multi-Brand Kitchen Model"])

    # Seating Capacity Engine
    internal_foh_sqm = internal_gla * model_data["foh_pct"]
    total_dining_sqm = internal_foh_sqm + external_gla
    max_comfortable_seats = math.floor(total_dining_sqm / 1.40) if total_dining_sqm > 0 else 0
    high_density_seats = math.floor(total_dining_sqm / 1.20) if total_dining_sqm > 0 else 0

    st.info(
        f"📐 **Recommended Size Range:** {model_data['size_range']} | "
        f"🪑 **Est. Total Dining Footprint:** {total_dining_sqm:.1f} sqm ({internal_foh_sqm:.1f} sqm Internal FOH + {external_gla:.1f} sqm External) | "
        f"🪑 **Suggested Seating Capacity:** {max_comfortable_seats} Seats (Standard) / {high_density_seats} Seats (High Density)"
    )

    st.divider()

    # ==========================================
    # SECTION 2: COMMERCIAL CAPITAL & EXPENSES
    # ==========================================
    st.subheader("2. Commercial Capital & Lease Setup")

    col_cap, col_wc = st.columns(2)
    with col_cap:
        turnkey_capital = st.number_input(
            "Total Turnkey Capital (Excl. VAT)",
            value=model_data["turnkey_capital"],
            step=50000.0,
            format="%.2f"
        )
    with col_wc:
        working_capital = st.number_input(
            "Suggested Working Capital Requirement",
            value=model_data["working_capital"],
            step=25000.0,
            format="%.2f"
        )

    # Internal vs. External Rental Rates Per SQM
    st.subheader("Rental Structure (Per SQM)")
    col_int_rent, col_ext_rent = st.columns(2)
    with col_int_rent:
        internal_rent_sqm = st.number_input("Internal Base Rent (R / sqm / month)", value=350.0, step=10.0, format="%.2f")
        total_internal_rent = internal_gla * internal_rent_sqm
        st.caption(f"💵 **Total Monthly Internal Rent:** R {total_internal_rent:,.2f} (Excl. VAT)")

    with col_ext_rent:
        external_rent_sqm = st.number_input("External Base Rent (R / sqm / month)", value=175.0, step=10.0, format="%.2f")
        total_external_rent = external_gla * external_rent_sqm
        st.caption(f"💵 **Total Monthly External Rent:** R {total_external_rent:,.2f} (Excl. VAT)")

    base_rent_monthly = total_internal_rent + total_external_rent
    blended_rate_sqm = base_rent_monthly / total_gla if total_gla > 0 else 0

    st.success(f"📊 **Combined Base Monthly Rent:** R {base_rent_monthly:,.2f} (Excl. VAT) | **Blended Average Rate:** R {blended_rate_sqm:,.2f} / sqm")

    col_esc, col_cogs = st.columns(2)
    with col_esc:
        annual_escalation_pct = st.number_input("Annual Lease Escalation (%)", value=7.0, step=0.5)
    with col_cogs:
        projected_monthly_turnover = st.number_input("Projected Monthly Turnover", value=model_data["est_monthly_turnover"], step=25000.0, format="%.2f")
        cogs_pct = st.number_input("COGS + Direct Operational Costs (%)", value=59.0, step=1.0)

    st.warning(
        "**Commercial Terms & Ongoing Obligations:**\n"
        "* **Royalty & Marketing Fees:** 6% Monthly Franchise Fee + 3% Monthly Marketing Fee (Total 9% of Turnover).\n"
        "* **Exclusions:** VAT, Working Capital, and Landlord Rental Deposits.\n"
        "* **Inclusions:** Franchise Fee, architectural submission plans, and turnkey fitout.\n"
        "* **Franchise Term:** 5-Year Agreement term with mandatory complete store refresh every 5 years.\n"
        "* **SANHA Compliance:** Strict adherence to SANHA certification, supply chain, and kitchen audits."
    )

    st.divider()

    # ==========================================
    # SECTION 3: ADDENDUM - 60-MONTH CASH FLOW & PAYBACK
    # ==========================================
    st.header("3. Addendum: 60-Month Cash Flow & Payback Model")

    total_initial_investment = turnkey_capital + working_capital
    months = list(range(1, 61))
    cash_flow_data = []

    cumulative_cash_flow = -total_initial_investment
    break_even_month = None

    for m in months:
        year_idx = (m - 1) // 12
        current_monthly_rent = base_rent_monthly * ((1 + (annual_escalation_pct / 100)) ** year_idx)
        
        royalty_marketing_fee = projected_monthly_turnover * 0.09
        monthly_cogs = projected_monthly_turnover * (cogs_pct / 100)
        total_monthly_expenses = current_monthly_rent + monthly_cogs + royalty_marketing_fee
        net_monthly_profit = projected_monthly_turnover - total_monthly_expenses
        
        cumulative_cash_flow += net_monthly_profit
        
        if cumulative_cash_flow >= 0 and break_even_month is None:
            break_even_month = m
            
        cash_flow_data.append({
            "Month": m,
            "Year": year_idx + 1,
            "Turnover": projected_monthly_turnover,
            "Rent Expense": current_monthly_rent,
            "COGS & Ops": monthly_cogs,
            "Royalties (9%)": royalty_marketing_fee,
            "Total Expenses": total_monthly_expenses,
            "Net Profit": net_monthly_profit,
            "Cumulative Cash Flow": cumulative_cash_flow
        })

    df_cashflow = pd.DataFrame(cash_flow_data)

    # KPI Summary Cards
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.metric("Total Initial Capital Outlay", f"R {total_initial_investment:,.2f}")
    with kpi_col2:
        contribution_margin_pct = 1 - (cogs_pct / 100) - 0.09
        op_breakeven_turnover = base_rent_monthly / contribution_margin_pct if contribution_margin_pct > 0 else 0
        st.metric("Monthly Op Break-Even Sales", f"R {op_breakeven_turnover:,.2f}")
    with kpi_col3:
        payback_text = f"Month {break_even_month}" if break_even_month else "Beyond 60 Months"
        st.metric("Full Capital Payback", payback_text)

    # Annual Overview
    st.subheader("5-Year Annual Feasibility Overview")
    df_cashflow['Year_Label'] = "Year " + df_cashflow['Year'].astype(str)
    annual_summary = df_cashflow.groupby('Year_Label').agg({
        'Turnover': 'sum',
        'Rent Expense': 'sum',
        'Royalties (9%)': 'sum',
        'Total Expenses': 'sum',
        'Net Profit': 'sum'
    }).reset_index()

    st.dataframe(
        annual_summary.style.format({
            'Turnover': 'R {:,.2f}',
            'Rent Expense': 'R {:,.2f}',
            'Royalties (9%)': 'R {:,.2f}',
            'Total Expenses': 'R {:,.2f}',
            'Net Profit': 'R {:,.2f}'
        }),
        use_container_width=True
    )

    st.divider()

    # ==========================================
    # SECTION 4: GOVERNANCE & APPROVAL CHECKLIST
    # ==========================================
    st.header("4. Application & Governance Sign-Off Workflow")

    st.markdown("""
    **Application & Onboarding Pre-Requisites:**
    1. **Admin Processing Fee:** R2,000.00 (Excl. VAT) non-refundable application fee.
    2. **Equity Verification:** 3–6 months bank statements proving $\ge$ 50% unencumbered cash.
    3. **Legal Consents:** Signed Non-Disclosure & Non-Circumvention Agreement (NDNCA) and POPIA/NCA credit vetting consent.
    4. **Interviews & Training:** Mandatory in-person franchisee interview and 4–6 week intensive staff training.
    5. **Final Approval:** All franchise approvals are strictly subject to final written sign-off by the **CEO of Phatbuns South Africa**. The CEO's decision is final.
    """)

with tab2:
    # ==========================================
    # INVESTOR REGISTRATION & CEO PIPELINE
    # ==========================================
    st.header("Franchisee & Investor Lead Intake")
    st.markdown("Enter prospective franchisee details below to store them directly in the Phatbuns applicant database.")

    with st.form("investor_registration_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            full_name = st.text_input("Full Name *", value="")
            entity_name = st.text_input("Entity / Company Name", value="")
            id_or_passport = st.text_input("ID or Passport Number *", value="")
            email = st.text_input("Email Address *", value="")
        with f_col2:
            mobile = st.text_input("Mobile Number *", value="")
            preferred_site = st.text_input("Preferred Target Site / Node *", value=location_name)
            store_model_choice = st.selectbox("Preferred Store Model", options=list(STORE_MODELS.keys()))
            capital_available = st.number_input("Proposed Total Capital Available (ZAR)", value=2500000.0, step=100000.0)

        unencumbered_cash_pct = st.slider("Verified Unencumbered Cash (%)", min_value=0.0, max_value=100.0, value=50.0)
        
        c_col1, c_col2, c_col3 = st.columns(3)
        with c_col1:
            admin_fee_paid = st.checkbox("Admin Fee Paid (R2,000 Excl. VAT)")
        with c_col2:
            ndnca_signed = st.checkbox("Signed NDNCA Received")
        with c_col3:
            popia_consent = st.checkbox("POPIA / NCA Consent Received")

        submitted = st.form_submit_button("Submit Application to Database")
        
        if submitted:
            if not full_name or not email or not mobile or not id_or_passport or not preferred_site:
                st.error("Please fill in all mandatory fields (*).")
            else:
                applicant_data = {
                    "full_name": full_name,
                    "entity_name": entity_name,
                    "id_or_passport": id_or_passport,
                    "email": email,
                    "mobile": mobile,
                    "preferred_site": preferred_site,
                    "store_model": store_model_choice,
                    "capital_available": capital_available,
                    "unencumbered_cash_pct": unencumbered_cash_pct,
                    "admin_fee_paid": 1 if admin_fee_paid else 0,
                    "ndnca_signed": 1 if ndnca_signed else 0,
                    "popia_consent": 1 if popia_consent else 0
                }
                save_investor_lead(applicant_data)
                st.success(f"Applicant record for **{full_name}** successfully logged in the database!")

    st.divider()

    # CEO Pipeline Database Display
    st.subheader("CEO Pipeline & Vetting Database")
    df_pipeline = get_pipeline_dataframe()
    if not df_pipeline.empty:
        st.dataframe(df_pipeline, use_container_width=True)
    else:
        st.info("No franchisee applications currently recorded in the database.")

st.divider()

# ==========================================
# MASTER RIGHTS HOLDER CONTACT FOOTER
# ==========================================
st.subheader("Master Rights Holder Contact Information")
st.markdown("""
**Master Rights Holder – South Africa**  
📧 **Email:** [nisaar@fantastic1.com](mailto:nisaar@fantastic1.com) | [fantastic1za@gmail.com](mailto:fantastic1za@gmail.com)  
💬 **WhatsApp:** [+27 82 786 7712](https://wa.me/27827867712)  
📲 **Mobile:** [+27 68 710 1939](tel:+27687101939) | [+27 68 727 4731](tel:+27687274731)  
""")
