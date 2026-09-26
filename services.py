# services.py - External Services, Database & Email Dispatch
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

GDRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
LOCATIONS_ROOT_DRIVE_ID = "1vGItMiw-ZYqzBOXvLfl0xkbhh7uYkhf5"
DB_FILE = "phatbuns_franchisees.db"

# Database Operations
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
    conn.commit()
    conn.close()

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
                company_docs_status = ?, franchisee_id_status = ?, proof_of_funds_status = ?,
                admin_fee_paid = ?, ndnca_signed = ?, popia_consent = ?
            WHERE email = ?
        """, (
            data['full_name'], data.get('entity_name', ''), data['id_or_passport'], data['mobile'],
            data['preferred_site'], data['store_model'], data['capital_available'], data['unencumbered_cash_pct'],
            data.get('company_docs_status', 'Not Provided'), data.get('franchisee_id_status', 'Not Provided'), data.get('proof_of_funds_status', 'Not Provided'),
            data.get('admin_fee_paid', 0), data.get('ndnca_signed', 0), data.get('popia_consent', 1), data['email']
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
            data['full_name'], data.get('entity_name', ''), data['id_or_passport'],
            data['email'], data['mobile'], data['preferred_site'],
            data['store_model'], data['capital_available'], data['unencumbered_cash_pct'],
            data.get('company_docs_status', 'Not Provided'), data.get('franchisee_id_status', 'Not Provided'), data.get('proof_of_funds_status', 'Not Provided'),
            data.get('admin_fee_paid', 0), data.get('ndnca_signed', 0), data.get('popia_consent', 1)
        ))
    conn.commit()
    conn.close()

def get_pipeline_dataframe():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT id, full_name, mobile, email, preferred_site, store_model, capital_available, unencumbered_cash_pct, company_docs_status, franchisee_id_status, proof_of_funds_status, ceo_approval, created_at FROM franchisee_pipeline ORDER BY id DESC", conn)
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
        clean_name = re.sub(r'[^a-zA-Z0-9_\- ]', '_', folder_name)
        query = f"name = '{clean_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = service.files().list(q=query, spaces='drive', fields="files(id, name)", supportsAllDrives=True, includeItemsFromAllDrives=True, corpora='allDrives').execute()
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
    loc_clean = re.sub(r'[^a-zA-Z0-9_\- ]', '_', location_name.strip()) if location_name else "Unassigned_Location"
    loc_sub_dir = os.path.join(LOCATIONS_DIR, loc_clean)
    os.makedirs(loc_sub_dir, exist_ok=True)
    local_file_path = os.path.join(loc_sub_dir, pdf_filename)
    
    with open(local_file_path, "wb") as f:
        f.write(pdf_bytes)

    drive_service = get_drive_service()
    if not drive_service:
        return local_file_path, "Drive API Inactive (Check Secrets/Service Account)"

    try:
        site_folder_id = get_or_create_drive_folder(drive_service, loc_clean, parent_id=LOCATIONS_ROOT_DRIVE_ID)
        if site_folder_id:
            file_id = upload_pdf_to_drive(drive_service, pdf_bytes, pdf_filename, site_folder_id)
            if file_id:
                return local_file_path, f"Successfully Synced to Google Drive: '{loc_clean}/{pdf_filename}'"
        return local_file_path, "Google Drive Sync Failed"
    except Exception as e:
        return local_file_path, f"Drive Exception: {str(e)}"

# Email Dispatcher
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
