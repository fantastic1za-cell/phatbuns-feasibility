# services.py - Production Service Engine (Drive Folder Hierarchy & Safe Extraction)
import os
import io
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
