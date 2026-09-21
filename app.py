import math
import os
import io
import re
import sqlite3
import streamlit as st
import pandas as pd
from PIL import Image

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

st.markdown("""
<div class="brand-banner">
    <div class="brand-title">PHATBUNS SOUTH AFRICA</div>
    <div class="brand-subtitle">Bankable Commercial Feasibility, Financial Modeling & Automated Lease Extraction</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE INITIALIZATION (SQLite)
# ==========================================
DB_FILE = "phatbuns_franchisees.db"

def init_db():
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

# Default session state initialization
if "ext_shop_code" not in st.session_state:
    st.session_state["ext_shop_code"] = "Shop C01"
if "ext_internal_gla" not in st.session_state:
    st.session_state["ext_internal_gla"] = 202.91
if "ext_external_gla" not in st.session_state:
    st.session_state["ext_external_gla"] = 138.99
if "ext_internal_rent" not in st.session_state:
    st.session_state["ext_internal_rent"] = 270.00
if "ext_external_rent" not in st.session_state:
    st.session_state["ext_external_rent"] = 80.00
if "ext_ops_cost" not in st.session_state:
    st.session_state["ext_ops_cost"] = 40.00
if "ext_rates_taxes" not in st.session_state:
    st.session_state["ext_rates_taxes"] = 24.50
if "ext_generator" not in st.session_state:
    st.session_state["ext_generator"] = 8.00
if "ext_escalation" not in st.session_state:
    st.session_state["ext_escalation"] = 7.00
if "ext_mktg" not in st.session_state:
    st.session_state["ext_mktg"] = 5.00

# Text Parsing Fallback Engine
def parse_landlord_text(text):
    data = {}
    
    shop_m = re.search(r'Shop:\s*([A-Za-z0-9\s]+)', text, re.IGNORECASE)
    if shop_m: data['shop_code'] = shop_m.group(1).strip()
    
    int_area_m = re.search(r'Internal\s*Area:\s*([\d\.]+)\s*sqm', text, re.IGNORECASE)
    if int_area_m: data['internal_gla'] = float(int_area_m.group(1))
    
    ext_area_m = re.search(r'(?:Outside|External)\s*Area:\s*([\d\.]+)\s*sqm', text, re.IGNORECASE)
    if ext_area_m: data['external_gla'] = float(ext_area_m.group(1))
    
    int_rent_m = re.search(r'Rental\s*internal:\s*R?([\d\.]+)', text, re.IGNORECASE)
    if int_rent_m: data['internal_rent'] = float(int_rent_m.group(1))
    
    ext_rent_m = re.search(r'Rental\s*(?:outside|external):\s*R?([\d\.]+)', text, re.IGNORECASE)
    if ext_rent_m: data['external_rent'] = float(ext_rent_m.group(1))
    
    ops_m = re.search(r'Ops\s*Cost:\s*R?([\d\.]+)', text, re.IGNORECASE)
    if ops_m: data['ops_cost'] = float(ops_m.group(1))
    
    rates_m = re.search(r'Rates\s*&\s*taxes:\s*R?([\d\.]+)', text, re.IGNORECASE)
    if rates_m: data['rates_taxes'] = float(rates_m.group(1))
    
    gen_m = re.search(r'Generator\s*cost:\s*R?([\d\.]+)', text, re.IGNORECASE)
    if gen_m: data['generator'] = float(gen_m.group(1))
    
    esc_m = re.search(r'Escalation:\s*([\d\.]+)%', text, re.IGNORECASE)
    if esc_m: data['escalation'] = float(esc_m.group(1))
    
    mktg_m = re.search(r'Marketing:\s*([\d\.]+)\s*%', text, re.IGNORECASE)
    if mktg_m: data['mktg'] = float(mktg_m.group(1))
    
    return data

# ==========================================
# STORE MODEL RULES & FINANCIAL DEFAULTS
# ==========================================
STORE_MODELS = {
    "Kiosk Model": {"size_range": "20 - 60 sqm", "turnkey_capital": 850000.0, "working_capital": 250000.0, "est_monthly_turnover": 350000.0, "labor_monthly": 45000.0, "foh_pct": 0.20},
    "Express Model": {"size_range": "40 - 90 sqm", "turnkey_capital": 2500000.0, "working_capital": 450000.0, "est_monthly_turnover": 650000.0, "labor_monthly": 85000.0, "foh_pct": 0.60},
    "Full Sit-Down Model": {"size_range": "100 - 160 sqm", "turnkey_capital": 3250000.0, "working_capital": 700000.0, "est_monthly_turnover": 950000.0, "labor_monthly": 125000.0, "foh_pct": 0.60},
    "Multi-Brand Kitchen Model": {"size_range": "100 - 160 sqm", "turnkey_capital": 3250000.0, "working_capital": 700000.0, "est_monthly_turnover": 1100000.0, "labor_monthly": 135000.0, "foh_pct": 0.40},
}

SEASONAL_FACTORS = [0.90, 1.00, 1.00, 1.15, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.05, 1.25]

# ==========================================
# REPORTLAB PDF GENERATION FUNCTIONS
# ==========================================
def generate_pdf_report(loc_name, shop, suburb, int_gla, ext_gla, total_gla, model, max_seats, high_seats, capital, wc, total_inv, total_lease_outlay, m12_rev, m24_rev, m36_rev, m60_rev, payback, dscr):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#111111'), leading=22, alignment=1)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#555555'), leading=14, alignment=1)
    section_heading = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#8B0000'), leading=15, spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor('#222222'))

    elements = []

    elements.append(Paragraph("PHATBUNS SOUTH AFRICA", title_style))
    elements.append(Paragraph("Bankable Feasibility & Financial Assessment Pack", subtitle_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#8B0000'), spaceBefore=2, spaceAfter=10))

    elements.append(Paragraph("1. Site & Space Specification", section_heading))
    site_data = [
        [Paragraph("<b>Location Name:</b>", body_style), Paragraph(str(loc_name), body_style), Paragraph("<b>Shop Code:</b>", body_style), Paragraph(str(shop), body_style)],
        [Paragraph("<b>Suburb / Node:</b>", body_style), Paragraph(str(suburb), body_style), Paragraph("<b>Store Model:</b>", body_style), Paragraph(str(model), body_style)],
        [Paragraph("<b>Internal GLA:</b>", body_style), Paragraph(f"{int_gla:.2f} sqm", body_style), Paragraph("<b>External Area:</b>", body_style), Paragraph(f"{ext_gla:.2f} sqm", body_style)],
        [Paragraph("<b>Total Footprint:</b>", body_style), Paragraph(f"{total_gla:.2f} sqm", body_style), Paragraph("<b>Seating Capacity:</b>", body_style), Paragraph(f"{max_seats} Std / {high_seats} Dense", body_style)]
    ]
    t_site = Table(site_data, colWidths=[110, 150, 110, 150])
    t_site.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F9F9F9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_site)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("2. Financial Outlay & Debt Serviceability", section_heading))
    fin_data = [
        [Paragraph("<b>Total Turnkey Capital:</b>", body_style), Paragraph(f"R {capital:,.2f}", body_style)],
        [Paragraph("<b>Working Capital Reserve:</b>", body_style), Paragraph(f"R {wc:,.2f}", body_style)],
        [Paragraph("<b>Total Initial Capital Required:</b>", body_style), Paragraph(f"R {total_inv:,.2f}", body_style)],
        [Paragraph("<b>50% Unencumbered Cash Equity:</b>", body_style), Paragraph(f"R {total_inv * 0.5:,.2f}", body_style)],
        [Paragraph("<b>50% Debt Financing Balance:</b>", body_style), Paragraph(f"R {total_inv * 0.5:,.2f}", body_style)],
        [Paragraph("<b>Total Monthly Lease Outlay:</b>", body_style), Paragraph(f"R {total_lease_outlay:,.2f}", body_style)],
        [Paragraph("<b>Bank Debt Service Coverage Ratio (DSCR):</b>", body_style), Paragraph(f"<b>{dscr:.2f}x</b> (Required > 1.30x)", body_style)],
        [Paragraph("<b>Full Capital Recovery Period:</b>", body_style), Paragraph(str(payback), body_style)],
    ]
    t_fin = Table(fin_data, colWidths=[230, 290])
    t_fin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_fin)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("3. Target Turnover & Sales Horizons", section_heading))
    rev_data = [
        [Paragraph("<b>Milestone</b>", body_style), Paragraph("<b>Monthly Revenue Target</b>", body_style), Paragraph("<b>Daily Unit Sales (AOV R150)</b>", body_style)],
        [Paragraph("Month 12 Target", body_style), Paragraph(f"R {m12_rev:,.2f}", body_style), Paragraph(f"{int(m12_rev / 30 / 150)} tickets/day", body_style)],
        [Paragraph("Month 24 Target", body_style), Paragraph(f"R {m24_rev:,.2f}", body_style), Paragraph(f"{int(m24_rev / 30 / 150)} tickets/day", body_style)],
        [Paragraph("Month 36 Target", body_style), Paragraph(f"R {m36_rev:,.2f}", body_style), Paragraph(f"{int(m36_rev / 30 / 150)} tickets/day", body_style)],
        [Paragraph("Month 60 Target", body_style), Paragraph(f"R {m60_rev:,.2f}", body_style), Paragraph(f"{int(m60_rev / 30 / 150)} tickets/day", body_style)],
    ]
    t_rev = Table(rev_data, colWidths=[150, 185, 185])
    t_rev.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EFEFEF')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_rev)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("4. Governance & Executive Sign-Off", section_heading))
    gov_text = """
    <b>Pre-Requisites:</b> R2,000 (Excl. VAT) admin fee; proof of 50% unencumbered cash; SANHA Halaal compliance; 4-6 week operational staff training; final binding CEO sign-off.
    """
    elements.append(Paragraph(gov_text, body_style))
    elements.append(Spacer(1, 15))

    sig_data = [
        [Paragraph("<b>Franchise Manager Signature:</b> ____________________", body_style), Paragraph("<b>CEO Signature:</b> Nisaar Ally", body_style)],
        [Paragraph("<b>Date:</b> ____ / ____ / ________", body_style), Paragraph("<b>Date:</b> ____ / ____ / ________", body_style)]
    ]
    t_sig = Table(sig_data, colWidths=[260, 260])
    t_sig.setStyle(TableStyle([('PADDING', (0,0), (-1,-1), 6)]))
    elements.append(t_sig)

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_pipeline_pdf(df_pipeline):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=25, leftMargin=25, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.HexColor('#111111'), leading=20, alignment=1)
    section_heading = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#8B0000'), leading=14, spaceBefore=10, spaceAfter=5)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#222222'))

    elements = []
    elements.append(Paragraph("PHATBUNS SOUTH AFRICA", title_style))
    elements.append(Paragraph("Franchisee & Investor Pipeline Audit Report", section_heading))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#8B0000'), spaceBefore=5, spaceAfter=10))

    if not df_pipeline.empty:
        table_data = [[
            Paragraph("<b>ID</b>", body_style), Paragraph("<b>Applicant</b>", body_style),
            Paragraph("<b>Preferred Site</b>", body_style), Paragraph("<b>Model</b>", body_style),
            Paragraph("<b>Capital Available</b>", body_style), Paragraph("<b>Cash Equity %</b>", body_style),
            Paragraph("<b>CEO Status</b>", body_style)
        ]]
        for index, row in df_pipeline.iterrows():
            table_data.append([
                Paragraph(str(row['id']), body_style),
                Paragraph(f"{row['full_name']}<br/>{row['mobile']}", body_style),
                Paragraph(str(row['preferred_site']), body_style),
                Paragraph(str(row['store_model']), body_style),
                Paragraph(f"R {row['capital_available']:,.2f}", body_style),
                Paragraph(f"{row['unencumbered_cash_pct']:.0f}%", body_style),
                Paragraph(str(row['ceo_approval']), body_style)
            ])

        t_pipe = Table(table_data, colWidths=[25, 100, 110, 85, 90, 65, 65])
        t_pipe.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EFEFEF')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t_pipe)
    else:
        elements.append(Paragraph("No applicant records available in database.", body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ==========================================
# NAVIGATION TABS
# ==========================================
tab1, tab2 = st.tabs(["📊 Feasibility & Bank Model", "📋 Investor & Franchisee Registry"])

with tab1:
    st.header("Automated Landlord Proposal Extractor")
    st.markdown("Paste or upload a landlord offer screenshot/text below to auto-populate the site metrics.")

    col_up1, col_up2 = st.columns([1, 1])
    with col_up1:
        uploaded_img = st.file_uploader("Upload Offer Screenshot (PNG/JPG)", type=["png", "jpg", "jpeg"])
    with col_up2:
        pasted_text = st.text_area("Or Paste Email / Whatsapp Offer Text Directly", height=100, placeholder="Paste landlord offer text here...")

    if st.button("⚡ Extract & Pre-Fill Lease Terms"):
        if pasted_text:
            parsed_res = parse_landlord_text(pasted_text)
            if 'shop_code' in parsed_res: st.session_state["ext_shop_code"] = parsed_res['shop_code']
            if 'internal_gla' in parsed_res: st.session_state["ext_internal_gla"] = parsed_res['internal_gla']
            if 'external_gla' in parsed_res: st.session_state["ext_external_gla"] = parsed_res['external_gla']
            if 'internal_rent' in parsed_res: st.session_state["ext_internal_rent"] = parsed_res['internal_rent']
            if 'external_rent' in parsed_res: st.session_state["ext_external_rent"] = parsed_res['external_rent']
            if 'ops_cost' in parsed_res: st.session_state["ext_ops_cost"] = parsed_res['ops_cost']
            if 'rates_taxes' in parsed_res: st.session_state["ext_rates_taxes"] = parsed_res['rates_taxes']
            if 'generator' in parsed_res: st.session_state["ext_generator"] = parsed_res['generator']
            if 'escalation' in parsed_res: st.session_state["ext_escalation"] = parsed_res['escalation']
            if 'mktg' in parsed_res: st.session_state["ext_mktg"] = parsed_res['mktg']
            st.success("Lease terms successfully extracted and populated below!")
        else:
            st.info("Paste email text or select screenshot to extract.")

    st.divider()

    st.header("1. Site & Lease Specification")

    col1, col2 = st.columns(2)
    with col1:
        selected_location = st.selectbox("Select Commercial Location", options=list(LOCATION_LOOKUP.keys()), index=0)
        location_name = st.text_input("Enter Custom Location Name", value="Loftus Park, Pretoria") if selected_location == "Custom / Other Site..." else selected_location

    with col2:
        shop_code = st.text_input("Shop / Unit Code", value=st.session_state["ext_shop_code"])

    col_suburb, col_dummy = st.columns(2)
    with col_suburb:
        suburb_node = st.text_input("Suburb / Node (Auto-Populated)", value=LOCATION_LOOKUP.get(selected_location, ""))

    st.subheader("Space Allocation (GLA Breakdown)")
    col_int_gla, col_ext_gla = st.columns(2)
    with col_int_gla:
        internal_gla = st.number_input("Internal Area (sqm)", value=st.session_state["ext_internal_gla"], step=5.0)
    with col_ext_gla:
        external_gla = st.number_input("External / Patio Area (sqm)", value=st.session_state["ext_external_gla"], step=5.0)

    total_gla = internal_gla + external_gla
    st.caption(f"📐 **Total Combined Store Footprint:** {total_gla:.2f} sqm ({internal_gla:.2f} sqm Internal + {external_gla:.2f} sqm External)")

    st.divider()

    st.subheader("Store Model Type")
    selected_model = st.radio("Select Model Type", options=list(STORE_MODELS.keys()), index=3, horizontal=True)
    model_data = STORE_MODELS.get(selected_model, STORE_MODELS["Multi-Brand Kitchen Model"])

    internal_foh_sqm = internal_gla * model_data["foh_pct"]
    total_dining_sqm = internal_foh_sqm + external_gla
    max_comfortable_seats = math.floor(total_dining_sqm / 1.40) if total_dining_sqm > 0 else 0
    high_density_seats = math.floor(total_dining_sqm / 1.20) if total_dining_sqm > 0 else 0

    st.info(f"📐 **Recommended Size:** {model_data['size_range']} | 🪑 **Est. Total Dining Footprint:** {total_dining_sqm:.2f} sqm | 🪑 **Suggested Seating:** {max_comfortable_seats} Seats (Standard) / {high_density_seats} Seats (High Density)")

    st.divider()

    st.subheader("2. Commercial Capital, Lease & Operational Cost Breakdown")

    col_cap, col_wc = st.columns(2)
    with col_cap:
        turnkey_capital = st.number_input("Total Turnkey Capital (Excl. VAT)", value=model_data["turnkey_capital"], step=50000.0, format="%.2f")
    with col_wc:
        working_capital = st.number_input("Suggested Working Capital Requirement", value=model_data["working_capital"], step=25000.0, format="%.2f")

    st.subheader("Landlord Lease Breakdown (Per SQM)")
    col_int_rent, col_ext_rent = st.columns(2)
    with col_int_rent:
        internal_rent_sqm = st.number_input("Internal Base Rent (R / sqm / month)", value=st.session_state["ext_internal_rent"], step=10.0, format="%.2f")
        total_internal_rent = internal_gla * internal_rent_sqm
        st.caption(f"💵 **Total Monthly Internal Rent:** R {total_internal_rent:,.2f} (Excl. VAT)")

    with col_ext_rent:
        external_rent_sqm = st.number_input("External Base Rent (R / sqm / month)", value=st.session_state["ext_external_rent"], step=5.0, format="%.2f")
        total_external_rent = external_gla * external_rent_sqm
        st.caption(f"💵 **Total Monthly External Rent:** R {total_external_rent:,.2f} (Excl. VAT)")

    total_base_rent_monthly = total_internal_rent + total_external_rent

    col_ops, col_rates, col_gen = st.columns(3)
    with col_ops:
        ops_cost_sqm = st.number_input("Ops Cost (R / sqm)", value=st.session_state["ext_ops_cost"], step=1.0, format="%.2f")
        total_ops_cost = ops_cost_sqm * total_gla
    with col_rates:
        rates_taxes_sqm = st.number_input("Rates & Taxes (R / sqm)", value=st.session_state["ext_rates_taxes"], step=0.5, format="%.2f")
        total_rates_taxes = rates_taxes_sqm * total_gla
    with col_gen:
        generator_cost_sqm = st.number_input("Generator Cost (R / sqm)", value=st.session_state["ext_generator"], step=0.5, format="%.2f")
        total_generator_cost = generator_cost_sqm * total_gla

    col_mktg_pct, col_labor = st.columns(2)
    with col_mktg_pct:
        landlord_marketing_pct = st.number_input("Landlord Marketing (% of Basic Rent)", value=st.session_state["ext_mktg"], step=0.5, format="%.2f")
        total_landlord_marketing = total_base_rent_monthly * (landlord_marketing_pct / 100.0)
    with col_labor:
        monthly_labor_cost = st.number_input("Monthly Store Staffing / Payroll (ZAR)", value=model_data["labor_monthly"], step=5000.0, format="%.2f")

    total_lease_outlay_monthly = total_base_rent_monthly + total_ops_cost + total_rates_taxes + total_generator_cost + total_landlord_marketing
    st.warning(f"🏬 **Total Monthly Landlord Lease Outlay:** R {total_lease_outlay_monthly:,.2f} (Excl. VAT)")

    st.divider()

    st.header("3. Required Turnover & Unit Sales Matrix (AOV = R150)")
    base_turnover_input = st.number_input("Initial Year 1 Baseline Turnover (Monthly Average ZAR)", value=model_data["est_monthly_turnover"], step=25000.0, format="%.2f")
    aov_val = 150.0

    cogs_food_pct = 0.33
    royalty_mktg_pct = 0.09

    fixed_monthly_costs = total_lease_outlay_monthly + monthly_labor_cost
    contribution_margin = 1.0 - cogs_food_pct - royalty_mktg_pct
    op_breakeven_turnover = fixed_monthly_costs / contribution_margin if contribution_margin > 0 else 0
    breakeven_daily_tickets = math.ceil(op_breakeven_turnover / 30 / aov_val)

    turnover_m12 = base_turnover_input
    turnover_m24 = base_turnover_input * (1.08 ** 1)
    turnover_m36 = base_turnover_input * (1.08 ** 2)
    turnover_m60 = base_turnover_input * (1.08 ** 4)

    df_matrix = pd.DataFrame({
        "Horizon": ["Op Break-Even", "Month 12 Target", "Month 24 Target", "Month 36 Target", "Month 60 Target"],
        "Monthly Turnover Target": [op_breakeven_turnover, turnover_m12, turnover_m24, turnover_m36, turnover_m60],
        "Monthly Ticket Volume": [op_breakeven_turnover / aov_val, turnover_m12 / aov_val, turnover_m24 / aov_val, turnover_m36 / aov_val, turnover_m60 / aov_val],
        "Required Daily Tickets (30 Days)": [breakeven_daily_tickets, math.ceil(turnover_m12 / 30 / aov_val), math.ceil(turnover_m24 / 30 / aov_val), math.ceil(turnover_m36 / 30 / aov_val), math.ceil(turnover_m60 / 30 / aov_val)]
    })
    st.dataframe(df_matrix.style.format({"Monthly Turnover Target": "R {:,.2f}", "Monthly Ticket Volume": "{:,.0f}", "Required Daily Tickets (30 Days)": "{:,.0f}"}), use_container_width=True)

    st.divider()

    st.header("4. Financial Statements & 60-Month Forecast (Addendum)")

    total_initial_investment = turnkey_capital + working_capital
    debt_portion = total_initial_investment * 0.50
    equity_portion = total_initial_investment * 0.50

    monthly_interest_rate = (0.1175) / 12
    monthly_loan_payment = debt_portion * (monthly_interest_rate * (1 + monthly_interest_rate)**60) / ((1 + monthly_interest_rate)**60 - 1)

    months = list(range(1, 61))
    cash_flow_data = []

    cumulative_cash_flow = -total_initial_investment
    break_even_month = None

    for m in months:
        year_idx = (m - 1) // 12
        season_multiplier = SEASONAL_FACTORS[(m - 1) % 12]
        
        monthly_turnover = (base_turnover_input * (1.08 ** year_idx)) * season_multiplier
        monthly_lease = total_lease_outlay_monthly * (st.session_state["ext_escalation"] / 100 + 1) ** year_idx
        monthly_cogs = monthly_turnover * cogs_food_pct
        monthly_royalties = monthly_turnover * royalty_mktg_pct
        
        total_monthly_expenses = monthly_lease + monthly_cogs + monthly_royalties + monthly_labor_cost
        ebitda = monthly_turnover - total_monthly_expenses
        net_profit = ebitda - monthly_loan_payment
        
        cumulative_cash_flow += net_profit
        if cumulative_cash_flow >= 0 and break_even_month is None: break_even_month = m
            
        cash_flow_data.append({"Month": m, "Year": year_idx + 1, "Turnover": monthly_turnover, "Lease Outlay": monthly_lease, "COGS (33%)": monthly_cogs, "Labor": monthly_labor_cost, "Royalties (9%)": monthly_royalties, "Total Expenses": total_monthly_expenses, "EBITDA": ebitda, "Bank Repayment": monthly_loan_payment, "Net Operating Profit": net_profit, "Cumulative Cash Flow": cumulative_cash_flow})

    df_cashflow = pd.DataFrame(cash_flow_data)

    year_1_ebitda_avg = df_cashflow[df_cashflow['Year'] == 1]['EBITDA'].mean()
    dscr_metric = year_1_ebitda_avg / monthly_loan_payment if monthly_loan_payment > 0 else 0

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1: st.metric("Total Investment Required", f"R {total_initial_investment:,.2f}")
    with kpi_col2: st.metric("50% Unencumbered Cash Equity", f"R {equity_portion:,.2f}")
    with kpi_col3: st.metric("Capital Recovery Horizon", f"Month {break_even_month}" if break_even_month else "Beyond 60 Months")
    with kpi_col4: st.metric("Bank DSCR Serviceability", f"{dscr_metric:.2f}x", delta="Bank Approved" if dscr_metric >= 1.30 else "Under Constraint")

    st.subheader("5-Year Pro Forma Income Statement (P&L)")
    df_cashflow['Year_Label'] = "Year " + df_cashflow['Year'].astype(str)
    annual_pnl = df_cashflow.groupby('Year_Label').agg({'Turnover': 'sum', 'Lease Outlay': 'sum', 'COGS (33%)': 'sum', 'Labor': 'sum', 'Royalties (9%)': 'sum', 'EBITDA': 'sum', 'Bank Repayment': 'sum', 'Net Operating Profit': 'sum'}).reset_index()

    st.dataframe(annual_pnl.style.format({'Turnover': 'R {:,.2f}', 'Lease Outlay': 'R {:,.2f}', 'COGS (33%)': 'R {:,.2f}', 'Labor': 'R {:,.2f}', 'Royalties (9%)': 'R {:,.2f}', 'EBITDA': 'R {:,.2f}', 'Bank Repayment': 'R {:,.2f}', 'Net Operating Profit': 'R {:,.2f}'}), use_container_width=True)

    st.divider()

    st.header("5. Generate & Download Official PDF Pack")
    pdf_file = generate_pdf_report(location_name, shop_code, suburb_node, internal_gla, external_gla, total_gla, selected_model, max_comfortable_seats, high_density_seats, turnkey_capital, working_capital, total_initial_investment, total_lease_outlay_monthly, turnover_m12, turnover_m24, turnover_m36, turnover_m60, f"Month {break_even_month}" if break_even_month else "Beyond 60 Months", dscr_metric)

    st.download_button(label="📥 Download Official Bank-Ready Feasibility & Financial PDF Pack", data=pdf_file, file_name=f"Phatbuns_Bankable_Pack_{location_name.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)

with tab2:
    st.header("Franchisee & Investor Lead Intake")
    with st.form("investor_registration_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            full_name = st.text_input("Full Name *")
            entity_name = st.text_input("Entity / Company Name")
            id_or_passport = st.text_input("ID or Passport Number *")
            email = st.text_input("Email Address *")
        with f_col2:
            mobile = st.text_input("Mobile Number *")
            preferred_site = st.text_input("Preferred Target Site / Node *", value=location_name)
            store_model_choice = st.selectbox("Preferred Store Model", options=list(STORE_MODELS.keys()))
            capital_available = st.number_input("Proposed Total Capital Available (ZAR)", value=2500000.0, step=100000.0)

        unencumbered_cash_pct = st.slider("Verified Unencumbered Cash (%)", min_value=0.0, max_value=100.0, value=50.0)
        c_col1, c_col2, c_col3 = st.columns(3)
        with c_col1: admin_fee_paid = st.checkbox("Admin Fee Paid (R2,000 Excl. VAT)")
        with c_col2: ndnca_signed = st.checkbox("Signed NDNCA Received")
        with c_col3: popia_consent = st.checkbox("POPIA / NCA Consent Received")

        submitted = st.form_submit_button("Submit Application to Database")
        if submitted:
            if not full_name or not email or not mobile or not id_or_passport or not preferred_site:
                st.error("Please fill in all mandatory fields (*).")
            else:
                save_investor_lead({"full_name": full_name, "entity_name": entity_name, "id_or_passport": id_or_passport, "email": email, "mobile": mobile, "preferred_site": preferred_site, "store_model": store_model_choice, "capital_available": capital_available, "unencumbered_cash_pct": unencumbered_cash_pct, "admin_fee_paid": 1 if admin_fee_paid else 0, "ndnca_signed": 1 if ndnca_signed else 0, "popia_consent": 1 if popia_consent else 0})
                st.success(f"Applicant record for **{full_name}** successfully logged in the database!")

    st.divider()

    st.subheader("CEO Pipeline & Vetting Database")
    df_pipeline = get_pipeline_dataframe()
    if not df_pipeline.empty:
        st.dataframe(df_pipeline, use_container_width=True)
        pipeline_pdf_file = generate_pipeline_pdf(df_pipeline)
        st.download_button(label="📥 Download CEO Pipeline & Investor Audit PDF Report", data=pipeline_pdf_file, file_name="Phatbuns_Investor_Pipeline_Report.pdf", mime="application/pdf", use_container_width=True)
    else:
        st.info("No franchisee applications currently recorded in the database.")

st.divider()

st.subheader("Master Rights Holder Contact Information")
st.markdown("""
**Master Rights Holder – South Africa**  
📧 **Email:** [nisaar@fantastic1.com](mailto:nisaar@fantastic1.com) | [fantastic1za@gmail.com](mailto:fantastic1za@gmail.com)  
💬 **WhatsApp:** [+27 82 786 7712](https://wa.me/27827867712)  
📲 **Mobile:** [+27 68 710 1939](tel:+27687101939) | [+27 68 727 4731](tel:+27687274731)  
""")
