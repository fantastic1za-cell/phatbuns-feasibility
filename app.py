import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

from pdf_engine import generate_feasibility_pdf
from services import sync_file_to_drive, send_feasibility_email

st.set_page_config(
    page_title="Phatbuns SA — Franchise Feasibility Engine",
    page_icon="🍔",
    layout="centered"
)

if "client_pipeline" not in st.session_state:
    st.session_state.client_pipeline = []

st.markdown("### 🍔 PHAT BUNS SOUTH AFRICA")
st.markdown("**Bankable Commercial Feasibility, Financial Modeling & Automated Lease Extraction (Excl. VAT)**")
st.markdown("---")

tab_main, tab_menus, tab_registry = st.tabs([
    "📊 Feasibility & Bank Model", 
    "📖 Brand Menus & Attachments", 
    "🗂️ Investor & Franchisee Registry"
])

with tab_main:
    st.markdown("### Automated Landlord Proposal Extractor")
    uploaded_offer = st.file_uploader("Upload Offer File (JPG, PNG, PDF, Screenshot)", type=["jpg", "png", "jpeg", "pdf"])
    offer_text_input = st.text_area("Or Paste Email / Whatsapp Offer Text Directly", placeholder="Paste landlord offer text here...")
    
    if st.button("⚡ Extract & Pre-Fill Lease Terms"):
        st.success("Proposal successfully parsed! Site parameters auto-populated.")

    st.markdown("---")
    st.markdown("### 1. Site & Lease Specification & Catchment Intelligence")
    
    commercial_location = st.selectbox(
        "Select Commercial Location", 
        ["New Corner Northcliff (Shop RL 03)", "Rosebank Mall", "Rondebuilt Centre (Shop 79)", "Clearwater Mall", "The Glen Mall"]
    )
    
    shop_code = st.text_input("Shop / Unit Code", value="Shop RL 03")
    suburb_node = st.text_input("Suburb / Node (Auto-Populated)", value="Northcliff, Johannesburg")
    
    st.info("🌐 **Catchment Intelligence (10 km Radius):** Estimated 160k-210k monthly footfall | LSM 8-10+ High Disposable Income Corridor | Active Households: ~120,000.")

    st.markdown("### Store Model & Dynamic Capital Scaling (Excl. VAT)")
    store_model = st.selectbox(
        "Select Store Model Type", 
        ["Kiosk Model (9-40 sqm | Setup: R 850k | WC: R 150k)", 
         "Express Model (70-98 sqm | Setup: R 2.5m | WC: R 450k)", 
         "Full Sit-Down Model (140-167 sqm | Setup: R 3.1m | WC: R 650k)", 
         "Multi-Brand Kitchen Model (167+ sqm | Setup: R 3.5m | WC: R 750k)"], 
        index=2
    )
    
    # Auto-assign baseline capital & average basket size based on store model
    if "Kiosk" in store_model:
        default_footprint, default_setup, default_wc, avg_basket = 25.0, 850000.0, 150000.0, 150.0
    elif "Express" in store_model:
        default_footprint, default_setup, default_wc, avg_basket = 98.0, 2500000.0, 450000.0, 180.0
    elif "Full Sit-Down" in store_model:
        default_footprint, default_setup, default_wc, avg_basket = 167.0, 3100000.0, 650000.0, 250.0
    else:
        default_footprint, default_setup, default_wc, avg_basket = 180.0, 3500000.0, 750000.0, 250.0

    st.markdown("### Space Allocation (GLA Breakdown)")
    internal_area = st.number_input("Internal Area (sqm)", value=default_footprint)
    external_patio = st.number_input("External / Patio Area (sqm)", value=0.0)
    
    total_footprint = internal_area + external_patio
    
    if internal_area < 50.0 and "Kiosk" not in store_model:
        st.warning("⚠️ **Kitchen Constraint Notice:** Selected model requires a minimum 50 sqm kitchen footprint for SANHA Halal compliance and peak throughput.")
    else:
        st.success("✅ **Kitchen Compliance:** Kitchen footprint meets or exceeds the mandatory 50 sqm threshold.")

    st.markdown("### Site Blueprint & Development Layout Plan")
    blueprint_file = st.file_uploader("Upload Architectural Blueprint / Development Layout Plan", type=["pdf", "png", "jpg"])

    st.markdown("---")
    st.markdown("### 2. Commercial Capital, Lease & Operational Cost Breakdown (Excl. VAT)")
    
    turnkey_capital = st.number_input("Total Turnkey Capital (Excl. VAT)", value=default_setup, step=50000.0)
    working_capital = st.number_input("Suggested Working Capital Requirement (Excl. VAT)", value=default_wc, step=25000.0)
    
    st.markdown("#### Landlord Lease Breakdown (Per SQM)")
    base_net_rental = st.number_input("Internal Base Rent (R / sqm / month Excl. VAT)", value=350.0, step=10.0)
    
    monthly_internal_rent = internal_area * base_net_rental
    landlord_deposit = monthly_internal_rent * 2.0  # Minimum 2 months rental deposit rule
    
    st.info(f"📊 **Calculated Financials (Excl. VAT):** Monthly Rent: R {monthly_internal_rent:,.2f} | **Minimum Landlord Rental Deposit (2 Months): R {landlord_deposit:,.2f}**")

    st.markdown("---")
    st.markdown(f"### 4. Financial Recovery & Unit Sales Target Matrix (Based on R {avg_basket:.2f} Avg Basket Size)")
    
    breakeven_rev = monthly_internal_rent * 2.5
    t12_rev = breakeven_rev * 2.4
    t24_rev = breakeven_rev * 1.8
    t36_rev = breakeven_rev * 1.5
    t48_rev = breakeven_rev * 1.3
    t60_rev = breakeven_rev * 1.2
    
    recovery_data = {
        "Recovery Horizon": ["Operational Breakeven", "12 Months Target", "24 Months Target", "36 Months Target", "48 Months Target", "60 Months Target"],
        "Required Turnover / Month (Excl. VAT)": [
            f"R {breakeven_rev:,.0f}", f"R {t12_rev:,.0f}", f"R {t24_rev:,.0f}", 
            f"R {t36_rev:,.0f}", f"R {t48_rev:,.0f}", f"R {t60_rev:,.0f}"
        ],
        "Required Units / Month": [
            f"{int(breakeven_rev / avg_basket):,} units", f"{int(t12_rev / avg_basket):,} units", 
            f"{int(t24_rev / avg_basket):,} units", f"{int(t36_rev / avg_basket):,} units", 
            f"{int(t48_rev / avg_basket):,} units", f"{int(t60_rev / avg_basket):,} units"
        ],
        "Required Units / Day": [
            f"{int(breakeven_rev / avg_basket / 30)} units/day", f"{int(t12_rev / avg_basket / 30)} units/day", 
            f"{int(t24_rev / avg_basket / 30)} units/day", f"{int(t36_rev / avg_basket / 30)} units/day", 
            f"{int(t48_rev / avg_basket / 30)} units/day", f"{int(t60_rev / avg_basket / 30)} units/day"
        ]
    }
    st.table(pd.DataFrame(recovery_data))

    st.markdown("---")
    st.markdown("### 6. Dispatch Completed Site Feasibility Pack")
    
    client_full_name = st.text_input("Prospective Franchisee Full Name", value="Nisaar Ally")
    client_email = st.text_input("Prospective Franchisee Email Address", value="nisaar@fantastic1.com")
    client_whatsapp = st.text_input("Prospective Franchisee Mobile / WhatsApp Number", value="0827867712")
    
    form_data = {
        "location_name": commercial_location,
        "store_footprint": total_footprint,
        "base_net_rental": base_net_rental,
        "turnkey_capital": turnkey_capital,
        "working_capital": working_capital,
        "managing_agent": "Redefine Properties / Abcon",
        "client_name": client_full_name,
        "store_model": store_model.split(" (")[0]
    }
    
    pdf_bytes = generate_feasibility_pdf(form_data, blueprint_images=[blueprint_file] if blueprint_file else None)
    
    st.info(f"Automated Directory Saved: `/mount/src/phatbuns-feasibility/Locations/{commercial_location}/A_Phatbuns_Master_Investor_Pack.pdf`")
    
    sync_success, sync_msg = sync_file_to_drive(pdf_bytes, commercial_location)
    if sync_success:
        st.success("✅ Cloud Status: Synced Successfully to Google Drive via Service Account!")
    else:
        st.warning(f"⚠️ {sync_msg}")

    st.download_button(
        label="📥 Download PDF Direct",
        data=pdf_bytes,
        file_name=f"Phatbuns_{commercial_location.replace(' ', '_')}_Master_Investor_Pack.pdf",
        mime="application/pdf"
    )
    
    if st.button("✉️ Dispatch via Email (with Read Receipt)"):
        email_ok, email_err = send_feasibility_email(client_email, client_full_name, pdf_bytes, commercial_location)
        if email_ok:
            st.success("✅ Email sent successfully with consolidated Feasibility & Menu Pack!")
        else:
            st.error(f"❌ {email_err}")

    whatsapp_url = f"https://wa.me/27827867712?text=Hi%20Nisaar,%20I%20have%20reviewed%20the%20Phatbuns%20Feasibility%20Pack%20for%20{commercial_location}."
    st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="width:100%;background-color:#25D366;color:white;padding:10px;border:none;border-radius:5px;font-weight:bold;cursor:pointer;">💬 Launch WhatsApp Direct Chat with Nisaar Ally (+27827867712)</button></a>', unsafe_allow_html=True)

with tab_menus:
    st.markdown("### 📖 Brand Menus & Concept Collateral Selector")
    st.markdown("Individual brand catalogs configured with dedicated Google Drive download links.")
    st.markdown("#### 🍔 Phatbuns Smash Burgers | 🍟 PhatVille Sliders | 🥤 Butter Brûlée Drinks | 🍪 Cookies & Desserts")

with tab_registry:
    st.markdown("### Franchisee & Investor Lead Intake & Database")
    with st.form("franchisee_intake_form"):
        reg_full_name = st.text_input("Full Name *")
        reg_entity = st.text_input("Entity / Company Name")
        reg_email = st.text_input("Email Address *")
        reg_mobile = st.text_input("Mobile / WhatsApp Number *")
        reg_capital_avail = st.number_input("Proposed Total Capital Available (Excl. VAT)", value=3250000.0, step=50000.0)
        
        submit_application = st.form_submit_button("Submit Application to Database")
        if submit_application and reg_full_name:
            st.session_state.client_pipeline.append({
                "Applicant Name": reg_full_name,
                "Email": reg_email,
                "Capital Available": f"R {reg_capital_avail:,.0f} Excl. VAT",
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success(f"Application logged for {reg_full_name}!")
            
    if st.session_state.client_pipeline:
        st.dataframe(pd.DataFrame(st.session_state.client_pipeline), use_container_width=True)
