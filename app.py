import streamlit as st
import os

# Fail-safe module imports
try:
    from proposals import parse_landlord_proposal, process_blueprint_files
    from services import sync_file_to_drive, send_feasibility_email
    from pdf_engine import generate_feasibility_pdf
    MODULES_LOADED = True
except ImportError as e:
    MODULES_LOADED = False
    IMPORT_ERROR = str(e)

st.set_page_config(
    page_title="Phatbuns Franchise Feasibility Engine",
    page_icon="🍔",
    layout="centered"
)

def main():
    st.title("🍔 Phatbuns Franchise Feasibility Engine")
    st.markdown("### Enterprise-Grade Automated Proposal & Feasibility Pack Generator")
    
    if not MODULES_LOADED:
        st.error(f"System Warning: Module import error detected ({IMPORT_ERROR}). Running in baseline fallback mode.")

    # Initialize Session State for form persistence
    if "form_data" not in st.session_state:
        st.session_state.form_data = {
            "location_name": "New Corner Northcliff (Shop RL 03)",
            "store_footprint": 167.0,
            "base_net_rental": 350.0,
            "turnkey_capital": 3100000.0,
            "managing_agent": "Redefine Properties / Abcon",
            "client_name": "",
            "client_email": "",
            "client_mobile": ""
        }

    with st.expander("📥 1. Ingest Landlord Proposal / Legacy Pack", expanded=True):
        uploaded_proposal = st.file_uploader(
            "Upload Landlord Proposal, Lease Agreement, or Feasibility PDF",
            type=["pdf", "png", "jpg", "jpeg"]
        )
        
        if uploaded_proposal:
            if st.button("⚡ Extract & Parse Proposal Data"):
                with st.spinner("Extracting parameters from document..."):
                    parsed_data = parse_landlord_proposal(uploaded_proposal)
                    st.session_state.form_data.update({
                        "location_name": parsed_data.get("location_name", st.session_state.form_data["location_name"]),
                        "store_footprint": parsed_data.get("store_footprint", st.session_state.form_data["store_footprint"]),
                        "base_net_rental": parsed_data.get("base_net_rental", st.session_state.form_data["base_net_rental"]),
                        "turnkey_capital": parsed_data.get("turnkey_capital", st.session_state.form_data["turnkey_capital"]),
                        "managing_agent": parsed_data.get("managing_agent", st.session_state.form_data["managing_agent"])
                    })
                st.success("Proposal parameters extracted and loaded successfully!")

    with st.expander("📐 2. Upload Store Blueprints & Mall Layout Plans"):
        uploaded_blueprints = st.file_uploader(
            "Upload Blueprints / Mall Plans (Multi-format: PDF, PNG, JPG)",
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True
        )

    with st.form("feasibility_form"):
        st.markdown("### 📋 3. Dispatch & Site Feasibility Parameters")
        
        client_name = st.text_input("Prospective Franchisee Full Name", value=st.session_state.form_data.get("client_name", ""))
        client_email = st.text_input("Prospective Franchisee Email", value=st.session_state.form_data.get("client_email", ""))
        client_mobile = st.text_input("Prospective Franchisee Mobile / WhatsApp", value=st.session_state.form_data.get("client_mobile", ""))
        
        st.markdown("---")
        location_name = st.text_input("Location Name / Node", value=st.session_state.form_data["location_name"])
        store_footprint = st.number_input("Store Footprint (m²)", value=float(st.session_state.form_data["store_footprint"]))
        base_net_rental = st.number_input("Base Net Rental Rate (R/m²)", value=float(st.session_state.form_data["base_net_rental"]))
        turnkey_capital = st.number_input("Turnkey Capital Outlay (R)", value=float(st.session_state.form_data["turnkey_capital"]))
        managing_agent = st.text_input("Managing Agent / Landlord", value=st.session_state.form_data["managing_agent"])
        
        submitted = st.form_submit_button("⚡ Generate & Sync Feasibility Pack")

    if submitted:
        # Save session inputs
        st.session_state.form_data.update({
            "location_name": location_name,
            "store_footprint": store_footprint,
            "base_net_rental": base_net_rental,
            "turnkey_capital": turnkey_capital,
            "managing_agent": managing_agent,
            "client_name": client_name,
            "client_email": client_email,
            "client_mobile": client_mobile
        })

        with st.spinner("Compiling enterprise-grade 8-page investment pack..."):
            # Process uploaded blueprints if available
            blueprint_images = process_blueprint_files(uploaded_blueprints) if 'uploaded_blueprints' in locals() else []
            
            # Generate PDF bytes
            pdf_bytes = generate_feasibility_pdf(st.session_state.form_data, blueprint_images)
            
            # Sync to Google Drive
            sync_status = "Drive API Inactive"
            if MODULES_LOADED:
                # Create a pseudo file object for Drive upload
                class BytesFileWrapper:
                    def __init__(self, content, name):
                        self.content = content
                        self.name = name
                    def getvalue(self):
                        return self.content
                
                report_file = BytesFileWrapper(pdf_bytes, f"Phatbuns_{location_name.replace(' ', '_')}_Feasibility_Report.pdf")
                success, msg = sync_file_to_drive(report_file, location_name)
                sync_status = msg if success else f"({msg})"

                # Also sync uploaded proposals/blueprints if any
                if uploaded_proposal:
                    sync_file_to_drive(uploaded_proposal, location_name)
                if 'uploaded_blueprints' in locals() and uploaded_blueprints:
                    for bp in uploaded_blueprints:
                        sync_file_to_drive(bp, location_name)

        st.success(f"PDF Generated Successfully! | {sync_status}")

        # Download button for immediate local access
        st.download_button(
            label="📥 Download PDF Direct",
            data=pdf_bytes,
            file_name=f"Phatbuns_{location_name.replace(' ', '_')}_Feasibility_Report.pdf",
            mime="application/pdf"
        )

        # Email dispatch if client email is provided
        if client_email and MODULES_LOADED:
            with st.spinner(f"Dispatched email report to {client_email}..."):
                email_success, email_msg = send_feasibility_email(client_email, client_name or "Valued Partner", pdf_bytes, location_name)
                if email_success:
                    st.success(f"Email successfully dispatched to {client_email}!")
                else:
                    st.warning(f"PDF generated and synced, but email dispatch failed: {email_msg}")

if __name__ == "__main__":
    main()
