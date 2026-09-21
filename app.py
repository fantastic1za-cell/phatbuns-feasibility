import math
import os
import io
import sqlite3
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
# REPORTLAB PDF GENERATION FUNCTIONS
# ==========================================
def generate_pdf_report(loc_name, shop, suburb, int_gla, ext_gla, total_gla, model, max_seats, high_seats, capital, wc, total_inv, int_rent, ext_rent, total_rent, turnover, breakeven, payback):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#111111'), leading=22, alignment=1)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#555555'), leading=14, alignment=1)
    section_heading = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor('#8B0000'), leading=16, spaceBefore=10, spaceAfter=5)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#222222'))

    elements = []

    elements.append(Paragraph("PHATBUNS SOUTH AFRICA", title_style))
    elements.append(Paragraph("Commercial Feasibility & Location Intelligence Assessment", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#8B0000'), spaceBefore=5, spaceAfter=15))

    elements.append(Paragraph("1. Site & Lease Specification", section_heading))
    site_data = [
        [Paragraph("<b>Location Name:</b>", body_style), Paragraph(str(loc_name), body_style), Paragraph("<b>Shop Code:</b>", body_style), Paragraph(str(shop), body_style)],
        [Paragraph("<b>Suburb / Node:</b>", body_style), Paragraph(str(suburb), body_style), Paragraph("<b>Store Model:</b>", body_style), Paragraph(str(model), body_style)],
        [Paragraph("<b>Internal GLA:</b>", body_style), Paragraph(f"{int_gla:.1f} sqm", body_style), Paragraph("<b>External Area:</b>", body_style), Paragraph(f"{ext_gla:.1f} sqm", body_style)],
        [Paragraph("<b>Total Store Size:</b>", body_style), Paragraph(f"{total_gla:.1f} sqm", body_style), Paragraph("<b>Suggested Seating:</b>", body_style), Paragraph(f"{max_seats} Standard / {high_seats} Dense", body_style)]
    ]
    t_site = Table(site_data, colWidths=[110, 150, 110, 150])
    t_site.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F9F9F9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_site)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("2. Financial & Rental Structure", section_heading))
    fin_data = [
        [Paragraph("<b>Turnkey Capital (Excl. VAT):</b>", body_style), Paragraph(f"R {capital:,.2f}", body_style)],
        [Paragraph("<b>Working Capital:</b>", body_style), Paragraph(f"R {wc:,.2f}", body_style)],
        [Paragraph("<b>Total Initial Capital Outlay:</b>", body_style), Paragraph(f"R {total_inv:,.2f}", body_style)],
        [Paragraph("<b>Internal Base Rent (Monthly):</b>", body_style), Paragraph(f"R {int_rent:,.2f}", body_style)],
        [Paragraph("<b>External Base Rent (Monthly):</b>", body_style), Paragraph(f"R {ext_rent:,.2f}", body_style)],
        [Paragraph("<b>Total Combined Base Rent:</b>", body_style), Paragraph(f"R {total_rent:,.2f}", body_style)],
        [Paragraph("<b>Projected Monthly Turnover:</b>", body_style), Paragraph(f"R {turnover:,.2f}", body_style)],
        [Paragraph("<b>Monthly Op Break-Even Sales:</b>", body_style), Paragraph(f"R {breakeven:,.2f}", body_style)],
        [Paragraph("<b>Full Capital Payback:</b>", body_style), Paragraph(str(payback), body_style)],
    ]
    t_fin = Table(fin_data, colWidths=[220, 300])
    t_fin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_fin)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("3. Governance & Approval Sign-Off", section_heading))
    gov_text = """
    <b>Approval Pre-Requisites:</b><br/>
    • Payment of R2,000 (Excl. VAT) non-refundable application fee.<br/>
    • Proof of 50% unencumbered cash equity via 3-6 months bank statements.<br/>
    • SANHA Halaal compliance & supply chain accreditation.<br/>
    • Mandatory 4–6 week hands-on operational staff training.<br/>
    • Final binding written approval by the CEO of Phatbuns South Africa.
    """
    elements.append(Paragraph(gov_text, body_style))
    elements.append(Spacer(1, 20))

    sig_data = [
        [Paragraph("<b>Franchise Manager Signature:</b> ____________________", body_style), Paragraph("<b>CEO Signature:</b> Nisaar Ally", body_style)],
        [Paragraph("<b>Date:</b> ____ / ____ / ________", body_style), Paragraph("<b>Date:</b> ____ / ____ / ________", body_style)]
    ]
    t_sig = Table(sig_data, colWidths=[260, 260])
    t_sig.setStyle(TableStyle([('PADDING', (0,0), (-1,-1), 8)]))
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
tab1, tab2 = st.tabs(["📊 Feasibility Engine", "📋 Investor & Franchisee Registry"])

with tab1:
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
        location_name = st.text_input("Enter Custom Location Name", value="Loftus Park, Pretoria") if selected_location == "Custom / Other Site..." else selected_location

    with col2:
        shop_code = st.text_input("Shop / Unit Code", value="Shop C01")

    col_suburb, col_dummy = st.columns(2)
    with col_suburb:
        suburb_node = st.text_input("Suburb / Node (Auto-Populated)", key="suburb_val")

    st.subheader("Space Allocation (GLA Breakdown)")
    col_int_gla, col_ext_gla = st.columns(2)
    with col_int_gla:
        internal_gla = st.number_input("Internal Area (sqm)", value=100.0, step=5.0)
    with col_ext_gla:
        external_gla = st.number_input("External / Patio Area (sqm)", value=20.0, step=5.0)

    total_gla = internal_gla + external_gla
    st.caption(f"📐 **Total Combined Store Footprint:** {total_gla:.1f} sqm ({internal_gla:.1f} sqm Internal + {external_gla:.1f} sqm External)")

    st.divider()

    st.subheader("Store Model Type")
    selected_model = st.radio("Select Model Type", options=list(STORE_MODELS.keys()), index=3, horizontal=True)
    model_data = STORE_MODELS.get(selected_model, STORE_MODELS["Multi-Brand Kitchen Model"])

    internal_foh_sqm = internal_gla * model_data["foh_pct"]
    total_dining_sqm = internal_foh_sqm + external_gla
    max_comfortable_seats = math.floor(total_dining_sqm / 1.40) if total_dining_sqm > 0 else 0
    high_density_seats = math.floor(total_dining_sqm / 1.20) if total_dining_sqm > 0 else 0

    st.info(
        f"📐 **Recommended Size Range:** {model_data['size_range']} | "
        f"🪑 **Est. Total Dining Footprint:** {total_dining_sqm:.1f} sqm | "
        f"🪑 **Suggested Seating Capacity:** {max_comfortable_seats} Seats (Standard) / {high_density_seats} Seats (High Density)"
    )

    st.divider()

    st.subheader("2. Commercial Capital & Lease Setup")

    col_cap, col_wc = st.columns(2)
    with col_cap:
        turnkey_capital = st.number_input("Total Turnkey Capital (Excl. VAT)", value=model_data["turnkey_capital"], step=50000.0, format="%.2f")
    with col_wc:
        working_capital = st.number_input("Suggested Working Capital Requirement", value=model_data["working_capital"], step=25000.0, format="%.2f")

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

    st.divider()

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
            "Month": m, "Year": year_idx + 1, "Turnover": projected_monthly_turnover,
            "Rent Expense": current_monthly_rent, "COGS & Ops": monthly_cogs,
            "Royalties (9%)": royalty_marketing_fee, "Total Expenses": total_monthly_expenses,
            "Net Profit": net_monthly_profit, "Cumulative Cash Flow": cumulative_cash_flow
        })

    df_cashflow = pd.DataFrame(cash_flow_data)

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

    st.divider()

    st.header("4. Generate & Download Feasibility PDF Report")
    st.markdown("Click the button below to compile all selected metrics, rental structures, and governance rules into a branded Phatbuns PDF report.")

    pdf_file = generate_pdf_report(
        location_name, shop_code, st.session_state.get("suburb_val", ""),
        internal_gla, external_gla, total_gla, selected_model,
        max_comfortable_seats, high_density_seats,
        turnkey_capital, working_capital, total_initial_investment,
        total_internal_rent, total_external_rent, base_rent_monthly,
        projected_monthly_turnover, op_breakeven_turnover, payback_text
    )

    st.download_button(
        label="📥 Download Official Feasibility & Governance PDF Report",
        data=pdf_file,
        file_name=f"Phatbuns_Feasibility_{location_name.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with tab2:
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
                    "full_name": full_name, "entity_name": entity_name, "id_or_passport": id_or_passport,
                    "email": email, "mobile": mobile, "preferred_site": preferred_site,
                    "store_model": store_model_choice, "capital_available": capital_available,
                    "unencumbered_cash_pct": unencumbered_cash_pct,
                    "admin_fee_paid": 1 if admin_fee_paid else 0,
                    "ndnca_signed": 1 if ndnca_signed else 0,
                    "popia_consent": 1 if popia_consent else 0
                }
                save_investor_lead(applicant_data)
                st.success(f"Applicant record for **{full_name}** successfully logged in the database!")

    st.divider()

    st.subheader("CEO Pipeline & Vetting Database")
    df_pipeline = get_pipeline_dataframe()
    if not df_pipeline.empty:
        st.dataframe(df_pipeline, use_container_width=True)
        
        pipeline_pdf_file = generate_pipeline_pdf(df_pipeline)
        st.download_button(
            label="📥 Download CEO Pipeline & Investor Audit PDF Report",
            data=pipeline_pdf_file,
            file_name="Phatbuns_Investor_Pipeline_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("No franchisee applications currently recorded in the database.")

st.divider()

# Master Rights Holder Contact Footer
st.subheader("Master Rights Holder Contact Information")
st.markdown("""
**Master Rights Holder – South Africa**  
📧 **Email:** [nisaar@fantastic1.com](mailto:nisaar@fantastic1.com) | [fantastic1za@gmail.com](mailto:fantastic1za@gmail.com)  
💬 **WhatsApp:** [+27 82 786 7712](https://wa.me/27827867712)  
📲 **Mobile:** [+27 68 710 1939](tel:+27687101939) | [+27 68 727 4731](tel:+27687274731)  
""")
