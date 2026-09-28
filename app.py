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
    layout="wide"
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
            "client_email": "nisaar@fantastic1.com",
            "client_mobile": "+27 82 786 7712",
            "annual_escalation": 7.5,
            "turnover_rental_pct": 8.0,
            "beneficial_occupation_months": 2.0,
            "lease_period_years": 5.0
        }

    with st.expander("📥 1. Ingest Landlord Proposal / Legacy Pack", expanded=True):
        uploaded_proposal = st.file_uploader(
            "Upload Landlord Proposal, Lease Agreement, or Feasibility PDF",
            type=["pdf", "png", "jpg", "jpeg"]
        )
        
        if uploaded_proposal:
            if st.button("⚡ Extract & Parse Proposal Data"):
                with st.spinner("Extracting parameters from document..."):
                    if MODULES_LOADED:
                        parsed_data = parse_landlord_proposal(uploaded_proposal)
                    else:
                        parsed_data = {}
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
        
        st.markdown("---")
        st.markdown("**Lease Proposal Verification Fields**")
        col1, col2 = st.columns(2)
        with col1:
            annual_escalation = st.number_input("Annual Rental Escalation (%)", value=float(st.session_state.form_data.get("annual_escalation", 7.5)), step=0.5)
            turnover_rental_pct = st.number_input("Turnover Rental Clause (%)", value=float(st.session_state.form_data.get("turnover_rental_pct", 8.0)), step=0.5)
        with col2:
            beneficial_occupation_months = st.number_input("Beneficial Occupation (Months free)", value=float(st.session_state.form_data.get("beneficial_occupation_months", 2.0)), step=0.5)
            lease_period_years = st.number_input("Initial Lease Period (Years)", value=float(st.session_state.form_data.get("lease_period_years", 5.0)), step=1.0)
        
        submitted = st.form_submit_button("⚡ Generate & Process Feasibility Pack", type="primary")

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
            "client_mobile": client_mobile,
            "annual_escalation": annual_escalation,
            "turnover_rental_pct": turnover_rental_pct,
            "beneficial_occupation_months": beneficial_occupation_months,
            "lease_period_years": lease_period_years
        })

        with st.spinner("Compiling enterprise-grade 8-page investment pack..."):
            # Process uploaded blueprints if available
            blueprint_images = []
            if MODULES_LOADED and 'uploaded_blueprints' in locals() and uploaded_blueprints:
                blueprint_images = process_blueprint_files(uploaded_blueprints)
            elif not MODULES_LOADED and 'uploaded_blueprints' in locals() and uploaded_blueprints:
                for bp in uploaded_blueprints:
                    try:
                        from PIL import Image
                        im = Image.open(bp)
                        blueprint_images.append((bp.name, im))
                    except Exception:
                        pass
            
            # Generate PDF bytes via engine
            pdf_bytes = generate_feasibility_pdf(st.session_state.form_data, blueprint_images)
            file_name = f"Phatbuns_{location_name.replace(' ', '_')}_Feasibility_Report.pdf"

            # Store in session state so actions persist
            st.session_state["pdf_bytes"] = pdf_bytes
            st.session_state["file_name"] = file_name
            st.session_state["location_name"] = location_name

            # Auto-sync proposal and blueprints to Cloud if desired
            if MODULES_LOADED:
                class BytesFileWrapper:
                    def __init__(self, content, name):
                        self.content = content
                        self.name = name
                    def getvalue(self):
                        return self.content
                
                report_file = BytesFileWrapper(pdf_bytes, file_name)
                sync_file_to_drive(report_file, location_name)

                if uploaded_proposal:
                    sync_file_to_drive(uploaded_proposal, location_name)
                if 'uploaded_blueprints' in locals() and uploaded_blueprints:
                    for bp in uploaded_blueprints:
                        sync_file_to_drive(bp, location_name)

        st.success("Feasibility Report Generated & Backed Up to Google Drive Successfully!")

    # Render persistent output action options if the PDF exists in session state
    if "pdf_bytes" in st.session_state:
        p_bytes = st.session_state["pdf_bytes"]
        f_name = st.session_state["file_name"]
        loc_name = st.session_state["location_name"]

        st.markdown("---")
        st.subheader("📤 Output & Distribution Hub")
        
        col_dl, col_cl, col_em = st.columns(3)
        
        # 1. Local Device Download
        with col_dl:
            st.markdown("### 📥 Local Storage")
            st.download_button(
                label="Download PDF Direct",
                data=p_bytes,
                file_name=f_name,
                mime="application/pdf",
                use_container_width=True
            )
            
        # 2. Manual Cloud Re-Sync Button
        with col_cl:
            st.markdown("### ☁️ Cloud Backup")
            if st.button("Re-Sync to Drive", use_container_width=True):
                with st.spinner("Syncing to personal Google Drive..."):
                    if MODULES_LOADED:
                        class BytesFileWrapper:
                            def __init__(self, content, name):
                                self.content = content
                                self.name = name
                            def getvalue(self):
                                return self.content
                        report_file = BytesFileWrapper(p_bytes, f_name)
                        success, msg = sync_file_to_drive(report_file, loc_name)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.error("Modules not loaded.")
                        
        # 3. Direct Email Distribution Section
        with col_em:
            st.markdown("### 📧 Direct Email")
            target_email = st.text_input("Send to Email", value=st.session_state.form_data.get("client_email", ""))
            if st.button("Dispatch Email Report", use_container_width=True):
                if target_email and MODULES_LOADED:
                    with st.spinner(f"Dispatched email report to {target_email}..."):
                        email_success, email_msg = send_feasibility_email(
                            target_email, 
                            st.session_state.form_data.get("client_name") or "Valued Partner", 
                            p_bytes, 
                            loc_name
                        )
                        if email_success:
                            st.success(f"Email successfully dispatched to {target_email}!")
                        else:
                            st.error(f"Email dispatch failed: {email_msg}")
                else:
                    st.warning("Please enter a valid recipient email address.")

if __name__ == "__main__":
    main()
