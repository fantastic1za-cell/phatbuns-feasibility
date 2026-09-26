# Complete Python Script to Generate Dynamic Phatbuns Master Investor & Franchisee Document (Bank-Ready)
# Comprehensive 10-Point Header Expansion, Interactive Google Drive Menu Downloads, Cross-Browser App Icon Injection, HTML Email Signature with 30px Logos, FASA/POPIA/CPA Compliant NCNDA & Live Web Search Intelligence
# Author: Nisaar Ally

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
from email.mime.image import MIMEImage
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# Google Drive API Imports
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    HAS_GDRIVE = True
except ImportError:
    HAS_GDRIVE = False

# ReportLab Imports for Executive PDF Generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# PDF Processing Engine
try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

# Google GenAI Import for Vision Extraction & Search
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# DuckDuckGo Search Fallback
try:
    from duckduckgo_search import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False

# ==========================================
# DIRECTORY & ASSET FILE INITIALIZATION
# ==========================================
ASSETS_DIR = os.path.join(os.getcwd(), "assets")
MENUS_DIR = os.path.join(ASSETS_DIR, "menus")
LOCATIONS_DIR = os.path.join(os.getcwd(), "Locations")

os.makedirs(MENUS_DIR, exist_ok=True)
os.makedirs(LOCATIONS_DIR, exist_ok=True)

def find_file_in_assets(target_names):
    search_dirs = [ASSETS_DIR, os.getcwd()]
    targets_clean = [t.lower() for t in target_names]

    for d in search_dirs:
        if os.path.exists(d):
            for file in os.listdir(d):
                file_lower = file.lower()
                if file_lower in targets_clean:
                    return os.path.join(d, file)
                for t in targets_clean:
                    t_stem = t.split('.')[0]
                    if t_stem in file_lower and file_lower.endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                        return os.path.join(d, file)
    return None

def find_site_blueprint(loc_name):
    if not loc_name:
        return None
    clean_target = re.sub(r'[^a-zA-Z0-9]', '', loc_name.lower())
    search_dirs = [LOCATIONS_DIR, ASSETS_DIR, os.getcwd()]
    for d in search_dirs:
        if os.path.exists(d):
            for root, dirs, files in os.walk(d):
                for f in files:
                    f_lower = f.lower()
                    if f_lower.endswith(('.png', '.jpg', '.jpeg')) and ('dev' in f_lower or 'plan' in f_lower or 'layout' in f_lower or 'blueprint' in f_lower or clean_target in re.sub(r'[^a-zA-Z0-9]', '', f_lower)):
                        return os.path.join(root, f)
    return None

def get_asset_images_map():
    asset_map = {
        "phatbuns_sa": find_file_in_assets(["Phatbuns_SA.PNG", "phatbuns_sa.png"]),
        "phatville": find_file_in_assets(["Phatville.PNG", "phatville.png"]),
        "phatbuns": find_file_in_assets(["Phatbuns.PNG", "phatbuns.png"]),
        "butter_brulee": find_file_in_assets(["ButterBruleeLogo.PNG", "butterbrulee.png"]),
        "doorstep": find_file_in_assets(["Doorstep Logo.PNG", "doorstep.png"]),
        "adega": find_file_in_assets(["Adega.PNG", "adega.png"]),
        "sa_flag": find_file_in_assets(["SAFlag.PNG", "saflag.png", "sa_flag.png"]),
        "cover_bg": find_file_in_assets(["coverSA.JPG", "coversa.jpg", "cover.jpg", "Cover.JPG", "IMG_5357.jpeg", "img_5357.jpeg"])
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

def format_sa_mobile_number(raw_mobile):
    if not raw_mobile:
        return ""
    digits = re.sub(r'[^0-9]', '', str(raw_mobile))
    if digits.startswith("0") and len(digits) == 10:
        return "27" + digits[1:]
    elif digits.startswith("27") and len(digits) == 11:
        return digits
    elif len(digits) == 9:
        return "27" + digits
    return digits

def get_available_brand_menus():
    menu_files = []
    search_dirs = [MENUS_DIR, ASSETS_DIR]
    for d in search_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.lower().endswith(".pdf") and f not in menu_files:
                    menu_files.append(f)
    
    default_menus = [
        "Phatbuns_Smash_Burger_Main_Menu.pdf",
        "Phatbuns_Menu_2_Sliders_and_Sides.pdf",
        "Butter_Brulee_Signature_Drinks.pdf",
        "Butter_Brulee_Classic_Exclusive_Cookies.pdf",
        "Butter_Brulee_Seasonal_Menu_Item.pdf",
        "Doorstep_Desserts_Artisan_Catalog.pdf"
    ]
    for dm in default_menus:
        if dm not in menu_files:
            menu_files.append(dm)

    return sorted(menu_files)

# ==========================================
# STREAMLIT CONFIGURATION
# ==========================================
sa_app_logo_path = find_file_in_assets(["Phatbuns_SA.PNG", "phatbuns_sa.png"])

if sa_app_logo_path and os.path.exists(sa_app_logo_path):
    try:
        app_favicon_img = Image.open(sa_app_logo_path)
    except Exception:
        app_favicon_img = "🍔"
else:
    app_favicon_img = "🍔"

st.set_page_config(
    page_title="Phatbuns Engine",
    page_icon=app_favicon_img,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# ADVANCED UNIVERSAL GEO & RENTAL INTELLIGENCE ENGINE
# ==========================================
def research_location_online(location_name):
    search_query = f"{location_name} shopping centre mall suburb food tenants rental rate per sqm South Africa"
    results_text = ""
    
    if HAS_DDGS:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(search_query, max_results=8))
                for r in results:
                    results_text += f"{r.get('title', '')}: {r.get('body', '')}\n"
        except Exception:
            pass

    extracted_info = {
        "suburb": "",
        "options": [],
        "landlord": "Property Developers / Landlord",
        "mall_size": "Regional Retail Centre",
        "footfall": "~500,000 visits/month",
        "households": "85,000 Active Households (10 km Radius)",
        "competitors": "Nando's, Steers, Debonairs, Wimpy, RocoMamas",
        "lsm_profile": "LSM 7–10 / High Purchasing Power Node",
        "default_rent": 280.0,
        "turnover_clause_pct": 7.0
    }

    SA_GEO_DICTIONARY = {
        "rondebuilt": {
            "suburb": "Germiston, Ekurhuleni, Gauteng",
            "options": ["Germiston, Ekurhuleni, Gauteng", "Rondebuilt Centre, Germiston"],
            "footfall": "~380,000 visits/month (~4.5M Annually)",
            "households": "24,061 Active Households / ~76,995 Area Population",
            "competitors": "Shoprite, Boxer, Build-It Flagship, Debonairs, Wimpy, Pedro's, Hungry Lion, Clicks, Pep, Ackermans, Capitec",
            "lsm_profile": "LSM 6–9 / Established Commercial & Industrial Corridor",
            "default_rent": 220.0,
            "turnover_clause_pct": 7.0
        },
        "cedar square": {
            "suburb": "Fourways, Johannesburg, Gauteng",
            "options": ["Fourways, Johannesburg, Gauteng", "Fourways / Craigavon, Sandton", "Cedar Lakes / Fourways, JHB"],
            "footfall": "~550,000 visits/month",
            "households": "95,000 Active Households (10 km Radius)",
            "competitors": "Tiger's Milk, Panarottis, Mugg & Bean, Nando's, Salsa Mexican Grill",
            "lsm_profile": "LSM 8–10+ / Prime Lifestyle & Entertainment Precinct",
            "default_rent": 300.0,
            "turnover_clause_pct": 7.0
        },
        "scottburgh": {
            "suburb": "Scottburgh, KwaZulu-Natal",
            "options": ["Scottburgh, KwaZulu-Natal", "Scottburgh South, Ugu District", "Park Rynie / Scottburgh, KZN"],
            "footfall": "~350,000 visits/month",
            "households": "45,000 Active Households (10 km Radius)",
            "competitors": "Nando's, Steers, Debonairs, Wimpy, Fishaways",
            "lsm_profile": "LSM 6–9 / Coastal Regional Retail Hub",
            "default_rent": 160.0,
            "turnover_clause_pct": 7.0
        },
        "campus square": {
            "suburb": "Auckland Park, Johannesburg, Gauteng",
            "options": ["Auckland Park, Johannesburg, Gauteng", "Melville / Auckland Park, Johannesburg"],
            "footfall": "~650,000 visits/month",
            "households": "110,000 Active Households (10 km Radius)",
            "competitors": "RocoMamas, Nando's, Chicken Licken, Wimpy, Roman's Pizza, Anat, Bossies Pies",
            "lsm_profile": "LSM 6–9 / Student, Academic & Urban Youth Hub (UJ & Wits Corridor)",
            "default_rent": 210.0,
            "turnover_clause_pct": 7.0
        },
        "clearwater": {
            "suburb": "Strubensvalley, Roodepoort, Gauteng",
            "options": ["Strubensvalley, Roodepoort, Gauteng", "Little Falls / Roodepoort, Gauteng"],
            "footfall": "~700,000 visits/month",
            "households": "135,000 Active Households (10 km Radius)",
            "competitors": "Burger King, Panarottis, Steers, Debonairs, Mochachos, Ocean Basket",
            "lsm_profile": "LSM 8–10+ / High Purchasing Power Suburb",
            "default_rent": 181.0,
            "turnover_clause_pct": 7.0
        }
    }

    loc_clean = location_name.lower().strip()
    for key_term, geo_data in SA_GEO_DICTIONARY.items():
        if key_term in loc_clean:
            extracted_info["suburb"] = geo_data["suburb"]
            extracted_info["options"] = geo_data["options"]
            extracted_info["footfall"] = geo_data["footfall"]
            extracted_info["households"] = geo_data["households"]
            extracted_info["competitors"] = geo_data.get("competitors", extracted_info["competitors"])
            extracted_info["lsm_profile"] = geo_data.get("lsm_profile", extracted_info["lsm_profile"])
            extracted_info["default_rent"] = geo_data.get("default_rent", 280.0)
            extracted_info["turnover_clause_pct"] = geo_data.get("turnover_clause_pct", 7.0)
            return extracted_info

    if HAS_GENAI:
        api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
        if api_key:
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""
                You are an expert South African commercial property analyst.
                Identify the exact suburb, town/city, province, actual food tenants, and realistic QSR gross rental rate per sqm for: '{location_name}'.
                Web Search Context: {results_text}

                Return ONLY a valid JSON object:
                {{
                  "suburb": "Precise Suburb, City, Province",
                  "options": ["Option 1", "Option 2"],
                  "landlord": "Managing agent or landlord if known",
                  "mall_size": "Estimated GLA e.g. 23,275 m² Community Centre",
                  "footfall": "Estimated monthly visits e.g. ~380,000 visits/month",
                  "households": "Estimated catchment e.g. 24,061 Households / ~76,995 Population",
                  "competitors": "Key actual food tenants present in the mall (AUDITED & ACCURATE)",
                  "lsm_profile": "Accurate LSM profile e.g. LSM 6-9 / Commercial Node",
                  "default_rent": float (Realistic market rent target per sqm e.g. 220.0),
                  "turnover_clause_pct": 7.0
                }}
                """
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[prompt],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                parsed = json.loads(response.text)
                if parsed and parsed.get("suburb"):
                    return parsed
            except Exception:
                pass

    prov_match = re.search(r'(KwaZulu-Natal|Gauteng|Western Cape|Eastern Cape|Free State|Mpumalanga|Limpopo|North West|Northern Cape)', results_text, re.IGNORECASE)
    detected_prov = prov_match.group(1).title() if prov_match else "Gauteng"
    
    sub_m = re.search(r'(?:in|at|near)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', results_text)
    detected_sub = sub_m.group(1).strip() if sub_m else location_name.title()

    primary_node = f"{detected_sub}, Johannesburg, {detected_prov}"
    extracted_info["suburb"] = primary_node
    extracted_info["options"] = [primary_node, f"{location_name.title()} Central, {detected_prov}"]

    return extracted_info

# ==========================================
# BRAND MENU DIRECTORY & MEDIA SHOWCASE CATALOG
# ==========================================
BRAND_MENU_CATALOG = {
    "Phatbuns Smash Burgers": {
        "logo_key": "phatbuns_sa",
        "filename": "Phatbuns_Smash_Burger_Main_Menu.pdf",
        "drive_file_id": "1Goe4yS1E5R0KiZt6N_cQ4HcCad9OUJgr",
        "tagline": "Artisan Smash Burgers & Signature Buns",
        "description": "Hand-pressed Angus beef smash patties served on seeded brioche, topped with proprietary secret sauces, Cheesy Doritos, Fiery Cheetos ranges, and buttermilk fried chicken."
    },
    "PhatVille Sliders & Sides": {
        "logo_key": "phatville",
        "filename": "Phatbuns_Menu_2_Sliders_and_Sides.pdf",
        "drive_file_id": "1lLGjL73SJeRfXXJKFl0a8ZnhfFQb1ich",
        "tagline": "Nashville Hot Sliders & Loaded Sides",
        "description": "Nashville-style sliders, crispy tender boxes, dusted crinkle fries, and specialized dipping sauces optimized for rapid kitchen assembly and delivery channels."
    },
    "Butter Brûlée Signature Drinks": {
        "logo_key": "butter_brulee",
        "filename": "Butter_Brulee_Signature_Drinks.pdf",
        "drive_file_id": "1dUxvPSZTyWfbjDXRxuBNFhFSOYc5ctWc",
        "tagline": "Signature Beverages & Artisanal Mocktails",
        "description": "Hand-crafted specialty iced teas, indulgent gourmet milkshakes, artisanal refresher coolers, and barista specialty coffees designed to complement sweet and savory offerings."
    },
    "Butter Brûlée Cookies & Desserts": {
        "logo_key": "butter_brulee",
        "filename": "Butter_Brulee_Classic_Exclusive_Cookies.pdf",
        "drive_file_id": "1nc1I7_-bLZkq4oJDE5wHwic8DZ8QCVxE",
        "tagline": "Classic & Exclusive Artisanal Cookies",
        "description": "Gourmet freshly baked classic cookies, stuffed exclusive artisan ranges, cookie caviar tiramisu, and specialty sweet pairings engineered for high average ticket yield."
    },
    "Butter Brûlée Seasonal Specials": {
        "logo_key": "butter_brulee",
        "filename": "Butter_Brulee_Seasonal_Menu_Item.pdf",
        "drive_file_id": "1OaWyRBwvoQQX-OZMQNlbdpXBgXQaFAZs",
        "tagline": "Luxury Milk Cakes, Seasonal Specials & Fine Shakes",
        "description": "Artisanal seasonal dessert offerings, caramelized french toast, pistachio kunafa treats, and high-margin signature drinks."
    },
    "Doorstep Desserts": {
        "logo_key": "doorstep",
        "filename": "Doorstep_Desserts_Artisan_Catalog.pdf",
        "drive_file_id": "1rghEVeNi5SRgy9NbTVp6UwbHgn_4pSHY",
        "tagline": "Gourmet Warm Desserts, Waffles & Sundaes",
        "description": "Indulgent double-stick waffle sticks, freshly baked dough tubs, Lotus Biscoff crunch cakes, gelato sundaes, and dessert delivery boxes."
    }
}

STORE_MEDIA_LINKS = {
    "store_photos": "https://drive.google.com/file/d/1qbJ6kvaBxja2gBWoaoHLWme0MEA1omOH/view?usp=drivesdk",
    "uk_video_1": "https://drive.google.com/file/d/1txmElx_qkUeY6gJS8P5h7Diqoa_uRGr7/view?usp=drivesdk",
    "dubai_video": "https://drive.google.com/file/d/1mH-4NOQpqCv8oeft0FjOV-6JSjGfT1VK/view?usp=drivesdk",
    "uk_video_2": "https://drive.google.com/file/d/1XYpOF-_aKlzcEgaUouhE8Ewlvdpn7nFI/view?usp=drivesdk"
}

def get_drive_menu_download_url(file_id_or_folder):
    if file_id_or_folder and len(file_id_or_folder) > 25 and file_id_or_folder != "14K_pChaU-dYfNlKi-HvzcEytFY6qOR_m":
        return f"https://drive.google.com/uc?export=download&id={file_id_or_folder}"
    return f"https://drive.google.com/drive/folders/{file_id_or_folder}"

# ==========================================
# STRICT GOOGLE DRIVE API & SHARED FOLDER ENGINE (supportsAllDrives=True)
# ==========================================
GDRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
LOCATIONS_ROOT_DRIVE_ID = "1vGItMiw-ZYqzBOXvLfl0xkbhh7uYkhf5"

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
        print(f"Google Drive API Authentication error: {e}")
    return None

def get_or_create_drive_folder(service, folder_name, parent_id=None):
    try:
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = service.files().list(
            q=query,
            spaces='drive',
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora='allDrives'
        ).execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
        else:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]
            folder = service.files().create(
                body=file_metadata,
                fields='id',
                supportsAllDrives=True
            ).execute()
            return folder.get('id')
    except Exception as e:
        print(f"Drive Folder Creation Error: {e}")
        return None

def upload_pdf_to_drive(service, file_bytes, filename, parent_folder_id):
    try:
        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype='application/pdf', resumable=True)
        query = f"name = '{filename}' and '{parent_folder_id}' in parents and trashed = false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora='allDrives'
        ).execute()
        files = results.get('files', [])
        
        if files:
            file_id = files[0]['id']
            updated_file = service.files().update(
                fileId=file_id,
                media_body=media,
                supportsAllDrives=True
            ).execute()
            return updated_file.get('id')
        else:
            file_metadata = {
                'name': filename,
                'parents': [parent_folder_id]
            }
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()
            return file.get('id')
    except Exception as e:
        print(f"Drive Upload Error: {e}")
        return None

def sync_pdf_to_local_and_cloud(location_name, pdf_bytes, pdf_filename):
    loc_clean = location_name.strip() if location_name else "Unassigned_Location"
    loc_sub_dir = os.path.join(LOCATIONS_DIR, loc_clean)
    os.makedirs(loc_sub_dir, exist_ok=True)
    local_file_path = os.path.join(loc_sub_dir, pdf_filename)
    
    with open(local_file_path, "wb") as f:
        f.write(pdf_bytes)

    drive_service = get_drive_service()
    if drive_service:
        try:
            site_folder_id = get_or_create_drive_folder(drive_service, loc_clean, parent_id=LOCATIONS_ROOT_DRIVE_ID)
            if site_folder_id:
                file_id = upload_pdf_to_drive(drive_service, pdf_bytes, pdf_filename, site_folder_id)
                if file_id:
                    return local_file_path, f"Successfully Synced Site Pack to Google Drive: Locations/{loc_clean}/{pdf_filename}"
        except Exception as e:
            return local_file_path, f"Saved Locally | Drive Sync Warning: {e}"

    return local_file_path, "PDF Generated & Saved to Local Directory | Google Drive Menu Links Active"
# ==========================================
# COVER PAGE COMPOSITOR (8K CRISP FULL-BLEED)
# ==========================================
def create_cover_page_image():
    asset_map = get_asset_images_map()
    bg_path = asset_map.get("cover_bg")

    if bg_path and os.path.exists(bg_path):
        try:
            bg_img = Image.open(bg_path).convert("RGB")
            bg_img = bg_img.resize((2480, 3508), Image.Resampling.LANCZOS)
        except Exception:
            bg_img = Image.new("RGB", (2480, 3508), color=(235, 120, 35))
    else:
        bg_img = Image.new("RGB", (2480, 3508), color=(235, 120, 35))

    img_byte_arr = io.BytesIO()
    bg_img.save(img_byte_arr, format='JPEG', quality=100, subsampling=0)
    img_byte_arr.seek(0)
    return img_byte_arr

def extract_lease_from_source(source_input):
    if not HAS_GENAI:
        if isinstance(source_input, str):
            return parse_landlord_text(source_input)
        return parse_landlord_text("")
    
    api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
    if not api_key:
        if isinstance(source_input, str):
            return parse_landlord_text(source_input)
        return parse_landlord_text("")

    try:
        client = genai.Client(api_key=api_key)
        prompt = """
        Extract commercial lease offer details precisely from this input into a JSON object:
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
          "generator": float,
          "turnover_pct": float
        }
        Extract exact numbers, strictly separating internal area from external/patio seating GLA (e.g., if shop size is 70m² plus 28m² outside, internal_gla=70.0, external_gla=28.0; if rent is R220 shop and R110 outside, internal_rent=220.0, external_rent=110.0; if turnover clause is 7%, turnover_pct=7.0).
        """
        contents_payload = [source_input, prompt] if not isinstance(source_input, str) else [source_input + "\n\n" + prompt]
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents_payload,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        data = json.loads(response.text)
        if data:
            return data
    except Exception:
        pass

    if isinstance(source_input, str):
        return parse_landlord_text(source_input)
    return parse_landlord_text("")

def parse_landlord_text(text):
    data = {}
    text_clean = text.replace('\r', '\n')

    shop_m = re.search(r'(?:Shop|Premises)(?:\s*(?:No|code))?\s*[:\-]?\s*([A-Za-z0-9\s]+)', text_clean, re.IGNORECASE)
    if shop_m:
        val = shop_m.group(1).split('\n')[0].strip()
        if len(val) < 15: data['shop_code'] = val

    int_area_m = re.search(r'(?:Shop\s*Size|Internal\s*Area|Area)\s*[:\-]?\s*([\d\.\,]+)\s*(?:sqm|m2|m²)', text_clean, re.IGNORECASE)
    if int_area_m: data['internal_gla'] = float(int_area_m.group(1).replace(',', '.'))

    ext_area_m = re.search(r'(?:outside|external|patio)\s*(?:seating|area)?\s*[:\-]?\s*([\d\.\,]+)\s*(?:sqm|m2|m²)', text_clean, re.IGNORECASE)
    if ext_area_m: data['external_gla'] = float(ext_area_m.group(1).replace(',', '.'))

    int_rent_m = re.search(r'R?\s*([\d]+(?:\.[\d]+)?)\s*(?:excl|per|\/)?\s*(?:vat)?\s*(?:Shop|Basic)', text_clean, re.IGNORECASE)
    if not int_rent_m:
        int_rent_m = re.search(r'(?:Basic\s*Monthly\s*Rental|Rental\s*internal|Gross\s*Rental)\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)', text_clean, re.IGNORECASE)
    if int_rent_m: data['internal_rent'] = float(int_rent_m.group(1))

    ext_rent_m = re.search(r'R?\s*([\d]+(?:\.[\d]+)?)\s*(?:excl|per|\/)?\s*(?:vat)?\s*(?:outside|seating)', text_clean, re.IGNORECASE)
    if ext_rent_m: data['external_rent'] = float(ext_rent_m.group(1))

    ops_m = re.search(r'(?:Operating\s*Costs|Ops\s*Cost|Municipal\s*Charges)\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)', text_clean, re.IGNORECASE)
    if ops_m: data['ops_cost'] = float(ops_m.group(1))

    esc_m = re.search(r'Escalation\s*[:\-]?\s*([\d]+(?:\.[\d]+)?)\s*%', text_clean, re.IGNORECASE)
    if esc_m: data['escalation'] = float(esc_m.group(1))

    rates_m = re.search(r'Rates\s*(?:&|and)?\s*taxes\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)', text_clean, re.IGNORECASE)
    if rates_m: data['rates_taxes'] = float(rates_m.group(1))

    mktg_m = re.search(r'Marketing\s*(?:Contribution)?\s*[:\-]?\s*([\d]+(?:\.[\d]+)?)\s*%', text_clean, re.IGNORECASE)
    if mktg_m: data['mktg'] = float(mktg_m.group(1))

    turn_m = re.search(r'(?:Annual\s*Turnover|Turnover\s*Rental)\s*[:\-]?\s*([\d]+(?:\.[\d]+)?)\s*%', text_clean, re.IGNORECASE)
    if turn_m: data['turnover_pct'] = float(turn_m.group(1))

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
# EMAIL DISPATCH ENGINE WITH 30PX SIDE-BY-SIDE LOGOS
# ==========================================
def send_franchisee_email_pack(recipient_email, recipient_name, site_name, pdf_bytes, pdf_filename):
    sender_email = st.secrets.get("GMAIL_USER", "fantastic1za@gmail.com")
    sender_password = "ehyjsvzhffmbvuaf"

    try:
        msg = MIMEMultipart('related')
        msg['From'] = f"Phatbuns SA Master Rights <{sender_email}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"Phatbuns SA — Executive Franchisee Feasibility Pack & Brand Menus ({site_name})"
        
        msg['Disposition-Notification-To'] = sender_email
        msg['Return-Receipt-To'] = sender_email
        msg['X-Confirm-Reading-To'] = sender_email

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; font-size: 14px; color: #333333; line-height: 1.6;">
            <p>Dear {recipient_name if recipient_name else 'Valued Prospective Franchisee'},</p>
            
            <p>Thank you for taking the time to show interest in the Phatbuns South Africa franchise expansion program.</p>
            
            <p>We are excited to share our comprehensive Master Franchisee Investor Pack for <b>{site_name}</b>. Phatbuns represents a premier, high-growth commercial brand footprint across South Africa.</p>
            
            <p>Please find attached to this email (Consolidated within the Feasibility PDF Pack):<br/>
            1. Executive Cover Page & Brand Identity Presentation<br/>
            2. Site Evaluation & Commercial Investment Analysis ({site_name})<br/>
            3. Financial Outlay & Debt Serviceability Breakdown<br/>
            4. 5-Year Pro Forma Income Statement & 60-Month Cash Flow Projections (35% COGS Model)<br/>
            5. Development Layout & Leasing Site Plan (Rendered)<br/>
            6. Addendum — Brand Menus with Direct Google Drive Download Links<br/>
            7. Master Non-Circumvention, Non-Disclosure & Confidentiality Agreement (NCNDA)</p>
            
            <p><b>Next Steps:</b><br/>
            Please review the attached documents, sign the NCNDA execution page, and return a copy to proceed with formal site allocation and executive approval.</p>
            
            <p>Should you have any questions or require additional information, please feel free to reach out directly via call or WhatsApp.</p>
            
            <p>Warm regards,</p>
            
            <div style="margin-top: 15px; margin-bottom: 10px;">
                <img src="cid:phatbuns_sa_logo" style="height: 30px; width: auto; vertical-align: middle; margin-right: 12px;" alt="Phatbuns SA Logo" />
                <img src="cid:sa_flag_logo" style="height: 30px; width: auto; vertical-align: middle;" alt="South African Flag" />
            </div>
            
            <p style="margin-top: 5px; margin-bottom: 3px;"><b>Nisaar Ally</b></p>
            <p style="margin: 2px 0;">Master Rights Holder — Phatbuns South Africa</p>
            <p style="margin: 2px 0;">Email: <a href="mailto:nisaar@fantastic1.com">nisaar@fantastic1.com</a> | <a href="mailto:fantastic1za@gmail.com">fantastic1za@gmail.com</a></p>
            <p style="margin: 2px 0;">WhatsApp: <a href="https://wa.me/27827867712">+27 82 786 7712</a></p>
            <p style="margin: 2px 0;">Mobile: <a href="tel:+27687101939">+27 68 710 1939</a> | <a href="tel:+27687274731">+27 68 727 4731</a></p>
        </body>
        </html>
        """

        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(html_body, 'html'))

        asset_map = get_asset_images_map()
        phatbuns_sa_path = asset_map.get("phatbuns_sa")
        sa_flag_path = asset_map.get("sa_flag")

        if phatbuns_sa_path and os.path.exists(phatbuns_sa_path):
            with open(phatbuns_sa_path, 'rb') as img_f:
                img_sa = MIMEImage(img_f.read())
                img_sa.add_header('Content-ID', '<phatbuns_sa_logo>')
                img_sa.add_header('Content-Disposition', 'inline', filename='Phatbuns_SA.png')
                msg.attach(img_sa)

        if sa_flag_path and os.path.exists(sa_flag_path):
            with open(sa_flag_path, 'rb') as img_f:
                img_flag = MIMEImage(img_f.read())
                img_flag.add_header('Content-ID', '<sa_flag_logo>')
                img_flag.add_header('Content-Disposition', 'inline', filename='SAFlag.png')
                msg.attach(img_flag)

        part = MIMEApplication(pdf_bytes, Name=pdf_filename)
        part['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
        msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        return True, "Email sent successfully with embedded logos and PDF Pack!"
    except Exception as e:
        return False, str(e)

# ==========================================
# STREAMLIT BRAND STYLING & RESPONSIVE UI FIXES
# ==========================================
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
    display: block;
    width: 100%;
    background-color: #0066CC;
    color: white !important;
    text-align: center;
    padding: 12px;
    border-radius: 8px;
    font-weight: bold;
    text-decoration: none;
    margin-top: 5px;
    box-sizing: border-box;
}
.lease-outlay-card {
    background-color: #2D3748;
    border-left: 5px solid #ECC94B;
    padding: 14px;
    border-radius: 8px;
    margin-top: 15px;
    margin-bottom: 15px;
    word-wrap: break-word;
    overflow-wrap: break-word;
}
.logo-row-locked {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    justify-content: space-around !important;
    align-items: center !important;
    width: 100% !important;
    padding: 10px 0 !important;
    gap: 6px !important;
    overflow-x: auto !important;
}
.logo-item-locked {
    height: 45px !important;
    max-height: 45px !important;
    width: auto !important;
    max-width: 18% !important;
    object-fit: contain !important;
    display: block !important;
    margin: 0 auto !important;
}
.brand-card-block {
    background-color: #1A1A1A;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #333;
    margin-bottom: 20px;
}
.brand-logo-above {
    height: 48px;
    width: auto;
    object-fit: contain;
    display: block;
    margin-bottom: 10px;
}
.contact-footer-box {
    background-color: #181818;
    border: 1px solid #333;
    border-radius: 10px;
    padding: 20px;
    margin-top: 30px;
}
.contact-header-flex {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}
.contact-mini-img {
    height: 25px;
    width: auto;
    object-fit: contain;
    border-radius: 3px;
}
</style>
""", unsafe_allow_html=True)

logo_map = get_asset_images_map()

b64_sa = get_image_base64(logo_map.get("phatbuns_sa"))
b64_flag = get_image_base64(logo_map.get("sa_flag"))
b64_ds = get_image_base64(logo_map.get("doorstep"))
b64_bb = get_image_base64(logo_map.get("butter_brulee"))
b64_pv = get_image_base64(logo_map.get("phatville"))
b64_pb = get_image_base64(logo_map.get("phatbuns"))

def render_contact_footer():
    sa_logo_html = f'<img src="data:image/png;base64,{b64_sa}" class="contact-mini-img"/>' if b64_sa else '🍔'
    flag_logo_html = f'<img src="data:image/png;base64,{b64_flag}" class="contact-mini-img"/>' if b64_flag else '🇿🇦'

    st.markdown(f"""
    <div class="contact-footer-box">
        <h3 style="margin-top:0; margin-bottom:10px; font-size:20px; font-weight:700;">Master Rights Holder Contact Information</h3>
        <div class="contact-header-flex">
            {sa_logo_html}
            {flag_logo_html}
            <span style="font-size:15px; font-weight:600; color:#CCCCCC;">Master Rights Holder – South Africa</span>
        </div>
        <p style="margin: 6px 0; font-size:14px;">
            📧 <b>Email:</b> <a href="mailto:nisaar@fantastic1.com" style="color:#66B2FF;">nisaar@fantastic1.com</a> | <a href="mailto:fantastic1za@gmail.com" style="color:#66B2FF;">fantastic1za@gmail.com</a>
        </p>
        <p style="margin: 6px 0; font-size:14px;">
            💬 <b>WhatsApp:</b> <a href="https://wa.me/27827867712" target="_blank" style="color:#25D366; font-weight:bold;">+27 82 786 7712</a>
        </p>
        <p style="margin: 6px 0; font-size:14px;">
            📲 <b>Mobile:</b> <a href="tel:+27687101939" style="color:#66B2FF;">+27 68 710 1939</a> | <a href="tel:+27687274731" style="color:#66B2FF;">+27 68 727 4731</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

banner_logo_html = f'<img src="data:image/png;base64,{b64_sa}" class="banner-logo-icon"/>' if b64_sa else '🍔'

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

locked_logos_html = f"""
<div class="logo-row-locked">
    {'<img src="data:image/png;base64,' + b64_ds + '" class="logo-item-locked"/>' if b64_ds else ''}
    {'<img src="data:image/png;base64,' + b64_bb + '" class="logo-item-locked"/>' if b64_bb else ''}
    {'<img src="data:image/png;base64,' + b64_pv + '" class="logo-item-locked"/>' if b64_pv else ''}
    {'<img src="data:image/png;base64,' + b64_sa + '" class="logo-item-locked"/>' if b64_sa else ''}
    {'<img src="data:image/png;base64,' + b64_pb + '" class="logo-item-locked"/>' if b64_pb else ''}
</div>
"""
st.markdown(locked_logos_html, unsafe_allow_html=True)

st.markdown('<hr class="green-divider">', unsafe_allow_html=True)

# ==========================================
# REFRESH BUTTON & DB INITIALIZATION
# ==========================================
c_ref1, c_ref2 = st.columns([4, 1])
with c_ref2:
    if st.button("🔄 Refresh App / Clear State"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.write("")

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
    cursor.execute("SELECT id FROM franchisee_pipeline WHERE email = ?", (data['email'],))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("""
            UPDATE franchisee_pipeline SET
                full_name = ?, entity_name = ?, id_or_passport = ?, mobile = ?,
                preferred_site = ?, store_model = ?, capital_available = ?, unencumbered_cash_pct = ?,
                admin_fee_paid = ?, ndnca_signed = ?, popia_consent = ?
            WHERE email = ?
        """, (
            data['full_name'], data['entity_name'], data['id_or_passport'], data['mobile'],
            data['preferred_site'], data['store_model'], data['capital_available'], data['unencumbered_cash_pct'],
            data['admin_fee_paid'], data['ndnca_signed'], data['popia_consent'], data['email']
        ))
        conn.commit()
    else:
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
    df = pd.read_sql_query("SELECT id, full_name, mobile, email, preferred_site, store_model, capital_available, unencumbered_cash_pct, ceo_approval, created_at FROM franchisee_pipeline ORDER BY id DESC", conn)
    conn.close()
    return df

SITE_PROFILES = {
    "Rondebuilt Centre": {
        "suburb": "Germiston, Ekurhuleni, Gauteng",
        "shop": "79",
        "landlord": "Vegieland Properties (Pty) Ltd",
        "mall_size": "23,275 m² Community Centre",
        "footfall": "~380,000 visits/month (~4.5M Annually)",
        "households": "24,061 Active Households / ~76,995 Area Population",
        "competitors": "Shoprite, Boxer, Build-It Flagship, Debonairs, Wimpy, Pedro's, Hungry Lion, Clicks, Pep, Ackermans, Capitec",
        "lsm_profile": "LSM 6–9 / Established Commercial & Industrial Corridor",
        "default_rent": 220.0,
        "default_ops": 32.50,
        "default_gla": 98.0,
        "model": "Express Model",
        "turnover_clause_pct": 7.0
    },
    "Cedar Square": {
        "suburb": "Fourways, Johannesburg, Gauteng",
        "shop": "CS12",
        "landlord": "Redefine Properties",
        "mall_size": "12,000 m² Lifestyle & Entertainment Centre",
        "footfall": "~550,000 visits/month (~6.6 Million Annually)",
        "households": "95,000 Active Households (10 km Radius)",
        "competitors": "Tiger's Milk, Panarottis, Mugg & Bean, Nando's, Salsa Mexican Grill",
        "lsm_profile": "LSM 8–10+ / Upscale Lifestyle Precinct",
        "default_rent": 300.0,
        "default_ops": 45.0,
        "default_gla": 80.0,
        "model": "Express Model",
        "turnover_clause_pct": 7.0
    },
    "Clearwater Mall": {
        "suburb": "Strubensvalley, Roodepoort, Gauteng",
        "shop": "UM017B",
        "landlord": "Hyprop Investments Ltd",
        "mall_size": "86,000 m² Regional Flagship",
        "footfall": "~700,000 visits/month (~9.8 Million Annually)",
        "households": "125,000–145,000 Active Households (10 km Radius)",
        "competitors": "Burger King, Panarottis, Steers, Debonairs, Mochachos, Ocean Basket",
        "lsm_profile": "LSM 8–10+ / High Purchasing Power Suburb",
        "default_rent": 181.0,
        "default_ops": 50.0,
        "default_gla": 252.0,
        "model": "Multi-Brand Kitchen Model",
        "turnover_clause_pct": 6.0
    }
}

LOCATION_LOOKUP = {
    "Custom / Other Site...": "",
    "Rondebuilt Centre": "Germiston, Ekurhuleni, Gauteng",
    "Cedar Square": "Fourways, Johannesburg, Gauteng",
    "Clearwater Mall": "Strubensvalley, Roodepoort, Gauteng",
    "Campus Square": "Auckland Park, Johannesburg, Gauteng",
    "Sandton City Shopping Centre": "Sandton Central, Johannesburg, Gauteng",
    "Mall of Africa": "Waterfall City, Midrand, Gauteng"
}

STORE_MODELS = {
    "Kiosk Model": {
        "size_range": "20 - 60 sqm",
        "turnkey_capital": 850000.0,
        "working_capital": 250000.0,
        "est_monthly_turnover": 350000.0,
        "labor_monthly": 45000.0,
        "foh_pct": 0.00,
        "default_gla": 40.0,
        "min_footfall_req": 300000,
        "ideal_lsm": "LSM 6-10+"
    },
    "Express Model": {
        "size_range": "40 - 90 sqm",
        "turnkey_capital": 2500000.0,
        "working_capital": 450000.0,
        "est_monthly_turnover": 650000.0,
        "labor_monthly": 85000.0,
        "foh_pct": 0.10,
        "default_gla": 70.0,
        "min_footfall_req": 500000,
        "ideal_lsm": "LSM 7-10+"
    },
    "Full Sit-Down Model": {
        "size_range": "100 - 160 sqm",
        "turnkey_capital": 3250000.0,
        "working_capital": 750000.0,
        "est_monthly_turnover": 950000.0,
        "labor_monthly": 125000.0,
        "foh_pct": 0.40,
        "default_gla": 120.0,
        "min_footfall_req": 650000,
        "ideal_lsm": "LSM 8-10+"
    },
    "Multi-Brand Kitchen Model": {
        "size_range": "100 - 160 sqm",
        "turnkey_capital": 3500000.0,
        "working_capital": 700000.0,
        "est_monthly_turnover": 1100000.0,
        "labor_monthly": 135000.0,
        "foh_pct": 0.40,
        "default_gla": 130.0,
        "min_footfall_req": 700000,
        "ideal_lsm": "LSM 8-10+"
    },
}

SEASONAL_FACTORS = [0.90, 1.00, 1.00, 1.15, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.05, 1.25]

# ==========================================
# NUMBERED CANVAS WITH CENTERED DUAL LOGOS ABOVE FOOTER
# ==========================================
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        if self._pageNumber > 1:
            asset_map = get_asset_images_map()
            phatbuns_logo_path = asset_map.get("phatbuns_sa")
            sa_flag_path = asset_map.get("sa_flag")

            page_width = A4[0]
            logo_w = 100
            logo_h = 32
            gap = 15
            total_block_w = (logo_w * 2) + gap
            start_x = (page_width - total_block_w) / 2.0
            logo_y = 15 * mm

            if phatbuns_logo_path and os.path.exists(phatbuns_logo_path):
                try:
                    self.drawImage(phatbuns_logo_path, start_x, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
                except Exception:
                    pass

            if sa_flag_path and os.path.exists(sa_flag_path):
                try:
                    self.drawImage(sa_flag_path, start_x + logo_w + gap, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
                except Exception:
                    pass

        self.setFont("Helvetica", 5.5)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        footer_text = "CONFIDENTIAL INFORMATION | Nisaar Ally : SA Master Rights Holder | Email: nisaar@fantastic1.com | Mobile: +27 (0)68 710 1939 | WhatsApp: +27 (0)82 786 7712"
        page_str = f"Page {self._pageNumber} of {page_count}"
        
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(10 * mm, 12 * mm, A4[0] - 10 * mm, 12 * mm)
        
        self.drawString(10 * mm, 8 * mm, footer_text)
        self.drawRightString(A4[0] - 10 * mm, 8 * mm, page_str)
        
        self.restoreState()
# ==========================================
# MASTER 10-HEADING PDF GENERATION ENGINE
# ==========================================
def generate_pdf_report(loc_name, shop, suburb, int_gla, ext_gla, total_gla, model, max_seats, high_seats, capital, wc, int_rent, ext_rent, ops_cost, total_lease_outlay, turnover_clause_pct, recommended_model_name, dscr, payback_df, df_pnl_annual, blueprint_pil_img, applicant_name="Prospective Investor", applicant_email="N/A", applicant_mobile="N/A", selected_menus=[]):
    site_p = SITE_PROFILES.get(loc_name, {
        "landlord": "Property Developers / Landlord",
        "mall_size": "Regional Flagship Retail Node",
        "footfall": "~550,000 visits/month (~6.6M Annually)",
        "households": "24,061 Active Households / ~76,995 Area Population",
        "competitors": "Shoprite, Boxer, Build-It Flagship, Debonairs, Wimpy, Pedro's, Hungry Lion",
        "lsm_profile": "LSM 7–10 / High Purchasing Power Corridor",
        "default_rent": 280.0,
        "default_ops": 35.0,
        "turnover_clause_pct": 7.0
    })

    asset_map = get_asset_images_map()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18, leftMargin=18, topMargin=18, bottomMargin=28)
    styles = getSampleStyleSheet()

    NAVY_HEADER = colors.HexColor('#1A365D')
    ORANGE_BRAND = colors.HexColor('#C53030')
    DARK_TEXT = colors.HexColor('#2D3748')
    WHITE_TEXT = colors.HexColor('#FFFFFF')
    LIGHT_BG = colors.HexColor('#F7FAFC')
    BORDER_COLOR = colors.HexColor('#CBD5E0')
    MAROON_LINE = colors.HexColor('#C53030')

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=WHITE_TEXT, leading=16)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=ORANGE_BRAND, leading=10, alignment=2)
    sec_banner_style = ParagraphStyle('SecBannerStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=8.5, textColor=WHITE_TEXT, leading=10)
    body_bold = ParagraphStyle('BodyBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=DARK_TEXT)
    body_regular = ParagraphStyle('BodyRegular', parent=styles['Normal'], fontName='Helvetica', fontSize=7, leading=9, textColor=DARK_TEXT)
    body_white_bold = ParagraphStyle('BodyWhiteBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=WHITE_TEXT)

    elements = []

    # COVER PAGE (8K FULL-BLEED)
    cover_img_bytes = create_cover_page_image()
    rl_cover_img = RLImage(cover_img_bytes, width=558, height=775)
    elements.append(rl_cover_img)
    elements.append(PageBreak())

    # PAGE 1: SITE EVALUATION
    header_data = [
        [Paragraph("PHATBUNS SOUTH AFRICA", title_style), Paragraph(f"{model.upper()} ({total_gla:.0f} M²)", subtitle_style)],
        [Paragraph(f"SITE EVALUATION & INVESTMENT ANALYSIS — {loc_name.upper() if loc_name else 'TARGET SITE'}", ParagraphStyle('H2Style', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.HexColor('#CCCCCC'))), ""]
    ]
    t_header = Table(header_data, colWidths=[370, 188])
    t_header.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 4), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elements.append(t_header)
    elements.append(Spacer(1, 3))

    kpi_bar_data = [
        [Paragraph("TURNKEY SETUP", body_regular), Paragraph("WORKING CAPITAL", body_regular), Paragraph("BASE NET RENTAL", body_regular), Paragraph("OPS COST", body_regular)],
        [Paragraph(f"<b>R {int(round(capital)):,}</b>", body_bold), Paragraph(f"<b>R {int(round(wc)):,}</b>", body_bold), Paragraph(f"<b>R {int(round((int_rent * int_gla) + (ext_rent * ext_gla))):,}</b>", body_bold), Paragraph(f"<b>R {int(round(ops_cost * total_gla)):,}</b>", body_bold)],
        [Paragraph("Excl. VAT (Turnkey)", ParagraphStyle('Micro', parent=body_regular, fontSize=5.5)), Paragraph("Suggested Reserve", ParagraphStyle('Micro', parent=body_regular, fontSize=5.5)), Paragraph(f"R {int(round(int_rent))} / m² pm", ParagraphStyle('Micro', parent=body_regular, fontSize=5.5)), Paragraph("Gross Rental Terms", ParagraphStyle('Micro', parent=body_regular, fontSize=5.5))]
    ]
    t_kpi_bar = Table(kpi_bar_data, colWidths=[139, 139, 139, 141])
    t_kpi_bar.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), LIGHT_BG), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    elements.append(t_kpi_bar)
    elements.append(Spacer(1, 4))

    # 01. SITE PROFILE & CAPITAL SCHEDULE
    sec1_banner = Table([[Paragraph("01. SITE PROFILE & CAPITAL SCHEDULE", sec_banner_style)]], colWidths=[558])
    sec1_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec1_banner)

    sec1_table_data = [
        [Paragraph("SITE PARAMETER", body_white_bold), Paragraph("SPECIFICATION", body_white_bold), Paragraph("TURNKEY CAPITAL SCHEDULE (EXCL. VAT)", body_white_bold), Paragraph("AMOUNT", body_white_bold)],
        [Paragraph("Location Name", body_bold), Paragraph(f"{loc_name if loc_name else 'Unassigned'} (Shop {shop})", body_regular), Paragraph("50% Deposit on Signing Agreement", body_regular), Paragraph(f"R {int(round(capital*0.50)):,}", body_regular)],
        [Paragraph("Address / Node", body_bold), Paragraph(str(suburb), body_regular), Paragraph("40% Beneficial Occupation (BO)", body_regular), Paragraph(f"R {int(round(capital*0.40)):,}", body_regular)],
        [Paragraph("Store Footprint", body_bold), Paragraph(f"{total_gla:.2f} m² {model} ({int_gla:.0f}m² Int + {ext_gla:.0f}m² Ext)", body_regular), Paragraph("10% Prior to Store Opening", body_regular), Paragraph(f"R {int(round(capital*0.10)):,}", body_regular)],
        [Paragraph("Managing Agent", body_bold), Paragraph(site_p["landlord"], body_regular), Paragraph("Total Turnkey Capital Outlay", body_bold), Paragraph(f"R {int(round(capital)):,}", body_regular)],
        [Paragraph("Mall GLA Size", body_bold), Paragraph(site_p["mall_size"], body_regular), Paragraph("Working Capital Reserve", body_regular), Paragraph(f"R {int(round(wc)):,}", body_regular)],
        [Paragraph("Site Plan Attached", body_bold), Paragraph("Yes (Rendered on Page 5)", body_regular), Paragraph("Landlord Rental Deposit", body_regular), Paragraph(f"R {int(round(total_lease_outlay*3)):,}", body_regular)],
    ]
    t_sec1 = Table(sec1_table_data, colWidths=[110, 160, 198, 90])
    t_sec1.setStyle(TableStyle([('BACKGROUND', (0,0), (1,0), NAVY_HEADER), ('BACKGROUND', (2,0), (3,0), ORANGE_BRAND), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec1)
    elements.append(Spacer(1, 4))

    # 02. LEASE STRUCTURE & FINANCIAL PROVISIONS (RECOMMENDED OFFER TARGET)
    sec2_banner = Table([[Paragraph("02. LEASE STRUCTURE & PROPOSED LANDLORD OFFER TARGETS", sec_banner_style)]], colWidths=[558])
    sec2_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec2_banner)

    monthly_base_rent_total = (int_rent * int_gla) + (ext_rent * ext_gla)
    monthly_threshold_zar = monthly_base_rent_total / (turnover_clause_pct / 100.0)

    sec2_table_data = [
        [Paragraph("LEASE CLAUSE / PROVISION", body_white_bold), Paragraph("TERMS & RATE STRUCTURE", body_white_bold), Paragraph("FINANCIAL ALIGNMENT", body_white_bold)],
        [Paragraph("Lease Period & Renewal", body_bold), Paragraph("5 Years Initial Period + 5-Year Renewal Option", body_regular), Paragraph("60 Months Base Amortization", body_regular)],
        [Paragraph("Base Net Rental Rate Target", body_bold), Paragraph(f"Shop: R {int(round(int_rent))} /m² | Patio: R {int(round(ext_rent))} /m²", body_regular), Paragraph(f"R {int(round(monthly_base_rent_total)):,} / month", body_regular)],
        [Paragraph("Annual Rental Escalation", body_bold), Paragraph("7.0% per annum effective anniversary", body_regular), Paragraph(f"Year 2 Base: R {int(round(monthly_base_rent_total * 1.07)):,} / month", body_regular)],
        [Paragraph("Annual Turnover Rental Clause", body_bold), Paragraph(f"{turnover_clause_pct}% of net turnover vs Base Net Rental (whichever greater)", body_regular), Paragraph(f"Effective Threshold: > R {int(round(monthly_threshold_zar)):,} p.m.", body_regular)],
        [Paragraph("Beneficial Occupation (BO)", body_bold), Paragraph("2 Month Rent-Free BO for Turnkey Store Fitout", body_regular), Paragraph("Fitout Schedule: 60 Days", body_regular)]
    ]
    t_sec2 = Table(sec2_table_data, colWidths=[150, 248, 160])
    t_sec2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec2)
    elements.append(Spacer(1, 4))

    # 03. DYNAMIC CATCHMENT & LOCATION INTELLIGENCE (AUDITED LIVE TENANTS & DEMOGRAPHICS)
    sec3_banner = Table([[Paragraph("03. DYNAMIC CATCHMENT & LOCATION INTELLIGENCE", sec_banner_style)]], colWidths=[558])
    sec3_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec3_banner)

    sec3_grid_data = [
        [Paragraph("CATCHMENT METRIC", body_white_bold), Paragraph("DATA POINT / LOCATION ANALYSIS", body_white_bold)],
        [Paragraph("LSM / ESM Profile", body_bold), Paragraph(site_p.get("lsm_profile", "LSM 7–10 / High Purchasing Power Corridor"), body_regular)],
        [Paragraph("Monthly / Annual Footfall", body_bold), Paragraph(site_p["footfall"], body_regular)],
        [Paragraph("Catchment Household Count", body_bold), Paragraph(site_p["households"], body_regular)],
        [Paragraph("In-Mall Competitor Profile", body_bold), Paragraph(site_p["competitors"], body_regular)]
    ]
    t_sec3_grid = Table(sec3_grid_data, colWidths=[150, 408])
    t_sec3_grid.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec3_grid)

    elements.append(PageBreak())
    # PAGE 2: HEADINGS 04, 04A, 05, 06
    p2_title = ParagraphStyle('P2Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=13, textColor=DARK_TEXT, alignment=1)
    elements.append(Paragraph(f"PHATBUNS SOUTH AFRICA — {loc_name.upper() if loc_name else 'TARGET SITE'} PROSPECTUS", p2_title))
    elements.append(HRFlowable(width="100%", thickness=1, color=MAROON_LINE, spaceBefore=2, spaceAfter=5))

    # 04. FINANCIAL RECOVERY & UNIT SALES TARGET MATRIX
    sec4_banner = Table([[Paragraph("04. FINANCIAL RECOVERY & UNIT SALES TARGET MATRIX", sec_banner_style)]], colWidths=[558])
    sec4_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec4_banner)

    matrix_table_data = [[Paragraph(f"<b>{col}</b>", body_white_bold) for col in payback_df.columns]]
    for idx, row in payback_df.iterrows():
        row_cells = []
        for col in payback_df.columns:
            row_cells.append(Paragraph(str(row[col]), body_regular))
        matrix_table_data.append(row_cells)

    t_matrix = Table(matrix_table_data, colWidths=[148, 82, 82, 82, 82, 82], hAlign='CENTER')
    t_matrix.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY_HEADER),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 2),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG),
    ]))
    elements.append(t_matrix)
    elements.append(Spacer(1, 3))

    # 04A. RECOVERY PERIOD & TURNOVER TARGET WITH AVERAGE DAILY UNIT SALES
    sec4a_banner = Table([[Paragraph("04A. RECOVERY PERIOD & TURNOVER TARGET WITH AVERAGE DAILY UNIT SALES", sec_banner_style)]], colWidths=[558])
    sec4a_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec4a_banner)

    elements.append(Paragraph("<b>Detailed Investment Recovery Window (12 to 24 Months Target Analysis):</b><br/>"
                              "• <b>12-Month Accelerated Recovery:</b> Requires monthly turnover of <b>R 579,193</b> (approx. 3,049 units/month or <b>102 units/day</b>).<br/>"
                              "• <b>18-Month Balanced Recovery:</b> Requires monthly turnover of <b>R 440,000</b> (approx. 2,315 units/month or <b>77 units/day</b>).<br/>"
                              "• <b>24-Month Standard Recovery:</b> Requires monthly turnover of <b>R 389,799</b> (approx. 2,052 units/month or <b>69 units/day</b>).<br/>"
                              "<i>Note: All turnover projections and daily unit velocity targets are modeled estimates (E&OE) and subject to actual store footfall conversion and operational execution.</i>", body_regular))
    elements.append(Spacer(1, 3))

    # 05. OPERATIONS, STAFFING & CHANNEL BREAKDOWN
    sec5_banner = Table([[Paragraph("05. OPERATIONS, STAFFING & CHANNEL BREAKDOWN", sec_banner_style)]], colWidths=[558])
    sec5_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec5_banner)

    sec5_data = [
        [Paragraph("REVENUE CHANNEL SPLIT", body_white_bold), Paragraph("STAFFING STRUCTURE (BCEA 8-HR SHIFTS)", body_white_bold)],
        [Paragraph("• Online Deliveries (UberEats/Mr D): 45%<br/>• Takeaway & Counter Collect: 30%<br/>• In-Store Express Dining: 25%", body_regular),
         Paragraph("• 1 x Store Manager — Operations & Inventory Control<br/>• 2 x Shift Supervisors — Floor Leads & POS Management<br/>• 3 x Line Grillers & Fryers — Smash Griddle & Assembly<br/>• 2 x Till Operators / Runners — Front-of-House Dispatch<br/>• 2 x Cleaners & Scullery — Hygiene & SANHA Standards", body_regular)]
    ]
    t_sec5 = Table(sec5_data, colWidths=[180, 378])
    t_sec5.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2.5), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec5)
    elements.append(Spacer(1, 3))

    # 06. TURNKEY KITCHEN EQUIPMENT MANIFEST
    sec6_banner = Table([[Paragraph("06. TURNKEY KITCHEN EQUIPMENT MANIFEST", sec_banner_style)]], colWidths=[558])
    sec6_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec6_banner)

    sec6_data = [
        [Paragraph("STATION / CATEGORY", body_white_bold), Paragraph("EQUIPMENT SPECIFICATION", body_white_bold)],
        [Paragraph("Smash Grill Station", body_bold), Paragraph("Chrome Smash Griddle (3-Phase Heavy Duty), Bun Toaster & Pass-Through Heated Holding Cabinet.", body_regular)],
        [Paragraph("Frying & Prep Line", body_bold), Paragraph("Dual-Pan High-Recovery Deep Fryer, 3-Door Under-Counter Prep Fridge with Topping Rail.", body_regular)],
        [Paragraph("Extraction & Canopy", body_bold), Paragraph("Stainless Steel Wall-Mounted Extraction Canopy complete with ANSUL Fire Suppression System.", body_regular)],
        [Paragraph("POS & Automation", body_bold), Paragraph("Dual-Screen Touch POS Terminal, Kitchen Display System (KDS), Thermal Printers & Router setup.", body_regular)],
        [Paragraph("Beverage & Shakes", body_bold), Paragraph("Heavy Duty Commercial Variable Speed Blender & Commercial Ice Machine (40kg/24hr capacity).", body_regular)],
        [Paragraph("Storage & Washup", body_bold), Paragraph("Stainless Steel Work Tables, Double Bowl Scullery Sink, Hand Wash Basin & Wall Shelving units.", body_regular)]
    ]
    t_sec6 = Table(sec6_data, colWidths=[140, 418])
    t_sec6.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec6)

    elements.append(PageBreak())

    # PAGE 3: HEADINGS 07, 08, 09, 10
    sec7_banner = Table([[Paragraph("07. BRAND HERITAGE, USP & PRODUCT STANDARDS", sec_banner_style)]], colWidths=[558])
    sec7_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec7_banner)
    elements.append(Paragraph(f"Founded in 2019, Phatbuns was built from a vision to reinvent the smash burger experience within the fast-casual market. Phatbuns brings a premier culinary disruption to {loc_name if loc_name else 'the selected market'}, specializing in artisan smash burgers, proprietary secret sauces, and hand-crafted brioche buns. All ingredients and proteins adhere strictly to central supply chain quality assurance protocols, ensuring 100% consistency, Halal compliance (SANHA), and exceptional taste profiles across the store.", body_regular))
    elements.append(Spacer(1, 3))

    sec8_banner = Table([[Paragraph("08. MARKETING, LAUNCH STRATEGY & DIGITAL ACQUISITION", sec_banner_style)]], colWidths=[558])
    sec8_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec8_banner)
    elements.append(Paragraph(f"Franchisees at {loc_name if loc_name else 'this location'} benefit from a robust multi-channel marketing framework including pre-launch digital teaser campaigns, local influencer seeding, geo-fenced social media performance marketing targeting surrounding residential nodes, and integrated delivery aggregator partnerships (UberEats, Mr D).", body_regular))
    elements.append(Spacer(1, 3))

    sec9_banner = Table([[Paragraph("09. FRANCHISEE SUPPORT, TRAINING & OPERATIONAL GOVERNANCE", sec_banner_style)]], colWidths=[558])
    sec9_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec9_banner)
    elements.append(Paragraph(f"Every Phatbuns franchise partner receives extensive onboarding and operational training to ensure successful store performance from day one. Comprehensive initial training covers a 4-week intensive program across back-of-house grill mastery, inventory control, and front-of-house guest hospitality.", body_regular))
    elements.append(Spacer(1, 3))

    sec10_banner = Table([[Paragraph("10. GOVERNANCE, COMPLIANCE & NEXT STEPS", sec_banner_style)]], colWidths=[558])
    sec10_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec10_banner)
    elements.append(Paragraph(f"To proceed with site allocation at {loc_name if loc_name else 'the targeted site'}, prospective investors must: (1) Execute the attached Non-Circumvention, Non-Disclosure Agreement (NCNDA), (2) Submit verified proof of unencumbered cash equity, (3) Settle the review administrative fee, and (4) Sign formal franchise agreements upon executive board approval.", body_regular))

    elements.append(PageBreak())

    # PAGE 4: 5-YEAR P&L & 11A TOTAL ROI BREAKDOWN
    elements.append(Paragraph("11. 5-YEAR PRO FORMA INCOME STATEMENT & P&L FORECAST", ParagraphStyle('P3PnlH', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=MAROON_LINE)))
    elements.append(Paragraph("Standard Model Parameters: 50% Debt Funding @ 11.75% Prime Rate | 35% COGS | 9% Royalties & Marketing | E&OE", body_regular))
    elements.append(Spacer(1, 4))

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

    t_pnl = Table(pnl_table_data, colWidths=[51, 69, 64, 62, 59, 62, 64, 60, 67], hAlign='CENTER')
    t_pnl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY_HEADER),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 2),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG),
    ]))
    elements.append(t_pnl)
    elements.append(Spacer(1, 6))

    # 11A: TOTAL ROI, TOTAL LANDLORD RENTALS, TOTAL ROYALTIES & MASTER RECOMMENDATION
    sec11a_banner = Table([[Paragraph("11A. AGGREGATE 5-YEAR FINANCIAL RETURN (ROI), LANDLORD RENTALS & MASTER RECOMMENDATION", sec_banner_style)]], colWidths=[558])
    sec11a_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec11a_banner)

    total_5yr_rentals = sum([row['Lease Outlay'] for idx, row in df_pnl_annual.iterrows()])
    total_5yr_royalties = sum([row['Royalties (9%)'] for idx, row in df_pnl_annual.iterrows()])
    total_5yr_net_profit = sum([row['Net Operating Profit'] for idx, row in df_pnl_annual.iterrows()])
    initial_total_investment = capital + wc

    roi_yr_list = []
    for idx, row in df_pnl_annual.iterrows():
        net_prof_yr = row['Net Operating Profit']
        yr_roi = (net_prof_yr / initial_total_investment) * 100.0 if initial_total_investment > 0 else 0.0
        roi_yr_list.append(f"{row['Year_Label']}: {yr_roi:.1f}%")
    
    five_yr_roi_pct = (total_5yr_net_profit / initial_total_investment) * 100.0 if initial_total_investment > 0 else 0.0
    roi_breakdown_str = ", ".join(roi_yr_list) + f" | <b>5-Year Cumulative ROI: {five_yr_roi_pct:.1f}%</b>"

    is_site_feasible = total_5yr_net_profit > 0
    feasibility_status_text = "Phatbuns South Africa, advise the site as Feasible." if is_site_feasible else "Phatbuns South Africa, Does not advise this Site."
    feasibility_bg_color = colors.HexColor('#28a745') if is_site_feasible else colors.HexColor('#C53030')
    feasibility_text_color = colors.HexColor('#000000') if is_site_feasible else colors.HexColor('#FFFFFF')

    sec11a_data = [
        [Paragraph("FINANCIAL METRIC / AGGREGATE CATEGORY", body_white_bold), Paragraph("5-YEAR PROJECTED CUMULATIVE VALUE (ZAR)", body_white_bold)],
        [Paragraph("Total Landlord Rentals Paid (5 Years)", body_bold), Paragraph(f"R {int(round(total_5yr_rentals)):,}", body_regular)],
        [Paragraph("Total Central Royalties Paid (9% over 5 Years)", body_bold), Paragraph(f"R {int(round(total_5yr_royalties)):,}", body_regular)],
        [Paragraph("Cumulative Net Operating Profit (After Debt Service)", body_bold), Paragraph(f"R {int(round(total_5yr_net_profit)):,}", body_regular)],
        [Paragraph("Year-by-Year & Cumulative ROI (%)", body_bold), Paragraph(roi_breakdown_str, body_regular)],
        [Paragraph("Site Feasibility & Master Recommendation", body_bold), Paragraph(f"<b>{feasibility_status_text}</b><br/>Recommended Model: {recommended_model_name}. Any store footprint larger than recommended requires formal re-evaluation (E&OE).", ParagraphStyle('FeasStyle', parent=body_regular, textColor=feasibility_text_color, fontName='Helvetica-Bold'))]
    ]
    t_sec11a = Table(sec11a_data, colWidths=[200, 358])
    t_sec11a.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY_HEADER),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 2.5),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG),
        ('BACKGROUND', (1, 5), (1, 5), feasibility_bg_color)
    ]))
    elements.append(t_sec11a)

    elements.append(PageBreak())

    # PAGE 5: DEDICATED STORE DEVELOPMENT LEASING LAYOUT PLAN (PROPORTIONAL VECTOR SCALING)
    blueprint_header_style = ParagraphStyle('BPHeader', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=NAVY_HEADER, alignment=1)
    blueprint_subheader_style = ParagraphStyle('BPSubHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=ORANGE_BRAND, alignment=1)

    elements.append(Paragraph(f"<b>{loc_name.upper() if loc_name else 'TARGET LOCATION'} — SHOP {shop.upper()}</b>", blueprint_header_style))
    elements.append(Paragraph(f"<b>DEVELOPMENT LEASING LAYOUT PLAN ({total_gla:.2f} M² | {model}) — RECOMMENDED: {recommended_model_name.upper()}</b>", blueprint_subheader_style))
    elements.append(Spacer(1, 4))
    elements.append(HRFlowable(width="100%", thickness=1, color=NAVY_HEADER, spaceBefore=2, spaceAfter=8))

    effective_blueprint_img = blueprint_pil_img
    if effective_blueprint_img is None and loc_name:
        auto_bp_path = find_site_blueprint(loc_name)
        if auto_bp_path and os.path.exists(auto_bp_path):
            try:
                effective_blueprint_img = Image.open(auto_bp_path).convert("RGB")
            except Exception:
                pass

    if effective_blueprint_img is not None:
        try:
            bp_byte_arr = io.BytesIO()
            effective_blueprint_img.save(bp_byte_arr, format='JPEG', quality=95)
            bp_byte_arr.seek(0)
            rl_blueprint = RLImage(bp_byte_arr, width=480, height=310, preserveAspectRatio=True)
            elements.append(rl_blueprint)
        except Exception:
            elements.append(Paragraph("<b>Blueprint Render Initialized</b>", ParagraphStyle('NAStyle', parent=body_regular, textColor=colors.HexColor('#8B0000'), fontSize=10)))
    else:
        placeholder_img = Image.new("RGB", (900, 600), color=(245, 247, 250))
        draw = ImageDraw.Draw(placeholder_img)
        draw.rectangle([15, 15, 885, 585], outline=(26, 54, 93), width=4)
        
        for x in range(100, 800, 100):
            draw.line([(x, 15), (x, 585)], fill=(220, 225, 230), width=1)
        for y in range(100, 500, 100):
            draw.line([(15, y), (885, y)], fill=(220, 225, 230), width=1)

        total_internal = max(int_gla, 1.0)
        kitchen_ratio = min(60.0 / total_internal, 0.65) if total_internal > 0 else 0.40
        kitchen_width_px = int(845 * kitchen_ratio)
        
        kitchen_box_end = 40 + kitchen_width_px
        dining_box_start = kitchen_box_end + 10

        draw.rectangle([40, 40, kitchen_box_end, 560], outline=(197, 48, 48), width=3)
        draw.rectangle([dining_box_start, 40, 860, 560], outline=(43, 108, 176), width=3)
        
        try:
            draw.text((330, 260), f"PROPOSED STORE LAYOUT PLAN: {loc_name if loc_name else 'Select Location'} (Shop {shop})", fill=(26, 54, 93))
            draw.text((50, 280), f"KITCHEN & PREP ZONE ({min(60.0, total_internal*kitchen_ratio):.1f} SQM)", fill=(197, 48, 48))
            draw.text((dining_box_start + 20, 280), f"DINING & FOH AREA ({max_seats} SEATS)", fill=(43, 108, 176))
        except Exception:
            pass

        bp_byte_arr = io.BytesIO()
        placeholder_img.save(bp_byte_arr, format='JPEG', quality=95)
        bp_byte_arr.seek(0)
        rl_blueprint = RLImage(bp_byte_arr, width=480, height=310, preserveAspectRatio=True)
        elements.append(rl_blueprint)

    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"<b>Technical Specifications & Master Recommendation:</b> Internal GLA: {int_gla:.2f} sqm | External Patio GLA: {ext_gla:.2f} sqm | Total Footprint: {total_gla:.2f} sqm. Kitchen space engineered around preferred 60.00 sqm layout for SANHA Halal compliance. <b>Master Note:</b> Recommended model is <b>{recommended_model_name}</b>. Footprints exceeding this size require formal re-evaluation (E&OE).", body_regular))

    elements.append(PageBreak())

    # PAGE 6: DEDICATED BRAND MENUS & MEDIA SHOWCASE
    elements.append(Paragraph("<b>PHATBUNS BRAND PORTFOLIO & GLOBAL MEDIA SHOWCASE</b>", blueprint_header_style))
    elements.append(Paragraph("<b>CLICKABLE DOWNLOAD LINKS FOR BRAND MENUS, STORE VISUALS & VIDEO WALK-THROUGHS</b>", blueprint_subheader_style))
    elements.append(Spacer(1, 4))
    elements.append(HRFlowable(width="100%", thickness=1, color=NAVY_HEADER, spaceBefore=2, spaceAfter=8))

    menu_sec_banner = Table([[Paragraph("CLICKABLE BRAND MENUS & CONCEPT CATALOGS (GOOGLE DRIVE)", sec_banner_style)]], colWidths=[558])
    menu_sec_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(menu_sec_banner)

    menu_table_rows = [
        [Paragraph("BRAND & CONCEPT", body_white_bold), Paragraph("MENU SPECIFICATION & OVERVIEW", body_white_bold), Paragraph("GOOGLE DRIVE DOWNLOAD LINK", body_white_bold)]
    ]

    for brand_name, info in BRAND_MENU_CATALOG.items():
        drive_url = get_drive_menu_download_url(info["drive_file_id"])
        btn_html = f'<a href="{drive_url}" color="#0066CC"><b>📥 DOWNLOAD MENU (PDF)</b></a>'
        logo_path = asset_map.get(info.get("logo_key", "phatbuns_sa"))

        if logo_path and os.path.exists(logo_path):
            try:
                rl_logo = RLImage(logo_path, width=42, height=28)
                brand_cell_elements = [
                    rl_logo,
                    Spacer(1, 2),
                    Paragraph(f"<b>{brand_name}</b><br/><font color='#C53030'><i>{info['tagline']}</i></font>", body_regular)
                ]
            except Exception:
                brand_cell_elements = Paragraph(f"<b>{brand_name}</b><br/><font color='#C53030'><i>{info['tagline']}</i></font>", body_regular)
        else:
            brand_cell_elements = Paragraph(f"<b>{brand_name}</b><br/><font color='#C53030'><i>{info['tagline']}</i></font>", body_regular)

        menu_table_rows.append([
            brand_cell_elements,
            Paragraph(info["description"], body_regular),
            Paragraph(btn_html, ParagraphStyle('MenuLinkStyle', parent=body_regular, alignment=1))
        ])

    t_menu_links = Table(menu_table_rows, colWidths=[130, 288, 140])
    t_menu_links.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), ORANGE_BRAND),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG),
    ]))
    elements.append(t_menu_links)
    elements.append(Spacer(1, 6))

    media_sec_banner = Table([[Paragraph("GLOBAL STORE VISUALS & VIDEO WALK-THROUGHS", sec_banner_style)]], colWidths=[558])
    media_sec_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(media_sec_banner)

    media_table_rows = [
        [Paragraph("STORE LOCATION / MEDIA TYPE", body_white_bold), Paragraph("VISUAL CONTENT DESCRIPTION", body_white_bold), Paragraph("DIRECT WATCH / VIEW LINK", body_white_bold)],
        [Paragraph("<b>Sample Store Gallery & Photos</b>", body_regular), Paragraph("High-resolution photos of operational Phatbuns stores, interiors & lighting.", body_regular), Paragraph(f'<a href="{STORE_MEDIA_LINKS["store_photos"]}" color="#0066CC"><b>🖼️ VIEW PHOTO GALLERY</b></a>', ParagraphStyle('M1', parent=body_regular, alignment=1))],
        [Paragraph("<b>Phatbuns UK Store Video 1</b>", body_regular), Paragraph("Full video walk-through of active UK franchise store operations.", body_regular), Paragraph(f'<a href="{STORE_MEDIA_LINKS["uk_video_1"]}" color="#0066CC"><b>🎬 WATCH UK VIDEO 1</b></a>', ParagraphStyle('M2', parent=body_regular, alignment=1))],
        [Paragraph("<b>Phatbuns UK Store Video 2</b>", body_regular), Paragraph("Secondary UK store video showcasing peak trading & kitchen throughput.", body_regular), Paragraph(f'<a href="{STORE_MEDIA_LINKS["uk_video_2"]}" color="#0066CC"><b>🎬 WATCH UK VIDEO 2</b></a>', ParagraphStyle('M3', parent=body_regular, alignment=1))],
        [Paragraph("<b>Phatbuns Dubai Flagship Video</b>", body_regular), Paragraph("Flagship Dubai store layout, luxury finishes & customer experience.", body_regular), Paragraph(f'<a href="{STORE_MEDIA_LINKS["dubai_video"]}" color="#0066CC"><b>🎬 WATCH DUBAI VIDEO</b></a>', ParagraphStyle('M4', parent=body_regular, alignment=1))]
    ]
    t_media_links = Table(media_table_rows, colWidths=[140, 278, 140])
    t_media_links.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY_HEADER),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG),
    ]))
    elements.append(t_media_links)

    elements.append(PageBreak())

    # PAGE 7: FULL 1-PAGE CONSOLIDATED MASTER NCNDA LEGAL TEMPLATE (CLAUSES 1 - 6 & SIGNATURES)
    ncnda_header_style = ParagraphStyle('NCNDAHeader', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=NAVY_HEADER, alignment=1)
    elements.append(Paragraph("<b>NON-DISCLOSURE AND NON-CIRCUMVENTION AGREEMENT (NCNDA)</b>", ncnda_header_style))
    elements.append(Paragraph("<b>PHATBUNS SOUTH AFRICA FAST FOOD FRANCHISE</b>", ParagraphStyle('NCNDASub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=ORANGE_BRAND, alignment=1)))
    elements.append(HRFlowable(width="100%", thickness=1, color=MAROON_LINE, spaceBefore=2, spaceAfter=4))

    ncnda_legal_body = ParagraphStyle('NCNDABody', parent=styles['Normal'], fontName='Helvetica', fontSize=6.8, leading=8.8, textColor=DARK_TEXT)
    ncnda_title_style = ParagraphStyle('NCNDATitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=NAVY_HEADER)

    elements.append(Paragraph("<b>Entered into by and between:</b>", ncnda_title_style))
    elements.append(Paragraph(f"<b>1. PHATBUNS SOUTH AFRICA</b> (hereinafter referred to as the 'Disclosing Party' or 'Franchisor'), and <b>2. THE UNDERSIGNED PARTY</b> (hereinafter referred to as the 'Receiving Party' or 'Prospective Franchisee'), full legal details: <b>{applicant_name}</b> | Email: <b>{applicant_email}</b> | Tel: <b>{applicant_mobile}</b> | Target Node: <b>{loc_name if loc_name else 'Unassigned'} ({shop})</b>.", ncnda_legal_body))
    elements.append(Spacer(1, 3))

    elements.append(Paragraph("<b>1. PURPOSE & SCOPE OF DISCUSSION</b>", ncnda_title_style))
    elements.append(Paragraph("The Parties wish to enter into discussions concerning a potential business relationship relating to a fast-food franchise opportunity under the Phatbuns brand in South Africa (the 'Permitted Purpose'). In connection with this, the Disclosing Party will share proprietary business systems, financial models, recipes, operational manuals, and strategic information.", ncnda_legal_body))
    elements.append(Spacer(1, 3))

    elements.append(Paragraph("<b>2. FASA COMPLIANCE & ETHICAL STANDARDS</b>", ncnda_title_style))
    elements.append(Paragraph("The Parties acknowledge that this Agreement and subsequent franchise disclosures are intended to comply with the ethical frameworks and guidelines established by the Franchise Association of South Africa (FASA) and the Consumer Protection Act, No. 68 of 2008 (CPA). All negotiations, document exchanges, and disclosures shall be carried out in good faith and transparency.", ncnda_legal_body))
    elements.append(Spacer(1, 3))

    elements.append(Paragraph("<b>3. PROTECTION OF PERSONAL INFORMATION (POPIA)</b>", ncnda_title_style))
    elements.append(Paragraph("Both Parties explicitly commit to complying with the Protection of Personal Information Act, No. 4 of 2013 (POPIA) in relation to any personal information processed under this Agreement: (a) The Receiving Party shall only process personal information strictly for the Permitted Purpose; (b) Appropriate technical security measures shall be maintained; (c) Information shall be securely destroyed when no longer required.", ncnda_legal_body))
    elements.append(Spacer(1, 3))

    elements.append(Paragraph("<b>4. CONFIDENTIALITY OBLIGATIONS</b>", ncnda_title_style))
    elements.append(Paragraph("The Receiving Party agrees to maintain strict confidentiality regarding all Confidential Information disclosed by Phatbuns South Africa, including financial projections, supply chain data, setup costs, operational workflows, brand secrets, and marketing methodologies.", ncnda_legal_body))
    elements.append(Spacer(1, 3))

    elements.append(Paragraph("<b>5. NON-CIRCUMVENTION</b>", ncnda_title_style))
    elements.append(Paragraph("The Receiving Party covenants that it will not, directly or indirectly, circumvent, bypass, or avoid Phatbuns South Africa to enter into any business transaction, franchise system, or contract with suppliers, landlords, or partners introduced by the Disclosing Party during discussions. The Receiving Party shall not use the Disclosing Party's concepts to establish a competing business for 24 months following termination.", ncnda_legal_body))
    elements.append(Spacer(1, 3))

    elements.append(Paragraph("<b>6. GOVERNING LAW AND JURISDICTION</b>", ncnda_title_style))
    elements.append(Paragraph("This Agreement shall be governed by, construed, and enforced in accordance with the laws of the Republic of South Africa under the exclusive jurisdiction of the High Court of South Africa.", ncnda_legal_body))
    elements.append(Spacer(1, 8))

    sig_p_ncnda = [
        [Paragraph(f"<b>For: PHATBUNS SOUTH AFRICA</b><br/><br/>____________________________________<br/><b>Authorized Signature</b><br/><b>Name:</b> Nisaar Ally<br/><b>Title:</b> SA Master Rights Holder<br/><b>Date:</b> ____ / ____ / 2026 | <b>Place:</b> Johannesburg", body_regular),
         Paragraph(f"<b>For: THE RECEIVING PARTY</b><br/><br/>____________________________________<br/><b>Authorized Signature</b><br/><b>Name:</b> {applicant_name}<br/><b>Title:</b> Prospective Franchisee<br/><b>Date:</b> ____ / ____ / 2026 | <b>ID:</b> _______________________", body_regular)]
    ]
    t_sig_ncnda = Table(sig_p_ncnda, colWidths=[270, 270], hAlign='CENTER')
    t_sig_ncnda.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('PADDING', (0,0), (-1,-1), 5)
    ]))
    elements.append(t_sig_ncnda)

    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

def generate_pipeline_pdf(df_pipeline):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=15, textColor=colors.HexColor('#111111'), leading=18, alignment=1)
    section_heading = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#8B0000'), leading=12, spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#222222'))

    elements = []
    elements.append(Paragraph("PHATBUNS SOUTH AFRICA", title_style))
    elements.append(Paragraph("Franchisee & Investor Pipeline Audit Report", section_heading))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#8B0000'), spaceBefore=4, spaceAfter=8))

    if not df_pipeline.empty:
        table_data = [[
            Paragraph("<b>ID</b>", body_style),
            Paragraph("<b>Applicant</b>", body_style),
            Paragraph("<b>Mobile / Tel</b>", body_style),
            Paragraph("<b>Email Address</b>", body_style),
            Paragraph("<b>Preferred Site</b>", body_style),
            Paragraph("<b>Model</b>", body_style),
            Paragraph("<b>Capital</b>", body_style),
            Paragraph("<b>Equity %</b>", body_style),
            Paragraph("<b>CEO Status</b>", body_style)
        ]]
        for index, row in df_pipeline.iterrows():
            mob_val = str(row['mobile']) if str(row['mobile']).strip() else "N/A"
            email_val = str(row['email']) if str(row['email']).strip() else "N/A"
            table_data.append([
                Paragraph(str(row['id']), body_style),
                Paragraph(str(row['full_name']), body_style),
                Paragraph(mob_val, body_style),
                Paragraph(email_val, body_style),
                Paragraph(str(row['preferred_site']), body_style),
                Paragraph(str(row['store_model']), body_style),
                Paragraph(f"R {int(round(row['capital_available'])):,}", body_style),
                Paragraph(f"{row['unencumbered_cash_pct']:.0f}%", body_style),
                Paragraph(str(row['ceo_approval']), body_style)
            ])

        t_pipe = Table(table_data, colWidths=[20, 80, 75, 115, 90, 80, 55, 40, 45], hAlign='CENTER')
        t_pipe.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EFEFEF')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 3)
        ]))
        elements.append(t_pipe)
    else:
        elements.append(Paragraph("No applicant records available in database.", body_style))

    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

# ==========================================
# STREAMLIT UI TABS ENGINE
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "📊 Feasibility & Bank Model",
    "📖 Brand Menus & Media Showcase",
    "📋 Investor & Franchisee Registry"
])

# TAB 1: FEASIBILITY & BANK MODEL
with tab1:
    st.header("Site Feasibility & Landlord Analysis Engine")
    
    analysis_mode = st.radio(
        "Select Feasibility Analysis Mode:",
        ["1. I have a Landlord Proposal / Offer Sheet", "2. No Proposal — Check Mall Viability & Propose Target Rates"],
        index=0,
        horizontal=True
    )

    extracted_parsed_res = {}

    if "1. I have a Landlord Proposal" in analysis_mode:
        st.subheader("Automated Landlord Proposal Extractor")
        st.markdown("Upload a landlord proposal screenshot/email (JPG, PNG, PDF) or paste offer text below to auto-populate site parameters.")

        col_up1, col_up2 = st.columns(2)
        with col_up1:
            uploaded_offer_file = st.file_uploader("Upload Offer File (JPG, PNG, PDF, Screenshot)", type=["jpg", "jpeg", "png", "pdf"])
        with col_up2:
            pasted_text = st.text_area("Or Paste Email / Whatsapp Offer Text Directly", height=100, placeholder="Paste landlord offer text here...")

        if st.button("⚡ Extract & Pre-Fill Lease Terms"):
            if uploaded_offer_file is not None:
                pil_img, pdf_text = process_uploaded_file(uploaded_offer_file)
                if pil_img is not None:
                    extracted_parsed_res = extract_lease_from_source(pil_img)
                elif pdf_text:
                    extracted_parsed_res = extract_lease_from_source(pdf_text)

            if not extracted_parsed_res and pasted_text:
                extracted_parsed_res = extract_lease_from_source(pasted_text)

    else:
        st.subheader("Mall Viability & Store Model Recommender")
        st.markdown("Evaluates location feasibility using **Monthly Footfall**, **Catchment Profile**, and **In-Mall Competitor Density**.")

    st.divider()

    st.header("1. Site & Lease Specification")

    col1, col2 = st.columns(2)
    with col1:
        selected_location = st.selectbox("Select Commercial Location", options=list(LOCATION_LOOKUP.keys()), index=0)
        if selected_location == "Custom / Other Site...":
            custom_input = st.text_input("Enter Custom Location Name", value="", placeholder="e.g. Rondebuilt Centre", key="custom_site_name_input")
            location_name = custom_input
            
            if custom_input:
                if st.button("🔍 Research & Auto-Populate Site Data", key="research_web_btn"):
                    with st.spinner(f"Searching web and gathering intelligence for '{custom_input}'..."):
                        web_intel = research_location_online(custom_input)
                        SITE_PROFILES[custom_input] = web_intel
                        
                        suburb_val = web_intel.get("suburb", f"{custom_input.title()}, Gauteng")
                        suburb_options = web_intel.get("options", [suburb_val])
                        
                        st.session_state["discovered_suburb_options"] = suburb_options
                        st.session_state["suburb_node_input_key"] = suburb_val
                        st.session_state[f"{re.sub(r'[^a-zA-Z0-9]', '_', custom_input.lower())}_suburb_val"] = suburb_val
                        
                        st.success(f"Location intelligence retrieved for **{custom_input}**! Suburb Node: **{suburb_val}** | Market Rent Target: **R {web_intel.get('default_rent', 220.0)}/m²**")
        else:
            location_name = selected_location

    site_key = re.sub(r'[^a-zA-Z0-9]', '_', location_name.lower()) if location_name else "unassigned_site"
    
    def get_site_state(key, default_val):
        full_key = f"{site_key}_{key}"
        if full_key not in st.session_state:
            st.session_state[full_key] = default_val
        return st.session_state[full_key]

    def set_site_state(key, val):
        full_key = f"{site_key}_{key}"
        st.session_state[full_key] = val

    site_default_info = SITE_PROFILES.get(location_name, {
        "suburb": LOCATION_LOOKUP.get(selected_location, ""),
        "shop": "",
        "default_rent": 220.0,
        "default_ops": 32.50,
        "default_gla": 98.0,
        "model": "Express Model",
        "footfall": "~380,000 visits/month",
        "households": "24,061 Active Households / ~76,995 Area Population",
        "competitors": "Shoprite, Boxer, Build-It Flagship, Debonairs, Wimpy, Pedro's, Hungry Lion",
        "lsm_profile": "LSM 6-9",
        "turnover_clause_pct": 7.0
    })

    area_market_rent = site_default_info.get("default_rent", 220.0)

    footfall_raw = site_default_info.get("footfall", "380000")
    footfall_num_match = re.search(r'[\d\,]+', footfall_raw.replace('~', ''))
    parsed_footfall = int(footfall_num_match.group(0).replace(',', '')) if footfall_num_match else 380000

    rec_model = "Express Model"
    rec_status = "FEASIBLE"
    rec_color = "#28a745"
    rec_reason = ""

    if parsed_footfall >= 700000:
        rec_model = "Multi-Brand Kitchen Model"
        rec_reason = "High monthly footfall (>700k) supports a multi-brand kitchen setup with delivery integration."
    elif parsed_footfall >= 550000:
        rec_model = "Full Sit-Down Model"
        rec_reason = "Solid regional mall footfall (550k–700k) provides strong sit-down customer traffic."
    elif parsed_footfall >= 350000:
        rec_model = "Express Model"
        rec_reason = "Moderate footfall (350k–550k) suits a lean Express model for fast throughput."
    else:
        rec_model = "Kiosk Model"
        rec_reason = "Lower footfall (<350k) requires a low-overhead Kiosk model."

    if location_name:
        st.markdown(f"""
        <div style="background-color:#1c2333; padding:15px; border-radius:8px; border-left:5px solid {rec_color}; margin-bottom:15px;">
            <h4 style="margin:0; color:#FFFFFF;">💡 Phatbuns SA Master Recommendation: <b>{rec_model}</b></h4>
            <p style="margin:5px 0 0 0; color:#CCCCCC; font-size:13px;"><b>Status:</b> <span style="color:{rec_color}; font-weight:bold;">{rec_status}</span> | {rec_reason}<br/>
            <i>Master Note: Any store footprint or model larger than this recommended size will require a formal re-evaluation and feasibility study, as this will increase the recovery of investment term and impact ROI values (E&OE).</i></p>
        </div>
        """, unsafe_allow_html=True)

    if extracted_parsed_res:
        if 'shop_code' in extracted_parsed_res: set_site_state("shop_code", str(extracted_parsed_res['shop_code']))
        if 'internal_gla' in extracted_parsed_res: set_site_state("internal_gla", float(extracted_parsed_res['internal_gla']))
        if 'external_gla' in extracted_parsed_res: set_site_state("external_gla", float(extracted_parsed_res['external_gla']))
        if 'internal_rent' in extracted_parsed_res: set_site_state("internal_rent", float(extracted_parsed_res['internal_rent']))
        if 'external_rent' in extracted_parsed_res: set_site_state("external_rent", float(extracted_parsed_res['external_rent']))
        if 'ops_cost' in extracted_parsed_res: set_site_state("ops_cost", float(extracted_parsed_res['ops_cost']))
        if 'rates_taxes' in extracted_parsed_res: set_site_state("rates_taxes", float(extracted_parsed_res['rates_taxes']))
        if 'generator' in extracted_parsed_res: set_site_state("generator", float(extracted_parsed_res['generator']))
        if 'escalation' in extracted_parsed_res: set_site_state("escalation", float(extracted_parsed_res['escalation']))
        if 'mktg' in extracted_parsed_res: set_site_state("mktg", float(extracted_parsed_res['mktg']))
        if 'turnover_pct' in extracted_parsed_res: set_site_state("turnover_pct", float(extracted_parsed_res['turnover_pct']))
        st.success(f"Lease terms successfully extracted and isolated for {location_name if location_name else 'Target Site'}!")

    with col2:
        default_shop = get_site_state("shop_code", site_default_info.get("shop", ""))
        shop_code = st.text_input("Shop / Unit Code", value=default_shop, placeholder="e.g. 79", key=f"{site_key}_shop_input")
        set_site_state("shop_code", shop_code)

    col_suburb, col_sub_select = st.columns(2)
    
    with col_suburb:
        if "suburb_node_input_key" not in st.session_state:
            st.session_state["suburb_node_input_key"] = site_default_info.get("suburb", "")

        suburb_node = st.text_input(
            "Suburb / Node (Auto-Populated)",
            placeholder="e.g. Germiston, Ekurhuleni, Gauteng",
            key="suburb_node_input_key"
        )

    with col_sub_select:
        suburb_options_list = st.session_state.get("discovered_suburb_options", [])
        if suburb_options_list and len(suburb_options_list) > 1:
            def on_suburb_dropdown_changed():
                selected_opt = st.session_state.get("suburb_node_dropdown_choice")
                if selected_opt:
                    st.session_state["suburb_node_input_key"] = selected_opt

            st.selectbox(
                "Confirm / Select Specific Suburb Node",
                options=suburb_options_list,
                key="suburb_node_dropdown_choice",
                on_change=on_suburb_dropdown_changed
            )

    st.subheader("Store Model Type")

    def on_model_changed():
        m_choice = st.session_state.get(f"{site_key}_model_radio", site_default_info.get("model", rec_model))
        m_info = STORE_MODELS.get(m_choice, STORE_MODELS["Express Model"])
        st.session_state[f"{site_key}_capex_input"] = m_info["turnkey_capital"]
        st.session_state[f"{site_key}_wc_input"] = m_info["working_capital"]
        st.session_state[f"{site_key}_int_gla_input"] = m_info["default_gla"]

    default_model_name = site_default_info.get("model", "Express Model")
    model_keys_list = list(STORE_MODELS.keys())
    default_radio_idx = model_keys_list.index(default_model_name) if default_model_name in model_keys_list else 1

    selected_model = st.radio(
        "Select Model Type",
        options=model_keys_list,
        index=default_radio_idx,
        horizontal=True,
        key=f"{site_key}_model_radio",
        on_change=on_model_changed
    )
    model_data = STORE_MODELS.get(selected_model, STORE_MODELS["Express Model"])

    if f"{site_key}_int_gla_input" not in st.session_state:
        st.session_state[f"{site_key}_int_gla_input"] = 70.0 if location_name == "Rondebuilt Centre" else site_default_info.get("default_gla", model_data["default_gla"])
    if f"{site_key}_external_gla" not in st.session_state:
        st.session_state[f"{site_key}_external_gla"] = 28.0 if location_name == "Rondebuilt Centre" else 0.0
    if f"{site_key}_capex_input" not in st.session_state:
        st.session_state[f"{site_key}_capex_input"] = model_data["turnkey_capital"]
    if f"{site_key}_wc_input" not in st.session_state:
        st.session_state[f"{site_key}_wc_input"] = model_data["working_capital"]

    st.subheader("Space Allocation (GLA Breakdown)")
    col_int_gla, col_ext_gla = st.columns(2)
    with col_int_gla:
        internal_gla = st.number_input("Internal Area (sqm)", min_value=0.0, step=1.0, key=f"{site_key}_int_gla_input")
    with col_ext_gla:
        external_gla = st.number_input("External / Patio Area (sqm)", min_value=0.0, step=1.0, key=f"{site_key}_external_gla")

    total_gla = internal_gla + external_gla
    st.caption(f"📐 **Total Combined Store Footprint ({location_name if location_name else 'Unassigned'}):** {total_gla:.2f} sqm ({internal_gla:.2f} sqm Internal + {external_gla:.2f} sqm External)")

    model_foh_pct_map = {
        "Kiosk Model": 0.00,
        "Express Model": 0.10,
        "Full Sit-Down Model": 0.40,
        "Multi-Brand Kitchen Model": 0.40
    }
    foh_ratio = model_foh_pct_map.get(selected_model, 0.10)
    internal_dining_sqm = internal_gla * foh_ratio
    total_dining_sqm = internal_dining_sqm + external_gla

    preferred_kitchen_size = 60.0
    actual_kitchen_sqm = min(preferred_kitchen_size, internal_gla - internal_dining_sqm) if internal_gla > 0 else 0.0

    std_seats_calc = math.floor(total_dining_sqm / 1.40) if total_dining_sqm > 0 else 0
    high_seats_calc = math.floor(total_dining_sqm / 1.20) if total_dining_sqm > 0 else 0

    col_seat1, col_seat2 = st.columns(2)
    with col_seat1:
        max_comfortable_seats = st.number_input("Standard Seating Capacity", min_value=0, value=std_seats_calc, step=1)
    with col_seat2:
        high_density_seats = st.number_input("High-Density Seating Capacity", min_value=0, value=high_seats_calc, step=1)

    st.info(f"📐 **Recommended Size:** {model_data['size_range']} | 🍳 **Recommended Kitchen Footprint:** {actual_kitchen_sqm:.2f} sqm | 🪑 **Dining Footprint ({foh_ratio*100:.0f}% Internal):** {total_dining_sqm:.2f} sqm")

    st.subheader("Site Blueprint & Development Layout Plan")
    blueprint_file = st.file_uploader(f"Upload Architectural Blueprint for {location_name if location_name else 'Target Site'}", type=["pdf", "png", "jpg", "jpeg"], key=f"{site_key}_blueprint_uploader")
    
    if blueprint_file is not None:
        pil_img, pdf_text = process_uploaded_file(blueprint_file)
        if pil_img is not None:
            set_site_state("blueprint_img", pil_img)

    blueprint_pil_img = get_site_state("blueprint_img", None)
    if blueprint_pil_img is not None:
        st.image(blueprint_pil_img, caption=f"Proposed Store Blueprint: {location_name} ({shop_code})", use_container_width=True)

    st.divider()

    st.header("2. Commercial Capital & Lease Modeling")

    col_cap, col_wc = st.columns(2)
    with col_cap:
        turnkey_capital = st.number_input("Total Turnkey Capital (Excl. VAT)", step=50000.0, format="%.2f", key=f"{site_key}_capex_input")
    with col_wc:
        working_capital = st.number_input("Suggested Working Capital Requirement", step=25000.0, format="%.2f", key=f"{site_key}_wc_input")

    if "1. I have a Landlord Proposal" in analysis_mode:
        st.subheader("Landlord Lease Breakdown (Per SQM)")
        col_int_rent, col_ext_rent = st.columns(2)
        with col_int_rent:
            def_int_rent = get_site_state("internal_rent", area_market_rent)
            internal_rent_sqm = st.number_input("Internal Base Rent (R / sqm / month)", value=def_int_rent, step=10.0, format="%.2f", key=f"{site_key}_int_rent_input")
            set_site_state("internal_rent", internal_rent_sqm)
            total_internal_rent = internal_gla * internal_rent_sqm
            st.caption(f"💵 **Total Monthly Internal Rent:** R {int(round(total_internal_rent)):,} (Excl. VAT)")

        with col_ext_rent:
            def_ext_rent = get_site_state("external_rent", 110.0 if location_name == "Rondebuilt Centre" else 0.00)
            external_rent_sqm = st.number_input("External Base Rent (R / sqm / month)", value=def_ext_rent, step=5.0, format="%.2f", key=f"{site_key}_ext_rent_input")
            set_site_state("external_rent", external_rent_sqm)
            total_external_rent = external_gla * external_rent_sqm
            st.caption(f"💵 **Total Monthly External Rent:** R {int(round(total_external_rent)):,} (Excl. VAT)")

        total_base_rent_monthly = total_internal_rent + total_external_rent

        col_ops, col_rates, col_gen = st.columns(3)
        with col_ops:
            def_ops = get_site_state("ops_cost", site_default_info.get("default_ops", 32.50))
            ops_cost_sqm = st.number_input("Ops Cost / Municipal (R / sqm)", value=def_ops, step=1.0, format="%.2f", key=f"{site_key}_ops_input")
            set_site_state("ops_cost", ops_cost_sqm)
            total_ops_cost = ops_cost_sqm * total_gla
        with col_rates:
            def_rates = get_site_state("rates_taxes", 0.00)
            rates_taxes_sqm = st.number_input("Rates & Taxes (R / sqm)", value=def_rates, step=0.5, format="%.2f", key=f"{site_key}_rates_input")
            set_site_state("rates_taxes", rates_taxes_sqm)
            total_rates_taxes = rates_taxes_sqm * total_gla
        with col_gen:
            def_gen = get_site_state("generator", 8.00 if location_name == "Rondebuilt Centre" else 0.00)
            generator_cost_sqm = st.number_input("Generator Cost (R / sqm)", value=def_gen, step=0.5, format="%.2f", key=f"{site_key}_gen_input")
            set_site_state("generator", generator_cost_sqm)
            total_generator_cost = generator_cost_sqm * total_gla

        col_mktg_pct, col_labor, col_turn_pct = st.columns(3)
        with col_mktg_pct:
            def_mktg = get_site_state("mktg", 3.00 if location_name == "Rondebuilt Centre" else 5.00)
            landlord_marketing_pct = st.number_input("Landlord Marketing (% of Basic Rent)", value=def_mktg, step=0.5, format="%.2f", key=f"{site_key}_mktg_input")
            set_site_state("mktg", landlord_marketing_pct)
            total_landlord_marketing = total_base_rent_monthly * (landlord_marketing_pct / 100.0)
        with col_turn_pct:
            def_turn = get_site_state("turnover_pct", site_default_info.get("turnover_clause_pct", 7.0))
            turnover_clause_pct = st.number_input("Annual Turnover Clause (%)", value=def_turn, step=0.5, format="%.2f", key=f"{site_key}_turn_pct_input")
            set_site_state("turnover_pct", turnover_clause_pct)
            monthly_threshold_zar = total_base_rent_monthly / (turnover_clause_pct / 100.0)
        with col_labor:
            monthly_labor_cost = st.number_input("Monthly Store Staffing / Payroll (ZAR)", value=model_data["labor_monthly"], step=5000.0, format="%.2f", key=f"{site_key}_labor_input")

        total_lease_outlay_monthly = total_base_rent_monthly + total_ops_cost + total_rates_taxes + total_generator_cost + total_landlord_marketing

        st.markdown(f"""
        <div class="lease-outlay-card">
            <b style="color:#FFFFFF; font-size:15px;">🏬 Total Monthly Landlord Lease Outlay ({location_name if location_name else 'Target Site'}):</b><br/>
            <span style="color:#ECC94B; font-size:18px; font-weight:800;">R {int(round(total_lease_outlay_monthly)):,} (Excl. VAT)</span><br/>
            <span style="color:#CCCCCC; font-size:12px;">Turnover Clause: <b>{turnover_clause_pct}%</b> of net turnover effective when monthly turnover exceeds <b>R {int(round(monthly_threshold_zar)):,} p.m.</b></span>
        </div>
        """, unsafe_allow_html=True)

    else:
        internal_rent_sqm = area_market_rent
        external_rent_sqm = 0.00
        ops_cost_sqm = site_default_info.get("default_ops", 35.0)
        rates_taxes_sqm = 0.00
        generator_cost_sqm = 0.00
        landlord_marketing_pct = 5.00
        turnover_clause_pct = site_default_info.get("turnover_clause_pct", 7.0)
        monthly_labor_cost = model_data["labor_monthly"]

        total_base_rent_monthly = (internal_gla * internal_rent_sqm) + (external_gla * external_rent_sqm)
        total_ops_cost = ops_cost_sqm * total_gla
        total_landlord_marketing = total_base_rent_monthly * (landlord_marketing_pct / 100.0)
        total_lease_outlay_monthly = total_base_rent_monthly + total_ops_cost + total_landlord_marketing
        monthly_threshold_zar = total_base_rent_monthly / (turnover_clause_pct / 100.0)

        st.success(f"🎯 **Mode 2 Active:** Localized market intelligence lease target set to **R {int(round(internal_rent_sqm))}/m²** for **{location_name if location_name else 'Selected Area'}** P&L calculations and landlord offer sheet.")

    st.divider()

    st.header("4. Financial Recovery & Unit Sales Target Matrix (@ 55% Blended GP)")
    gp_margin = 0.55
    aov_ticket = 190.0

    capex_12 = turnkey_capital / 12
    capex_24 = turnkey_capital / 24
    capex_36 = turnkey_capital / 36
    capex_48 = turnkey_capital / 48
    capex_60 = turnkey_capital / 60

    outflow_breakeven = total_lease_outlay_monthly + monthly_labor_cost
    outflow_12 = outflow_breakeven + capex_12
    outflow_24 = outflow_breakeven + capex_24
    outflow_36 = outflow_breakeven + capex_36
    outflow_48 = outflow_breakeven + capex_48
    outflow_60 = outflow_breakeven + capex_60

    turnover_req_be = outflow_breakeven / gp_margin
    turnover_req_12 = outflow_12 / gp_margin
    turnover_req_24 = outflow_24 / gp_margin
    turnover_req_36 = outflow_36 / gp_margin
    turnover_req_48 = outflow_48 / gp_margin
    turnover_req_60 = outflow_60 / gp_margin

    def make_target_row(turnover_val):
        units_m = math.ceil(turnover_val / aov_ticket)
        units_d = math.ceil(units_m / 30)
        return f"R {int(round(turnover_val)):,}", f"{units_m:,} units", f"{units_d} units / day"

    be_t, be_um, be_ud = make_target_row(turnover_req_be)
    t12, um12, ud12 = make_target_row(turnover_req_12)
    t24, um24, ud24 = make_target_row(turnover_req_24)
    t36, um36, ud36 = make_target_row(turnover_req_36)
    t48, um48, ud48 = make_target_row(turnover_req_48)
    t60, um60, ud60 = make_target_row(turnover_req_60)

    payback_matrix_data = {
        "RECOVERY HORIZON": ["Operational Breakeven", "12 Months Recovery Target", "24 Months Recovery Target", "36 Months Recovery Target", "48 Months Recovery Target", "60 Months Recovery Target"],
        "REQUIRED TURNOVER/MONTH": [be_t, t12, t24, t36, t48, t60],
        "REQUIRED UNITS / MONTH": [be_um, um12, um24, um36, um48, um60],
        "REQUIRED UNITS / DAY": [be_ud, ud12, ud24, ud36, ud48, ud60]
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
        monthly_lease = total_lease_outlay_monthly * (0.07 + 1) ** year_idx
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

    st.header("6. Dispatch Completed Site Feasibility Pack")

    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        target_applicant_name = st.text_input("Prospective Franchisee Full Name", value="", placeholder="e.g. John Doe", key=f"{site_key}_app_name")
        target_applicant_email = st.text_input("Prospective Franchisee Email Address", value="", placeholder="e.g. applicant@domain.com", key=f"{site_key}_app_email")
    with col_inv2:
        target_applicant_mobile = st.text_input("Prospective Franchisee Mobile / WhatsApp Number", value="", placeholder="e.g. 0827867712 or +27827867712", key=f"{site_key}_app_mobile")

    selected_menus = st.session_state.get("selected_brand_menus", get_available_brand_menus())

    if target_applicant_name and target_applicant_email:
        save_investor_lead({
            "full_name": target_applicant_name,
            "entity_name": "Prospective Entity",
            "id_or_passport": "Pending / Unassigned",
            "email": target_applicant_email,
            "mobile": target_applicant_mobile if target_applicant_mobile else "N/A",
            "preferred_site": location_name if location_name else "Unassigned Site",
            "store_model": selected_model,
            "capital_available": turnkey_capital + working_capital,
            "unencumbered_cash_pct": 50.0,
            "admin_fee_paid": 0,
            "ndnca_signed": 0,
            "popia_consent": 1
        })

    clean_site_slug = re.sub(r'[^a-zA-Z0-9_]', '_', location_name.strip()) if location_name else "Unassigned_Site"
    pdf_filename = f"{clean_site_slug}_{selected_model.replace(' ', '_')}_{int(total_gla)}m2_.pdf"

    pdf_buffer = generate_pdf_report(
        location_name, shop_code, suburb_node, internal_gla, external_gla, total_gla, selected_model,
        max_comfortable_seats, high_density_seats, turnkey_capital, working_capital, internal_rent_sqm,
        external_rent_sqm, ops_cost_sqm, total_lease_outlay_monthly, turnover_clause_pct, rec_model, 7.42,
        df_payback_matrix, annual_pnl, blueprint_pil_img,
        applicant_name=target_applicant_name if target_applicant_name else "Prospective Investor",
        applicant_email=target_applicant_email if target_applicant_email else "N/A",
        applicant_mobile=target_applicant_mobile if target_applicant_mobile else "N/A",
        selected_menus=selected_menus
    )
    pdf_bytes = pdf_buffer.getvalue()

    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        dl_link_html = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}" class="direct-dl-btn">📥 Download PDF Direct</a>'
        st.markdown(dl_link_html, unsafe_allow_html=True)
        
        local_saved_path, sync_status_msg = sync_pdf_to_local_and_cloud(location_name, pdf_bytes, pdf_filename)
        st.caption(f"📂 **Local Directory Saved:** `{local_saved_path}`")
        st.info(f"☁️ **Google Drive Status:** {sync_status_msg}")

    with btn_col2:
        if st.button("📧 Dispatch via Email (with Read Receipt)", key=f"{site_key}_email_btn"):
            if not target_applicant_email:
                st.error("Please enter a valid Franchisee Email Address above.")
            else:
                sent_ok, send_msg = send_franchisee_email_pack(
                    target_applicant_email, target_applicant_name, location_name if location_name else "Target Site", pdf_bytes, pdf_filename
                )
                if sent_ok:
                    st.success(f"✅ {send_msg}")
                else:
                    st.error(f"❌ Email Failed: {send_msg}")

    if target_applicant_mobile:
        formatted_wa_mobile = format_sa_mobile_number(target_applicant_mobile)
        wa_text = f"Hi {target_applicant_name if target_applicant_name else 'there'}, thank you for showing interest in Phatbuns South Africa. I have dispatched the Executive Feasibility & Investor Pack for {location_name if location_name else 'your target site'} to your email ({target_applicant_email}). Please review the attached pack, brand menus, and NCNDA."
        encoded_wa_text = urllib.parse.quote(wa_text)
        wa_url = f"https://api.whatsapp.com/send?phone={formatted_wa_mobile}&text={encoded_wa_text}"

        st.markdown(f"""
        <a href="{wa_url}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:12px; border-radius:8px; text-align:center; font-weight:bold; font-size:15px; margin-top:10px;">
                💬 Launch WhatsApp Direct Chat with {target_applicant_name} (+{formatted_wa_mobile})
            </div>
        </a>
        """, unsafe_allow_html=True)

    render_contact_footer()

# TAB 2: BRAND MENUS & MEDIA SHOWCASE
with tab2:
    st.header("📖 Brand Menus & Global Media Showcase")
    st.markdown("Individual brand catalogs and global store walk-throughs below are configured with dedicated **Google Drive Download & Streaming Links**.")

    for brand_key, brand_info in BRAND_MENU_CATALOG.items():
        logo_file = logo_map.get(brand_info.get("logo_key", "phatbuns_sa"))
        b64_logo_str = get_image_base64(logo_file)

        st.markdown('<div class="brand-card-block">', unsafe_allow_html=True)
        
        if b64_logo_str:
            st.markdown(f'<img src="data:image/png;base64,{b64_logo_str}" class="brand-logo-above"/>', unsafe_allow_html=True)

        st.markdown(f"### {brand_key}")
        st.markdown(f"**Tagline:** {brand_info['tagline']}")
        st.markdown(f"**Overview:** {brand_info['description']}")
        drive_dl_url = get_drive_menu_download_url(brand_info["drive_file_id"])
        st.markdown(f"🔗 **Google Drive Direct Download Link:** [{brand_info['filename']}]({drive_dl_url})")
        
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("🎬 Global Store Video Walk-Throughs & Visual Gallery")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown(f"🖼️ **Sample Store Photos Gallery:** [View Google Drive Gallery]({STORE_MEDIA_LINKS['store_photos']})")
        st.markdown(f"🎬 **Phatbuns UK Walk-Through 1:** [Watch Video]({STORE_MEDIA_LINKS['uk_video_1']})")
    with m_col2:
        st.markdown(f"🎬 **Phatbuns UK Walk-Through 2:** [Watch Video]({STORE_MEDIA_LINKS['uk_video_2']})")
        st.markdown(f"🎬 **Phatbuns Dubai Flagship:** [Watch Video]({STORE_MEDIA_LINKS['dubai_video']})")

    render_contact_footer()

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
            preferred_site = st.text_input("Preferred Target Site / Node *", value="")
            store_model_choice = st.selectbox("Preferred Store Model", options=list(STORE_MODELS.keys()), index=1)
            capital_available = st.number_input("Proposed Total Capital Available (ZAR)", value=2500000.0, step=100000.0)

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

    st.subheader("CEO Pipeline & Potential Client Registry")
    st.markdown("All prospective client captures from Section 6 and direct registrations are automatically logged here.")
    
    df_pipeline = get_pipeline_dataframe()
    if not df_pipeline.empty:
        st.dataframe(
            df_pipeline.rename(columns={
                'id': 'ID',
                'full_name': 'Applicant Name',
                'mobile': 'Mobile / Tel',
                'email': 'Email Address',
                'preferred_site': 'Preferred Site',
                'store_model': 'Store Model',
                'capital_available': 'Capital Available (ZAR)',
                'unencumbered_cash_pct': 'Unencumbered Cash %',
                'ceo_approval': 'CEO Status',
                'created_at': 'Registration Date'
            }),
            use_container_width=True
        )
        pipeline_pdf_file = generate_pipeline_pdf(df_pipeline)
        st.download_button(label="📥 Download CEO Pipeline Audit PDF Report", data=pipeline_pdf_file, file_name="Phatbuns_Investor_Pipeline_Report.pdf", mime="application/pdf", use_container_width=True)
    else:
        st.info("No franchisee applications currently recorded in database.")

    render_contact_footer()
