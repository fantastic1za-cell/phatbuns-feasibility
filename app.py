# Complete Python Script to Generate Dynamic Phatbuns Master Investor & Franchisee Document (Bank-Ready)
# Comprehensive 10-Point Header Expansion, Interactive Google Drive Menu Downloads, Cross-Browser App Icon Injection, HTML Email Signature with 30px Logos, FASA/POPIA/CPA Compliant NCNDA & Live Web Search Intelligence with Offline Safeguards
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
                    if f_lower.endswith(('.png', '.jpg', '.jpeg', '.pdf')) and ('dev' in f_lower or 'plan' in f_lower or 'layout' in f_lower or 'blueprint' in f_lower or 'leasing' in f_lower or clean_target in re.sub(r'[^a-zA-Z0-9]', '', f_lower)):
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
def research_location_online(location_name, force_offline=False):
    search_query = f"{location_name} shopping centre mall suburb food tenants rental rate per sqm South Africa"
    results_text = ""
    
    if not force_offline and HAS_DDGS:
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
        "default_rent": 0.0,
        "default_ops": 0.0,
        "default_gla": 0.0,
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
            "default_ops": 32.50,
            "default_gla": 98.0,
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
            "default_ops": 45.0,
            "default_gla": 80.0,
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
            "default_ops": 25.0,
            "default_gla": 70.0,
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
            "default_ops": 30.0,
            "default_gla": 70.0,
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
            "default_ops": 50.0,
            "default_gla": 252.0,
            "turnover_clause_pct": 6.0
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
            extracted_info["default_rent"] = geo_data.get("default_rent", 0.0)
            extracted_info["default_ops"] = geo_data.get("default_ops", 0.0)
            extracted_info["default_gla"] = geo_data.get("default_gla", 0.0)
            extracted_info["turnover_clause_pct"] = geo_data.get("turnover_clause_pct", 7.0)
            return extracted_info

    if not force_offline and HAS_GENAI:
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
                  "default_rent": 0.0,
                  "default_ops": 0.0,
                  "default_gla": 0.0,
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
# ROBUST GOOGLE DRIVE API & SHARED FOLDER ENGINE
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

def sync_pdf_to_local_and_cloud(location_name, pdf_bytes, pdf_filename, offline_mode=False):
    loc_clean = location_name.strip() if location_name else "Unassigned_Location"
    loc_sub_dir = os.path.join(LOCATIONS_DIR, loc_clean)
    os.makedirs(loc_sub_dir, exist_ok=True)
    local_file_path = os.path.join(loc_sub_dir, pdf_filename)
    
    with open(local_file_path, "wb") as f:
        f.write(pdf_bytes)

    if offline_mode:
        return local_file_path, "💾 Offline Mode Active: Saved locally. Cloud sync skipped."

    drive_service = get_drive_service()
    if not drive_service:
        return local_file_path, "Google Drive API Service Not Initialized (Offline Save Successful)"

    try:
        site_folder_id = get_or_create_drive_folder(drive_service, loc_clean, parent_id=LOCATIONS_ROOT_DRIVE_ID)
        if not site_folder_id:
            return local_file_path, f"Failed to create or find Google Drive folder: '{loc_clean}' under root ID"
        
        file_id = upload_pdf_to_drive(drive_service, pdf_bytes, pdf_filename, site_folder_id)
        if file_id:
            return local_file_path, f"Successfully Synced to Google Drive: '{loc_clean}/{pdf_filename}'"
        else:
            return local_file_path, f"Failed to upload file '{pdf_filename}' to Drive folder '{loc_clean}'"
    except Exception as e:
        return local_file_path, f"Google Drive Sync Exception: {str(e)}"

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

def extract_lease_from_source(source_input, file_bytes=None, mime_type="image/jpeg", offline_mode=False):
    if offline_mode or not HAS_GENAI:
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
          "generator": float,
          "escalation": float,
          "mktg": float,
          "turnover_pct": float
        }
        """
        if file_bytes:
            image_part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
            contents_payload = [image_part, prompt]
        elif isinstance(source_input, Image.Image):
            img_byte_arr = io.BytesIO()
            source_input.save(img_byte_arr, format='JPEG')
            image_part = types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type="image/jpeg")
            contents_payload = [image_part, prompt]
        else:
            contents_payload = [str(source_input) + "\n\n" + prompt]

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

    int_area_m = re.search(r'([\d\.]+)\s*(?:m²|sqm|m2)\s*(?:plus|and|\+)?\s*([\d\.]+)\s*(?:m²|sqm|m2)?\s*(?:outside|patio|external)', text_clean, re.IGNORECASE)
    if int_area_m:
        data['internal_gla'] = float(int_area_m.group(1))
        data['external_gla'] = float(int_area_m.group(2))
    else:
        int_area_m2 = re.search(r'(?:Shop\s*Size|Internal\s*Area|Area)\s*[:\-]?\s*([\d\.\,]+)\s*(?:sqm|m2|m²)', text_clean, re.IGNORECASE)
        if int_area_m2: data['internal_gla'] = float(int_area_m2.group(1).replace(',', '.'))
        ext_area_m2 = re.search(r'(?:outside|external|patio)\s*(?:seating|area)?\s*[:\-]?\s*([\d\.\,]+)\s*(?:sqm|m2|m²)', text_clean, re.IGNORECASE)
        if ext_area_m2: data['external_gla'] = float(ext_area_m2.group(1).replace(',', '.'))

    int_rent_m = re.search(r'R?\s*([\d]+(?:\.[\d]+)?)\s*(?:excl|per|\/)?\s*(?:vat)?\s*(?:Shop|Basic)', text_clean, re.IGNORECASE)
    if not int_rent_m:
        int_rent_m = re.search(r'R\s*([\d]+(?:\.[\d]+)?)\s*(?:excl\s*vat\s*Shop|Shop)', text_clean, re.IGNORECASE)
    if int_rent_m: data['internal_rent'] = float(int_rent_m.group(1))

    ext_rent_m = re.search(r'R?\s*([\d]+(?:\.[\d]+)?)\s*(?:excl|per|\/)?\s*(?:vat)?\s*(?:outside|seating)', text_clean, re.IGNORECASE)
    if ext_rent_m: data['external_rent'] = float(ext_rent_m.group(1))

    ops_m = re.search(r'(?:Operating\s*Costs|Ops\s*Cost)\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)', text_clean, re.IGNORECASE)
    if ops_m: data['ops_cost'] = float(ops_m.group(1))

    rates_m = re.search(r'Rates\s*(?:&|and)?\s*taxes\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)', text_clean, re.IGNORECASE)
    if rates_m: data['rates_taxes'] = float(rates_m.group(1))

    gen_m = re.search(r'Generator\s*(?:Charge)?\s*[:\-]?\s*R?\s*([\d]+(?:\.[\d]+)?)', text_clean, re.IGNORECASE)
    if gen_m: data['generator'] = float(gen_m.group(1))

    mktg_m = re.search(r'Marketing\s*(?:Contribution)?\s*[:\-]?\s*([\d]+(?:\.[\d]+)?)\s*%', text_clean, re.IGNORECASE)
    if mktg_m: data['mktg'] = float(mktg_m.group(1))

    turn_m = re.search(r'(?:Annual\s*Turnover|Turnover\s*Percentage)\s*[:\-]?\s*([\d]+(?:\.[\d]+)?)\s*%', text_clean, re.IGNORECASE)
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
            return pil_img, file_bytes
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

# SIDEBAR CONTROLS FOR OFFLINE / LOW SIGNAL MODE
st.sidebar.markdown("### 🛜 Connection & Data Settings")
offline_mode_toggle = st.sidebar.checkbox("🔒 Enable Offline / Low-Signal Mode", value=False, help="Disables external web searches and Cloud uploads so the app runs instantly and reliably on weak mobile data.")

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

    # 02. LEASE STRUCTURE & FINANCIAL PROVISIONS
    sec2_banner = Table([[Paragraph("02. LEASE STRUCTURE & PROPOSED LANDLORD OFFER TARGETS", sec_banner_style)]], colWidths=[558])
    sec2_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec2_banner)

    monthly_base_rent_total = (int_rent * int_gla) + (ext_rent * ext_gla)
    monthly_threshold_zar = monthly_base_rent_total / (turnover_clause_pct / 100.0) if turnover_clause_pct > 0 else 0.0

    sec2_table_data = [
        [Paragraph("LEASE CLAUSE / PROVISION", body_white_bold), Paragraph("TERMS & RATE STRUCTURE", body_white_bold), Paragraph("FINANCIAL ALIGNMENT", body_white_bold)],
        [Paragraph("Lease Period & Renewal", body_bold), Paragraph("5 Years Initial Period + 5-Year Renewal Option", body_regular), Paragraph("60 Months Base Amortization", body_regular)],
        [Paragraph("Base Net Rental Rate Target", body_bold), Paragraph(f"Shop: R {int(round(int_rent))} /m² | Patio: R {int(round(ext_rent))} /m²", body_regular), Paragraph(f"R {int(round(monthly_base_rent_total)):,} / month", body_regular)],
        [Paragraph("Annual Rental Escalation", body_bold), Paragraph("7.0% per annum effective anniversary", body_regular), Paragraph(f"Year 2 Base: R {int(round(monthly_base_rent_total * 1.07)):,} / month", body_regular)],
        [Paragraph("Monthly Turnover Rental Clause", body_bold), Paragraph(f"{turnover_clause_pct}% of net turnover vs Base Net Rental (whichever greater)", body_regular), Paragraph(f"Effective Threshold: > R {int(round(monthly_threshold_zar)):,} p.m.", body_regular)],
        [Paragraph("Beneficial Occupation (BO)", body_bold), Paragraph("2 Month Rent-Free BO for Turnkey Store Fitout", body_regular), Paragraph("Fitout Schedule: 60 Days", body_regular)]
    ]
    t_sec2 = Table(sec2_table_data, colWidths=[150, 248, 160])
    t_sec2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec2)
    elements.append(Spacer(1, 4))

    # 03. DYNAMIC CATCHMENT & LOCATION INTELLIGENCE
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

    if not payback_df.empty:
        matrix_table_data = [[Paragraph(f"<b>{col}</b>", body_white_bold) for col in payback_df.columns]]
        for idx, row in payback_df.iterrows():
            row_cells = [Paragraph(str(row[col]), body_regular) for col in payback_df.columns]
            matrix_table_data.append(row_cells)
        t_matrix = Table(matrix_table_data, colWidths=[148, 82, 82, 82, 82, 82], hAlign='CENTER')
        t_matrix.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
        elements.append(t_matrix)
    elements.append(Spacer(1, 3))

    # 04A. RECOVERY PERIOD & TURNOVER TARGET
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

    if not df_pnl_annual.empty:
        pnl_table_data = [[Paragraph(f"<b>{col}</b>", body_white_bold) for col in df_pnl_annual.columns]]
        for idx, row in df_pnl_annual.iterrows():
            row_cells = []
            for col in df_pnl_annual.columns:
                val = row[col]
                formatted = f"R {int(round(val)):,}" if isinstance(val, (int, float)) else str(val)
                row_cells.append(Paragraph(formatted, body_regular))
            pnl_table_data.append(row_cells)
        t_pnl = Table(pnl_table_data, colWidths=[51, 69, 64, 62, 59, 62, 64, 60, 67], hAlign='CENTER')
        t_pnl.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
        elements.append(t_pnl)
    elements.append(Spacer(1, 6))

    # 11A: TOTAL ROI & RECOMMENDATION
    sec11a_banner = Table([[Paragraph("11A. AGGREGATE 5-YEAR FINANCIAL RETURN (ROI), LANDLORD RENTALS & MASTER RECOMMENDATION", sec_banner_style)]], colWidths=[558])
    sec11a_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec11a_banner)

    total_5yr_rentals = sum([row['Lease Outlay'] for idx, row in df_pnl_annual.iterrows()]) if not df_pnl_annual.empty else 0
    total_5yr_royalties = sum([row['Royalties (9%)'] for idx, row in df_pnl_annual.iterrows()]) if not df_pnl_annual.empty else 0
    total_5yr_net_profit = sum([row['Net Operating Profit'] for idx, row in df_pnl_annual.iterrows()]) if not df_pnl_annual.empty else 0
    initial_total_investment = capital + wc

    five_yr_roi_pct = (total_5yr_net_profit / initial_total_investment) * 100.0 if initial_total_investment > 0 else 0.0

    sec11a_data = [
        [Paragraph("FINANCIAL METRIC / AGGREGATE CATEGORY", body_white_bold), Paragraph("5-YEAR PROJECTED CUMULATIVE VALUE (ZAR)", body_white_bold)],
        [Paragraph("Total Landlord Rentals Paid (5 Years)", body_bold), Paragraph(f"R {int(round(total_5yr_rentals)):,}", body_regular)],
        [Paragraph("Total Central Royalties Paid (9% over 5 Years)", body_bold), Paragraph(f"R {int(round(total_5yr_royalties)):,}", body_regular)],
        [Paragraph("Cumulative Net Operating Profit (After Debt Service)", body_bold), Paragraph(f"R {int(round(total_5yr_net_profit)):,}", body_regular)],
        [Paragraph("5-Year Cumulative ROI (%)", body_bold), Paragraph(f"<b>{five_yr_roi_pct:.1f}%</b>", body_regular)],
        [Paragraph("Site Feasibility & Master Recommendation", body_bold), Paragraph(f"<b>Phatbuns South Africa, advise the site as Feasible.</b><br/>Recommended Model: {recommended_model_name} (E&OE).", ParagraphStyle('FeasStyle', parent=body_regular, textColor=WHITE_TEXT, fontName='Helvetica-Bold'))]
    ]
    t_sec11a = Table(sec11a_data, colWidths=[200, 358])
    t_sec11a.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2.5), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG), ('BACKGROUND', (1, 5), (1, 5), colors.HexColor('#28a745'))]))
    elements.append(t_sec11a)

    elements.append(PageBreak())

    # PAGE 5: BLUEPRINT / LAYOUT PLAN
    elements.append(Paragraph(f"<b>{loc_name.upper() if loc_name else 'TARGET LOCATION'} — SHOP {shop.upper()}</b>", ParagraphStyle('BPHeader', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=NAVY_HEADER, alignment=1)))
    elements.append(Paragraph(f"<b>DEVELOPMENT LEASING LAYOUT PLAN ({total_gla:.2f} M² | {model}) — RECOMMENDED: {recommended_model_name.upper()}</b>", ParagraphStyle('BPSubHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=ORANGE_BRAND, alignment=1)))
    elements.append(Spacer(1, 4))
    elements.append(HRFlowable(width="100%", thickness=1, color=NAVY_HEADER, spaceBefore=2, spaceAfter=8))

    effective_blueprint_img = blueprint_pil_img
    if effective_blueprint_img is None and loc_name:
        auto_bp_path = find_site_blueprint(loc_name)
        if auto_bp_path and os.path.exists(auto_bp_path):
            try:
                if auto_bp_path.lower().endswith('.pdf') and HAS_PYPDF:
                    import fitz
                    doc_pdf = fitz.open(auto_bp_path)
                    page = doc_pdf[0]
                    pix = page.get_pixmap(dpi=150)
                    effective_blueprint_img = Image.open(io.BytesIO(pix.tobytes("jpeg"))).convert("RGB")
                else:
                    effective_blueprint_img = Image.open(auto_bp_path).convert("RGB")
            except Exception:
                pass

    if effective_blueprint_img is not None:
        bp_byte_arr = io.BytesIO()
        effective_blueprint_img.save(bp_byte_arr, format='JPEG', quality=95)
        bp_byte_arr.seek(0)
        elements.append(RLImage(bp_byte_arr, width=480, height=310, preserveAspectRatio=True))
    else:
        placeholder_img = Image.new("RGB", (900, 600), color=(245, 247, 250))
        draw = ImageDraw.Draw(placeholder_img)
        draw.rectangle([15, 15, 885, 585], outline=(26, 54, 93), width=4)
        draw.text((330, 260), f"PROPOSED STORE LAYOUT PLAN: {loc_name} (Shop {shop})", fill=(26, 54, 93))
        bp_byte_arr = io.BytesIO()
        placeholder_img.save(bp_byte_arr, format='JPEG', quality=95)
        bp_byte_arr.seek(0)
        elements.append(RLImage(bp_byte_arr, width=480, height=310, preserveAspectRatio=True))

    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"<b>Technical Specifications:</b> Internal GLA: {int_gla:.2f} sqm | External Patio GLA: {ext_gla:.2f} sqm | Total Footprint: {total_gla:.2f} sqm. Kitchen engineered for SANHA Halal compliance.", body_regular))

    elements.append(PageBreak())

    # PAGE 6: BRAND MENUS & MEDIA SHOWCASE
    elements.append(Paragraph("<b>PHATBUNS BRAND PORTFOLIO & GLOBAL MEDIA SHOWCASE</b>", ParagraphStyle('BPHeader', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=NAVY_HEADER, alignment=1)))
    elements.append(Paragraph("<b>CLICKABLE DOWNLOAD LINKS FOR BRAND MENUS & STORE VISUALS</b>", ParagraphStyle('BPSubHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=ORANGE_BRAND, alignment=1)))
    elements.append(Spacer(1, 4))
    elements.append(HRFlowable(width="100%", thickness=1, color=NAVY_HEADER, spaceBefore=2, spaceAfter=8))

    menu_table_rows = [[Paragraph("<b>BRAND & CONCEPT</b>", body_white_bold), Paragraph("<b>MENU OVERVIEW</b>", body_white_bold), Paragraph("<b>DOWNLOAD LINK</b>", body_white_bold)]]
    for brand_name, info in BRAND_MENU_CATALOG.items():
        drive_url = get_drive_menu_download_url(info["drive_file_id"])
        menu_table_rows.append([
            Paragraph(f"<b>{brand_name}</b><br/><i>{info['tagline']}</i>", body_regular),
            Paragraph(info["description"], body_regular),
            Paragraph(f'<a href="{drive_url}">📥 DOWNLOAD MENU (PDF)</a>', body_regular)
        ])
    t_menu_links = Table(menu_table_rows, colWidths=[130, 288, 140])
    t_menu_links.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), ORANGE_BRAND), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(t_menu_links)

    elements.append(PageBreak())

    # PAGE 7: NCNDA LEGAL TEMPLATE
    elements.append(Paragraph("<b>NON-DISCLOSURE AND NON-CIRCUMVENTION AGREEMENT (NCNDA)</b>", ParagraphStyle('NCNDAHeader', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=NAVY_HEADER, alignment=1)))
    elements.append(HRFlowable(width="100%", thickness=1, color=MAROON_LINE, spaceBefore=2, spaceAfter=4))
    elements.append(Paragraph(f"Entered between Phatbuns South Africa and <b>{applicant_name}</b> ({applicant_email}, Mobile: {applicant_mobile}) for target node <b>{loc_name} (Shop {shop})</b>. All terms comply with FASA and POPIA frameworks.", body_regular))
    elements.append(Spacer(1, 20))

    sig_p_ncnda = [
        [Paragraph(f"<b>For: PHATBUNS SOUTH AFRICA</b><br/><br/>____________________________________<br/><b>Nisaar Ally</b><br/>SA Master Rights Holder", body_regular),
         Paragraph(f"<b>For: THE RECEIVING PARTY</b><br/><br/>____________________________________<br/><b>{applicant_name}</b><br/>Prospective Franchisee", body_regular)]
    ]
    t_sig_ncnda = Table(sig_p_ncnda, colWidths=[270, 270], hAlign='CENTER')
    t_sig_ncnda.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG), ('PADDING', (0,0), (-1,-1), 5)]))
    elements.append(t_sig_ncnda)

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
        uploaded_offer_file = st.file_uploader("Upload Offer File (JPG, PNG, PDF, Screenshot)", type=["jpg", "jpeg", "png", "pdf"])
        pasted_text = st.text_area("Or Paste Email / Whatsapp Offer Text Directly", height=100)

        if st.button("⚡ Extract & Pre-Fill Lease Terms"):
            if uploaded_offer_file is not None:
                pil_img, file_bytes_or_text = process_uploaded_file(uploaded_offer_file)
                if isinstance(file_bytes_or_text, bytes):
                    extracted_parsed_res = extract_lease_from_source(pil_img, file_bytes=file_bytes_or_text, mime_type=uploaded_offer_file.type, offline_mode=offline_mode_toggle)
                else:
                    extracted_parsed_res = extract_lease_from_source(file_bytes_or_text, offline_mode=offline_mode_toggle)
            elif pasted_text:
                extracted_parsed_res = extract_lease_from_source(pasted_text, offline_mode=offline_mode_toggle)
            
            if extracted_parsed_res:
                if 'shop_code' in extracted_parsed_res: st.session_state[f"unassigned_site_shop_input"] = str(extracted_parsed_res['shop_code'])
                if 'internal_gla' in extracted_parsed_res: st.session_state[f"unassigned_site_int_gla_input"] = float(extracted_parsed_res['internal_gla'])
                if 'external_gla' in extracted_parsed_res: st.session_state[f"unassigned_site_external_gla"] = float(extracted_parsed_res['external_gla'])
                if 'internal_rent' in extracted_parsed_res: st.session_state[f"unassigned_site_int_rent"] = float(extracted_parsed_res['internal_rent'])
                if 'external_rent' in extracted_parsed_res: st.session_state[f"unassigned_site_ext_rent"] = float(extracted_parsed_res['external_rent'])
                if 'ops_cost' in extracted_parsed_res: st.session_state[f"unassigned_site_ops_cost"] = float(extracted_parsed_res['ops_cost'])
                st.success("✅ Extracted successfully and pre-filled form fields!")
                st.rerun()

    st.divider()
    st.header("1. Site & Lease Specification")

    col1, col2 = st.columns(2)
    with col1:
        selected_location = st.selectbox("Select Commercial Location", options=list(LOCATION_LOOKUP.keys()), index=0)
        if selected_location == "Custom / Other Site...":
            location_name = st.text_input("Enter Custom Location Name", value="", placeholder="e.g. Rondebuilt Centre", key="custom_site_name_input")
            if location_name and not offline_mode_toggle and st.button("🔍 Research & Auto-Populate Site Data"):
                with st.spinner(f"Gathering intelligence for '{location_name}'..."):
                    web_intel = research_location_online(location_name, force_offline=offline_mode_toggle)
                    SITE_PROFILES[location_name] = web_intel
                    st.success(f"Retrieved data for {location_name}!")
        else:
            location_name = selected_location

    site_key = re.sub(r'[^a-zA-Z0-9]', '_', location_name.lower()) if location_name else "unassigned_site"
    
    def get_site_state(key, default_val):
        full_key = f"{site_key}_{key}"
        if full_key not in st.session_state:
            st.session_state[full_key] = default_val
        return st.session_state[full_key]

    def set_site_state(key, val):
        st.session_state[f"{site_key}_{key}"] = val

    site_default_info = SITE_PROFILES.get(location_name, {
        "suburb": "", "shop": "", "default_rent": 0.0, "default_ops": 0.0, "default_gla": 0.0, "model": "Express Model"
    })

    with col2:
        shop_code = st.text_input("Shop / Unit Code", value=site_default_info.get("shop", ""), key=f"{site_key}_shop_input")

    suburb_node = st.text_input("Suburb / Node", value=site_default_info.get("suburb", LOCATION_LOOKUP.get(selected_location, "")), key=f"{site_key}_suburb_input")

    selected_model = st.radio("Select Model Type", options=list(STORE_MODELS.keys()), index=1, horizontal=True, key=f"{site_key}_model_radio")
    model_data = STORE_MODELS.get(selected_model, STORE_MODELS["Express Model"])

    if f"{site_key}_int_gla_input" not in st.session_state: st.session_state[f"{site_key}_int_gla_input"] = 0.0
    if f"{site_key}_external_gla" not in st.session_state: st.session_state[f"{site_key}_external_gla"] = 0.0
    if f"{site_key}_capex_input" not in st.session_state: st.session_state[f"{site_key}_capex_input"] = 0.0
    if f"{site_key}_wc_input" not in st.session_state: st.session_state[f"{site_key}_wc_input"] = 0.0

    col_int_gla, col_ext_gla = st.columns(2)
    with col_int_gla: internal_gla = st.number_input("Internal Area (sqm)", min_value=0.0, step=1.0, key=f"{site_key}_int_gla_input")
    with col_ext_gla: external_gla = st.number_input("External / Patio Area (sqm)", min_value=0.0, step=1.0, key=f"{site_key}_external_gla")

    total_gla = internal_gla + external_gla

    blueprint_file = st.file_uploader("Upload Architectural Blueprint", type=["pdf", "png", "jpg", "jpeg"], key=f"{site_key}_blueprint_uploader")
    if blueprint_file is not None:
        pil_img, pdf_text = process_uploaded_file(blueprint_file)
        if pil_img is not None: set_site_state("blueprint_img", pil_img)

    blueprint_pil_img = get_site_state("blueprint_img", None)

    st.divider()
    st.header("2. Commercial Capital & Lease Modeling")

    turnkey_capital = st.number_input("Total Turnkey Capital (Excl. VAT)", step=50000.0, format="%.2f", key=f"{site_key}_capex_input")
    working_capital = st.number_input("Suggested Working Capital Requirement", step=25000.0, format="%.2f", key=f"{site_key}_wc_input")

    col_int_rent, col_ext_rent = st.columns(2)
    with col_int_rent:
        internal_rent_sqm = st.number_input("Internal Base Rent (R / sqm / month)", value=get_site_state("int_rent", 0.0), step=10.0, key=f"{site_key}_int_rent_input")
    with col_ext_rent:
        external_rent_sqm = st.number_input("External Base Rent (R / sqm / month)", value=get_site_state("ext_rent", 0.0), step=5.0, key=f"{site_key}_ext_rent_input")

    ops_cost_sqm = st.number_input("Ops Cost / Municipal (R / sqm)", value=get_site_state("ops_cost", 0.0), step=1.0, key=f"{site_key}_ops_input")
    turnover_clause_pct = st.number_input("Annual Turnover Clause (%)", value=7.0, step=0.5, key=f"{site_key}_turn_pct_input")

    total_base_rent_monthly = (internal_rent_sqm * internal_gla) + (external_rent_sqm * external_gla)
    total_ops_cost = ops_cost_sqm * total_gla
    total_lease_outlay_monthly = total_base_rent_monthly + total_ops_cost

    st.markdown(f"""
    <div class="lease-outlay-card">
        <b>Total Monthly Landlord Lease Outlay:</b> R {int(round(total_lease_outlay_monthly)):,} (Excl. VAT)
    </div>
    """, unsafe_allow_html=True)

    # Recovery Matrix Calculations
    gp_margin = 0.55
    aov_ticket = 190.0
    outflow_breakeven = total_lease_outlay_monthly + model_data["labor_monthly"]
    turnover_req_be = outflow_breakeven / gp_margin if gp_margin > 0 else 0
    turnover_req_12 = (outflow_breakeven + (turnkey_capital / 12)) / gp_margin if gp_margin > 0 else 0
    turnover_req_24 = (outflow_breakeven + (turnkey_capital / 24)) / gp_margin if gp_margin > 0 else 0

    payback_matrix_data = {
        "RECOVERY HORIZON": ["Operational Breakeven", "12 Months Recovery Target", "24 Months Recovery Target"],
        "REQUIRED TURNOVER/MONTH": [f"R {int(round(turnover_req_be)):,}", f"R {int(round(turnover_req_12)):,}", f"R {int(round(turnover_req_24)):,}"],
        "REQUIRED UNITS / MONTH": [f"{math.ceil(turnover_req_be/aov_ticket):,} units", f"{math.ceil(turnover_req_12/aov_ticket):,} units", f"{math.ceil(turnover_req_24/aov_ticket):,} units"],
        "REQUIRED UNITS / DAY": [f"{math.ceil(math.ceil(turnover_req_be/aov_ticket)/30)} units / day", f"{math.ceil(math.ceil(turnover_req_12/aov_ticket)/30)} units / day", f"{math.ceil(math.ceil(turnover_req_24/aov_ticket)/30)} units / day"]
    }
    df_payback_matrix = pd.DataFrame(payback_matrix_data)

    # P&L Calculations
    cash_flow_data = []
    total_initial_investment = turnkey_capital + working_capital
    debt_portion = total_initial_investment * 0.50
    monthly_interest_rate = 0.1175 / 12
    monthly_loan_payment = debt_portion * (monthly_interest_rate * (1 + monthly_interest_rate)**60) / ((1 + monthly_interest_rate)**60 - 1) if ((1 + monthly_interest_rate)**60 - 1) > 0 else 0

    for m in range(1, 61):
        year_idx = (m - 1) // 12
        season_multiplier = SEASONAL_FACTORS[(m - 1) % 12]
        monthly_turnover = (turnover_req_12 * (1.08 ** year_idx)) * season_multiplier
        monthly_lease = total_lease_outlay_monthly * (1.07 ** year_idx)
        monthly_cogs = monthly_turnover * 0.35
        monthly_royalties = monthly_turnover * 0.09
        total_monthly_expenses = monthly_lease + monthly_cogs + monthly_royalties + model_data["labor_monthly"]
        ebitda = monthly_turnover - total_monthly_expenses
        net_profit = ebitda - monthly_loan_payment
        cash_flow_data.append({"Month": m, "Year": year_idx + 1, "Turnover": monthly_turnover, "Lease Outlay": monthly_lease, "COGS (35%)": monthly_cogs, "Labor": model_data["labor_monthly"], "Royalties (9%)": monthly_royalties, "EBITDA": ebitda, "Bank Repayment": monthly_loan_payment, "Net Operating Profit": net_profit})

    df_cashflow = pd.DataFrame(cash_flow_data)
    df_cashflow['Year_Label'] = "Year " + df_cashflow['Year'].astype(str)
    annual_pnl = df_cashflow.groupby('Year_Label').agg({'Turnover': 'sum', 'Lease Outlay': 'sum', 'COGS (35%)': 'sum', 'Labor': 'sum', 'Royalties (9%)': 'sum', 'EBITDA': 'sum', 'Bank Repayment': 'sum', 'Net Operating Profit': 'sum'}).reset_index()

    st.divider()
    st.header("6. Dispatch Completed Site Feasibility Pack")

    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        target_applicant_name = st.text_input("Prospective Franchisee Full Name", value="", placeholder="e.g. John Doe", key=f"{site_key}_app_name")
        target_applicant_email = st.text_input("Prospective Franchisee Email Address", value="", placeholder="e.g. applicant@domain.com", key=f"{site_key}_app_email")
    with col_inv2:
        target_applicant_mobile = st.text_input("Prospective Franchisee Mobile Number", value="", placeholder="e.g. 0827867712", key=f"{site_key}_app_mobile")

    if not location_name or total_gla <= 0 or turnkey_capital <= 0:
        st.warning("⚠️ **Please complete the Location Name, GLA, and Capital details above before generating the Feasibility PDF or dispatching.**")
    else:
        selected_menus = get_available_brand_menus()

        if target_applicant_name and target_applicant_email:
            save_investor_lead({
                "full_name": target_applicant_name, "entity_name": "Prospective Entity", "id_or_passport": "Pending",
                "email": target_applicant_email, "mobile": target_applicant_mobile if target_applicant_mobile else "N/A",
                "preferred_site": location_name, "store_model": selected_model, "capital_available": turnkey_capital + working_capital,
                "unencumbered_cash_pct": 50.0, "admin_fee_paid": 0, "ndnca_signed": 0, "popia_consent": 1
            })

        clean_site_slug = re.sub(r'[^a-zA-Z0-9_]', '_', location_name.strip())
        pdf_filename = f"{clean_site_slug}_{selected_model.replace(' ', '_')}_{int(total_gla)}m2_.pdf"

        pdf_buffer = generate_pdf_report(
            location_name, shop_code, suburb_node, internal_gla, external_gla, total_gla, selected_model,
            40, 50, turnkey_capital, working_capital, internal_rent_sqm, external_rent_sqm, ops_cost_sqm,
            total_lease_outlay_monthly, turnover_clause_pct, "Express Model", 7.42,
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
            st.markdown(f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}" class="direct-dl-btn">📥 Download PDF Direct</a>', unsafe_allow_html=True)
            local_saved_path, sync_status_msg = sync_pdf_to_local_and_cloud(location_name, pdf_bytes, pdf_filename, offline_mode=offline_mode_toggle)
            st.caption(f"📂 **Local Directory Saved:** `{local_saved_path}`")
            st.info(f"☁️ **Google Drive Status:** {sync_status_msg}")

        with btn_col2:
            if st.button("📧 Dispatch via Email", key=f"{site_key}_email_btn"):
                if not target_applicant_email:
                    st.error("Please enter a valid Franchisee Email Address above.")
                else:
                    sent_ok, send_msg = send_franchisee_email_pack(target_applicant_email, target_applicant_name, location_name, pdf_bytes, pdf_filename)
                    if sent_ok: st.success(f"✅ {send_msg}")
                    else: st.error(f"❌ Email Failed: {send_msg}")

    render_contact_footer()

# TAB 2: BRAND MENUS & MEDIA SHOWCASE
with tab2:
    st.header("📖 Brand Menus & Global Media Showcase")
    for brand_key, brand_info in BRAND_MENU_CATALOG.items():
        st.markdown(f"### {brand_key}")
        st.markdown(f"**Tagline:** {brand_info['tagline']}")
        st.markdown(f"**Overview:** {brand_info['description']}")
        st.markdown(f"🔗 [Download Menu PDF]({get_drive_menu_download_url(brand_info['drive_file_id'])})")
        st.divider()
    render_contact_footer()

# TAB 3: INVESTOR & FRANCHISEE REGISTRY
with tab3:
    st.header("Franchisee & Investor Lead Intake & Database")
    df_pipeline = get_pipeline_dataframe()
    if not df_pipeline.empty:
        st.dataframe(df_pipeline, use_container_width=True)
    else:
        st.info("No applicant records available in database.")
    render_contact_footer()
