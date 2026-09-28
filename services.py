import os
import smtplib
from email.message import EmailMessage
from io import BytesIO
import streamlit as st

def get_drive_service():
    """
    Initializes Google Drive API service using User OAuth credentials.
    Bypasses Service Account 0-quota limits by directly utilizing the 
    user's personal Google Drive storage.
    """
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        if "gcp_user_oauth" not in st.secrets:
            st.error("Authentication Error: Missing [gcp_user_oauth] in Streamlit secrets.")
            return None
            
        oauth_data = st.secrets["gcp_user_oauth"]
        creds = Credentials(
            token=None,
            refresh_token=oauth_data["refresh_token"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=oauth_data["client_id"],
            client_secret=oauth_data["client_secret"],
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        st.error(f"Drive API Connection Error: {str(e)}")
        return None

def get_or_create_folder(service, folder_name, parent_id=None):
    """Finds or creates a subfolder within Google Drive."""
    try:
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
            
        results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
        
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            folder_metadata['parents'] = [parent_id]
            
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')
    except Exception:
        return None

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
            
        loc_folder_id = get_or_create_folder(service, location_name, root_folder_id)
        if not loc_folder_id:
            return False, f"Could not create location subfolder '{location_name}' inside target Drive folder."
            
        file_name = getattr(file_obj, "name", f"Feasibility_Report_{location_name.replace(' ', '_')}.pdf")
        
        if hasattr(file_obj, "getvalue"):
            file_bytes = file_obj.getvalue()
        elif hasattr(file_obj, "read"):
            file_obj.seek(0)
            file_bytes = file_obj.read()
        else:
            file_bytes = file_obj

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
            
        return True, "Synced Successfully to Google Drive!"
    except Exception as e:
        return False, f"Sync Error: {str(e)}"

def send_report_via_email(recipient_email, file_bytes, file_name, location_name):
    """Sends the generated PDF feasibility report directly via Gmail SMTP."""
    try:
        gmail_user = st.secrets.get("GMAIL_USER")
        gmail_pass = st.secrets.get("GMAIL_APP_PASSWORD")
        
        if not gmail_user or not gmail_pass:
            return False, "Gmail credentials missing in secrets."
            
        msg = EmailMessage()
        msg['Subject'] = f"Feasibility Report - {location_name}"
        msg['From'] = gmail_user
        msg['To'] = recipient_email
        msg.set_content(f"Hi,\n\nPlease find attached the generated feasibility report for {location_name}.\n\nBest regards,\nMr Mobile SA")
        
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
