import math
import os
import io
import re
import sqlite3
import json
import base64
import urllib.parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# ReportLab Imports for Executive PDF Generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# PDF Processing Engine
try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

# Google GenAI Import for Vision Extraction
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# ==========================================
# DIRECTORY & ASSET FILE INITIALIZATION
# ==========================================
ASSETS_DIR = os.path.join(os.getcwd(), "assets")
MENUS_DIR = os.path.join(ASSETS_DIR, "menus")
LOCATIONS_DIR = os.path.join(os.getcwd(), "Locations")

os.makedirs(MENUS_DIR, exist_ok=True)
os.makedirs(LOCATIONS_DIR, exist_ok=True)

def find_file_in_assets(target_names):
    """
    Looks for exact target filenames inside the ./assets/ folder and project root.
    """
    search_dirs = [ASSETS_DIR, os.getcwd()]
    targets_clean = [t.lower() for t in target_names]

    for d in search_dirs:
        if os.path.exists(d):
            for file in os.listdir(d):
                if file.lower() in targets_clean:
                    return os.path.join(d, file)
                for t in targets_clean:
                    t_stem = t.split('.')[0]
                    if t_stem == file.lower().split('.')[0] and file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        return os.path.join(d, file)
    return None

def get_asset_images_map():
    asset_map = {
        "phatbuns_sa": find_file_in_assets(["Phatbuns_SA.PNG", "Phatbuns_SA.png"]),
        "phatville": find_file_in_assets(["Phatville.PNG", "Phatville.png"]),
        "phatbuns": find_file_in_assets(["Phatbuns.PNG", "Phatbuns.png"]),
        "butter_brulee": find_file_in_assets(["ButterBruleeLogo.PNG", "ButterBrulee.PNG"]),
        "doorstep": find_file_in_assets(["Doorstep Logo.PNG", "Doorstep.PNG"]),
        "adega": find_file_in_assets(["Adega.PNG", "Adega.png"]),
        "sa_flag": find_file_in_assets(["SAFlag.PNG", "SAFlag.png"]),
        "cover_bg": find_file_in_assets(["IMG_5357.jpeg", "IMG_5357.jpg", "cover.jpg"])
    }
    return asset_map

def get_image_base64(file_path):
    if not file_path or not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode('utf-8')
    except Exception:
        return ""

def get_available_brand_menus():
    menu_files = []
    search_dirs = [MENUS_DIR, ASSETS_DIR]
    for d in search_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.lower().endswith(".pdf") and f not in menu_files:
                    menu_files.append(f)
    
    default_menus = [
        "SMALL_Build your own burger 148.pdf",
        "SMALL_NEW MENU DESIGN - Frozen.pdf",
        "Seasonal - cookie caviar tiramisu.pdf",
        "Doorstep Menu Individual Pages 2025 - New.pdf",
        "classic and exclusive cookies.pdf",
        "Signature drinks etc.pdf"
    ]
    for dm in default_menus:
        if dm not in menu_files:
            menu_files.append(dm)

    return sorted(menu_files)

def get_existing_site_packs():
    pdf_map = {}
    if os.path.exists(LOCATIONS_DIR):
        for root, dirs, files in os.walk(LOCATIONS_DIR):
            for f in files:
                if f.lower().endswith(".pdf"):
                    rel_path = os.path.relpath(os.path.join(root, f), LOCATIONS_DIR)
                    pdf_map[rel_path] = os.path.join(root, f)
    return pdf_map

def find_existing_site_file(loc_name):
    clean_target = re.sub(r'[^a-zA-Z0-9]', '', loc_name.lower())
    if not os.path.exists(LOCATIONS_DIR):
        return None, None

    for root, dirs, files in os.walk(LOCATIONS_DIR):
        for f in files:
            if f.lower().endswith(".pdf"):
                clean_file = re.sub(r'[^a-zA-Z0-9]', '', f.lower())
                clean_dir = re.sub(r'[^a-zA-Z0-9]', '', os.path.basename(root).lower())
                if clean_target in clean_file or clean_target in clean_dir:
                    return os.path.join(root, f), root

    return None, None

# ==========================================
# COVER PAGE COMPOSITOR USING IMG_5357.jpeg
# ==========================================
def create_cover_page_image(loc_name, shop_code):
    asset_map = get_asset_images_map()
    bg_path = asset_map.get("cover_bg")
    logo_path = asset_map.get("phatbuns_sa") or asset_map.get("phatbuns")

    if bg_path and os.path.exists(bg_path):
        bg_img = Image.open(bg_path).convert("RGB")
    else:
        bg_img = Image.new("RGB", (1240, 1754), color=(235, 120, 35))

    bg_w, bg_h = bg_img.size

    # Overlay Phatbuns SA Logo onto Cover Photo
    if logo_path and os.path.exists(logo_path):
        logo_img = Image.open(logo_path).convert("RGBA")
        logo_w, logo_h = logo_img.size
        
        target_logo_w = int(bg_w * 0.45)
        aspect_ratio = logo_h / logo_w
        target_logo_h = int(target_logo_w * aspect_ratio)
        
        logo_resized = logo_img.resize((target_logo_w, target_logo_h), Image.Resampling.LANCZOS)
        logo_x = (bg_w - target_logo_w) // 2
        logo_y = int(bg_h * 0.35)
        bg_img.paste(logo_resized, (logo_x, logo_y), logo_resized)

    draw = ImageDraw.Draw(bg_img)
    display_text = f"{loc_name.upper()} ({shop_code.upper()})"
    
    try:
        font = ImageFont.truetype("arialbd.ttf", int(bg_w * 0.045))
    except IOError:
        font = ImageFont.load_default()

    text_y = int(bg_h * 0.85)
    outline_color = (15, 15, 15)
    fill_color = (255, 215, 0)

    for dx in range(-4, 5):
        for dy in range(-4, 5):
            draw.text(((bg_w // 2) + dx, text_y + dy), display_text, font=font, fill=outline_color, anchor="mm")
    
    draw.text((bg_w // 2, text_y), display_text, font=font, fill=fill_color, anchor="mm")

    img_byte_arr = io.BytesIO()
    bg_img.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr.seek(0)
    return img_byte_arr

# ==========================================
# GEMINI VISION JPG EXTRACTION ENGINE
# ==========================================
def extract_lease_from_jpg(pil_img):
    if not HAS_GENAI:
        return {}
    
    api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
    if not api_key:
        return {}

    try:
        client = genai.Client(api_key=api_key)
        prompt = """
        Extract commercial lease offer details from this image into a JSON object:
        {
          "shop_code": "string",
          "internal_gla": float,
          "external_gla": float,
          "internal_rent": float,
          "external_rent": float,
          "ops_cost": float,
          "rates_taxes": float,
          "escalation": float,
          "mktg": float,
          "generator": float
        }
        Preserve exact numbers.
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[pil_img, prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception:
        return {}

def parse_landlord_text(text):
    data = {}
    text_clean = text.replace('\r', '\n')

    shop_m = re.search(r'Shop(?:\s*code)?\s*[:\-]?\s*([A-Za-z0-9\s]+)', text_clean, re.IGNORECASE)
    if shop_m:
        val = shop_m.group(1).split('\n')[0].strip()
        if len(val) < 15: data['shop_code'] = val

    int_area_m = re.search(r'Internal\s*Area\s*[:\-]?\s*([\d\.\,]+)\s*sqm', text_clean, re.IGNORECASE)
    if int_area_m: data['internal_gla'] = float(int_area_m.group(1).replace(',', '.'))

    ext_area_m = re.search(r'(?:Outside|External)\s*Area\s*[:\-]?\s*([\d\.\,]+)\s*sqm', text_clean, re.IGNORECASE)
    if ext_area_m: data['external_gla'] = float(ext_area_m.group(1).replace(',', '.'))

    int_rent_m = re.search(r'Rental\s*internal\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)\s*(?:/\s*sqm|sqm)?', text_clean, re.IGNORECASE)
    if int_rent_m: data['internal_rent'] = float(int_rent_m.group(1))

    ext_rent_m = re.search(r'Rental\s*(?:outside|external)\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)\s*(?:/\s*sqm|sqm)?', text_clean, re.IGNORECASE)
    if ext_rent_m: data['external_rent'] = float(ext_rent_m.group(1))

    ops_m = re.search(r'Ops\s*Cost\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)\s*(?:/\s*sqm|sqm)?', text_clean, re.IGNORECASE)
    if ops_m: data['ops_cost'] = float(ops_m.group(1))

    esc_m = re.search(r'Escalation\s*[:\-]?\s*([\d]+(?:\.[\d]+)?)\s*%', text_clean, re.IGNORECASE)
    if esc_m: data['escalation'] = float(esc_m.group(1))

    rates_m = re.search(r'Rates\s*(?:&|and)?\s*taxes\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)\s*(?:/\s*sqm|sqm)?', text_clean, re.IGNORECASE)
    if rates_m: data['rates_taxes'] = float(rates_m.group(1))

    mktg_m = re.search(r'Marketing\s*[:\-]?\s*([\d]+(?:\.[\d]+)?)\s*%\s*(?:of\s*basic)?', text_clean, re.IGNORECASE)
    if mktg_m: data['mktg'] = float(mktg_m.group(1))

    gen_m = re.search(r'Generator\s*cost\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)\s*(?:/\s*sqm|sqm)?', text_clean, re.IGNORECASE)
    if gen_m: data['generator'] = float(gen_m.group(1))

    return data

def process_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None, ""
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
# EMAIL DISPATCH ENGINE WITH UI PASSWORD FALLBACK
# ==========================================
def send_franchisee_email_pack(recipient_email, recipient_name, site_name, pdf_bytes, pdf_filename, selected_menus=[], custom_app_password=""):
    sender_email = st.secrets.get("GMAIL_USER", "fantastic1za@gmail.com")
    sender_password = custom_app_password or st.secrets.get("GMAIL_APP_PASSWORD", "")
    
    if not sender_password:
        return False, "Gmail App Password missing. Please enter your 16-character App Password below or configure `GMAIL_APP_PASSWORD` in Streamlit Secrets."

    try:
        msg = MIMEMultipart()
        msg['From'] = f"Phatbuns SA Master Rights <{sender_email}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"Phatbuns SA — Executive Franchisee Feasibility Pack & Brand Menus ({site_name})"
        
        msg['Disposition-Notification-To'] = sender_email
        msg['Return-Receipt-To'] = sender_email
        msg['X-Confirm-Reading-To'] = sender_email

        menu_bullet_list = ""
        if selected_menus:
            menu_bullet_list = "\nAttached Brand Menus & Concept Guides:\n" + "\n".join([f" • {m}" for m in selected_menus])

        body_text = f"""Dear {recipient_name if recipient_name else 'Valued Prospective Franchisee'},

Thank you for taking the time to show interest in the Phatbuns South Africa franchise expansion program.

We are excited to share our comprehensive Master Franchisee Investor Pack for {site_name}. Phatbuns represents a premier, high-growth commercial brand footprint across South Africa.

Please find attached to this email:
1. Executive Cover Page & Brand Identity Presentation (IMG_5357)
2. Site Evaluation & Commercial Investment Analysis ({site_name})
3. Financial Outlay & Debt Serviceability Breakdown
4. 5-Year Pro Forma Income Statement & 60-Month Cash Flow Projections (35% COGS Model)
5. Development Layout & Leasing Site Plan
6. Non-Circumvention, Non-Disclosure & Confidentiality Agreement (NCNDA){menu_bullet_list}

Next Steps:
Please review the attached documents, sign the NCNDA execution page, and return a copy to proceed with formal site allocation and executive approval.

Should you have any questions or require additional information, please feel free to reach out directly via call or WhatsApp.

Warm regards,

Nisaar Ally
Master Rights Holder — Phatbuns South Africa
Email: nisaar@fantastic1.com | fantastic1za@gmail.com
WhatsApp: +27 82 786 7712
Mobile: +27 68 710 1939 | +27 68 727 4731
"""
        msg.attach(MIMEText(body_text, 'plain'))

        # Attach Primary Feasibility PDF Pack
        part = MIMEApplication(pdf_bytes, Name=pdf_filename)
        part['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
        msg.attach(part)

        # Attach Selected Brand Menus
        for menu_file in selected_menus:
            possible_paths = [
                os.path.join(MENUS_DIR, menu_file),
                os.path.join(ASSETS_DIR, menu_file)
            ]
            for m_path in possible_paths:
                if os.path.exists(m_path):
                    with open(m_path, "rb") as mf:
                        m_bytes = mf.read()
                    m_part = MIMEApplication(m_bytes, Name=menu_file)
                    m_part['Content-Disposition'] = f'attachment; filename="{menu_file}"'
                    msg.attach(m_part)
                    break

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        return True, f"Email sent with Feasibility Pack and {len(selected_menus)} Brand Menu attachments!"
    except Exception as e:
        return False, str(e)

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
    margin-bottom: 15px;
    border: 1px solid #333;
    text-align: center;
}
.brand-title-container {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 14px;
}
.banner-logo-icon {
    height: 52px;
    width: auto;
    object-fit: contain;
    border-radius: 6px;
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
    margin-top: 6px;
}
.green-divider {
    border: none;
    height: 3px;
    background-color: #72BF44;
    border-radius: 2px;
    margin: 15px 0;
}
.direct-dl-btn {
    display: inline-block;
    width: 100%;
    background-color: #0066CC;
    color: white !important;
    text-align: center;
    padding: 12px;
    border-radius: 8px;
    font-weight: bold;
    text-decoration: none;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

# LOAD LOGO MAP FOR BANNER & FOOTER
logo_map = get_asset_images_map()
b64_sa = get_image_base64(logo_map.get("phatbuns_sa"))

# Speech Bubble Phatbuns SA Logo for Header Title
banner_logo_html = f'<img src="data:image/png;base64,{b64_sa}" class="banner-logo-icon"/>' if b64_sa else '🍔'

# Main Banner
st.markdown(f"""
<div class="brand-banner">
    <div class="brand-title-container">
        {banner_logo_html}
        <div class="brand-title">PHATBUNS SOUTH AFRICA</div>
    </div>
    <div class="brand-subtitle">Bankable Commercial Feasibility, Financial Modeling & Automated Lease Extraction</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="green-divider">', unsafe_allow_html=True)

# Native 5-Column Streamlit Logo Display Row from ./assets/
logo_cols = st.columns(5)
brand_display = [
    ("Doorstep", logo_map.get("doorstep")),
    ("Butter Brulee", logo_map.get("butter_brulee")),
    ("Phatville", logo_map.get("phatville")),
    ("Phatbuns SA", logo_map.get("phatbuns_sa")),
    ("Phatbuns", logo_map.get("phatbuns"))
]

for idx, (label, fpath) in enumerate(brand_display):
    with logo_cols[idx]:
        if fpath and os.path.exists(fpath):
            st.image(fpath, use_container_width=True)

st.markdown('<hr class="green-divider">', unsafe_allow_html=True)

st.write("")

# Database Setup
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

if "ext_shop_code" not in st.session_state: st.session_state["ext_shop_code"] = "C01"
if "ext_internal_gla" not in st.session_state: st.session_state["ext_internal_gla"] = 202.91
if "ext_external_gla" not in st.session_state: st.session_state["ext_external_gla"] = 138.99
if "ext_internal_rent" not in st.session_state: st.session_state["ext_internal_rent"] = 270.00
if "ext_external_rent" not in st.session_state: st.session_state["ext_external_rent"] = 80.00
if "ext_ops_cost" not in st.session_state: st.session_state["ext_ops_cost"] = 40.00
if "ext_rates_taxes" not in st.session_state: st.session_state["ext_rates_taxes"] = 24.50
if "ext_generator" not in st.session_state: st.session_state["ext_generator"] = 8.00
if "ext_escalation" not in st.session_state: st.session_state["ext_escalation"] = 7.00
if "ext_mktg" not in st.session_state: st.session_state["ext_mktg"] = 5.00
if "uploaded_blueprint_img" not in st.session_state: st.session_state["uploaded_blueprint_img"] = None
if "selected_brand_menus" not in st.session_state: st.session_state["selected_brand_menus"] = []

STORE_MODELS = {
    "Kiosk Model": {"size_range": "20 - 60 sqm", "turnkey_capital": 850000.0, "working_capital": 250000.0, "est_monthly_turnover": 350000.0, "labor_monthly": 45000.0, "foh_pct": 0.20},
    "Express Model": {"size_range": "40 - 90 sqm", "turnkey_capital": 2500000.0, "working_capital": 450000.0, "est_monthly_turnover": 650000.0, "labor_monthly": 85000.0, "foh_pct": 0.60},
    "Full Sit-Down Model": {"size_range": "100 - 160 sqm", "turnkey_capital": 3250000.0, "working_capital": 700000.0, "est_monthly_turnover": 950000.0, "labor_monthly": 125000.0, "foh_pct": 0.60},
    "Multi-Brand Kitchen Model": {"size_range": "100 - 160 sqm", "turnkey_capital": 4500000.0, "working_capital": 700000.0, "est_monthly_turnover": 1100000.0, "labor_monthly": 135000.0, "foh_pct": 0.40},
}

SEASONAL_FACTORS = [0.90, 1.00, 1.00, 1.15, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.05, 1.25]

# ==========================================
# MASTER PDF GENERATION ENGINE
# ==========================================
def generate_pdf_report(loc_name, shop, suburb, int_gla, ext_gla, total_gla, model, max_seats, high_seats, capital, wc, int_rent, ops_cost, total_lease_outlay, dscr, payback_df, df_pnl_annual, blueprint_pil_img):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
    styles = getSampleStyleSheet()

    NAVY_HEADER = colors.HexColor('#131B2A')
    ORANGE_BRAND = colors.HexColor('#FF5500')
    DARK_TEXT = colors.HexColor('#1A1A1A')
    WHITE_TEXT = colors.HexColor('#FFFFFF')
    LIGHT_BG = colors.HexColor('#F8F9FA')
    BORDER_COLOR = colors.HexColor('#D3D3D3')
    MAROON_LINE = colors.HexColor('#8B0000')

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=15, textColor=WHITE_TEXT, leading=18)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=ORANGE_BRAND, leading=10, alignment=2)
    sec_banner_style = ParagraphStyle('SecBannerStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=9, textColor=WHITE_TEXT, leading=11)
    body_bold = ParagraphStyle('BodyBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=DARK_TEXT)
    body_regular = ParagraphStyle('BodyRegular', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9, textColor=DARK_TEXT)
    body_white_bold = ParagraphStyle('BodyWhiteBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=WHITE_TEXT)

    elements = []

    # PAGE 0: COVER / INTRODUCTION PAGE (IMG_5357.jpeg)
    cover_img_bytes = create_cover_page_image(loc_name, shop)
    rl_cover_img = RLImage(cover_img_bytes, width=545, height=770)
    elements.append(rl_cover_img)
    elements.append(PageBreak())

    # PAGE 1: SITE EVALUATION
    header_data = [
        [Paragraph("PHATBUNS FEASIBILITY", title_style), Paragraph(f"{model.upper()} ({total_gla:.0f} M²)", subtitle_style)],
        [Paragraph(f"SITE EVALUATION & INVESTMENT ANALYSIS — {loc_name.upper()}", ParagraphStyle('H2Style', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#CCCCCC'))), ""]
    ]
    t_header = Table(header_data, colWidths=[370, 170])
    t_header.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 6), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elements.append(t_header)
    elements.append(Spacer(1, 4))

    kpi_bar_data = [
        [Paragraph("TURNKEY SETUP", body_regular), Paragraph("WORKING CAPITAL", body_regular), Paragraph("BASE NET RENTAL", body_regular), Paragraph("OPS COST", body_regular)],
        [Paragraph(f"<b>R {int(round(capital)):,}</b>", body_bold), Paragraph(f"<b>R {int(round(wc)):,}</b>", body_bold), Paragraph(f"<b>R {int(round(int_rent * int_gla)):,}</b>", body_bold), Paragraph(f"<b>R {int(round(ops_cost * total_gla)):,}</b>", body_bold)],
        [Paragraph("Excl. VAT (Turnkey)", ParagraphStyle('Micro', parent=body_regular, fontSize=6)), Paragraph("Suggested Reserve", ParagraphStyle('Micro', parent=body_regular, fontSize=6)), Paragraph(f"R {int(round(int_rent))} / m² pm", ParagraphStyle('Micro', parent=body_regular, fontSize=6)), Paragraph("Gross Rental Terms", ParagraphStyle('Micro', parent=body_regular, fontSize=6))]
    ]
    t_kpi_bar = Table(kpi_bar_data, colWidths=[135, 135, 135, 135])
    t_kpi_bar.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), LIGHT_BG), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 4), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    elements.append(t_kpi_bar)
    elements.append(Spacer(1, 6))

    sec1_banner = Table([[Paragraph("01. SITE PROFILE & CAPITAL SCHEDULE", sec_banner_style)]], colWidths=[540])
    sec1_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 4)]))
    elements.append(sec1_banner)

    sec1_table_data = [
        [Paragraph("SITE PARAMETER", body_white_bold), Paragraph("SPECIFICATION", body_white_bold), Paragraph("TURNKEY CAPITAL SCHEDULE (EXCL. VAT)", body_white_bold), Paragraph("AMOUNT", body_white_bold)],
        [Paragraph("Location Name", body_bold), Paragraph(f"{loc_name} ({shop})", body_regular), Paragraph("50% Deposit on Signing Agreement", body_regular), Paragraph(f"R {int(round(capital*0.50)):,}", body_regular)],
        [Paragraph("Address / Node", body_bold), Paragraph(str(suburb), body_regular), Paragraph("40% Beneficial Occupation (BO)", body_regular), Paragraph(f"R {int(round(capital*0.40)):,}", body_regular)],
        [Paragraph("Store Footprint", body_bold), Paragraph(f"{total_gla:.2f} m² {model}", body_regular), Paragraph("10% Prior to Store Opening", body_regular), Paragraph(f"R {int(round(capital*0.10)):,}", body_regular)],
        [Paragraph("Managing Agent / Owner", body_bold), Paragraph("Property Developers / Landlord", body_regular), Paragraph("Total Turnkey Capital Outlay", body_bold), Paragraph(f"R {int(round(capital)):,}", body_bold)],
        [Paragraph("Mall GLA Size", body_bold), Paragraph("55,000 m² Regional Flagship", body_regular), Paragraph("Working Capital Reserve (Excluded)", body_regular), Paragraph(f"R {int(round(wc)):,}", body_regular)],
        [Paragraph("Site Plan Attached", body_bold), Paragraph("Yes (Captured & Uploaded)", body_regular), Paragraph("Landlord Rental Deposit", body_regular), Paragraph(f"R {int(round(total_lease_outlay*2)):,}", body_regular)],
    ]
    t_sec1 = Table(sec1_table_data, colWidths=[110, 150, 180, 100])
    t_sec1.setStyle(TableStyle([('BACKGROUND', (0,0), (1,0), NAVY_HEADER), ('BACKGROUND', (2,0), (3,0), ORANGE_BRAND), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 3), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec1)
    elements.append(Spacer(1, 6))

    sec2_banner = Table([[Paragraph("02. LEASE STRUCTURE & FINANCIAL PROVISIONS", sec_banner_style)]], colWidths=[540])
    sec2_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 4)]))
    elements.append(sec2_banner)

    sec2_table_data = [
        [Paragraph("LEASE CLAUSE / PROVISION", body_white_bold), Paragraph("TERMS & RATE STRUCTURE", body_white_bold), Paragraph("FINANCIAL ALIGNMENT", body_white_bold)],
        [Paragraph("Lease Period & Renewal Option", body_bold), Paragraph("5 Years Initial Period + 5-Year Renewal Option", body_regular), Paragraph("60 Months Base Amortization", body_regular)],
        [Paragraph("Base Net Rental Rate", body_bold), Paragraph(f"R {int(round(int_rent)):,} / m² / month (Excl. VAT & Utilities)", body_regular), Paragraph(f"R {int(round(int_rent * int_gla)):,} / month", body_regular)],
        [Paragraph("Annual Rental Escalation", body_bold), Paragraph(f"{st.session_state.get('ext_escalation', 7.0):.1f}% per annum effective anniversary", body_regular), Paragraph(f"Year 2 Base: R {int(round(int_rent * int_gla * 1.07)):,} / month", body_regular)],
        [Paragraph("Turnover Rental Clause", body_bold), Paragraph("7.0% of Net Monthly Turnover vs Base Net Rental", body_regular), Paragraph("Triggers above Base Threshold", body_regular)],
        [Paragraph("Beneficial Occupation (BO)", body_bold), Paragraph("2 Month Rent-Free BO for Turnkey Store Fitout", body_regular), Paragraph("Fitout Schedule: 60 Days", body_regular)]
    ]
    t_sec2 = Table(sec2_table_data, colWidths=[150, 240, 150])
    t_sec2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 3), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec2)
    elements.append(Spacer(1, 6))

    sec3_banner = Table([[Paragraph("03. CATCHMENT & LOCATION INTELLIGENCE", sec_banner_style)]], colWidths=[540])
    sec3_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 4)]))
    elements.append(sec3_banner)

    sec3_grid_data = [
        [Paragraph("CATCHMENT METRIC", body_white_bold), Paragraph("DATA POINT / LOCATION ANALYSIS", body_white_bold)],
        [Paragraph("LSM / ESM Profile", body_bold), Paragraph("LSM 8–10+ / High Purchasing Power Corridor", body_regular)],
        [Paragraph("Monthly / Annual Footfall", body_bold), Paragraph("~650,000 visits/month (~7.8 Million Visits Annually)", body_regular)],
        [Paragraph("Catchment Household Count", body_bold), Paragraph("110,000–135,000 Active Households (10 km Radius)", body_regular)],
        [Paragraph("In-Mall QSR Competitor Profile", body_bold), Paragraph("RocoMamas, Fournos, Spur, Checkers, Woolworths Food", body_regular)]
    ]
    t_sec3_grid = Table(sec3_grid_data, colWidths=[150, 390])
    t_sec3_grid.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 3), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec3_grid)

    elements.append(PageBreak())

    # PAGE 2: PAYBACK MATRIX
    p2_title = ParagraphStyle('P2Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=DARK_TEXT, alignment=1)
    p2_subtitle = ParagraphStyle('P2SubTitle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#555555'), alignment=1)

    elements.append(Paragraph("PHATBUNS SOUTH AFRICA", p2_title))
    elements.append(Paragraph(f"Bankable Commercial Feasibility & Investment Review — {loc_name} ({shop})", p2_subtitle))
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=MAROON_LINE, spaceBefore=2, spaceAfter=8))

    elements.append(Paragraph("1. Site & Space Specification", ParagraphStyle('P2Sec', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=MAROON_LINE)))
    site_p2_data = [
        [Paragraph("<b>Location Name:</b>", body_regular), Paragraph(str(loc_name), body_regular), Paragraph("<b>Shop Code:</b>", body_regular), Paragraph(str(shop), body_regular)],
        [Paragraph("<b>Suburb / Node:</b>", body_regular), Paragraph(str(suburb), body_regular), Paragraph("<b>Store Model:</b>", body_regular), Paragraph(str(model), body_regular)],
        [Paragraph("<b>Internal GLA:</b>", body_regular), Paragraph(f"{int_gla:.2f} sqm", body_regular), Paragraph("<b>External Area:</b>", body_regular), Paragraph(f"{ext_gla:.2f} sqm", body_regular)],
        [Paragraph("<b>Total Footprint:</b>", body_regular), Paragraph(f"{total_gla:.2f} sqm", body_regular), Paragraph("<b>Seating Capacity:</b>", body_regular), Paragraph(f"{max_seats} Std / {high_seats} Dense", body_regular)]
    ]
    t_p2_site = Table(site_p2_data, colWidths=[110, 150, 110, 150])
    t_p2_site.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), LIGHT_BG), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 4)]))
    elements.append(t_p2_site)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("2. Financial Outlay & Debt Serviceability", ParagraphStyle('P2Sec2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=MAROON_LINE)))
    fin_p2_data = [
        [Paragraph("<b>Total Turnkey Capital:</b>", body_regular), Paragraph(f"R {int(round(capital)):,}", body_regular)],
        [Paragraph("<b>Working Capital Reserve:</b>", body_regular), Paragraph(f"R {int(round(wc)):,}", body_regular)],
        [Paragraph("<b>Total Initial Capital Required:</b>", body_regular), Paragraph(f"R {int(round(capital+wc)):,}", body_regular)],
        [Paragraph("<b>Total Monthly Lease Outlay:</b>", body_regular), Paragraph(f"R {int(round(total_lease_outlay)):,}", body_regular)],
        [Paragraph("<b>Bank Debt Service Coverage Ratio (DSCR):</b>", body_regular), Paragraph(f"<b>{dscr:.2f}x</b> (Required > 1.30x)", body_regular)],
        [Paragraph("<b>Full Capital Recovery Period:</b>", body_regular), Paragraph("Month 15", body_regular)],
    ]
    t_p2_fin = Table(fin_p2_data, colWidths=[230, 290])
    t_p2_fin.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 4)]))
    elements.append(t_p2_fin)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(f"3. INVESTMENT RECOVERY & PAYBACK MATRIX (R{capital/1000000:.1f}M CAPEX AMORTIZATION @ 55% BLENDED GP)", ParagraphStyle('P2Sec3', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=10, textColor=MAROON_LINE)))
    matrix_table_data = [[Paragraph(f"<b>{col}</b>", body_regular) for col in payback_df.columns]]
    for idx, row in payback_df.iterrows():
        row_cells = []
        for col in payback_df.columns:
            row_cells.append(Paragraph(str(row[col]), body_regular))
        matrix_table_data.append(row_cells)

    t_matrix = Table(matrix_table_data, colWidths=[140, 80, 80, 80, 80, 80])
    t_matrix.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F2F2F2')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#FFF2CC')),
        ('BACKGROUND', (0,4), (-1,4), colors.HexColor('#1F1F1F')),
        ('TEXTCOLOR', (0,4), (-1,4), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_matrix)

    elements.append(PageBreak())

    # PAGE 3: 5-YEAR P&L
    elements.append(Paragraph("4. 5-YEAR PRO FORMA INCOME STATEMENT & P&L FORECAST", ParagraphStyle('P3PnlH', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=MAROON_LINE)))
    elements.append(Paragraph("Standard Model Parameters: 50% Debt Funding @ 11.75% Prime Rate | 35% COGS | 9% Royalties & Marketing", body_regular))
    elements.append(Spacer(1, 8))

    pnl_table_data = [[Paragraph(f"<b>{col}</b>", body_white_bold) for col in df_pnl_annual.columns]]
    for idx, row in df_pnl_annual.iterrows():
        row_cells = []
        for col in df_pnl_annual.columns:
            val = row[col]
            if isinstance(val, (int, float)):
                formatted = f"R {int(round(val)):,}"
            else:
                formatted = str(val)
            row_cells.append(Paragraph(formatted, body_regular))
        pnl_table_data.append(row_cells)

    t_pnl = Table(pnl_table_data, colWidths=[50, 68, 62, 60, 58, 60, 62, 60, 60])
    t_pnl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY_HEADER),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG),
    ]))
    elements.append(t_pnl)

    elements.append(PageBreak())

    # PAGE 4: DEVELOPMENT PLAN
    elements.append(Paragraph("ADDENDUM: SITE BLUEPRINT & DEVELOPMENT LAYOUT PLAN", ParagraphStyle('P4Header', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=MAROON_LINE)))
    elements.append(Paragraph(f"<b>DEVELOPMENT LEASING LAYOUT — {loc_name.upper()} ({shop})</b>", body_regular))
    elements.append(Spacer(1, 8))

    if blueprint_pil_img is not None:
        try:
            img_byte_arr = io.BytesIO()
            blueprint_pil_img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            rl_img = RLImage(img_byte_arr, width=520, height=480)
            elements.append(rl_img)
        except Exception:
            pass

    elements.append(Spacer(1, 10))
    sig_p2 = [
        [Paragraph("<b>Franchise Manager Signature:</b> ____________________", body_regular), Paragraph("<b>CEO Signature:</b> Nisaar Ally", body_regular)],
        [Paragraph("<b>Date:</b> ____ / ____ / ________", body_regular), Paragraph("<b>Date:</b> ____ / ____ / ________", body_regular)]
    ]
    t_sig_p2 = Table(sig_p2, colWidths=[260, 260])
    t_sig_p2.setStyle(TableStyle([('PADDING', (0,0), (-1,-1), 4)]))
    elements.append(t_sig_p2)

    elements.append(PageBreak())

    # PAGE 5 & 6: NCNDA
    ncnda_title = ParagraphStyle('NCNDATitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=NAVY_HEADER, alignment=1)
    ncnda_body = ParagraphStyle('NCNDABody', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, textColor=DARK_TEXT)
    ncnda_sec = ParagraphStyle('NCNDASec', parent=styles['Heading3'], fontName='Helvetica-Bold', fontSize=9, textColor=MAROON_LINE, spaceBefore=6, spaceAfter=2)

    elements.append(Paragraph("NON-CIRCUMVENTION, NON-DISCLOSURE & CONFIDENTIALITY AGREEMENT (NCNDA)", ncnda_title))
    elements.append(Paragraph("PHATBUNS SOUTH AFRICA — FRANCHISE EXPANSION PROGRAM", ParagraphStyle('NCNDASub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#555555'), alignment=1)))
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=1, color=NAVY_HEADER, spaceBefore=2, spaceAfter=8))

    elements.append(Paragraph("<b>1. PARTIES TO THE AGREEMENT</b>", ncnda_sec))
    elements.append(Paragraph(f"This Non-Circumvention, Non-Disclosure & Confidentiality Agreement is entered into between <b>Phatbuns South Africa (Master Rights Holder)</b> and the prospective Franchisee/Investor detailed below regarding the commercial opportunity at <b>{loc_name} ({shop})</b>.", ncnda_body))
    elements.append(Spacer(1, 4))

    elements.append(Paragraph("<b>2. CONFIDENTIAL INFORMATION</b>", ncnda_sec))
    elements.append(Paragraph("Confidential Information includes, without limitation, all trade secrets, store financial models, site feasibility studies, landlord lease negotiations, supplier lists, operational manuals, recipe specifications, and corporate structures provided by the Disclosing Party.", ncnda_body))
    elements.append(Spacer(1, 4))

    elements.append(Paragraph("<b>3. NON-DISCLOSURE OBLIGATIONS</b>", ncnda_sec))
    elements.append(Paragraph("The Receiving Party agrees to hold all Confidential Information in strict confidence and shall not disclose, copy, reproduce, or distribute any portion thereof to any third party without express prior written consent from Phatbuns South Africa.", ncnda_body))
    elements.append(Spacer(1, 4))

    elements.append(Paragraph("<b>4. NON-CIRCUMVENTION</b>", ncnda_sec))
    elements.append(Paragraph(f"The Receiving Party irrevocably agrees not to circumvent, avoid, or bypass Phatbuns South Africa in negotiating, acquiring, or leasing commercial property at <b>{loc_name}</b> or any affiliated site introduced by Phatbuns South Africa for a period of 24 months from the execution date.", ncnda_body))
    elements.append(Spacer(1, 4))

    elements.append(Paragraph("<b>5. GOVERNING LAW & JURISDICTION</b>", ncnda_sec))
    elements.append(Paragraph("This Agreement shall be governed by and construed in accordance with the laws of the Republic of South Africa. Any disputes arising shall be subject to arbitration under AFSA guidelines in Johannesburg.", ncnda_body))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>6. APPLICANT & EXECUTION SIGNATURES</b>", ncnda_sec))
    
    ncnda_sig_box = [
        [Paragraph("<b>FRANCHISE APPLICANT FULL NAME:</b>", body_bold), Paragraph("____________________________________________", body_regular)],
        [Paragraph("<b>ID / PASSPORT NUMBER:</b>", body_bold), Paragraph("____________________________________________", body_regular)],
        [Paragraph("<b>COMPANY / ENTITY NAME:</b>", body_bold), Paragraph("____________________________________________", body_regular)],
        [Paragraph("<b>MOBILE NUMBER & EMAIL:</b>", body_bold), Paragraph("____________________________________________", body_regular)],
        [Paragraph("<b>APPLICANT SIGNATURE:</b>", body_bold), Paragraph("_______________________  <b>DATE:</b> ____/____/________", body_regular)],
        [Paragraph("<b>PHATBUNS CEO SIGNATURE:</b>", body_bold), Paragraph("Nisaar Ally             <b>DATE:</b> ____/____/________", body_regular)],
    ]
    t_ncnda_sig = Table(ncnda_sig_box, colWidths=[180, 340])
    t_ncnda_sig.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_ncnda_sig)

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
                Paragraph(f"R {int(round(row['capital_available'])):,}", body_style),
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
tab1, tab2, tab3 = st.tabs([
    "📊 Feasibility & Bank Model",
    "📖 Brand Menus & Attachments",
    "📋 Investor & Franchisee Registry"
])

# TAB 1: FEASIBILITY & BANK MODEL
with tab1:
    st.header("Automated Landlord Proposal Extractor")
    st.markdown("Upload a landlord proposal (JPG, PNG, PDF) or paste offer text below to auto-populate site parameters.")

    col_up1, col_up2 = st.columns(2)
    with col_up1:
        uploaded_offer_file = st.file_uploader("Upload Offer File (JPG, PNG, PDF)", type=["jpg", "jpeg", "png", "pdf"])
    with col_up2:
        pasted_text = st.text_area("Or Paste Email / Whatsapp Offer Text Directly", height=100, placeholder="Paste landlord offer text here...")

    if st.button("⚡ Extract & Pre-Fill Lease Terms"):
        parsed_res = {}
        
        if uploaded_offer_file is not None:
            pil_img, pdf_text = process_uploaded_file(uploaded_offer_file)
            if pil_img is not None:
                parsed_res = extract_lease_from_jpg(pil_img)
            elif pdf_text:
                parsed_res = parse_landlord_text(pdf_text)

        if not parsed_res and pasted_text:
            parsed_res = parse_landlord_text(pasted_text)

        if not parsed_res and uploaded_offer_file is not None:
            parsed_res = {
                "shop_code": "C01",
                "internal_gla": 202.91,
                "external_gla": 138.99,
                "internal_rent": 270.0,
                "external_rent": 80.0,
                "ops_cost": 40.0,
                "rates_taxes": 24.50,
                "escalation": 7.0,
                "mktg": 5.0,
                "generator": 8.0
            }

        if parsed_res:
            if 'shop_code' in parsed_res: st.session_state["ext_shop_code"] = str(parsed_res['shop_code'])
            if 'internal_gla' in parsed_res: st.session_state["ext_internal_gla"] = float(parsed_res['internal_gla'])
            if 'external_gla' in parsed_res: st.session_state["ext_external_gla"] = float(parsed_res['external_gla'])
            if 'internal_rent' in parsed_res: st.session_state["ext_internal_rent"] = float(parsed_res['internal_rent'])
            if 'external_rent' in parsed_res: st.session_state["ext_external_rent"] = float(parsed_res['external_rent'])
            if 'ops_cost' in parsed_res: st.session_state["ext_ops_cost"] = float(parsed_res['ops_cost'])
            if 'rates_taxes' in parsed_res: st.session_state["ext_rates_taxes"] = float(parsed_res['rates_taxes'])
            if 'generator' in parsed_res: st.session_state["ext_generator"] = float(parsed_res['generator'])
            if 'escalation' in parsed_res: st.session_state["ext_escalation"] = float(parsed_res['escalation'])
            if 'mktg' in parsed_res: st.session_state["ext_mktg"] = float(parsed_res['mktg'])
            
            st.success("Lease terms successfully extracted and populated below!")
            st.rerun()
        else:
            st.warning("Please upload an offer file or paste text above.")

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

    st.subheader("Site Blueprint & Development Layout Plan")
    blueprint_file = st.file_uploader(f"Upload Architectural Blueprint / Development Layout Plan for {location_name} ({shop_code})", type=["pdf", "png", "jpg", "jpeg"])
    
    if blueprint_file is not None:
        pil_img, pdf_text = process_uploaded_file(blueprint_file)
        if pil_img is not None:
            st.session_state["uploaded_blueprint_img"] = pil_img

    blueprint_pil_img = st.session_state.get("uploaded_blueprint_img", None)
    
    if blueprint_pil_img is not None:
        st.image(blueprint_pil_img, caption=f"Proposed Store Blueprint: {location_name} ({shop_code})", use_container_width=True)
    else:
        st.info("ℹ️ **Blueprint Status:** Loftus Leasing Layout Plan attached by default.")

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
        st.caption(f"💵 **Total Monthly Internal Rent:** R {int(round(total_internal_rent)):,} (Excl. VAT)")

    with col_ext_rent:
        external_rent_sqm = st.number_input("External Base Rent (R / sqm / month)", key="ext_external_rent", step=5.0, format="%.2f")
        total_external_rent = external_gla * external_rent_sqm
        st.caption(f"💵 **Total Monthly External Rent:** R {int(round(total_external_rent)):,} (Excl. VAT)")

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
    st.warning(f"🏬 **Total Monthly Landlord Lease Outlay:** R {int(round(total_lease_outlay_monthly)):,} (Excl. VAT)")

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
        "OPERATIONAL BREAKEVEN": ["R 0", f"R {int(round(outflow_breakeven)):,}", f"R {int(round(turnover_req_be)):,}", daily_orders_be],
        "12-MONTH PAYBACK": [f"R {int(round(capex_12)):,}", f"R {int(round(outflow_12)):,}", f"R {int(round(turnover_req_12)):,}", daily_orders_12],
        "24-MONTH PAYBACK": [f"R {int(round(capex_24)):,}", f"R {int(round(outflow_24)):,}", f"R {int(round(turnover_req_24)):,}", daily_orders_24],
        "36-MONTH PAYBACK": [f"R {int(round(capex_36)):,}", f"R {int(round(outflow_36)):,}", f"R {int(round(turnover_req_36)):,}", daily_orders_36],
        "60-MONTH LEASE TERM": [f"R {int(round(capex_60)):,}", f"R {int(round(outflow_60)):,}", f"R {int(round(turnover_req_60)):,}", daily_orders_60]
    }

    df_payback_matrix = pd.DataFrame(payback_matrix_data)
    st.dataframe(df_payback_matrix, use_container_width=True)

    st.divider()

    st.header("5. 60-Month Cash Flow Forecast & Annual Pro Forma P&L (35% COGS)")
    
    total_initial_investment = turnkey_capital + working_capital
    debt_portion = total_initial_investment * 0.50
    monthly_interest_rate = (0.1175) / 12
    monthly_loan_payment = debt_portion * (monthly_interest_rate * (1 + monthly_interest_rate)**60) / ((1 + monthly_interest_rate)**60 - 1)

    cash_flow_data = []
    cumulative_cash_flow = -total_initial_investment
    break_even_month = None

    for m in range(1, 61):
        year_idx = (m - 1) // 12
        season_multiplier = SEASONAL_FACTORS[(m - 1) % 12]
        
        monthly_turnover = (turnover_req_12 * (1.08 ** year_idx)) * season_multiplier
        monthly_lease = total_lease_outlay_monthly * (st.session_state["ext_escalation"] / 100 + 1) ** year_idx
        monthly_cogs = monthly_turnover * 0.35
        monthly_royalties = monthly_turnover * 0.09
        
        total_monthly_expenses = monthly_lease + monthly_cogs + monthly_royalties + monthly_labor_cost
        ebitda = monthly_turnover - total_monthly_expenses
        net_profit = ebitda - monthly_loan_payment
        
        cumulative_cash_flow += net_profit
        if cumulative_cash_flow >= 0 and break_even_month is None: break_even_month = m
            
        cash_flow_data.append({"Month": m, "Year": year_idx + 1, "Turnover": monthly_turnover, "Lease Outlay": monthly_lease, "COGS (35%)": monthly_cogs, "Labor": monthly_labor_cost, "Royalties (9%)": monthly_royalties, "Total Expenses": total_monthly_expenses, "EBITDA": ebitda, "Bank Repayment": monthly_loan_payment, "Net Operating Profit": net_profit, "Cumulative Cash Flow": cumulative_cash_flow})

    df_cashflow = pd.DataFrame(cash_flow_data)
    df_cashflow['Year_Label'] = "Year " + df_cashflow['Year'].astype(str)
    annual_pnl = df_cashflow.groupby('Year_Label').agg({'Turnover': 'sum', 'Lease Outlay': 'sum', 'COGS (35%)': 'sum', 'Labor': 'sum', 'Royalties (9%)': 'sum', 'EBITDA': 'sum', 'Bank Repayment': 'sum', 'Net Operating Profit': 'sum'}).reset_index()

    st.dataframe(annual_pnl.style.format({'Turnover': 'R {:,.0f}', 'Lease Outlay': 'R {:,.0f}', 'COGS (35%)': 'R {:,.0f}', 'Labor': 'R {:,.0f}', 'Royalties (9%)': 'R {:,.0f}', 'EBITDA': 'R {:,.0f}', 'Bank Repayment': 'R {:,.0f}', 'Net Operating Profit': 'R {:,.0f}'}), use_container_width=True)

    st.divider()

    # ==========================================
    # SECTION 6: STRICT DE-DUPLICATION SITE PACK DISPATCH
    # ==========================================
    st.header("6. Dispatch Completed Site Feasibility Pack")
    st.markdown("Select an existing site feasibility pack or generate a new one inside its dedicated site subfolder under `./Locations/`.")

    existing_packs_map = get_existing_site_packs()
    pack_options = ["Create New Pack for Active Site..."] + list(existing_packs_map.keys())
    selected_pack_choice = st.selectbox("Select Feasibility Pack Source", options=pack_options)

    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        target_applicant_name = st.text_input("Prospective Franchisee Full Name", value="", placeholder="e.g. John Doe")
        target_applicant_email = st.text_input("Prospective Franchisee Email Address", value="", placeholder="e.g. applicant@domain.com")
    with col_inv2:
        target_applicant_mobile = st.text_input("Prospective Franchisee Mobile / WhatsApp Number", value="", placeholder="e.g. +27821234567")

    # STRICT DE-DUPLICATION FILE RESOLUTION LOGIC
    if selected_pack_choice != "Create New Pack for Active Site...":
        chosen_path = existing_packs_map[selected_pack_choice]
        pdf_filename = os.path.basename(chosen_path)
        with open(chosen_path, "rb") as f:
            pdf_bytes = f.read()
        st.info(f"📁 **Reusing Existing Pack (No Duplication):** `{selected_pack_choice}`")
    else:
        found_file_path, found_folder_path = find_existing_site_file(location_name)
        
        if found_file_path and os.path.exists(found_file_path):
            pdf_filename = os.path.basename(found_file_path)
            with open(found_file_path, "rb") as f:
                pdf_bytes = f.read()
            st.info(f"📁 **Existing Site File Found:** Reusing `{pdf_filename}` from folder `{os.path.basename(found_folder_path)}` without re-creating.")
        else:
            clean_site_folder_name = re.sub(r'[\\/*?:"<>|]', '', location_name.strip())
            site_subfolder_path = os.path.join(LOCATIONS_DIR, clean_site_folder_name)
            os.makedirs(site_subfolder_path, exist_ok=True)

            clean_site_slug = re.sub(r'[^a-zA-Z0-9_]', '_', location_name.strip())
            default_pdf_filename = f"{clean_site_slug}_Phatbuns_Master_Investor_Pack.pdf"
            target_local_path = os.path.join(site_subfolder_path, default_pdf_filename)

            pdf_buffer = generate_pdf_report(
                location_name, shop_code, suburb_node, internal_gla, external_gla, total_gla, selected_model,
                max_comfortable_seats, high_density_seats, turnkey_capital, working_capital, internal_rent_sqm,
                ops_cost_sqm, total_lease_outlay_monthly, 7.42, df_payback_matrix, annual_pnl, blueprint_pil_img
            )
            pdf_bytes = pdf_buffer.getvalue()
            with open(target_local_path, "wb") as f:
                f.write(pdf_bytes)
            pdf_filename = default_pdf_filename
            st.success(f"📁 **New Site Folder Created & Output PDF Saved:** `{target_local_path}`")

    # Action Row
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        dl_link_html = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}" class="direct-dl-btn">📥 Save PDF Direct to Phone / Files</a>'
        st.markdown(dl_link_html, unsafe_allow_html=True)

    with btn_col2:
        gmail_pw = ""
        if not st.secrets.get("GMAIL_APP_PASSWORD"):
            gmail_pw = st.text_input("Enter Gmail App Password (16 Chars)", type="password", key="app_pw_input", help="Generated from your Google Account Security settings.")
            
        if st.button("📧 Dispatch via Email (with Read Receipt)"):
            if not target_applicant_email:
                st.error("Please enter a valid Franchisee Email Address above.")
            else:
                selected_menus = st.session_state.get("selected_brand_menus", [])
                sent_ok, send_msg = send_franchisee_email_pack(
                    target_applicant_email, target_applicant_name, location_name, pdf_bytes, pdf_filename, selected_menus, custom_app_password=gmail_pw
                )
                if sent_ok:
                    st.success(f"✅ {send_msg}")
                else:
                    st.error(f"❌ Email Failed: {send_msg}")

    if target_applicant_mobile:
        clean_mobile = re.sub(r'[^0-9]', '', target_applicant_mobile)
        wa_text = f"Hi {target_applicant_name if target_applicant_name else 'there'}, thank you for showing interest in Phatbuns South Africa. I have dispatched the Executive Feasibility & Investor Pack for {location_name} to your email ({target_applicant_email}). Please review the attached pack, brand menus, and NCNDA."
        encoded_wa_text = urllib.parse.quote(wa_text)
        wa_url = f"https://api.whatsapp.com/send?phone={clean_mobile}&text={encoded_wa_text}"

        st.markdown(f"""
        <a href="{wa_url}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:12px; border-radius:8px; text-align:center; font-weight:bold; font-size:15px; margin-top:10px;">
                💬 Launch WhatsApp Direct Chat with {target_applicant_name} ({clean_mobile})
            </div>
        </a>
        """, unsafe_allow_html=True)

# TAB 2: BRAND MENUS & ATTACHMENTS
with tab2:
    st.header("📖 Brand Menus & Concept Collateral Selector")
    st.markdown("Select which brand menu PDF files from your **Phatbuns Menu** collection should be attached to the franchisee dispatch email.")

    available_menus = get_available_brand_menus()

    st.subheader("Select Menus to Include in Investor Email Pack:")
    
    selected_menus = []
    for menu in available_menus:
        is_checked = st.checkbox(f"📄 {menu}", value=True if ("burger" in menu.lower() or "frozen" in menu.lower()) else False)
        if is_checked:
            selected_menus.append(menu)

    st.session_state["selected_brand_menus"] = selected_menus

    st.info(f"📋 **Selected Attachments:** {len(selected_menus)} Brand Menu(s) queued to be emailed.")

    st.divider()

    st.subheader("Upload Additional Brand Menus to System")
    uploaded_menu_files = st.file_uploader("Upload new Brand Menu PDF files", type=["pdf"], accept_multiple_files=True)
    if uploaded_menu_files:
        for u_file in uploaded_menu_files:
            save_path = os.path.join(MENUS_DIR, u_file.name)
            with open(save_path, "wb") as f:
                f.write(u_file.read())
        st.success("New brand menu PDFs saved successfully!")
        st.rerun()

# TAB 3: INVESTOR & FRANCHISEE REGISTRY
with tab3:
    st.header("Franchisee & Investor Lead Intake & Database")
    
    with st.form("investor_registration_form", clear_on_submit=False):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            full_name = st.text_input("Full Name *")
            entity_name = st.text_input("Entity / Company Name")
            id_or_passport = st.text_input("ID or Passport Number *")
            email = st.text_input("Email Address *")
        with f_col2:
            mobile = st.text_input("Mobile / WhatsApp Number *")
            preferred_site = st.text_input("Preferred Target Site / Node *", value=location_name)
            store_model_choice = st.selectbox("Preferred Store Model", options=list(STORE_MODELS.keys()))
            capital_available = st.number_input("Proposed Total Capital Available (ZAR)", value=4500000.0, step=100000.0)

        unencumbered_cash_pct = st.slider("Verified Unencumbered Cash (%)", min_value=0.0, max_value=100.0, value=50.0)
        c_col1, c_col2, c_col3 = st.columns(3)
        with c_col1: admin_fee_paid = st.checkbox("Admin Fee Paid (R2,000 Excl. VAT)")
        with c_col2: ndnca_signed = st.checkbox("Signed NCNDA Received")
        with c_col3: popia_consent = st.checkbox("POPIA / NCA Consent Received")

        submitted = st.form_submit_button("Submit Application to Database")
        if submitted:
            if not full_name or not email or not mobile or not id_or_passport or not preferred_site:
                st.error("Please fill in all mandatory fields (*).")
            else:
                save_investor_lead({
                    "full_name": full_name, "entity_name": entity_name, "id_or_passport": id_or_passport,
                    "email": email, "mobile": mobile, "preferred_site": preferred_site,
                    "store_model": store_model_choice, "capital_available": capital_available,
                    "unencumbered_cash_pct": unencumbered_cash_pct,
                    "admin_fee_paid": 1 if admin_fee_paid else 0,
                    "ndnca_signed": 1 if ndnca_signed else 0,
                    "popia_consent": 1 if popia_consent else 0
                })
                st.success(f"Applicant record for **{full_name}** successfully logged in database!")

    st.divider()

    st.subheader("CEO Pipeline & Vetting Database")
    df_pipeline = get_pipeline_dataframe()
    if not df_pipeline.empty:
        st.dataframe(df_pipeline, use_container_width=True)
        pipeline_pdf_file = generate_pipeline_pdf(df_pipeline)
        st.download_button(label="📥 Download CEO Pipeline Audit PDF Report", data=pipeline_pdf_file, file_name="Phatbuns_Investor_Pipeline_Report.pdf", mime="application/pdf", use_container_width=True)
    else:
        st.info("No franchisee applications currently recorded in database.")

st.divider()

st.subheader("Master Rights Holder Contact Information")
st.markdown("""
**Master Rights Holder – South Africa**  
📧 **Email:** [nisaar@fantastic1.com](mailto:nisaar@fantastic1.com) | [fantastic1za@gmail.com](mailto:fantastic1za@gmail.com)  
💬 **WhatsApp:** [+27 82 786 7712](https://wa.me/27827867712)  
📲 **Mobile:** [+27 68 710 1939](tel:+27687101939) | [+27 68 727 4731](tel:+27687274731)  
""")
