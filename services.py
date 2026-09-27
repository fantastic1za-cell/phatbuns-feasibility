import os
import smtplib
from email.message import EmailMessage
import streamlit as st

# Google Cloud / Drive API imports with fail-safe checks
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

def get_drive_service():
    """
    Initializes and returns the Google Drive API service using Streamlit Secrets.
    Includes fail-safe handling if credentials are missing or inactive.
    """
    if not GOOGLE_API_AVAILABLE:
        return None
    
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=["https://www.googleapis.com/auth/drive"]
            )
            return build("drive", "v3", credentials=creds)
    except Exception:
        pass
    return None

def get_or_create_folder(service, folder_name, parent_id=None):
    """
    Finds or creates a folder on Google Drive (e.g., Locations/{location_name}).
    """
    try:
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
            
        results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
        
        # Create folder if it doesn't exist
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
    """
    Uploads an uploaded file or generated PDF directly into the 
    dedicated Google Drive location folder: Locations/{location_name}/
    """
    service = get_drive_service()
    if not service:
        return False, "Drive API Inactive"
        
    try:
        # Root 'Locations' folder
        root_folder_id = get_or_create_folder(service, "Locations")
        if not root_folder_id:
            return False, "Could not create root folder"
            
        # Site-specific subfolder
        loc_folder_id = get_or_create_folder(service, location_name, root_folder_id)
        if not loc_folder_id:
            return False, "Could not create location folder"
            
        # Prepare file metadata and stream
        file_name = getattr(file_obj, "name", "feasibility_report.pdf")
        
        if hasattr(file_obj, "getvalue"):
            file_bytes = file_obj.getvalue()
        elif hasattr(file_obj, "read"):
            file_obj.seek(0)
            file_bytes = file_obj.read()
        else:
            file_bytes = file_obj

        from io import BytesIO
        media = MediaIoBaseUpload(BytesIO(file_bytes), mimetype='application/octet-stream', resumable=True)
        
        file_metadata = {
            'name': file_name,
            'parents': [loc_folder_id]
        }
        
        # Check if file already exists in folder to update or create new
        query = f"name = '{file_name}' and '{loc_folder_id}' in parents and trashed = false"
        existing = service.files().list(q=query, spaces='drive', fields="files(id)").execute().get('files', [])
        
        if existing:
            service.files().update(fileId=existing[0]['id'], media_body=media).execute()
        else:
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            
        return True, "Synced Successfully"
    except Exception as e:
        return False, f"Sync Error: {str(e)}"

def send_feasibility_email(recipient_email, recipient_name, pdf_bytes, location_name):
    """
    Dispatches the compiled feasibility PDF report via Gmail SMTP 
    using credentials stored in Streamlit Secrets.
    """
    try:
        sender_email = st.secrets.get("GMAIL_USER", "fantastic1za@gmail.com")
        app_password = st.secrets.get("GMAIL_APP_PASSWORD", "")
        
        if not app_password:
            return False, "Gmail App Password not configured."

        msg = EmailMessage()
        msg['Subject'] = f"Phatbuns Franchise Feasibility Pack - {location_name}"
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        msg.set_content(
            f"Dear {recipient_name},\n\n"
            f"Please find attached the official Phatbuns franchise feasibility and investment pack "
            f"for your prospective site at {location_name}.\n\n"
            f"This confidential pack includes financial models, layout structures, and brand standards.\n\n"
            f"Best regards,\n"
            f"Nisaar Ally\n"
            f"SA Master Rights Holder | Phatbuns South Africa"
        )
        
        # Attach the compiled PDF report
        msg.add_attachment(
            pdf_bytes,
            maintype='application',
            subtype='pdf',
            filename=f"Phatbuns_{location_name}_Feasibility_Report.pdf"
        )
        
        # Connect to Gmail SMTP secure server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
            
        return True, "Email Dispatched Successfully"
    except Exception as e:
        return False, f"Email Error: {str(e)}"
