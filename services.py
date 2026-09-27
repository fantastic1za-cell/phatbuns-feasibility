# services.py - Complete Google Drive, Gmail & PDF Extraction Services
import os
import io
import re
import smtplib
from email.message import EmailMessage
import streamlit as st

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    HAS_GDRIVE = True
except ImportError:
    HAS_GDRIVE = False

SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_drive_service():
    if not HAS_GDRIVE:
        return None
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            return build("drive", "v3", credentials=creds)
    except Exception as e:
        print(f"Drive Service Error: {e}")
    return None

def upload_pdf_to_drive(pdf_bytes, file_name, location_name="General"):
    drive_service = get_drive_service()
    if not drive_service:
        return None, "(Drive API Inactive - check st.secrets)"
    
    try:
        # Find or create Location folder
        folder_query = f"name = '{location_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = drive_service.files().list(q=folder_query, spaces='drive', fields="files(id, name)").execute()
        folders = results.get('files', [])
        
        if folders:
            folder_id = folders[0]['id']
        else:
            folder_metadata = {
                'name': location_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
            folder_id = folder.get('id')

        # Upload PDF file
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(pdf_bytes), mimetype='application/pdf', resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        return file.get('webViewLink'), "Uploaded Successfully to Google Drive"
    except Exception as e:
        return None, f"Drive Upload Error: {str(e)}"

def send_feasibility_email(to_email, pdf_bytes, file_name, location_name):
    try:
        gmail_user = st.secrets.get("GMAIL_USER", "fantastic1za@gmail.com")
        gmail_password = st.secrets.get("GMAIL_APP_PASSWORD", "")
        
        if not gmail_password:
            return False, "Gmail App Password not configured in secrets."

        msg = EmailMessage()
        msg['Subject'] = f"Phatbuns Feasibility & Franchise Pack - {location_name}"
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg.set_content(f"Dear Prospective Partner,\n\nPlease find attached the formal Phatbuns Feasibility Pack and Investment Matrix for {location_name}.\n\nKind Regards,\nNisaar Ally\nSA Master Rights Holder")

        msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=file_name)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_user, gmail_password)
            smtp.send_message(msg)
        return True, "Email dispatched successfully"
    except Exception as e:
        return False, f"Email dispatch failed: {str(e)}"

def extract_legacy_pdf_parameters(pdf_file_bytes):
    extracted_data = {}
    if not HAS_PYPDF:
        return extracted_data
    
    try:
        reader = PdfReader(io.BytesIO(pdf_file_bytes))
        full_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
            
        # 1. Location / Site Extraction
        loc_match = re.search(r"(?:New Corner|Mall|Site|Location)[^\|\n]*[:\|\-]?\s*([^\n\(]+)", full_text, re.IGNORECASE)
        if loc_match:
            extracted_data["location_name"] = loc_match.group(0).strip().replace("PHATBUNS FEASIBILITY", "").strip()
        else:
            extracted_data["location_name"] = "New Corner Northcliff"

        # 2. Shop Code Extraction (e.g., "Shop RL 03" or "RL03")[span_1](start_span)[span_1](end_span)
        shop_match = re.search(r"(?:Shop|Unit|Store)\s*([0-9A-Za-z\s\-]+)", full_text, re.IGNORECASE)
        if shop_match:
            extracted_data["shop_code"] = shop_match.group(1).strip()
        else:
            extracted_data["shop_code"] = "RL 03"

        # 3. GLA / Area Extraction (e.g., "167sqm" or "167 m²")[span_2](start_span)[span_2](end_span)
        gla_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:m²|sqm|sq m)", full_text, re.IGNORECASE)
        if gla_match:
            extracted_data["internal_gla"] = float(gla_match.group(1))
        else:
            extracted_data["internal_gla"] = 167.0

        # 4. Rental Rate Extraction (e.g., "R350.00/m²")[span_3](start_span)[span_3](end_span)
        rent_match = re.search(r"R\s*([\d,]+(?:\.\d+)?)\s*/\s*(?:m²|sqm)", full_text, re.IGNORECASE)
        if rent_match:
            extracted_data["int_rent"] = float(rent_match.group(1).replace(",", ""))
        else:
            extracted_data["int_rent"] = 350.0

        # 5. Capital & Working Capital[span_4](start_span)[span_4](end_span)
        cap_match = re.search(r"(?:Turnkey|Capital|Setup)\s*(?:Cost)?[:\|\-]?\s*R\s*([\d,]+)", full_text, re.IGNORECASE)
        if cap_match:
            extracted_data["turnkey_capital"] = float(cap_match.group(1).replace(",", ""))
        else:
            extracted_data["turnkey_capital"] = 3100000.0

        wc_match = re.search(r"(?:Working Capital)\s*[:\|\-]?\s*R\s*([\d,]+)", full_text, re.IGNORECASE)
        if wc_match:
            extracted_data["working_capital"] = float(wc_match.group(1).replace(",", ""))
        else:
            extracted_data["working_capital"] = 750000.0

    except Exception as e:
        print(f"Extraction Exception: {e}")
        
    return extracted_data
