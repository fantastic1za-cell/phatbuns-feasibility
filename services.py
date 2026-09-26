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
                        <tr style="background-color: #EDF2F7;">
                            <td style="padding: 10px; font-weight: bold; border: 1px solid #E2E8F0;">Company Documentation</td>
                            <td style="padding: 10px; border: 1px solid #E2E8F0;">{data.get('company_docs_status', 'Not Provided')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-weight: bold; border: 1px solid #E2E8F0;">Franchisee ID / Passport</td>
                            <td style="padding: 10px; border: 1px solid #E2E8F0;">{data.get('franchisee_id_status', 'Not Provided')}</td>
                        </tr>
                        <tr style="background-color: #EDF2F7;">
                            <td style="padding: 10px; font-weight: bold; border: 1px solid #E2E8F0;">Proof of Funds Status</td>
                            <td style="padding: 10px; border: 1px solid #E2E8F0;">{data.get('proof_of_funds_status', 'Not Provided')}</td>
                        </tr>
                    </table>

                    <div style="margin-top: 20px; padding: 12px; background-color: #EBF8FF; border-left: 4px solid #3182CE; border-radius: 4px;">
                        <p style="margin: 0; font-size: 12px; color: #2B6CB0;">
                            <b>System Status:</b> Lead successfully recorded in SQLite database (<code>phatbuns_franchisees.db</code>) and visible in the CEO Pipeline Registry.
                        </p>
                    </div>
                </div>
                <div style="background-color: #EDF2F7; padding: 12px; text-align: center; font-size: 11px; color: #718096;">
                    Phatbuns SA Master Operations | Confidential Executive Notification
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
