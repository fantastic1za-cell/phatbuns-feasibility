import os
import time
import smtplib
from email.message import EmailMessage
from io import BytesIO
import streamlit as st

def retry_with_backoff(retries=3, backoff_in_seconds=2):
    """Decorator to retry flaky network or API calls with exponential backoff."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            x = 0
            while x < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    x += 1
                    if x == retries:
                        raise e
                    time.sleep(backoff_in_seconds * (2 ** (x - 1)))
        return wrapper
    return decorator

def get_drive_service():
    """
    Initializes Google Drive API service using Google Cloud Service Account credentials.
    """
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        if "gcp_service_account" not in st.secrets:
            st.error("Authentication Error: Missing [gcp_service_account] in Streamlit secrets.")
            return None
            
        service_account_info = dict(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        st.error(f"Drive API Connection Error: {str(e)}")
        return None

@retry_with_backoff(retries=3, backoff_in_seconds=2)
def get_or_create_folder_with_retry(service, folder_name, parent_id=None):
    """Robust folder lookup or creation with built-in retry failover loop supporting Shared Drives."""
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
        
    results = service.files().list(
        q=query, 
        spaces='drive', 
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True, 
        fields="files(id, name)"
    ).execute()
    files = results.get('files', [])
    
    if files:
        return files[0]['id']
    
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        folder_metadata['parents'] = [parent_id]
        
    folder = service.files().create(
        body=folder_metadata, 
        supportsAllDrives=True, 
        fields='id'
    ).execute()
    return folder.get('id')

def sync_file_to_drive(file_obj, location_name):
    """
    Uploads or updates the generated PDF report in Google Drive Shared Drive 
    using Service Account credentials with retry failover protection.
    """
    service = get_drive_service()
    if not service:
        return False, "Drive API Inactive (Check Secrets)"
        
    try:
        from googleapiclient.http import MediaIoBaseUpload
        
        root_folder_id = st.secrets.get("DRIVE_FOLDER_ID")
        if not root_folder_id:
            return False, "Drive Error: DRIVE_FOLDER_ID not found in secrets."
            
        try:
            loc_folder_id = get_or_create_folder_with_retry(service, location_name, root_folder_id)
        except Exception as fe:
            return False, f"Folder Creation Retry Failed: {str(fe)}"
            
        file_name = getattr(file_obj, "name", f"Phatbuns_{location_name.replace(' ', '_')}_Feasibility_Report.pdf")
        
        if isinstance(file_obj, bytes):
            file_bytes = file_obj
        elif hasattr(file_obj, "getvalue"):
            file_bytes = file_obj.getvalue()
        elif hasattr(file_obj, "read"):
            file_obj.seek(0)
            file_bytes = file_obj.read()
        else:
            file_bytes = bytes(file_obj)

        media = MediaIoBaseUpload(BytesIO(file_bytes), mimetype='application/pdf', resumable=True)
        
        file_metadata = {
            'name': file_name,
            'parents': [loc_folder_id]
        }
        
        query = f"name = '{file_name}' and '{loc_folder_id}' in parents and trashed = false"
        existing = service.files().list(
            q=query, 
            spaces='drive', 
            includeItemsFromAllDrives=True, 
            supportsAllDrives=True, 
            fields="files(id)"
        ).execute().get('files', [])
        
        if existing:
            service.files().update(
                fileId=existing[0]['id'], 
                media_body=media, 
                supportsAllDrives=True
            ).execute()
        else:
            service.files().create(
                body=file_metadata, 
                media_body=media, 
                supportsAllDrives=True, 
                fields='id'
            ).execute()
            
        return True, "Synced Successfully to Google Drive Shared Drive!"
    except Exception as e:
        return False, f"Sync Failover Triggered - Local Backup Active. Error: {str(e)}"

@retry_with_backoff(retries=3, backoff_in_seconds=2)
def send_email_with_retry(gmail_user, gmail_pass, msg):
    """SMTP transmission wrapped in retry loop for network instability."""
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(gmail_user, gmail_pass)
        server.send_message(msg)

def send_feasibility_email(recipient_email, client_name, file_bytes, location_name):
    """Sends the generated PDF feasibility report via Gmail SMTP with failover retry handling."""
    try:
        gmail_user = st.secrets.get("GMAIL_USER")
        gmail_pass = st.secrets.get("GMAIL_APP_PASSWORD")
        
        if not gmail_user or not gmail_pass:
            return False, "Gmail credentials missing in secrets."
            
        msg = EmailMessage()
        msg['Subject'] = f"Phatbuns SA — Executive Franchisee Feasibility Pack & Investor Dossier ({location_name})"
        msg['From'] = f"Phatbuns South Africa <{gmail_user}>"
        msg['To'] = recipient_email
        
        msg.set_content(
            f"Dear {client_name},\n\n"
            f"Thank you for taking the time to show interest in the Phatbuns South Africa franchise expansion program.\n\n"
            f"We are excited to share our comprehensive Master Franchisee Investor Pack for {location_name}. Phatbuns represents a premier, high-growth commercial brand footprint across South Africa.\n\n"
            f"Please find attached to this email (Consolidated within the Feasibility PDF Pack):\n\n"
            f"1. Executive Cover Page & Brand Identity Presentation\n"
            f"2. Site Evaluation & Commercial Investment Analysis ({location_name})\n"
            f"3. Financial Outlay & Debt Serviceability Breakdown (Excl. VAT)\n"
            f"4. 5-Year Pro Forma Income Statement & 60-Month Cash Flow Projections (35% COGS Model)\n"
            f"5. Development Layout & Leasing Site Plan (Rendered)\n"
            f"6. Addendum — Brand Menus with Direct Google Drive Download Links\n"
            f"7. Master Non-Circumvention, Non-Disclosure & Confidentiality Agreement (NCNDA)\n\n"
            f"Next Steps:\n"
            f"Please review the attached documents, sign the NCNDA execution page, and return a copy to proceed with formal site allocation and executive approval.\n\n"
            f"Should you have any questions or require additional information, please feel free to reach out directly via call or WhatsApp.\n\n"
            f"Warm regards,\n\n"
            f"Nisaar Ally\n"
            f"SA Master Rights Holder | Phatbuns Expansion\n"
            f"Mobile: +27 (0)68 710 1939 | WhatsApp: +27 (0)82 786 7712\n"
            f"Email: nisaar@fantastic1.com"
        )
        
        file_name = f"Phatbuns_{location_name.replace(' ', '_')}_Feasibility_Report.pdf"
        msg.add_attachment(
            file_bytes,
            maintype='application',
            subtype='pdf',
            filename=file_name
        )
        
        send_email_with_retry(gmail_user, gmail_pass, msg)
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Email Dispatch Error after retries: {str(e)}"
