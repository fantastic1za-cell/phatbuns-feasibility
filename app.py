import math
import os
import io
import re
import sqlite3
import json
import streamlit as st
import pandas as pd
from PIL import Image

# ReportLab Imports for PDF Generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Optional PDF Processing Engine
try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

# ==========================================
# GEMINI VISION & REGEX EXTRACTION ENGINE
# ==========================================
def parse_landlord_text_fallback(text):
    """
    Fallback Regex Parser with Value Protection.
    Fixes dropped zeros (e.g., 27 -> 270, 8 -> 80, 4 -> 40) automatically.
    """
    data = {}
    text_clean = text.replace('\r', '\n')

    # Shop Code
    shop_m = re.search(r'Shop(?:\s*code)?\s*[:\-]?\s*([A-Za-z0-9\s]+)', text_clean, re.IGNORECASE)
    if shop_m:
        val = shop_m.group(1).split('\n')[0].strip()
        if len(val) < 15: data['shop_code'] = val

    # Areas
    int_area_m = re.search(r'Internal\s*Area\s*[:\-]?\s*([\d\.\,]+)', text_clean, re.IGNORECASE)
    if int_area_m: data['internal_gla'] = float(int_area_m.group(1).replace(',', '.'))

    ext_area_m = re.search(r'(?:Outside|External)\s*Area\s*[:\-]?\s*([\d\.\,]+)', text_clean, re.IGNORECASE)
    if ext_area_m: data['external_gla'] = float(ext_area_m.group(1).replace(',', '.'))

    # Internal Rent (Auto-corrects dropped zero)
    int_rent_m = re.search(r'Rental\s*internal\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)', text_clean, re.IGNORECASE)
    if int_rent_m:
        val = float(int_rent_m.group(1))
        data['internal_rent'] = val * 10 if 10 <= val <= 40 else val

    # External Rent (Auto-corrects dropped zero)
    ext_rent_m = re.search(r'Rental\s*(?:outside|external)\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)', text_clean, re.IGNORECASE)
    if ext_rent_m:
        val = float(ext_rent_m.group(1))
        data['external_rent'] = val * 10 if 1 <= val <= 15 else val

    # Ops Cost (Auto-corrects dropped zero)
    ops_m = re.search(r'Ops\s*Cost\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)', text_clean, re.IGNORECASE)
    if ops_m:
        val = float(ops_m.group(1))
        data['ops_cost'] = val * 10 if 1 <= val <= 9 else val

    # Rates & Taxes
    rates_m = re.search(r'Rates\s*(?:&|and)?\s*taxes\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)', text_clean, re.IGNORECASE)
    if rates_m: data['rates_taxes'] = float(rates_m.group(1))

    # Generator Cost
    gen_m = re.search(r'Generator\s*cost\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)', text_clean, re.IGNORECASE)
    if gen_m: data['generator'] = float(gen_m.group(1))

    # Escalation
    esc_m = re.search(r'Escalation\s*[:\-]?\s*([\d]+(?:\.[\d]+)?)\s*%', text_clean, re.IGNORECASE)
    if esc_m: data['escalation'] = float(esc_m.group(1))

    # Marketing
    mktg_m = re.search(r'Marketing\s*[:\-]?\s*([\d]+(?:\.[\d]+)?)\s*%', text_clean, re.IGNORECASE)
    if mktg_m: data['mktg'] = float(mktg_m.group(1))

    return data

def process_uploaded_file(uploaded_file):
    if uploaded_file is None: return None, ""
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)
    file_type = uploaded_file.type

    if "pdf" in file_type or uploaded_file.name.lower().endswith(".pdf"):
        pdf_text = ""
        if HAS_PYPDF:
            try:
                reader = PdfReader(io.BytesIO(file_bytes))
                for page in reader.pages:
                    pdf_text += page.extract_text() or ""
            except Exception: pass
        return None, pdf_text
    else:
        try:
            pil_img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
            return pil_img, ""
        except Exception:
            return None, ""

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

# Session State Initialization with Widget Keys
if "ext_shop_code" not in st.session_state: st.session_state["ext_shop_code"] = "Shop C01"
if "ext_internal_gla" not in st.session_state: st.session_state["ext_internal_gla"] = 202.91
if "ext_external_gla" not in st.session_state: st.session_state["ext_external_gla"] = 138.99
if "ext_internal_rent" not in st.session_state: st.session_state["ext_internal_rent"] = 270.00
if "ext_external_rent" not in st.session_state: st.session_state["ext_external_rent"] = 80.00
if "ext_ops_cost" not in st.session_state: st.session_state["ext_ops_cost"] = 40.00
if "ext_rates_taxes" not in st.session_state: st.session_state["ext_rates_taxes"] = 24.50
if "ext_generator" not in st.session_state: st.session_state["ext_generator"] = 8.00
if "ext_escalation" not in st.session_state: st.session_state["ext_escalation"] = 7.00
if "ext_mktg" not in st.session_state: st.session_state["ext_mktg"] = 5.00

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
# REPORTLAB PDF GENERATION ENGINE
# ==========================================
def generate_pdf_report(loc_name, shop, suburb, int_gla, ext_gla, total_gla, model, max_seats, high_seats, capital, wc, total_inv, total_lease_outlay, payback, dscr, df_payback_matrix, blueprint_pil_img):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#111111'), leading=22, alignment=1)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#555555'), leading=14, alignment=1)
    section_heading = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#8B0000'), leading=14, spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#222222'))

    elements = []

    elements.append(Paragraph("PHATBUNS SOUTH AFRICA", title_style))
    elements.append(Paragraph(f"Bankable Commercial Feasibility & Investment Review — {loc_name} ({shop})", subtitle_style))
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#8B0000'), spaceBefore=2, spaceAfter=8))

    # 1. Site Specs
    elements.append(Paragraph("1. Site & Space Specification", section_heading))
    site_data = [
        [Paragraph("<b>Location Name:</b>", body_style), Paragraph(str(loc_name), body_style), Paragraph("<b>Shop Code:</b>", body_style), Paragraph(str(shop), body_style)],
        [Paragraph("<b>Suburb / Node:</b>", body_style), Paragraph(str(suburb), body_style), Paragraph("<b>Store Model:</b>", body_style), Paragraph(str(model), body_style)],
        [Paragraph("<b>Internal GLA:</b>", body_style), Paragraph(f"{int_gla:.2f} sqm", body_style), Paragraph("<b>External Area:</b>", body_style), Paragraph(f"{ext_gla:.2f} sqm", body_style)],
        [Paragraph("<b>Total Footprint:</b>", body_style), Paragraph(f"{total_gla:.2f} sqm", body_style), Paragraph("<b>Seating Capacity:</b>", body_style), Paragraph(f"{max_seats} Std / {high_seats} Dense", body_style)]
    ]
    t_site = Table(site_data, colWidths=[110, 150, 110, 150])
    t_site.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F9F9F9')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')), ('PADDING', (0,0), (-1,-1), 4)]))
    elements.append(t_site)
    elements.append(Spacer(1, 8))

    # 2. Financial Summary
    elements.append(Paragraph("2. Financial Outlay & Debt Serviceability", section_heading))
    fin_data = [
        [Paragraph("<b>Total Turnkey Capital:</b>", body_style), Paragraph(f"R {capital:,.2f}", body_style)],
        [Paragraph("<b>Working Capital Reserve:</b>", body_style), Paragraph(f"R {wc:,.2f}", body_style)],
        [Paragraph("<b>Total Initial Capital Required:</b>", body_style), Paragraph(f"R {total_inv:,.2f}", body_style)],
        [Paragraph("<b>Total Monthly Lease Outlay:</b>", body_style), Paragraph(f"R {total_lease_outlay:,.2f}", body_style)],
        [Paragraph("<b>Bank Debt Service Coverage Ratio (DSCR):</b>", body_style), Paragraph(f"<b>{dscr:.2f}x</b> (Required > 1.30x)", body_style)],
        [Paragraph("<b>Full Capital Recovery Period:</b>", body_style), Paragraph(str(payback), body_style)],
    ]
    t_fin = Table(fin_data, colWidths=[230, 290])
    t_fin.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')), ('PADDING', (0,0), (-1,-1), 4)]))
    elements.append(t_fin)
    elements.append(Spacer(1, 8))

    # 3. Payback Matrix
    elements.append(Paragraph(f"3. INVESTMENT RECOVERY & PAYBACK MATRIX (R{capital/1000000:.1f}M CAPEX AMORTIZATION @ 55% BLENDED GP)", section_heading))
    matrix_table_data = [[Paragraph(f"<b>{col}</b>", body_style) for col in df_payback_matrix.columns]]
    for idx, row in df_payback_matrix.iterrows():
        row_cells = []
        for col in df_payback_matrix.columns:
            val = row[col]
            if isinstance(val, float): formatted = f"R {val:,.2f}"
            else: formatted = str(val)
            row_cells.append(Paragraph(formatted, body_style))
        matrix_table_data.append(row_cells)

    t_matrix = Table(matrix_table_data, colWidths=[150, 90, 90, 95, 95])
    t_matrix.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F2F2F2')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#FFF2CC')),
        ('BACKGROUND', (0,4), (-1,4), colors.HexColor('#1F1F1F')),
        ('TEXTCOLOR', (0,4), (-1,4), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_matrix)
    elements.append(Spacer(1, 10))

    # 4. Blueprint Addendum
    elements.append(Paragraph("ADDENDUM: SITE BLUEPRINT & LOCATION FEASIBILITY", section_heading))
    if blueprint_pil_img is not None:
        try:
            img_byte_arr = io.BytesIO()
            blueprint_pil_img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            rl_img = RLImage(img_byte_arr, width=480, height=220)
            elements.append(rl_img)
        except Exception:
            elements.append(Paragraph("<i>Site layout blueprint attached, but could not be embedded into PDF report.</i>", body_style))
    else:
        elements.append(Paragraph("<b>PROPOSED SITE LAYOUT BLUEPRINT:</b> Not available yet — Pending landlord architectural submission.", body_style))

    elements.append(Spacer(1, 10))

    # Signatures
    sig_data = [
        [Paragraph("<b>Franchise Manager Signature:</b> ____________________", body_style), Paragraph("<b>CEO Signature:</b> Nisaar Ally", body_style)],
        [Paragraph("<b>Date:</b> ____ / ____ / ________", body_style), Paragraph("<b>Date:</b> ____ / ____ / ________", body_style)]
    ]
    t_sig = Table(sig_data, colWidths=[260, 260])
    t_sig.setStyle(TableStyle([('PADDING', (0,0), (-1,-1), 4)]))
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
        t_pipe.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EFEFEF')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')), ('PADDING', (0,0), (-1,-1), 4)]))
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
    st.markdown("Upload a landlord proposal (PDF, PNG, JPG) or paste offer text below to auto-populate site parameters.")

    col_up1, col_up2 = st.columns(2)
    with col_up1:
        uploaded_offer_file = st.file_uploader("Upload Offer File (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"])
    with col_up2:
        pasted_text = st.text_area("Or Paste Email / Whatsapp Offer Text Directly", height=100, placeholder="Paste landlord offer text here...")

    if st.button("⚡ Extract & Pre-Fill Lease Terms"):
        extracted_text = ""
        
        if uploaded_offer_file is not None:
            pil_img, pdf_text = process_uploaded_file(uploaded_offer_file)
            if pdf_text:
                extracted_text += "\n" + pdf_text

        if pasted_text:
            extracted_text += "\n" + pasted_text

        if extracted_text.strip():
            parsed_res = parse_landlord_text_fallback(extracted_text)
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
            st.rerun()
        else:
            st.warning("Please upload an offer document or paste text above.")

    st.divider()

    st.header("1. Site & Lease Specification")

    col1, col2 = st.columns(2)
    with col1:
        selected_location = st.selectbox("Select Commercial Location", options=list(LOCATION_LOOKUP.keys()), index=0)
        location_name = st.text_input("Enter Custom Location Name", value="Loftus Park, Pretoria") if selected_location == "Custom / Other Site..." else selected_location

    with col2:
        shop_code = st.text_input("Shop / Unit Code", key="ext_shop_code")

    col_suburb, col_dummy = st.columns(2)
    with col_suburb:
        suburb_node = st.text_input("Suburb / Node (Auto-Populated)", value=LOCATION_LOOKUP.get(selected_location, ""))

    st.subheader("Space Allocation (GLA Breakdown)")
    col_int_gla, col_ext_gla = st.columns(2)
    with col_int_gla:
        internal_gla = st.number_input("Internal Area (sqm)", key="ext_internal_gla", step=5.0)
    with col_ext_gla:
        external_gla = st.number_input("External / Patio Area (sqm)", key="ext_external_gla", step=5.0)

    total_gla = internal_gla + external_gla
    st.caption(f"📐 **Total Combined Store Footprint:** {total_gla:.2f} sqm ({internal_gla:.2f} sqm Internal + {external_gla:.2f} sqm External)")

    # Site Blueprint Upload Engine (Supports PDF & PNG/JPG)
    st.subheader("Site Blueprint & Layout Plan")
    blueprint_file = st.file_uploader(f"Upload Architectural Blueprint for {location_name} ({shop_code})", type=["pdf", "png", "jpg", "jpeg"])
    blueprint_pil_img = None
    if blueprint_file is not None:
        pil_img, pdf_text = process_uploaded_file(blueprint_file)
        if pil_img is not None:
            blueprint_pil_img = pil_img
            st.image(blueprint_pil_img, caption=f"Proposed Store Blueprint: {location_name} ({shop_code})", use_container_width=True)
        else:
            st.info(f"📄 **Blueprint PDF Attached:** {blueprint_file.name}")
    else:
        st.info("ℹ️ **Blueprint Status:** Not available yet — Pending landlord architectural submission.")

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
        internal_rent_sqm = st.number_input("Internal Base Rent (R / sqm / month)", key="ext_internal_rent", step=10.0, format="%.2f")
        total_internal_rent = internal_gla * internal_rent_sqm
        st.caption(f"💵 **Total Monthly Internal Rent:** R {total_internal_rent:,.2f} (Excl. VAT)")

    with col_ext_rent:
        external_rent_sqm = st.number_input("External Base Rent (R / sqm / month)", key="ext_external_rent", step=5.0, format="%.2f")
        total_external_rent = external_gla * external_rent_sqm
        st.caption(f"💵 **Total Monthly External Rent:** R {total_external_rent:,.2f} (Excl. VAT)")

    total_base_rent_monthly = total_internal_rent + total_external_rent

    col_ops, col_rates, col_gen = st.columns(3)
    with col_ops:
        ops_cost_sqm = st.number_input("Ops Cost (R / sqm)", key="ext_ops_cost", step=1.0, format="%.2f")
        total_ops_cost = ops_cost_sqm * total_gla
    with col_rates:
        rates_taxes_sqm = st.number_input("Rates & Taxes (R / sqm)", key="ext_rates_taxes", step=0.5, format="%.2f")
        total_rates_taxes = rates_taxes_sqm * total_gla
    with col_gen:
        generator_cost_sqm = st.number_input("Generator Cost (R / sqm)", key="ext_generator", step=0.5, format="%.2f")
        total_generator_cost = generator_cost_sqm * total_gla

    col_mktg_pct, col_labor = st.columns(2)
    with col_mktg_pct:
        landlord_marketing_pct = st.number_input("Landlord Marketing (% of Basic Rent)", key="ext_mktg", step=0.5, format="%.2f")
        total_landlord_marketing = total_base_rent_monthly * (landlord_marketing_pct / 100.0)
    with col_labor:
        monthly_labor_cost = st.number_input("Monthly Store Staffing / Payroll (ZAR)", value=model_data["labor_monthly"], step=5000.0, format="%.2f")

    total_lease_outlay_monthly = total_base_rent_monthly + total_ops_cost + total_rates_taxes + total_generator_cost + total_landlord_marketing
    st.warning(f"🏬 **Total Monthly Landlord Lease Outlay:** R {total_lease_outlay_monthly:,.2f} (Excl. VAT)")

    st.divider()

    st.header("4. Investment Recovery & Payback Matrix (@ 55% Blended GP)")
    gp_margin = 0.55
    aov_ticket = 150.0

    capex_12 = turnkey_capital / 12
    capex_24 = turnkey_capital / 24
    capex_36 = turnkey_capital / 36
    capex_60 = turnkey_capital / 60

    outflow_breakeven = total_lease_outlay_monthly + monthly_labor_cost
    outflow_12 = outflow_breakeven + capex_12
    outflow_24 = outflow_breakeven + capex_24
    outflow_36 = outflow_breakeven + capex_36
    outflow_60 = outflow_breakeven + capex_60

    turnover_req_be = outflow_breakeven / gp_margin
    turnover_req_12 = outflow_12 / gp_margin
    turnover_req_24 = outflow_24 / gp_margin
    turnover_req_36 = outflow_36 / gp_margin
    turnover_req_60 = outflow_60 / gp_margin

    daily_orders_be = f"{math.ceil(turnover_req_be / 30 / aov_ticket)} Orders/Day"
    daily_orders_12 = f"{math.ceil(turnover_req_12 / 30 / aov_ticket)} Orders/Day"
    daily_orders_24 = f"{math.ceil(turnover_req_24 / 30 / aov_ticket)} Orders/Day"
    daily_orders_36 = f"{math.ceil(turnover_req_36 / 30 / aov_ticket)} Orders/Day"
    daily_orders_60 = f"{math.ceil(turnover_req_60 / 30 / aov_ticket)} Orders/Day"

    payback_matrix_data = {
        "FINANCIAL METRIC": ["Monthly CapEx Amortization", "Total Monthly Cash Outflow", "Required Monthly Turnover", "Daily Orders Needed (R150 Avg Ticket)"],
        "OPERATIONAL BREAKEVEN": [0.00, outflow_breakeven, turnover_req_be, daily_orders_be],
        "12-MONTH PAYBACK": [capex_12, outflow_12, turnover_req_12, daily_orders_12],
        "24-MONTH PAYBACK": [capex_24, outflow_24, turnover_req_24, daily_orders_24],
        "36-MONTH PAYBACK": [capex_36, outflow_36, turnover_req_36, daily_orders_36],
        "60-MONTH LEASE TERM": [capex_60, outflow_60, turnover_req_60, daily_orders_60]
    }

    df_payback_matrix = pd.DataFrame(payback_matrix_data)
    
    st.dataframe(
        df_payback_matrix.style.format({
            "OPERATIONAL BREAKEVEN": lambda x: f"R {x:,.2f}" if isinstance(x, (int, float)) else str(x),
            "12-MONTH PAYBACK": lambda x: f"R {x:,.2f}" if isinstance(x, (int, float)) else str(x),
            "24-MONTH PAYBACK": lambda x: f"R {x:,.2f}" if isinstance(x, (int, float)) else str(x),
            "36-MONTH PAYBACK": lambda x: f"R {x:,.2f}" if isinstance(x, (int, float)) else str(x),
            "60-MONTH LEASE TERM": lambda x: f"R {x:,.2f}" if isinstance(x, (int, float)) else str(x)
        }),
        use_container_width=True
    )

    st.divider()

    st.header("5. Financial Statements & 60-Month Forecast (Addendum)")

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
        
        monthly_turnover = (turnover_req_12 * (1.08 ** year_idx)) * season_multiplier
        monthly_lease = total_lease_outlay_monthly * (st.session_state["ext_escalation"] / 100 + 1) ** year_idx
        monthly_cogs = monthly_turnover * 0.33
        monthly_royalties = monthly_turnover * 0.09
        
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

    st.header("6. Generate & Download Official PDF Pack")
    pdf_file = generate_pdf_report(
        location_name, shop_code, suburb_node, internal_gla, external_gla, total_gla, selected_model,
        max_comfortable_seats, high_density_seats, turnkey_capital, working_capital, total_initial_investment,
        total_lease_outlay_monthly, f"Month {break_even_month}" if break_even_month else "Beyond 60 Months", dscr_metric,
        df_payback_matrix, blueprint_pil_img
    )

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
