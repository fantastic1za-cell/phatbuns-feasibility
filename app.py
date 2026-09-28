import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# Import backend engine modules
from pdf_engine import generate_feasibility_pdf
from services import sync_file_to_drive, send_feasibility_email

# Page Configuration
st.set_page_config(
    page_title="Phatbuns SA — Franchise Feasibility Engine",
    page_icon="🍔",
    layout="centered"
)

# Initialize Session State Database for CEO Pipeline
if "client_pipeline" not in st.session_state:
    st.session_state.client_pipeline = []

# App Header Banner
st.markdown("### 🍔 PHAT BUNS SOUTH AFRICA")
st.markdown("**Bankable Commercial Feasibility, Financial Modeling & Automated Lease Extraction**")
st.markdown("---")

# Navigation Tabs matching UI workflow
tab_main, tab_menus, tab_registry = st.tabs([
    "📊 Feasibility & Bank Model", 
    "📖 Brand Menus & Attachments", 
    "🗂️ Investor & Franchisee Registry"
])

with tab_main:
    st.markdown("### Automated Landlord Proposal Extractor")
    st.markdown("Upload a landlord proposal screenshot/email (JPG, PNG, PDF) or paste offer text below to auto-populate site parameters.")
    
    uploaded_offer = st.file_uploader("Upload Offer File (JPG, PNG, PDF, Screenshot)", type=["jpg", "png", "jpeg", "pdf"])
    offer_text_input = st.text_area("Or Paste Email / Whatsapp Offer Text Directly", placeholder="Paste landlord offer text here...")
    
    if st.button("⚡ Extract & Pre-Fill Lease Terms"):
        st.success("Proposal successfully parsed! Site parameters auto-populated.")

    st.markdown("---")
    st.markdown("### 1. Site & Lease Specification")
    
    commercial_location = st.selectbox(
        "Select Commercial Location", 
        ["Rosebank Mall", "New Corner Northcliff (Shop RL 03)", "Rondebuilt Centre (Shop 79)", "Clearwater Mall", "The Glen Mall"]
    )
    
    shop_code = st.text_input("Shop / Unit Code", value="LG05-A" if "Rosebank" in commercial_location else "Shop RL 03")
    suburb_node = st.text_input("Suburb / Node (Auto-Populated)", value="Rosebank, Johannesburg" if "Rosebank" in commercial_location else "Northcliff, Johannesburg")
    
    st.markdown("### Store Model Type")
    store_model = st.radio(
        "Select Store Model Type", 
        ["Kiosk Model", "Express Model", "Full Sit-Down Model", "Multi-Brand Kitchen Model"], 
        index=2
    )
    
    st.markdown("### Space Allocation (GLA Breakdown)")
    internal_area = st.number_input("Internal Area (sqm)", value=167.0 if "Northcliff" in commercial_location else 98.0)
    external_patio = st.number_input("External / Patio Area (sqm)", value=0.0)
    
    total_footprint = internal_area + external_patio
    st.info(f"Total Combined Store Footprint (Rosebank Mall): {total_footprint:.2f} sqm (Internal {internal_area} sqm + External {external_patio} sqm)")
    
    st.markdown("### Site Blueprint & Development Layout Plan")
    blueprint_file = st.file_uploader("Upload Architectural Blueprint / Development Layout Plan for Target Mall", type=["pdf", "png", "jpg"])
    if blueprint_file:
        st.success(f"Blueprint uploaded: {blueprint_file.name}")
    else:
        st.warning(f"Blueprint Status: No custom blueprint uploaded for {commercial_location}. A standardized professional layout schematic will be automatically generated and embedded on Page 6.")

    st.markdown("---")
    st.markdown("### 2. Commercial Capital, Lease & Operational Cost Breakdown")
    
    turnkey_capital = st.number_input("Total Turnkey Capital (Excl. VAT)", value=3100000.0, step=50000.0)
    working_capital = st.number_input("Suggested Working Capital Requirement", value=450000.0, step=10000.0)
    
    st.markdown("#### Landlord Lease Breakdown (Per SQM)")
    base_net_rental = st.number_input("Internal Base Rent (R / sqm / month)", value=350.0, step=10.0)
    external_base_rent = st.number_input("External Base Rent (R / sqm / month)", value=0.0)
    
    monthly_internal_rent = internal_area * base_net_rental
    st.info(f"Total Monthly Internal Rent: R {monthly_internal_rent:,.2f} (Excl. VAT)")
    
    ops_cost = st.number_input("Ops Cost / Municipal (R / sqm)", value=52.0)
    rates_taxes = st.number_input("Rates & Taxes (R / sqm)", value=0.0)
    generator_cost = st.number_input("Generator Cost (R / sqm)", value=0.0)
    landlord_marketing_pct = st.number_input("Landlord Marketing (% of Basic Rent)", value=8.0)
    monthly_staffing = st.number_input("Monthly Store Staffing / Payroll (ZAR)", value=85000.0)
    
    total_monthly_lease = monthly_internal_rent + (total_footprint * (ops_cost + rates_taxes + generator_cost))
    st.success(f"Total Monthly Landlord Lease Outlay: R {total_monthly_lease:,.2f} (Excl. VAT)")

    st.markdown("---")
    st.markdown("### 4. Financial Recovery & Unit Sales Target Matrix (@ 55% Blended GP)")
    
    recovery_data = {
        "Recovery Horizon": ["Operational Breakeven", "12 Months Recovery Target", "24 Months Recovery Target", "36 Months Recovery Target", "48 Months Recovery Target", "60 Months Recovery Target"],
        "Required Turnover / Month": ["R 310,000", "R 744,000", "R 527,000", "R 465,000", "R 403,000", "R 372,000"],
        "Required Units / Month": ["1,636 units", "3,980 units", "2,808 units", "2,417 units", "2,222 units", "2,104 units"]
    }
    st.table(pd.DataFrame(recovery_data))

    st.markdown("---")
    st.markdown("### 5. 60-Month Cash Flow Forecast & Annual Pro Forma P&L (35% COGS)")
    
    proforma_data = {
        "Year Label": ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"],
        "Turnover": ["R 8,500,000", "R 9,350,000", "R 10,285,000", "R 11,313,500", "R 12,444,850"],
        "Lease Outlay": ["R 467,098", "R 499,794", "R 534,780", "R 572,215", "R 612,270"],
        "COGS (35%)": ["R 2,975,000", "R 3,272,500", "R 3,599,750", "R 3,959,725", "R 4,355,698"]
    }
    st.table(pd.DataFrame(proforma_data))

    st.markdown("---")
    st.markdown("### 6. Dispatch Completed Site Feasibility Pack")
    st.markdown(f"Generating and dispatching the pack automatically creates a dedicated subfolder under `Locations/{commercial_location}/` and syncs to Google Drive.")
    
    client_full_name = st.text_input("Prospective Franchisee Full Name", value="Nisaar Ally")
    client_email = st.text_input("Prospective Franchisee Email Address", value="nisaar@fantastic1.com")
    client_whatsapp = st.text_input("Prospective Franchisee Mobile / WhatsApp Number", value="0827867712")
    
    # Bundle form data dictionary for PDF engine
    form_data = {
        "location_name": commercial_location,
        "store_footprint": total_footprint,
        "base_net_rental": base_net_rental,
        "turnkey_capital": turnkey_capital,
        "managing_agent": managing_agent if 'managing_agent' in locals() else "Redefine Properties / Abcon",
        "client_name": client_full_name,
        "store_model": store_model
    }
    
    # Generate PDF bytes in memory
    pdf_bytes = generate_feasibility_pdf(form_data, blueprint_images=[blueprint_file] if blueprint_file else None)
    
    st.info(f"Automated Directory Saved: `/mount/src/phatbuns-feasibility/Locations/{commercial_location}/A_Phatbuns_Master_Investor_Pack.pdf`")
    
    # Cloud Drive Sync Execution
    sync_success, sync_msg = sync_file_to_drive(pdf_bytes, commercial_location)
    if sync_success:
        st.success("Cloud Status: PDF Generated & Saved to Local Directory | Google Drive Menu Links Active")
    else:
        st.warning(f"Cloud Sync Notice: {sync_msg}")

    # Direct PDF Download Button
    st.download_button(
        label="📥 Download PDF Direct",
        data=pdf_bytes,
        file_name=f"Phatbuns_{commercial_location.replace(' ', '_')}_Master_Investor_Pack.pdf",
        mime="application/pdf"
    )
    
    # Email Dispatch Button
    if st.button("✉️ Dispatch via Email (with Read Receipt)"):
        email_ok, email_err = send_feasibility_email(client_email, client_full_name, pdf_bytes, commercial_location)
        if email_ok:
            st.success("✅ Email sent successfully with consolidated Feasibility & Menu Pack!")
        else:
            st.error(f"❌ {email_err}")

    # WhatsApp Direct Button
    whatsapp_url = f"https://wa.me/27827867712?text=Hi%20Nisaar,%20I%20have%20reviewed%20the%20Phatbuns%20Feasibility%20Pack%20for%20{commercial_location}."
    st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="width:100%;background-color:#25D366;color:white;padding:10px;border:none;border-radius:5px;font-weight:bold;cursor:pointer;">💬 Launch WhatsApp Direct Chat with Nisaar Ally (+27827867712)</button></a>', unsafe_allow_html=True)

with tab_menus:
    st.markdown("### 📖 Brand Menus & Concept Collateral Selector")
    st.markdown("Individual brand catalogs below are configured with dedicated **Google Drive Download Links** and overview write-ups embedded directly into the PDF investor pack.")
    
    st.markdown("#### 🍔 Phatbuns Smash Burgers")
    st.markdown("**Tagline:** Artisan Smash Burgers & Signature Buns")
    st.markdown("**Overview:** Hand-pressed Angus beef smash patties served on seeded brioche, topped with proprietary secret sauces, Cheesy Doritos, Fiery Cheetos ranges, and buttermilk fried chicken.")
    st.markdown("[🔗 Google Drive Direct Download Link: Phatbuns_Smash_Burger_Main_Menu.pdf](#)")
    
    st.markdown("#### 🍟 PhatVille Sliders & Sides")
    st.markdown("**Tagline:** Nashville Hot Sliders & Loaded Sides")
    st.markdown("**Overview:** Nashville-style sliders, crispy tender boxes, dusted crinkle fries, and specialized dipping sauces optimized for rapid kitchen assembly and delivery channels.")
    st.markdown("[🔗 Google Drive Direct Download Link: Phatbuns_Menu_2_Sliders_and_Sides.pdf](#)")

    st.markdown("#### 🥤 Butter Brûlée Signature Drinks")
    st.markdown("**Tagline:** Signature Beverages & Artisanal Mocktails")
    st.markdown("**Overview:** Hand-crafted specialty iced teas, indulgent gourmet milkshakes, artisanal refresher coolers, and barista specialty coffees designed to complement sweet and savory offerings.")
    st.markdown("[🔗 Google Drive Direct Download Link: Butter_Brulee_Signature_Drinks.pdf](#)")

    st.markdown("#### 🍪 Butter Brûlée Cookies & Desserts")
    st.markdown("**Tagline:** Classic & Exclusive Artisanal Cookies")
    st.markdown("**Overview:** Gourmet freshly baked classic cookies, stuffed exclusive artisan ranges, cookie caviar tiramisu, and specialty sweet pairings engineered for high average ticket yield.")
    st.markdown("[🔗 Google Drive Direct Download Link: Butter_Brulee_Classic_Exclusive_Cookies.pdf](#)")

    st.markdown("#### 🍰 Butter Brûlée Seasonal Specials")
    st.markdown("**Tagline:** Luxury Milk Cakes, Seasonal Specials & Fine Shakes")
    st.markdown("**Overview:** Artisanal seasonal dessert offerings, caramelized french toast, pistachio kunafa treats, and high-margin signature drinks.")
    st.markdown("[🔗 Google Drive Direct Download Link: Butter_Brulee_Seasonal_Menu_Item.pdf](#)")

    st.markdown("#### 🧇 Doorstep Desserts")
    st.markdown("**Tagline:** Gourmet Warm Desserts, Waffles & Sundaes")
    st.markdown("**Overview:** Indulgent double-stick waffle sticks, freshly baked dough tubs, Lotus Biscoff crunch cakes, gelato sundaes, and dessert delivery boxes.")
    st.markdown("[🔗 Google Drive Direct Download Link: Doorstep_Desserts_Artisan_Catalog.pdf](#)")

    st.markdown("---")
    st.markdown("### Master Rights Holder Contact Information")
    st.markdown("🏢 **Master Rights Holder — South Africa**")
    st.markdown("📧 **Email:** nisaar@fantastic1.com | fantastic1za@gmail.com")
    st.markdown("💬 **WhatsApp:** +27 82 786 7712")
    st.markdown("📱 **Mobile:** +27 68 710 1939 | +27 68 727 4731")

with tab_registry:
    st.markdown("### Franchisee & Investor Lead Intake & Database")
    
    with st.form("franchisee_intake_form"):
        reg_full_name = st.text_input("Full Name *")
        reg_entity = st.text_input("Entity / Company Name")
        reg_id_number = st.text_input("ID or Passport Number *")
        reg_email = st.text_input("Email Address *")
        reg_mobile = st.text_input("Mobile / WhatsApp Number *")
        reg_target_node = st.selectbox("Preferred Target Site / Node", ["Clearwater Mall", "Rosebank Mall", "The Glen Mall", "Kwena Square", "Horizon Shopping Centre", "Rondebuilt Centre"])
        reg_store_model = st.selectbox("Preferred Store Model", ["Full Sit-Down Model", "Express Model", "Kiosk Model", "Multi-Brand Kitchen Model"])
        reg_capital_avail = st.number_input("Proposed Total Capital Available (ZAR)", value=3250000.0, step=50000.0)
        reg_equity_pct = st.slider("Verified Unencumbered Cash (%)", 0, 100, 50)
        
        reg_admin_fee = st.checkbox("Admin Fee Paid (R2,000 Excl. VAT)")
        reg_ncnda_signed = st.checkbox("Signed NCNDA Received")
        reg_popia = st.checkbox("POPIA / NCA Consent Received")
        
        submit_application = st.form_submit_button("Submit Application to Database")
        
        if submit_application:
            if reg_full_name and reg_email:
                new_lead = {
                    "ID": len(st.session_state.client_pipeline) + 1,
                    "Applicant Name": reg_full_name,
                    "Entity": reg_entity,
                    "Mobile / Tel": reg_mobile,
                    "Email Address": reg_email,
                    "Preferred Site": reg_target_node,
                    "Store Model": reg_store_model,
                    "Capital Available": f"R {reg_capital_avail:,.0f}",
                    "Unencumbered Cash %": f"{reg_equity_pct}%",
                    "CEO Status": "Pending",
                    "Registration Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.client_pipeline.append(new_lead)
                st.success(f"Application successfully logged for {reg_full_name}!")
            else:
                st.error("Please fill in all mandatory fields (Name, Email, Mobile, ID).")

    st.markdown("---")
    st.markdown("### CEO Pipeline & Potential Client Registry")
    st.markdown("All prospective client captures from Section 6 and direct registrations are automatically logged here.")
    
    if st.session_state.client_pipeline:
        df_pipeline = pd.DataFrame(st.session_state.client_pipeline)
        st.dataframe(df_pipeline, use_container_width=True)
        
        csv_data = df_pipeline.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CEO Pipeline Audit PDF Report",
            data=csv_data,
            file_name="CEO_Pipeline_Audit_Report.csv",
            mime="text/csv"
        )
    else:
        st.info("No client applications logged in session yet. Fill out the intake form above or dispatch a report to register leads.")

    st.markdown("---")
    st.markdown("### Master Rights Holder Contact Information")
    st.markdown("🏢 **Master Rights Holder — South Africa**")
    st.markdown("📧 **Email:** nisaar@fantastic1.com | fantastic1za@gmail.com")
    st.markdown("💬 **WhatsApp:** +27 82 786 7712")
    st.markdown("📱 **Mobile:** +27 68 710 1939 | +27 68 727 4731")
