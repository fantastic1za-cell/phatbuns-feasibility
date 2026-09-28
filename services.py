import os
import smtplib
import json
import re
import tempfile
from email.message import EmailMessage
import streamlit as st

def get_drive_service():
    """
    Initializes Google Drive API service. Extracts raw base64 key bytes using regex 
    and reconstructs a valid RFC 1421 PEM block (exact 64-character wrapping) to 
    eliminate cryptography/OpenSSL MalformedFraming errors.
    """
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            
            if "private_key" in creds_dict:
                pk = str(creds_dict["private_key"])
                
                # Un-escape escaped newline characters
                pk_clean = pk.replace("\\n", "\n").replace("\r", "")
                
                # Strip out any existing header/footer markers or trailing hyphens
                body = re.sub(r'-----.*?-----', '', pk_clean)
                
                # Extract pure Base64 characters only
                b64_chars = "".join(re.findall(r'[A-Za-z0-9+/=]', body))
                
                # Re-wrap strictly into 64-character lines required by cryptography.io
                chunks = [b64_chars[i:i+64] for i in range(0, len(b64_chars), 64)]
                formatted_pem = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(chunks) + "\n-----END PRIVATE KEY-----\n"
                
                creds_dict["private_key"] = formatted_pem
            
            # Write to temporary credentials file to bypass dictionary parsing bugs
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp:
                json.dump(creds_dict, temp)
                temp_path = temp.name
                
            try:
                creds = service_account.Credentials.from_service_account_file(
                    temp_path, scopes=["https://www.googleapis.com/auth/drive"]
                )
                return build("drive", "v3", credentials=creds)
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
    except Exception as e:
        st.error(f"Drive API Connection Error: {str(e)}")
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
        return False, "Drive API Inactive (Check Secrets)"
        
    try:
        from googleapiclient.http import MediaIoBaseUpload
        from io import BytesIO
        
        root_folder_id = get_or_create_folder(service, "Locations")
        if not root_folder_id:
            return False, "Could not create root 'Locations' folder"
            
        loc_folder_id = get_or_create_folder(service, location_name, root_folder_id)
        if not loc_folder_id:
            return False, "Could not create location subfolder"
            
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
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; font-size: 14px; color: #1A1A1A; line-height: 1.5;">
            <p>Dear {recipient_name},</p>
            
            <p>Thank you for taking the time to show interest in the Phatbuns South Africa franchise expansion program.</p>
            
            <p>We are excited to share our comprehensive Master Franchisee Investor Pack for <b>{location_name}</b>. Phatbuns represents a premier, high-growth commercial brand footprint across South Africa.</p>
            
            <p><b>Please find attached to this email (Consolidated within the Feasibility PDF Pack):</b></p>
            <ol>
                <li>Executive Cover Page & Brand Identity Presentation</li>
                <li>Site Evaluation & Commercial Investment Analysis ({location_name})</li>
                <li>Financial Outlay & Debt Serviceability Breakdown</li>
                <li>5-Year Pro Forma Income Statement & 60-Month Cash Flow Projections (35% COGS Model)</li>
                <li>Development Layout & Leasing Site Plan (Rendered)</li>
                <li>Addendum — Brand Menus with Direct Google Drive Download Links</li>
                <li>Master Non-Circumvention, Non-Disclosure & Confidentiality Agreement (NCNDA)</li>
            </ol>
            
            <p><b>Next Steps:</b><br/>
            Please review the attached documents, sign the NCNDA execution page, and return a copy to proceed with formal site allocation and executive approval.</p>
            
            <p>Should you have any questions or require additional information, please feel free to reach out directly via call or WhatsApp.</p>
            
            <div style="margin-top: 30px; margin-bottom: 15px;">
                <img src="https://i.imgur.com/7kZ0h7T.png" alt="Phatbuns Icon" height="30" style="vertical-align: middle; margin-right: 15px;" />
                <img src="https://upload.wikimedia.org/wikipedia/commons/a/af/Flag_of_South_Africa.svg" alt="South African Flag" height="30" style="vertical-align: middle;" />
            </div>
            
            <p>Warm regards,</p>
            
            <p>
                <b>Nisaar Ally</b><br/>
                SA Master Rights Holder | Phatbuns South Africa<br/>
                Mobile: +27 (0)68 710 1939 | WhatsApp: +27 (0)82 786 7712<br/>
                Email: <a href="mailto:nisaar@fantastic1.com">nisaar@fantastic1.com</a>
            </p>
        </body>
        </html>
        """
        
        msg.set_content("Please view this email in an HTML-compatible email client.")
        msg.add_alternative(html_content, subtype='html')
        
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
