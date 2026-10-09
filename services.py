import os
import time
import smtplib
from email.message import EmailMessage
from io import BytesIO
import streamlit as st

def retry_with_backoff(retries=3, backoff_in_seconds=2):
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

def save_local_backup(file_bytes, location_name):
    """Saves PDF backup directly to local server directory."""
    try:
        safe_loc_name = location_name.replace(" ", "_").replace("(", "").replace(")", "")
        dir_path = os.path.join("Locations", safe_loc_name)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, "A_Phatbuns_Master_Investor_Pack.pdf")
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        return file_path
    except Exception:
        return None

def get_drive_service():
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        if "gcp_service_account" not in st.secrets:
            return None
            
        service_account_info = dict(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        return build("drive", "v3", credentials=creds)
    except Exception:
        return None

@retry_with_backoff(retries=3, backoff_in_seconds=2)
def get_or_create_folder_with_retry(service, folder_name, parent_id):
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed = false"
    results = service.files().list(
        q=query, 
        spaces='drive', 
        corpora='allDrives',
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True, 
        fields="files(id, name)"
    ).execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']
    
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(
        body=folder_metadata, 
        supportsAllDrives=True, 
        fields='id'
    ).execute()
    return folder.get('id')

def sync_file_to_drive(file_obj, location_name):
    """Uploads directly into Google Drive Shared Drive with local directory failover."""
    if isinstance(file_obj, bytes):
        file_bytes = file_obj
    elif hasattr(file_obj, "getvalue"):
        file_bytes = file_obj.getvalue()
    elif hasattr(file_obj, "read"):
        file_obj.seek(0)
        file_bytes = file_obj.read()
    else:
        file_bytes = bytes(file_obj)

    local_path = save_local_backup(file_bytes, location_name)
    
    service = get_drive_service()
    if not service:
        return True, f"Automated Directory Saved: {local_path}"

    try:
        from googleapiclient.http import MediaIoBaseUpload
        root_folder_id = st.secrets.get("DRIVE_FOLDER_ID")
        if not root_folder_id:
            return True, f"Automated Directory Saved: {local_path}"

        safe_loc_name = location_name.replace(" ", "_").replace("(", "").replace(")", "")
        loc_folder_id = get_or_create_folder_with_retry(service, safe_loc_name, root_folder_id)
        file_name = f"Phatbuns_{safe_loc_name}_Master_Investor_Pack.pdf"

        media = MediaIoBaseUpload(BytesIO(file_bytes), mimetype='application/pdf', resumable=True)
        file_metadata = {'name': file_name, 'parents': [loc_folder_id]}
        
        query = f"name = '{file_name}' and '{loc_folder_id}' in parents and trashed = false"
        existing = service.files().list(
            q=query, 
            spaces='drive', 
            corpora='allDrives',
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
        return True, f"Automated Directory Saved: {local_path}\n(Sync Failover Triggered: {str(e)})"

@retry_with_backoff(retries=3, backoff_in_seconds=2)
def send_email_with_retry(gmail_user, gmail_pass, msg):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(gmail_user, gmail_pass)
        server.send_message(msg)

def send_feasibility_email(recipient_email, client_name, file_bytes, location_name):
    try:
        gmail_user = st.secrets.get("GMAIL_USER")
        gmail_pass = st.secrets.get("GMAIL_APP_PASSWORD")
        if not gmail_user or not gmail_pass:
            return False, "Gmail credentials missing in secrets."
            
        msg = EmailMessage()
        msg['Subject'] = f"Phatbuns SA — Executive Franchisee Feasibility Pack ({location_name})"
        msg['From'] = f"Phatbuns South Africa <{gmail_user}>"
        msg['To'] = recipient_email
        msg.set_content(
            f"Dear {client_name},\n\nPlease find attached the Master Investor Pack for {location_name}.\n\n"
            f"Regards,\nNisaar Ally\nPhatbuns SA Rights Holder"
        )
        msg.add_attachment(file_bytes, maintype='application', subtype='pdf', filename=f"Phatbuns_{location_name}_Feasibility.pdf")
        
        send_email_with_retry(gmail_user, gmail_pass, msg)
        return True, "Email dispatched successfully!"
    except Exception as e:
        return False, f"Email Dispatch Error: {str(e)}"
