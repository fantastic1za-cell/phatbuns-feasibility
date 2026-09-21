import os
import shutil
import urllib.parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ==============================================================================
# STREAMLIT PAGE CONFIG & BRAND STYLING
# ==============================================================================
st.set_page_config(
    page_title="Phatbuns Feasibility Engine",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Responsive CSS for iPhone & Mobile Web
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .brand-banner {
        background: linear-gradient(135deg, #1A2530 0%, #FF6B00 100%);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 15px rgba(255, 107, 0, 0.35);
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
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        justify-content: center;
        margin-bottom: 15px;
    }
    .badge-item {
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: bold;
        color: white;
        text-align: center;
    }
    .badge-phatbuns { background-color: #FF6B00; }
    .badge-phatville { background-color: #E31B23; }
    .badge-doorstep { background-color: #D18B93; }
    .badge-butter { background-color: #5C3A21; }
    .badge-adega { background-color: #2E7D32; }

    .stButton>button {
        background: linear-gradient(90deg, #FF6B00 0%, #E25804 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 14px 20px;
        font-size: 16px;
        width: 100%;
        box-shadow: 0 4px 12px rgba(255, 107, 0, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
    <div class="brand-banner">
        <h1 class="brand-title">🍔 PHATBUNS SOUTH AFRICA</h1>
        <div class="brand-subtitle">Feasibility Engine & Location Feasibility Generator</div>
    </div>
""", unsafe_allow_html=True)

# Active Franchise Brands
st.markdown("""
    <div class="badge-container">
        <div class="badge-item badge-phatbuns">PHATBUNS</div>
        <div class="badge-item badge-phatville">PHATVILLE</div>
        <div class="badge-item badge-doorstep">DOORSTEP DESSERTS</div>
        <div class="badge-item badge-butter">BUTTER BRŪLÉE</div>
        <div class="badge-item badge-adega">ADEGA EXPRESS</div>
    </div>
""", unsafe_allow_html=True)

# ==============================================================================
# CONSTANTS & CONFIGURATION
# ==============================================================================
SENDER_GMAIL = "fantastic1za@gmail.com"
SENDER_GMAIL_APP_PASSWORD = "eoca cijs uaze cbpv"
CC_EMAIL = "nisaar@fantastic1.com"

ALL_BRANDS_MAP = {
    'PHATBUNS': 'Phatbuns (Gourmet Smash Burgers)',
    'PHATVILLE': 'PhatVille (Southern Fried Chicken & Wings)',
    'DOORSTEP_DESSERTS': 'Doorstep Desserts (Waffles, Crepes & Desserts)',
    'BUTTER_BRULEE': 'Butter Brûlée (Artisanal Pastries & Coffee)',
    'ADEGA': 'Adega Express (Portuguese Flame-Grilled Chicken, Prawns & Steaks)'
}

# ==============================================================================
# FORM INPUTS
# ==============================================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Site & Lease Specification")
    site_name = st.text_input("Location Name", "The Glen Shopping Centre")
    premises_code = st.text_input("Shop / Unit Code", "Shop M12C")
    address_node = st.text_input("Suburb / Node", "Oakdene, Johannesburg South")
    model_type = st.selectbox(
        "Store Model Type", 
        ["Express Model", "Full Sit-Down Model", "Express Kiosk Model", "Multi-Brand Kitchen Model"]
    )
    store_size = st.number_input("Store Size (m²)", min_value=10, value=62)
    managing_agent = st.text_input("Managing Agent / Landlord", "Hyprop Investments / Ellies")
    condition_of_premises = st.text_input("Premises Condition", "Standard Grey Box (Screeded/HVAC/1st Fix)")
    mall_gla = st.text_input("Mall GLA Size", "78,000 m² Regional Shopping Centre")
    
    selected_brand_keys = st.multiselect(
        "Select Deployed Kitchen Brands",
        options=list(ALL_BRANDS_MAP.keys()),
        default=['PHATBUNS'],
        format_func=lambda x: ALL_BRANDS_MAP[x]
    )

with col2:
    st.subheader("2. Commercial & Financials (Excl. VAT)")
    setup_cost = st.number_input("Total Turnkey Capital (ZAR)", value=2600000, step=50000)
    working_capital = st.number_input("Working Capital Reserve (ZAR)", value=500000, step=25000)
    basic_rent = st.number_input("Monthly Basic Rent (ZAR)", value=31500, step=1000)
    rent_sqm = st.number_input("Rental Rate per m² (ZAR)", value=round(basic_rent/store_size, 2) if store_size else 0.0)
    ops_costs = st.number_input("Monthly Operating Costs (ZAR)", value=6200, step=500)
    rates_taxes = st.number_input("Rates & Taxes (ZAR)", value=3894, step=500)
    marketing_cost = st.number_input("Marketing Levy (ZAR)", value=1575, step=250)
    lease_period = st.number_input("Lease Period (Years)", value=5)
    renewal_option = st.number_input("Renewal Option (Years)", value=5)
    escalation_rate = st.number_input("Annual Escalation %", value=8.0, step=0.5)
    turnover_pct = st.number_input("Turnover Rental Clause %", value=8.0, step=0.5)
    
    st.subheader("3. Franchisee Contact Details")
    franchisee_email = st.text_input("Franchisee Email Address", "")
    franchisee_phone = st.text_input("Franchisee WhatsApp Number (e.g. +27821234567)", "")

# Calculated Variables
fee_allocation = 400000 if 'kiosk' in model_type.lower() else 650000
physical_fitout = setup_cost - fee_allocation
total_monthly_lease = basic_rent + ops_costs + rates_taxes + marketing_cost
turnover_breakpoint = int(basic_rent / (turnover_pct / 100)) if turnover_pct > 0 else 0

# ==============================================================================
# REPORT BUILDER ENGINE
# ==============================================================================
def generate_pdf(filename):
    doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=25, rightMargin=25, topMargin=25, bottomMargin=25)
    styles = getSampleStyleSheet()

    COLOR_NAVY = colors.HexColor("#1A2530")
    COLOR_ORANGE = colors.HexColor("#FF6B00")
    COLOR_BG_LIGHT = colors.HexColor("#F8F9FA")

    title_style = ParagraphStyle('DocTitleUnique', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.white)
    subtitle_style = ParagraphStyle('DocSubTitleUnique', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=COLOR_ORANGE)
    header_sub_style = ParagraphStyle('HeaderSubUnique', parent=title_style, fontSize=9, leading=11, textColor=colors.HexColor("#DDDDDD"))
    section_header = ParagraphStyle('SectionHeaderUnique', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=12, textColor=COLOR_NAVY)
    body_bold = ParagraphStyle('BodyBoldUnique', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.black)
    body_text = ParagraphStyle('BodyTextUnique', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.black)
    body_muted = ParagraphStyle('BodyMutedUnique', parent=styles['Normal'], fontName='Helvetica', fontSize=6.5, leading=8.5, textColor=colors.HexColor("#555555"))
    table_hdr = ParagraphStyle('TableHdrUnique', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white)

    story = []

    active_brands = [ALL_BRANDS_MAP[k] for k in selected_brand_keys if k in ALL_BRANDS_MAP]
    brand_header_label = f"{len(active_brands)} BRAND(S) KITCHEN CONCEPT" if len(active_brands) > 1 else model_type.upper()
    brand_bullets = "<br/>".join([f"• {b}" for b in active_brands]) if active_brands else "• Phatbuns (Gourmet Smash Burgers)"

    # --- PAGE 1 ---
    header_data = [
        [Paragraph("PHATBUNS FEASIBILITY", title_style), Paragraph(f"{brand_header_label} ({store_size} M²)", subtitle_style)],
        [Paragraph(f"SITE EVALUATION & INVESTMENT ANALYSIS — {site_name.upper()}", header_sub_style), ""]
    ]
    header_table = Table(header_data, colWidths=[370, 175])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_NAVY),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    card_data = [
        [
            Paragraph(f"TURNKEY SETUP<br/><font size=10 color='#1A2530'><b>R {setup_cost:,}</b></font><br/><font size=6 color='#555555'>Excl. VAT (Turnkey Total)</font>", body_text),
            Paragraph(f"WORKING CAPITAL<br/><font size=10 color='#1A2530'><b>R {working_capital:,}</b></font><br/><font size=6 color='#555555'>Suggested Reserve</font>", body_text),
            Paragraph(f"BASE NET RENTAL<br/><font size=10 color='#1A2530'><b>R {basic_rent:,}</b></font><br/><font size=6 color='#555555'>R {rent_sqm:.2f} / m² pm</font>", body_text),
            Paragraph(f"OPS COST<br/><font size=10 color='#1A2530'><b>R {ops_costs:,}</b></font><br/><font size=6 color='#555555'>Gross Rental Terms</font>", body_text),
        ]
    ]
    card_table = Table(card_data, colWidths=[136, 136, 136, 136])
    card_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(card_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("01. SITE PROFILE & CAPITAL SCHEDULE", section_header))
    story.append(Spacer(1, 4))

    sec1_data = [
        [Paragraph("SITE PARAMETER", table_hdr), Paragraph("SPECIFICATION", table_hdr), Paragraph("TURNKEY CAPITAL SCHEDULE (EXCL. VAT)", table_hdr), Paragraph("AMOUNT", table_hdr)],
        [Paragraph("Location / Premises", body_bold), Paragraph(f"{site_name} ({premises_code})", body_text), Paragraph("Physical Store Fitout & Equipment Outlay:", body_text), Paragraph(f"R {physical_fitout:,}", body_text)],
        [Paragraph("Address / Node", body_bold), Paragraph(address_node, body_text), Paragraph("Franchise & Project Management Fee:", body_bold), Paragraph(f"R {fee_allocation:,}", body_bold)],
        [Paragraph("Store Footprint", body_bold), Paragraph(f"{store_size} m² ({model_type})", body_text), Paragraph("Total Projected Setup Outlay (Excl. VAT):", body_bold), Paragraph(f"R {setup_cost:,}", body_bold)],
        [Paragraph("Active Brands", body_bold), Paragraph(brand_bullets, body_text), Paragraph("50% Deposit on Signing Agreement:", body_text), Paragraph(f"R {int(setup_cost*0.5):,}", body_text)],
        [Paragraph("Managing Agent", body_bold), Paragraph(managing_agent, body_text), Paragraph("40% Beneficial Occupation (BO):", body_text), Paragraph(f"R {int(setup_cost*0.4):,}", body_text)],
        [Paragraph("Mall GLA Size", body_bold), Paragraph(mall_gla, body_text), Paragraph("10% Prior to Store Opening:", body_text), Paragraph(f"R {int(setup_cost*0.1):,}", body_text)],
        [Paragraph("Condition of Premises", body_bold), Paragraph(condition_of_premises, body_text), Paragraph("Working Capital Reserve (Excluded):", body_muted), Paragraph(f"R {working_capital:,}", body_muted)],
    ]
    sec1_table = Table(sec1_data, colWidths=[110, 160, 184, 90])
    sec1_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), COLOR_NAVY),
        ('BACKGROUND', (2,0), (3,0), COLOR_ORANGE),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (3,1), (3,-1), 'RIGHT'),
    ]))
    story.append(sec1_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("02. LEASE STRUCTURE & FINANCIAL PROVISIONS", section_header))
    story.append(Spacer(1, 4))
    sec2_data = [
        [Paragraph("LEASE CLAUSE / PROVISION", table_hdr), Paragraph("TERMS & RATE STRUCTURE", table_hdr), Paragraph("FINANCIAL ALIGNMENT", table_hdr)],
        [Paragraph("Lease Period & Renewal Option", body_bold), Paragraph(f"{lease_period} Years Initial Period + {renewal_option}-Year Renewal Option", body_text), Paragraph(f"{lease_period*12} Months Base Amortization", body_text)],
        [Paragraph("Base Net Rental Rate", body_bold), Paragraph(f"R {rent_sqm:.2f} / m² / month (Excl. VAT & Utilities)", body_text), Paragraph(f"R {basic_rent:,} / month", body_bold)],
        [Paragraph("Annual Rental Escalation", body_bold), Paragraph(f"{escalation_rate}% per annum effective anniversary of commencement", body_text), Paragraph(f"Year 2 Base: R {int(basic_rent*(1+escalation_rate/100)):,} / month", body_text)],
        [Paragraph("Turnover Rental Clause", body_bold), Paragraph(f"{turnover_pct}% of Net Monthly Turnover vs Base Net Rental", body_text), Paragraph(f"Triggers above R {turnover_breakpoint:,} pm", body_bold)],
        [Paragraph("Beneficial Occupation (BO)", body_bold), Paragraph("1 Month Rent-Free BO for Turnkey Fitout", body_text), Paragraph("Fitout Schedule: 30 Days", body_text)],
    ]
    sec2_table = Table(sec2_data, colWidths=[140, 230, 174])
    sec2_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(sec2_table)
    story.append(Spacer(1, 10))

    # --- PAGE 2 ---
    story.append(PageBreak())

    story.append(Paragraph("04. FINANCIAL RECOVERY & UNIT SALES TARGET MATRIX", section_header))
    story.append(Spacer(1, 4))
    model_p = Paragraph(
        f"<b>Model Assumptions:</b> Average Basket Value (ABV) set at R 175 (ex VAT). Fixed Operating Expenses include Total Lease (R {total_monthly_lease:,}), Staff Payroll, Utilities/Gas, Royalties & Marketing (7%), and COGS (35%). All values rounded cleanly.",
        body_text
    )
    story.append(model_p)
    story.append(Spacer(1, 6))

    recovery_matrix = {
        'Operational Breakeven': int(total_monthly_lease * 4.5),
        '12 Months Recovery Target': int(total_monthly_lease * 9.1),
        '24 Months Recovery Target': int(total_monthly_lease * 6.8),
        '36 Months Recovery Target': int(total_monthly_lease * 6.0),
        '48 Months Recovery Target': int(total_monthly_lease * 5.6),
        '60 Months Recovery Target': int(total_monthly_lease * 5.4),
    }

    sec4_data = [[Paragraph("RECOVERY HORIZON", table_hdr), Paragraph("REQUIRED TURNOVER / MONTH", table_hdr), Paragraph("REQUIRED UNITS / MONTH", table_hdr), Paragraph("REQUIRED UNITS / DAY", table_hdr)]]
    for horizon, turnover in recovery_matrix.items():
        units_mo = int(turnover / 175)
        units_day = int(units_mo / 30)
        sec4_data.append([
            Paragraph(horizon, body_bold),
            Paragraph(f"R {turnover:,}", body_text),
            Paragraph(f"{units_mo:,} units", body_text),
            Paragraph(f"{units_day:,} units / day", body_bold)
        ])
    sec4_table = Table(sec4_data, colWidths=[160, 134, 125, 125])
    sec4_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('PADDING', (0,0), (-1,-1), 4.5),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(sec4_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("05. OPERATIONS, STAFFING & CHANNEL BREAKDOWN", section_header))
    story.append(Spacer(1, 4))
    sec5_data = [
        [Paragraph("REVENUE CHANNEL SPLIT", table_hdr), Paragraph("STAFFING STRUCTURE (BCEA 8-HR SHIFTS)", table_hdr)],
        [
            Paragraph("Online Deliveries: <b>45%</b><br/>Takeaway & Collect: <b>40%</b><br/>In-Store Dining: <b>15%</b>", body_text),
            Paragraph("<b>1 x Store Manager</b> — Full Store Oversight<br/><b>1 x Shift Supervisor</b> — POS & Dispatch<br/><b>2 x Line Grillers</b> — Smash Griddle Operations<br/><b>1 x Prep / Cleaner</b> — Hygiene Maintenance", body_text)
        ]
    ]
    sec5_table = Table(sec5_data, colWidths=[200, 344])
    sec5_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(sec5_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("06. TURNKEY KITCHEN EQUIPMENT MANIFEST", section_header))
    story.append(Spacer(1, 4))
    sec6_data = [
        [
            Paragraph("<b>SMASH GRILL STATION</b><br/>Chrome Smash Griddle, Bun Toaster & Pass-Through Heated Holding.", body_text),
            Paragraph("<b>POS & AUTOMATION</b><br/>Dual-Screen Touch POS Terminal, KDS, Thermal Printers & Router setup.", body_text)
        ],
        [
            Paragraph("<b>FRYING & PREP LINE</b><br/>Dual Deep Fryer, 3-Door Under-Counter Prep Fridge with Topping Rail.", body_text),
            Paragraph("<b>BEVERAGE & SHAKES</b><br/>Heavy Duty Commercial Blender & Ice Machine (40kg/24hr).", body_text)
        ]
    ]
    sec6_table = Table(sec6_data, colWidths=[272, 272])
    sec6_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(sec6_table)

    doc.build(story)

# ==============================================================================
# DISPATCH ACTIONS
# ==============================================================================
st.markdown("---")
if st.button("🚀 Compile Report & Dispatch", type="primary"):
    pdf_filename = f"Phatbuns_{site_name.replace(' ', '_')}_Feasibility_Report.pdf"
    generate_pdf(pdf_filename)
    
    st.success(f"Feasibility Report Compiled: `{pdf_filename}`")
    
    with open(pdf_filename, "rb") as file:
        st.download_button(
            label="📥 Download PDF Feasibility Report",
            data=file,
            file_name=pdf_filename,
            mime="application/pdf"
        )
    
    if franchisee_email:
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_GMAIL
            msg['To'] = franchisee_email
            msg['Cc'] = CC_EMAIL
            msg['Subject'] = f"Phatbuns Franchise Feasibility Report — {site_name}"
            
            body = f"Dear Franchisee,\n\nPlease find attached the official Feasibility Report for {site_name}.\n\nKind regards,\nNisaar Ally"
            msg.attach(MIMEText(body, 'plain'))
            
            with open(pdf_filename, "rb") as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
                msg.attach(attach)
                
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER_GMAIL, SENDER_GMAIL_APP_PASSWORD)
            server.sendmail(SENDER_GMAIL, [franchisee_email, CC_EMAIL], msg.as_string())
            server.quit()
            st.success(f"✉️ Email sent to {franchisee_email} (CC: {CC_EMAIL})")
        except Exception as e:
            st.error(f"Email error: {e}")

    if franchisee_phone:
        clean_phone = franchisee_phone.replace("+", "").replace(" ", "").replace("-", "")
        if clean_phone.startswith("0"):
            clean_phone = "27" + clean_phone[1:]
        
        wa_text = urllib.parse.quote(f"Hi! Here is the Phatbuns Franchise Feasibility Report for *{site_name}*.")
        wa_url = f"https://wa.me/{clean_phone}?text={wa_text}"
        
        st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366;color:white;padding:12px 24px;border:none;border-radius:8px;cursor:pointer;font-weight:bold;width:100%;">💬 Open WhatsApp & Send to Franchisee</button></a>', unsafe_allow_html=True)
