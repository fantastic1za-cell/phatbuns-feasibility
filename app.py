import streamlit as st
from pdf_engine import generate_feasibility_pdf
from parser import parse_uploaded_offer_image
from services import sync_file_to_drive, send_feasibility_email

st.set_page_config(page_title="Phatbuns SA Feasibility Engine", layout="centered")

st.title("Phatbuns SA — Master Feasibility Engine")

# Pre-populate Session State defaults
if "location_name" not in st.session_state:
    st.session_state["location_name"] = "New Corner Northcliff (Shop RL 03)"
if "shop_code" not in st.session_state:
    st.session_state["shop_code"] = "Shop RL 03"
if "sqm" not in st.session_state:
    st.session_state["sqm"] = 80.0
if "rental_rate" not in st.session_state:
    st.session_state["rental_rate"] = 220.0

# 1. Offer Upload & Extraction Section
st.subheader("Upload Landlord Lease Offer / Screenshot")
uploaded_file = st.file_uploader("Upload Proposal Image", type=["jpg", "jpeg", "png"])

if st.button("⚡ Extract & Pre-Fill Lease Terms"):
    if uploaded_file:
        parsed_info = parse_uploaded_offer_image(uploaded_file)
        st.session_state["location_name"] = parsed_info.get("location_name", "New Corner Northcliff")
        st.session_state["shop_code"] = parsed_info.get("shop_code", "Shop RL 03")
        st.session_state["sqm"] = parsed_info.get("sqm", 80.0)
        st.session_state["rental_rate"] = parsed_info.get("rental_rate", 220.0)
        
        st.success("Proposal successfully parsed! Site parameters auto-populated.")
        st.rerun()

st.markdown("---")

# 2. Site Specifications Section
st.header("1. Site & Lease Specification & Catchment Intelligence")

locations_list = [
    st.session_state["location_name"],
    "Clearwater Mall (Food Court)",
    "Horizon Shopping Centre",
    "Kwena Square",
    "The Glen Mall"
]

selected_location = st.selectbox("Select Commercial Location", locations_list, index=0)
shop_code = st.text_input("Shop / Unit Code", value=st.session_state["shop_code"])
sqm_val = st.number_input("Demised Premises Size (sqm)", value=float(st.session_state["sqm"]))
rental_val = st.number_input("Base Rental Rate (R/sqm Excl. VAT)", value=float(st.session_state["rental_rate"]))

st.info("🌐 Catchment Intelligence (10 km Radius): Estimated 160k-210k monthly footfall | LSM 8-10+ High Disposable Income Corridor | Active Households: ~120,000.")

st.markdown("---")

# 3. Applicant & Dispatch Inputs
st.header("3. Dispatch Completed Site Feasibility Pack")

client_name = st.text_input("Prospective Franchisee Full Name", value="Nisaar Ally")
client_email = st.text_input("Prospective Franchisee Email Address", value="nisaar@fantastic1.com")
client_mobile = st.text_input("Prospective Franchisee Mobile / WhatsApp Number", value="0827867712")

# Construct consolidated data dictionary
form_data = {
    "location_name": selected_location,
    "shop_code": shop_code,
    "client_name": client_name,
    "store_type": "Express Inline Model",
    "sqm": sqm_val,
    "rental_rate": rental_val,
    "fitout_cost": 850000.0,
    "equipment_cost": 650000.0,
    "pos_signage": 120000.0,
    "working_capital": 150000.0,
    "opening_stock": 80000.0
}

# PDF Generation and Sync Execution
try:
    pdf_bytes = generate_feasibility_pdf(form_data)
    
    # Execute Auto Sync
    sync_status, sync_msg = sync_file_to_drive(pdf_bytes, selected_location)
    if sync_status:
        st.info(f"Automated Directory Saved: {sync_msg}")
    
    # Direct Download Option
    st.download_button(
        label="📥 Download PDF Direct",
        data=pdf_bytes,
        file_name=f"Phatbuns_{selected_location.replace(' ', '_')}_Investor_Pack.pdf",
        mime="application/pdf"
    )

    # Email Dispatch Option
    if st.button("✉️ Dispatch via Email (with Read Receipt)"):
        email_status, email_msg = send_feasibility_email(client_email, client_name, pdf_bytes, selected_location)
        if email_status:
            st.success(email_msg)
        else:
            st.error(email_msg)

except Exception as e:
    st.error(f"Execution Error: {str(e)}")
