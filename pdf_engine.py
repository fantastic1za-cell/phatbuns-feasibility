# services.py - Production Service Engine (Drive Folder Hierarchy & Safe Extraction)
import os
import iodef generate_pdf_report(loc_name, shop, suburb, int_gla, ext_gla, total_gla, model, max_seats, high_seats, capital, wc, int_rent, ext_rent, ops_cost, total_lease_outlay, turnover_clause_pct, recommended_model_name, dscr, payback_df, df_pnl_annual, blueprint_pil_img, applicant_name="Prospective Investor", applicant_email="N/A", applicant_mobile="N/A", **kwargs):
    styles = getSampleStyleSheet()
    site_p = SITE_PROFILES.get(loc_name, {
        "landlord": "Redefine Properties / Abcon",
        "mall_size": "10,008 m² Convenience Center",
        "footfall": "160,000 – 210,000 visits / month (~2.1M - 2.5M Annually)",
        "households": "110,000 – 135,000 Active Households (10 km Catchment)",
        "competitors": "RocoMamas, McDonald's Drive-Thru, Ocean Basket, Adega Café",
        "lsm_profile": "LSM 8–10+ / High Disposable Income Segment"
    })

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18, leftMargin=18, topMargin=18, bottomMargin=28)

    NAVY_HEADER = colors.HexColor('#1A365D')
    ORANGE_BRAND = colors.HexColor('#C53030')
    DARK_TEXT = colors.HexColor('#2D3748')
    WHITE_TEXT = colors.HexColor('#FFFFFF')
    LIGHT_BG = colors.HexColor('#F7FAFC')
    BORDER_COLOR = colors.HexColor('#CBD5E0')

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=WHITE_TEXT, leading=16)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=ORANGE_BRAND, leading=10, alignment=2)
    sec_banner_style = ParagraphStyle('SecBannerStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=8.5, textColor=WHITE_TEXT, leading=10)
    body_bold = ParagraphStyle('BodyBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=DARK_TEXT)
    body_regular = ParagraphStyle('BodyRegular', parent=styles['Normal'], fontName='Helvetica', fontSize=7, leading=9, textColor=DARK_TEXT)
    body_white_bold = ParagraphStyle('BodyWhiteBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=WHITE_TEXT)

    elements = []

    # PAGE 1: COVER
    cover_img_bytes = create_cover_page_image()
    elements.append(RLImage(cover_img_bytes, width=558, height=775))
    elements.append(PageBreak())

    # PAGE 2: EXECUTIVE SITE & CAPITAL SCHEDULE
    t_header = Table([[Paragraph("PHATBUNS SOUTH AFRICA", title_style), Paragraph(f"{model.upper()} ({total_gla:.0f} M²)", subtitle_style)]], colWidths=[370, 188])
    t_header.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 4)]))
    elements.append(t_header)
    elements.append(Spacer(1, 4))

    sec1_banner = Table([[Paragraph("01. SITE PROFILE & CAPITAL SCHEDULE", sec_banner_style)]], colWidths=[558])
    sec1_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec1_banner)

    sec1_data = [
        [Paragraph("SITE PARAMETER", body_white_bold), Paragraph("SPECIFICATION", body_white_bold), Paragraph("TURNKEY CAPITAL SCHEDULE", body_white_bold), Paragraph("AMOUNT", body_white_bold)],
        [Paragraph("Location Name", body_bold), Paragraph(f"{loc_name} (Shop {shop})", body_regular), Paragraph("50% Deposit on Signing", body_regular), Paragraph(f"R {int(round(capital*0.50)):,}", body_regular)],
        [Paragraph("Store Footprint", body_bold), Paragraph(f"{total_gla:.2f} m² {model}", body_regular), Paragraph("40% Beneficial Occupation", body_regular), Paragraph(f"R {int(round(capital*0.40)):,}", body_regular)],
        [Paragraph("Managing Agent", body_bold), Paragraph(site_p.get("landlord", "Commercial Landlord"), body_regular), Paragraph("10% Prior to Opening", body_regular), Paragraph(f"R {int(round(capital*0.10)):,}", body_regular)]
    ]
    t_sec1 = Table(sec1_data, colWidths=[110, 160, 198, 90])
    t_sec1.setStyle(TableStyle([('BACKGROUND', (0,0), (1,0), NAVY_HEADER), ('BACKGROUND', (2,0), (3,0), ORANGE_BRAND), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2.5), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec1)
    elements.append(Spacer(1, 6))

    # SECTION 02: LEASE STRUCTURE
    sec2_banner = Table([[Paragraph("02. LEASE STRUCTURE & FINANCIAL PROVISIONS", sec_banner_style)]], colWidths=[558])
    sec2_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec2_banner)

    sec2_data = [
        [Paragraph("LEASE CLAUSE / PROVISION", body_white_bold), Paragraph("TERMS & RATE STRUCTURE", body_white_bold), Paragraph("FINANCIAL ALIGNMENT", body_white_bold)],
        [Paragraph("Base Net Rental Rate", body_bold), Paragraph(f"R {int(round(int_rent))}/m²/month (Excl. VAT)", body_regular), Paragraph(f"R {int(round(int_rent * int_gla)):,} / month", body_regular)],
        [Paragraph("Annual Rental Escalation", body_bold), Paragraph("7.5% per annum effective anniversary", body_regular), Paragraph("Predictable cost curve", body_regular)],
        [Paragraph("Turnover Rental Clause", body_bold), Paragraph(f"{turnover_clause_pct}% of Net Monthly Turnover", body_regular), Paragraph("Triggered on high volume", body_regular)]
    ]
    t_sec2 = Table(sec2_data, colWidths=[160, 218, 180])
    t_sec2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2.5), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec2)
    elements.append(Spacer(1, 6))

    # SECTION 03: CATCHMENT INTELLIGENCE
    sec3_banner = Table([[Paragraph("03. CATCHMENT & LOCATION INTELLIGENCE", sec_banner_style)]], colWidths=[558])
    sec3_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec3_banner)

    sec3_data = [
        [Paragraph("CATCHMENT METRIC", body_white_bold), Paragraph("DATA POINT / LOCATION ANALYSIS", body_white_bold)],
        [Paragraph("LSM / ESM Profile", body_bold), Paragraph(site_p.get("lsm_profile", "High Disposable Income"), body_regular)],
        [Paragraph("Monthly / Annual Footfall", body_bold), Paragraph(site_p.get("footfall", "180,000 visits / month"), body_regular)],
        [Paragraph("Catchment Household Count", body_bold), Paragraph(site_p.get("households", "120,000 Active Households"), body_regular)],
        [Paragraph("QSR Competitor Profile", body_bold), Paragraph(site_p.get("competitors", "Leading Fast Casual Brands"), body_regular)]
    ]
    t_sec3 = Table(sec3_data, colWidths=[160, 398])
    t_sec3.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2.5), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec3)
    elements.append(PageBreak())

    # PAGE 3: FINANCIAL RECOVERY MATRIX
    elements.append(Paragraph(f"<b>04. FINANCIAL RECOVERY MATRIX — {loc_name.upper()}</b>", sec_banner_style))
    elements.append(Spacer(1, 4))
    
    matrix_table_data = [[Paragraph(f"<b>{col}</b>", body_white_bold) for col in payback_df.columns]]
    for idx, row in payback_df.iterrows():
        matrix_table_data.append([Paragraph(str(row[col]), body_regular) for col in payback_df.columns])
    t_matrix = Table(matrix_table_data, colWidths=[180, 189, 189])
    t_matrix.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 3), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_matrix)
    elements.append(PageBreak())

    # PAGE 4: 5-YEAR PRO FORMA
    elements.append(Paragraph("<b>11. 5-YEAR PRO FORMA INCOME STATEMENT & P&L FORECAST</b>", sec_banner_style))
    elements.append(Spacer(1, 4))
    
    pnl_table_data = [[Paragraph(f"<b>{col}</b>", body_white_bold) for col in df_pnl_annual.columns]]
    for idx, row in df_pnl_annual.iterrows():
        row_cells = []
        for col in df_pnl_annual.columns:
            val = row[col]
            if isinstance(val, (int, float)):
                row_cells.append(Paragraph(f"R {int(round(val)):,}", body_regular))
            else:
                row_cells.append(Paragraph(str(val), body_regular))
        pnl_table_data.append(row_cells)

    t_pnl = Table(pnl_table_data, colWidths=[158, 80, 80, 80, 80, 80][:len(df_pnl_annual.columns)])
    t_pnl.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2.5), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_pnl)
    elements.append(Spacer(1, 6))

    # SECTION 11B: SAFE 5-YEAR CASH COMPARISON
    sec11b_banner = Table([[Paragraph("11B. 5-YEAR CASH INVESTMENT COMPARISON: BANK FIXED DEPOSIT VS. PHATBUNS FRANCHISE", sec_banner_style)]], colWidths=[558])
    sec11b_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec11b_banner)

    bank_principal = float(capital)
    bank_total_5yr = bank_principal * ((1 + 0.085) ** 5)
    bank_total_return = bank_total_5yr - bank_principal

    # Positional Row Search
    phatbuns_profit_5yr = bank_principal * 1.25
    try:
        first_col = df_pnl_annual.columns[0]
        for idx, row in df_pnl_annual.iterrows():
            if 'Net Operating Profit' in str(row[first_col]):
                num_cols = [c for c in df_pnl_annual.columns if c != first_col]
                phatbuns_profit_5yr = sum([float(row[nc]) for nc in num_cols if isinstance(row[nc], (int, float))])
                break
    except Exception:
        pass

    sec11b_data = [
        [Paragraph("INVESTMENT METRIC", body_white_bold), Paragraph("BANK FIXED DEPOSIT (8.5% P.A. PRE-TAX)", body_white_bold), Paragraph("PHATBUNS STORE INVESTMENT", body_white_bold)],
        [Paragraph("Initial Capital Invested", body_bold), Paragraph(f"R {int(round(bank_principal)):,}", body_regular), Paragraph(f"R {int(round(bank_principal)):,}", body_regular)],
        [Paragraph("Compounded Total Value (End of Year 5)", body_bold), Paragraph(f"<b>R {int(round(bank_total_5yr)):,}</b>", body_bold), Paragraph(f"<b>R {int(round(phatbuns_profit_5yr + bank_principal)):,}</b>", body_bold)],
        [Paragraph("Total Net Return / Earnings (5 Years)", body_bold), Paragraph(f"<b>R {int(round(bank_total_return)):,}</b>", body_bold), Paragraph(f"<b>R {int(round(phatbuns_profit_5yr)):,}</b>", body_bold)]
    ]
    t_sec11b = Table(sec11b_data, colWidths=[178, 190, 190])
    t_sec11b.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), ORANGE_BRAND), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2.5), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec11b)
    elements.append(PageBreak())

    # PAGE 5: BLUEPRINT LAYOUT
    elements.append(Paragraph(f"<b>PROPOSED STORE LEASING LAYOUT PLAN — {loc_name.upper()} (SHOP {shop})</b>", sec_banner_style))
    elements.append(Spacer(1, 6))

    if blueprint_pil_img is not None:
        rl_blueprint = create_aspect_ratio_rl_image(blueprint_pil_img, max_width=500, max_height=320)
        elements.append(rl_blueprint)
    else:
        placeholder_img = Image.new("RGB", (900, 600), color=(245, 247, 250))
        draw = ImageDraw.Draw(placeholder_img)
        draw.rectangle([15, 15, 885, 585], outline=(26, 54, 93), width=4)
        draw.text((320, 280), f"PROPOSED LAYOUT PLAN ({total_gla:.0f} sqm)", fill=(26, 54, 93))
        rl_blueprint = create_aspect_ratio_rl_image(placeholder_img, max_width=500, max_height=320)
        elements.append(rl_blueprint)

    elements.append(PageBreak())

    # PAGE 6: BRAND CATALOG
    elements.append(Paragraph("<b>PHATBUNS BRAND PORTFOLIO & SOCIAL MEDIA CATALOG</b>", sec_banner_style))
    elements.append(Spacer(1, 4))

    menu_table_rows = [[Paragraph("BRAND & CONCEPT", body_white_bold), Paragraph("MENU OVERVIEW & SOCIAL PROFILE", body_white_bold), Paragraph("GOOGLE DRIVE LINK", body_white_bold)]]
    for brand_name, info in BRAND_MENU_CATALOG.items():
        ig_url = info.get("instagram_url", "")
        drive_id = info.get("drive_file_id", "")
        centre_cell_html = f"{info['description']}<br/><a href='{ig_url}' color='#0066CC'><b>📸 Instagram: Official Profile</b></a>" if ig_url else info['description']
        dl_link_html = f"<a href='[https://drive.google.com/uc?export=download&id=](https://drive.google.com/uc?export=download&id=){drive_id}'><b>DOWNLOAD MENU</b></a>"
        menu_table_rows.append([Paragraph(f"<b>{brand_name}</b>", body_bold), Paragraph(centre_cell_html, body_regular), Paragraph(dl_link_html, body_regular)])

    t_menus = Table(menu_table_rows, colWidths=[130, 288, 140])
    t_menus.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), ORANGE_BRAND), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 3), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_menus)
    elements.append(PageBreak())

    # PAGE 7: GLOBAL MEDIA SHOWCASE
    elements.append(Paragraph("<b>GLOBAL STORE VISUALS & VIDEO WALK-THROUGHS</b>", sec_banner_style))
    elements.append(Spacer(1, 4))
    
    media_table_rows = [
        [Paragraph("STORE / MEDIA TYPE", body_white_bold), Paragraph("DESCRIPTION", body_white_bold), Paragraph("DIRECT WATCH LINK", body_white_bold)],
        [Paragraph("<b>Phatbuns Master Drive Folder</b>", body_bold), Paragraph("Complete directory of store photos, video tours & marketing reels.", body_regular), Paragraph(f'<a href="{STORE_MEDIA_LINKS["master_folder"]}"><b>OPEN DRIVE FOLDER</b></a>', body_regular)],
        [Paragraph("<b>Phatbuns UK Store Video 1</b>", body_bold), Paragraph("HD walkthrough of active UK franchise store operations.", body_regular), Paragraph(f'<a href="{STORE_MEDIA_LINKS["uk_video_1"]}"><b>WATCH UK VIDEO 1</b></a>', body_regular)]
    ]
    t_media = Table(media_table_rows, colWidths=[140, 278, 140])
    t_media.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 3.5), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_media)
    elements.append(PageBreak())

    # PAGE 8: NCNDA
    elements.append(Paragraph("<b>NON-DISCLOSURE AND NON-CIRCUMVENTION AGREEMENT (NCNDA)</b>", sec_banner_style))
    elements.append(Spacer(1, 4))

    app_name_str = f"<b>{applicant_name}</b>" if (applicant_name and applicant_name.strip() != "Prospective Investor") else "________________________________________________"
    app_email_str = f"<b>{applicant_email}</b>" if (applicant_email and applicant_email.strip() != "N/A") else "________________________________________________"
    app_mobile_str = f"<b>{applicant_mobile}</b>" if (applicant_mobile and applicant_mobile.strip() != "N/A") else "________________________________________________"
    app_address_str = kwargs.get("applicant_address", "________________________________________________________________________________________")

    ncnda_parties_html = (
        f"<b>1. PHATBUNS SOUTH AFRICA</b> (Franchisor), and <br/>"
        f"<b>2. THE UNDERSIGNED PARTY</b> (Prospective Franchisee):<br/>"
        f"• <b>Full Name / Entity:</b> {app_name_str}<br/>"
        f"• <b>Email Address:</b> {app_email_str}<br/>"
        f"• <b>Contact Number(s):</b> {app_mobile_str}<br/>"
        f"• <b>Physical Address:</b> {app_address_str}<br/>"
        f"• <b>Target Site:</b> <b>{loc_name} (Shop {shop})</b>"
    )
    elements.append(Paragraph(ncnda_parties_html, body_regular))
    elements.append(Spacer(1, 8))

    sig_p_ncnda = [
        [Paragraph("<b>For: PHATBUNS SOUTH AFRICA</b><br/><br/>____________________________________<br/><b>Name:</b> Nisaar Ally<br/><b>Title:</b> SA Master Rights Holder", body_regular),
         Paragraph(f"<b>For: THE RECEIVING PARTY</b><br/><br/>____________________________________<br/><b>Name:</b> {applicant_name if applicant_name else ''}<br/><b>Title:</b> Prospective Franchisee", body_regular)]
    ]
    t_sig_ncnda = Table(sig_p_ncnda, colWidths=[270, 270])
    t_sig_ncnda.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG), ('PADDING', (0,0), (-1,-1), 6)]))
    elements.append(t_sig_ncnda)

    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

import re
import sqlite3
import urllib.parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import streamlit as st
import pandas as pd
from PIL import Image

# Google Drive Imports
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    HAS_GDRIVE = True
except ImportError:
    HAS_GDRIVE = False

# PDF Imports
try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

from config import ASSETS_DIR, MENUS_DIR, LOCATIONS_DIR, BRAND_MENU_CATALOG

GDRIVE_SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.appdata'
]
LOCATIONS_ROOT_DRIVE_ID = "1vGItMiw-ZYqzBOXvLfl0xkbhh7uYkhf5"
DB_FILE = "phatbuns_franchisees.db"

# Fail-Safe Database Operations & Schema Management
def init_db(force_recreate=False):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if force_recreate:
        cursor.execute("DROP TABLE IF EXISTS franchisee_pipeline")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS franchisee_pipeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            entity_name TEXT,
            id_or_passport TEXT,
            email TEXT,
            mobile TEXT,
            preferred_site TEXT,
            store_model TEXT,
            capital_available REAL,
            unencumbered_cash_pct REAL,
            company_docs_status TEXT DEFAULT 'Not Provided',
            franchisee_id_status TEXT DEFAULT 'Not Provided',
            proof_of_funds_status TEXT DEFAULT 'Not Provided',
            admin_fee_paid INTEGER DEFAULT 0,
            ndnca_signed INTEGER DEFAULT 0,
            popia_consent INTEGER DEFAULT 0,
            application_status TEXT DEFAULT 'Initial Inquiry',
            ceo_approval TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("PRAGMA table_info(franchisee_pipeline)")
    existing_cols = [col[1] for col in cursor.fetchall()]
    
    missing_cols = {
        "company_docs_status": "TEXT DEFAULT 'Not Provided'",
        "franchisee_id_status": "TEXT DEFAULT 'Not Provided'",
        "proof_of_funds_status": "TEXT DEFAULT 'Not Provided'",
        "ceo_approval": "TEXT DEFAULT 'Pending'"
    }
    
    for col_name, col_type in missing_cols.items():
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE franchisee_pipeline ADD COLUMN {col_name} {col_type}")
            except Exception:
                pass
                
    conn.commit()
    conn.close()

def save_investor_lead(data):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    email_val = data.get('email', '')
    if not email_val:
        conn.close()
        return

    cursor.execute("SELECT id FROM franchisee_pipeline WHERE email = ?", (email_val,))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("""
            UPDATE franchisee_pipeline SET
                full_name = ?, entity_name = ?, id_or_passport = ?, mobile = ?,
                preferred_site = ?, store_model = ?, capital_available = ?, unencumbered_cash_pct = ?,
                company_docs_status = ?, franchisee_id_status = ?, proof_of_funds_status = ?,
                admin_fee_paid = ?, ndnca_signed = ?, popia_consent = ?
            WHERE email = ?
        """, (
            data.get('full_name', ''), data.get('entity_name', ''), data.get('id_or_passport', 'Provided'), data.get('mobile', ''),
            data.get('preferred_site', ''), data.get('store_model', 'Express Model'), float(data.get('capital_available', 2500000.0)), float(data.get('unencumbered_cash_pct', 50.0)),
            data.get('company_docs_status', 'Not Provided'), data.get('franchisee_id_status', 'Not Provided'), data.get('proof_of_funds_status', 'Not Provided'),
            int(data.get('admin_fee_paid', 0)), int(data.get('ndnca_signed', 0)), int(data.get('popia_consent', 1)), email_val
        ))
    else:
        cursor.execute("""
            INSERT INTO franchisee_pipeline (
                full_name, entity_name, id_or_passport, email, mobile,
                preferred_site, store_model, capital_available, unencumbered_cash_pct,
                company_docs_status, franchisee_id_status, proof_of_funds_status,
                admin_fee_paid, ndnca_signed, popia_consent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('full_name', ''), data.get('entity_name', ''), data.get('id_or_passport', 'Provided'),
            email_val, data.get('mobile', ''), data.get('preferred_site', ''),
            data.get('store_model', 'Express Model'), float(data.get('capital_available', 2500000.0)), float(data.get('unencumbered_cash_pct', 50.0)),
            data.get('company_docs_status', 'Not Provided'), data.get('franchisee_id_status', 'Not Provided'), data.get('proof_of_funds_status', 'Not Provided'),
            int(data.get('admin_fee_paid', 0)), int(data.get('ndnca_signed', 0)), int(data.get('popia_consent', 1))
        ))
    conn.commit()
    conn.close()

def get_pipeline_dataframe():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    try:
        df = pd.read_sql_query("SELECT * FROM franchisee_pipeline ORDER BY id DESC", conn)
    except Exception:
        conn.close()
        init_db(force_recreate=True)
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM franchisee_pipeline ORDER BY id DESC", conn)
    
    conn.close()
    return df

# Google Drive API Operations
def get_drive_service():
    if not HAS_GDRIVE:
        return None
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=GDRIVE_SCOPES)
            return build('drive', 'v3', credentials=creds)
        elif os.path.exists("service_account.json"):
            creds = service_account.Credentials.from_service_account_file("service_account.json", scopes=GDRIVE_SCOPES)
            return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Drive Auth Error: {e}")
    return None

def get_or_create_drive_folder(service, folder_name, parent_id=None):
    try:
        clean_name = folder_name.strip()
        query = f"name = '{clean_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = service.files().list(
            q=query, 
            spaces='drive', 
            fields="files(id, name)", 
            supportsAllDrives=True, 
            includeItemsFromAllDrives=True
        ).execute()
        
        files = results.get('files', [])
        if files:
            return files[0]['id']
        else:
            file_metadata = {'name': clean_name, 'mimeType': 'application/vnd.google-apps.folder'}
            if parent_id:
                file_metadata['parents'] = [parent_id]
            folder = service.files().create(body=file_metadata, fields='id', supportsAllDrives=True).execute()
            return folder.get('id')
    except Exception as e:
        print(f"Drive Folder Error: {e}")
        return None

def upload_pdf_to_drive(service, file_bytes, filename, parent_folder_id):
    try:
        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype='application/pdf', resumable=True)
        file_metadata = {'name': filename, 'parents': [parent_folder_id]}
        file = service.files().create(body=file_metadata, media_body=media, fields='id', supportsAllDrives=True).execute()
        return file.get('id')
    except Exception as e:
        print(f"Drive Upload Error: {e}")
        return None

def sync_pdf_to_local_and_cloud(location_name, pdf_bytes, pdf_filename):
    loc_clean = location_name.strip() if location_name else "Kwena_Square"
    loc_sub_dir = os.path.join(LOCATIONS_DIR, loc_clean)
    os.makedirs(loc_sub_dir, exist_ok=True)
    local_file_path = os.path.join(loc_sub_dir, pdf_filename)
    
    with open(local_file_path, "wb") as f:
        f.write(pdf_bytes)

    drive_service = get_drive_service()
    if not drive_service:
        return local_file_path, "Local saved (Drive API Inactive - check st.secrets)"

    try:
        site_folder_id = get_or_create_drive_folder(drive_service, loc_clean, parent_id=LOCATIONS_ROOT_DRIVE_ID)
        if site_folder_id:
            file_id = upload_pdf_to_drive(drive_service, pdf_bytes, pdf_filename, site_folder_id)
            if file_id:
                return local_file_path, f"✅ Folder created & PDF uploaded to Google Drive: 'Locations/{loc_clean}/{pdf_filename}'"
        return local_file_path, "Local saved, Drive folder sync skipped"
    except Exception as e:
        return local_file_path, f"Drive Sync Exception: {str(e)}"

# Email Dispatchers
def send_franchisee_email_pack(recipient_email, recipient_name, site_name, pdf_bytes, pdf_filename):
    sender_email = st.secrets.get("GMAIL_USER", "fantastic1za@gmail.com")
    sender_password = "ehyjsvzhffmbvuaf"

    try:
        msg = MIMEMultipart('related')
        msg['From'] = f"Phatbuns SA Master Rights <{sender_email}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"Phatbuns SA — Executive Franchisee Feasibility Pack & Brand Menus ({site_name})"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; font-size: 14px; color: #333333; line-height: 1.6;">
            <p>Dear {recipient_name if recipient_name else 'Valued Prospective Franchisee'},</p>
            <p>Thank you for your interest in Phatbuns South Africa. Attached is your Master Franchisee Investor Pack for <b>{site_name}</b>.</p>
            <p>Warm regards,</p>
            <p><b>Nisaar Ally</b><br/>Master Rights Holder — Phatbuns South Africa</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        part = MIMEApplication(pdf_bytes, Name=pdf_filename)
        part['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
        msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        return True, "Email dispatched successfully with PDF Pack!"
    except Exception as e:
        return False, str(e)

def send_investor_lead_notification(data):
    sender_email = st.secrets.get("GMAIL_USER", "fantastic1za@gmail.com")
    sender_password = "ehyjsvzhffmbvuaf"
    recipients = ["fantastic1za@gmail.com", "nisaar@fantastic1.com"]

    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"Phatbuns SA Pipeline Engine <{sender_email}>"
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = f"🚨 NEW FRANCHISEE LEAD: {data.get('full_name', 'Unknown Applicant')} ({data.get('preferred_site', 'Target Site Unassigned')})"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; font-size: 14px; color: #1A202C; line-height: 1.6; background-color: #F7FAFC; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #FFFFFF; border-radius: 10px; border: 1px solid #E2E8F0; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <div style="background-color: #1A365D; color: #FFFFFF; padding: 18px 24px; text-align: center;">
                    <h2 style="margin: 0; font-size: 20px; font-weight: 800;">PHATBUNS SOUTH AFRICA</h2>
                    <p style="margin: 4px 0 0 0; font-size: 12px; color: #CBD5E0;">Executive Franchisee Intake & Pipeline Notification</p>
                </div>
                <div style="padding: 24px;">
                    <p style="font-size: 15px; font-weight: bold; color: #2C5282; margin-top: 0;">A new prospective franchisee inquiry has been submitted and registered in the database.</p>
                    
                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                        <tr style="background-color: #EDF2F7;">
                            <td style="padding: 10px; font-weight: bold; border: 1px solid #E2E8F0; width: 40%;">Full Name</td>
                            <td style="padding: 10px; border: 1px solid #E2E8F0;">{data.get('full_name', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-weight: bold; border: 1px solid #E2E8F0;">Email Address</td>
                            <td style="padding: 10px; border: 1px solid #E2E8F0;"><a href="mailto:{data.get('email', '')}" style="color: #3182CE; text-decoration: none;">{data.get('email', 'N/A')}</a></td>
                        </tr>
                        <tr style="background-color: #EDF2F7;">
                            <td style="padding: 10px; font-weight: bold; border: 1px solid #E2E8F0;">Mobile / WhatsApp</td>
                            <td style="padding: 10px; border: 1px solid #E2E8F0;">{data.get('mobile', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-weight: bold; border: 1px solid #E2E8F0;">Preferred Target Site</td>
                            <td style="padding: 10px; font-weight: bold; color: #C53030; border: 1px solid #E2E8F0;">{data.get('preferred_site', 'N/A')}</td>
                        </tr>
                    </table>
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        return True, "Notification email sent to both addresses!"
    except Exception as e:
        return False, str(e)

def extract_legacy_pdf_parameters(pdf_file_bytes):
    extracted_data = {}
    if not HAS_PYPDF:
        return extracted_data
    
    try:
        reader = PdfReader(io.BytesIO(pdf_file_bytes))
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
            
        loc_match = re.search(r"Location Name\s*\|\s*([^\n\(]+)", full_text)
        if loc_match:
            extracted_data["location_name"] = loc_match.group(1).strip()
            
        shop_match = re.search(r"Shop\s*([0-9A-Za-z]+)", full_text)
        if shop_match:
            extracted_data["shop_code"] = shop_match.group(1).strip()

        gla_match = re.search(r"(\d+)\s*m²", full_text)
        if gla_match:
            extracted_data["internal_gla"] = float(gla_match.group(1))

        rent_match = re.search(r"R\s*([\d,]+)\s*/\s*m²", full_text)
        if rent_match:
            extracted_data["int_rent"] = float(rent_match.group(1).replace(",", ""))

        cap_match = re.search(r"R\s*([\d,]+)\s*Excl\.\s*VAT", full_text)
        if cap_match:
            extracted_data["turnkey_capital"] = float(cap_match.group(1).replace(",", ""))

        wc_match = re.search(r"WORKING CAPITAL\s*R\s*([\d,]+)", full_text)
        if wc_match:
            extracted_data["working_capital"] = float(wc_match.group(1).replace(",", ""))

    except Exception as e:
        print(f"PDF Parsing Exception: {e}")
        
    return extracted_data
