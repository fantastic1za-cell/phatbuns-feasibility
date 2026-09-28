import os
import smtplib
from email.message import EmailMessage
from io import BytesIO
import streamlit as st

def get_drive_service():
    """
    Initializes Google Drive API service using Google Cloud Service Account credentials.
    Bypasses token expiration and client validation errors by utilizing 
    the service account key configuration in Streamlit secrets.
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

def get_or_create_folder(service, folder_name, parent_id=None):
    """Finds or creates a subfolder within Google Drive and returns (folder_id, error_message)."""
    try:
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
            
        results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id'], None
        
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            folder_metadata['parents'] = [parent_id]
            
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id'), None
    except Exception as e:
        return None, str(e)

def sync_file_to_drive(file_obj, location_name):
    """Uploads or updates the generated PDF report in the designated Google Drive folder."""
    service = get_drive_service()
    if not service:
        return False, "Drive API Inactive (Check Secrets)"
        
    try:
        from googleapiclient.http import MediaIoBaseUpload
        
        root_folder_id = st.secrets.get("DRIVE_FOLDER_ID")
        if not root_folder_id:
            return False, "Drive Error: DRIVE_FOLDER_ID not found in secrets."
            
        loc_folder_id, folder_err = get_or_create_folder(service, location_name, root_folder_id)
        if not loc_folder_id:
            return False, f"Folder Creation Error: {folder_err}"
            
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
        existing = service.files().list(q=query, spaces='drive', fields="files(id)").execute().get('files', [])
        
        if existing:
            service.files().update(fileId=existing[0]['id'], media_body=media).execute()
        else:
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            
        return True, "Synced Successfully to Google Drive via Service Account!"
    except Exception as e:
        return False, f"Sync Error: {str(e)}"

def send_feasibility_email(recipient_email, client_name, file_bytes, location_name):
    """Sends the generated PDF feasibility report via Gmail SMTP with Phatbuns South Africa sender branding."""
    try:
        gmail_user = st.secrets.get("GMAIL_USER")
        gmail_pass = st.secrets.get("GMAIL_APP_PASSWORD")
        
        if not gmail_user or not gmail_pass:
            return False, "Gmail credentials missing in secrets."
            
        msg = EmailMessage()
        msg['Subject'] = f"Phatbuns SA — Executive Franchisee Feasibility Pack & Investor Dossier ({location_name})"
        
        # Explicitly set sender display name to Phatbuns South Africa
        msg['From'] = f"Phatbuns South Africa <{gmail_user}>"
        msg['To'] = recipient_email
        
        msg.set_content(
            f"Dear {client_name},\n\n"
            f"Thank you for taking the time to show interest in the Phatbuns South Africa franchise expansion program.\n\n"
            f"We are excited to share our comprehensive Master Franchisee Investor Pack for {location_name}. Phatbuns represents a premier, high-growth commercial brand footprint across South Africa.\n\n"
            f"Please find attached to this email (Consolidated within the Feasibility PDF Pack):\n\n"
            f"1. Executive Cover Page & Brand Identity Presentation\n"
            f"2. Site Evaluation & Commercial Investment Analysis ({location_name})\n"
            f"3. Financial Outlay & Debt Serviceability Breakdown\n"
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
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_pass)
            server.send_message(msg)
            
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Email Error: {str(e)}"
