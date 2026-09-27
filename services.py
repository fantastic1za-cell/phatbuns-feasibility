import os
import smtplib
from email.message import EmailMessage
import streamlit as st

def get_drive_service():
    """
    Initializes Google Drive API service. Explicitly normalizes and re-frames 
    the RSA private key to permanently resolve Streamlit TOML PEM MalformedFraming errors.
    """
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            
            if "private_key" in creds_dict:
                pk = creds_dict["private_key"]
                pk = pk.replace("\\n", "\n")
                
                if "-----BEGIN PRIVATE KEY-----" in pk and "-----END PRIVATE KEY-----" in pk:
                    header = "-----BEGIN PRIVATE KEY-----"
                    footer = "-----END PRIVATE KEY-----"
                    body = pk.replace(header, "").replace(footer, "").replace("\n", "").strip()
                    chunks = [body[i:i+64] for i in range(0, len(body), 64)]
                    pk = f"{header}\n" + "\n".join(chunks) + f"\n{footer}\n"
                    
                creds_dict["private_key"] = pk
                
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=["https://www.googleapis.com/auth/drive"]
            )
            return build("drive", "v3", credentials=creds)
    except Exception as e:
        st.error(f"Drive Sync Error: {str(e)}")
    return None

def get_or_create_folder(service, folder_name, parent_id=None):
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
    service = get_drive_service()
    if not service:
        return False, "Drive API Inactive"
        
    try:
        from googleapiclient.http import MediaIoBaseUpload
        from io import BytesIO
        
        root_folder_id = get_or_create_folder(service, "Locations")
        if not root_folder_id:
            return False, "Could not create root folder"
            
        loc_folder_id = get_or_create_folder(service, location_name, root_folder_id)
        if not loc_folder_id:
            return False, "Could not create location folder"
            
        file_name = getattr(file_obj, "name", "feasibility_report.pdf")
        
        if hasattr(file_obj, "getvalue"):
            file_bytes = file_obj.getvalue()
        elif hasattr(file_obj, "read"):
            file_obj.seek(0)
            file_bytes = file_obj.read()
        else:
            file_bytes = file_obj

        media = MediaIoBaseUpload(BytesIO(file_bytes), mimetype='application/octet-stream', resumable=True)
        
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
            
        return True, "Synced Successfully to Drive"
    except Exception as e:
        return False, f"Sync Error: {str(e)}"

def send_feasibility_email(recipient_email, recipient_name, pdf_bytes, location_name):
    try:
        sender_email = st.secrets.get("GMAIL_USER", "fantastic1za@gmail.com")
        app_password = st.secrets.get("GMAIL_APP_PASSWORD", "")
        
        if not app_password:
            return False, "Gmail App Password not configured."

        msg = EmailMessage()
        msg['Subject'] = f"Phatbuns SA — Executive Franchisee Feasibility Pack & Investor Review ({location_name})"
        msg['From'] = f"Phatbuns South Africa <{sender_email}>"
        msg['To'] = recipient_email
        
        email_body = (
            f"Dear {recipient_name},\n\n"
            f"Thank you for taking the time to show interest in the Phatbuns South Africa franchise expansion program.\n\n"
            f"We are excited to share our comprehensive Master Franchisee Investor Pack for {location_name}. "
            f"Phatbuns represents a premier, high-growth commercial brand footprint across South Africa.\n\n"
            f"Please find attached to this email (Consolidated within the Feasibility PDF Pack):\n"
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
            f"SA Master Rights Holder | Phatbuns South Africa\n"
            f"Mobile: +27 (0)68 710 1939 | WhatsApp: +27 (0)82 786 7712\n"
            f"Email: nisaar@fantastic1.com"
        )
        
        msg.set_content(email_body)
        
        msg.add_attachment(
            pdf_bytes,
            maintype='application',
            subtype='pdf',
            filename=f"Phatbuns_{location_name.replace(' ', '_')}_Feasibility_Report.pdf"
        )
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
            
        return True, "Email Dispatched Successfully"
    except Exception as e:
        return False, f"Email Error: {str(e)}"
