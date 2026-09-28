import streamlit as st
import os
from pdf_engine import generate_feasibility_pdf
from services import sync_file_to_drive, send_feasibility_email

st.set_page_config(page_title="Phatbuns SA Feasibility Generator", page_icon="🍔", layout="centered")

st.title("🍔 Phatbuns SA — Executive Feasibility Generator")
st.markdown("### Master Franchisee Site Evaluation & Investor Pack Generator")

with st.form("feasibility_form"):
    st.subheader("1. Investor & Contact Details")
    recipient_email = st.text_input("Prospective Franchisee Email", value="nisaar@fantastic1.com")
    recipient_mobile = st.text_input("Prospective Franchisee Mobile / WhatsApp", value="+27 82 786 7712")
    
    st.subheader("2. Site & Location Parameters")
    location_name = st.text_input("Location Name / Node", value="New Corner Northcliff (Shop RL 03)")
    store_footprint = st.number_input("Store Footprint (m²)", value=167.0, step=1.0)
    managing_agent = st.text_input("Managing Agent / Landlord", value="Redefine Properties / Abcon")
    
    st.subheader("3. Comprehensive Lease & Financial Proposal Details")
    col1, col2 = st.columns(2)
    with col1:
        base_net_rental = st.number_input("Base Net Rental Rate (R/m²)", value=350.0, step=10.0)
        annual_escalation = st.number_input("Annual Rental Escalation (%)", value=7.5, step=0.5)
        turnover_rental_pct = st.number_input("Turnover Rental Clause (%)", value=8.0, step=0.5)
    with col2:
        turnkey_capital = st.number_input("Turnkey Capital Outlay (R)", value=3100000.0, step=50000.0)
        beneficial_occupation_months = st.number_input("Beneficial Occupation (Months free)", value=2.0, step=0.5)
        lease_period_years = st.number_input("Initial Lease Period (Years)", value=5.0, step=1.0)

    submitted = st.form_submit_button("⚡ Generate & Sync Feasibility Pack")

if submitted:
    with st.spinner("Compiling Master Feasibility PDF Pack..."):
        # Compile input dictionary containing all detailed lease terms for verification
        feasibility_data = {
            "client_name": recipient_email.split('@')[0].title(),
            "recipient_email": recipient_email,
            "recipient_mobile": recipient_mobile,
            "location_name": location_name,
            "store_footprint": store_footprint,
            "base_net_rental": base_net_rental,
            "annual_escalation": annual_escalation,
            "turnover_rental_pct": turnover_rental_pct,
            "turnkey_capital": turnkey_capital,
            "beneficial_occupation_months": beneficial_occupation_months,
            "lease_period_years": lease_period_years,
            "managing_agent": managing_agent
        }
        
        # Load blueprint images if available in assets
        blueprint_images = []
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        if os.path.exists(assets_dir):
            for f in os.listdir(assets_dir):
                if f.lower().endswith(('.png', '.jpg', '.jpeg')) and f != "Cover.JPG":
                    from PIL import Image
                    img_path = os.path.join(assets_dir, f)
                    try:
                        im = Image.open(img_path)
                        blueprint_images.append((f, im))
                    except Exception:
                        pass

        # Generate PDF bytes
        pdf_bytes = generate_feasibility_pdf(feasibility_data, blueprint_images)

    st.success("PDF Generated Successfully!")
    
    # Direct Download Option
    st.download_button(
        label="📥 Download PDF Direct",
        data=pdf_bytes,
        file_name=f"Phatbuns_{location_name.replace(' ', '_')}_Feasibility_Report.pdf",
        mime="application/pdf"
    )

    # Sync to Google Drive
    with st.spinner("Synchronizing to Google Drive..."):
        success_drive, drive_msg = sync_file_to_drive(pdf_bytes, location_name)
        if success_drive:
            st.success(f"Google Drive Sync: {drive_msg}")
        else:
            st.warning(f"Drive Sync Notice: {drive_msg}")

    # Dispatch Email
    with st.spinner("Dispatching Executive Email Pack..."):
        success_email, email_msg = send_feasibility_email(
            recipient_email, 
            feasibility_data["client_name"], 
            pdf_bytes, 
            location_name
        )
        if success_email:
            st.success(f"Email successfully dispatched to {recipient_email}!")
        else:
            st.error(f"Email Error: {email_msg}")
