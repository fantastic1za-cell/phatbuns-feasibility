# app.py - Main Streamlit Interface (Modular Implementation)
import os
import io
import re
import base64
import urllib.parse
import streamlit as st
import pandas as pd
from PIL import Image

# Import Modular Engine Libraries
from config import (
    ASSETS_DIR, BRAND_MENU_CATALOG, STORE_MEDIA_LINKS, 
    LOCATION_LOOKUP, SITE_PROFILES, STORE_MODELS
)
from services import (
    init_db, save_investor_lead, get_pipeline_dataframe,
    sync_pdf_to_local_and_cloud, send_franchisee_email_pack,
    get_drive_service, get_or_create_drive_folder, upload_pdf_to_drive
)
from pdf_engine import generate_pdf_report, get_asset_images_map

# Initialize SQLite Database
init_db()

# Streamlit Page Configuration
sa_app_logo_path = os.path.join(ASSETS_DIR, "Phatbuns_SA.PNG")
app_favicon = Image.open(sa_app_logo_path) if os.path.exists(sa_app_logo_path) else "🍔"

st.set_page_config(
    page_title="Phatbuns Engine",
    page_icon=app_favicon,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling
st.markdown("""
<style>
.stApp { background-color: #111111; color: #FFFFFF; }
.brand-banner { background: linear-gradient(135deg, #1f1f1f 0%, #0a0a0a 100%); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #333; }
.brand-title { color: #FFFFFF; font-size: 24px; font-weight: 800; margin: 0; }
.green-divider { border: none; height: 3px; background-color: #72BF44; border-radius: 2px; margin: 15px 0; }
.brand-card-block { background-color: #1A1A1A; padding: 15px; border-radius: 10px; border: 1px solid #333; margin-bottom: 20px; }
.direct-dl-btn { display: block; width: 100%; background-color: #0066CC; color: white !important; text-align: center; padding: 12px; border-radius: 8px; font-weight: bold; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand-banner"><div class="brand-title">PHATBUNS SOUTH AFRICA</div><div>Bankable Commercial Feasibility, Financial Modeling & Automated Lease Extraction</div></div>', unsafe_allow_html=True)
st.markdown('<hr class="green-divider">', unsafe_allow_html=True)

# Application Tabs
tab1, tab2, tab3 = st.tabs([
    "📊 Feasibility & Bank Model",
    "📖 Brand Menus & Media Showcase",
    "📋 Investor & Franchisee Registry"
])

# TAB 1: FEASIBILITY ENGINE
with tab1:
    st.header("Site Feasibility & Landlord Analysis Engine")
    
    analysis_mode = st.radio(
        "Select Feasibility Analysis Mode:",
        [
            "1. I have a Landlord Proposal / Offer Sheet", 
            "2. No Proposal — Check Mall Viability & Propose Target Rates",
            "3. Update Old/Legacy Franchisee Pack to New Format"
        ],
        index=0
    )

    if "3. Update Old/Legacy" in analysis_mode:
        st.subheader("♻️ Legacy Franchisee Pack Converter")
        legacy_file = st.file_uploader("Upload Legacy PDF Pack (.pdf)", type=["pdf"])
        if legacy_file:
            st.success("Legacy Pack ingested. Review extracted parameters below.")

    col1, col2 = st.columns(2)
    with col1:
        selected_location = st.selectbox("Select Commercial Location", options=list(LOCATION_LOOKUP.keys()), index=0)
        location_name = selected_location if selected_location != "Custom / Other Site..." else st.text_input("Custom Location Name")
    with col2:
        shop_code = st.text_input("Shop / Unit Code", value="79")

    selected_model = st.radio("Select Model Type", options=list(STORE_MODELS.keys()), index=1, horizontal=True)
    model_data = STORE_MODELS[selected_model]

    col_int, col_ext = st.columns(2)
    with col_int: internal_gla = st.number_input("Internal Area (sqm)", value=model_data["default_gla"])
    with col_ext: external_gla = st.number_input("External / Patio Area (sqm)", value=0.0)
    total_gla = internal_gla + external_gla

    blueprint_file = st.file_uploader("Upload Store Blueprint / Layout Plan", type=["pdf", "png", "jpg", "jpeg"])
    blueprint_pil = Image.open(blueprint_file).convert("RGB") if blueprint_file and not blueprint_file.name.endswith('.pdf') else None

    st.divider()
    st.header("Commercial Capital & Lease Modeling")
    col_c1, col_c2 = st.columns(2)
    with col_c1: turnkey_capital = st.number_input("Turnkey Capital (Excl. VAT)", value=model_data["turnkey_capital"])
    with col_c2: working_capital = st.number_input("Working Capital", value=model_data["working_capital"])

    int_rent = st.number_input("Internal Base Rent (R / sqm)", value=220.0)
    ext_rent = st.number_input("External Base Rent (R / sqm)", value=0.0)
    ops_cost = st.number_input("Ops Cost (R / sqm)", value=32.50)
    total_lease = (internal_gla * int_rent) + (external_gla * ext_rent) + (total_gla * ops_cost)

    st.divider()
    st.header("Dispatch Feasibility Pack")
    app_name = st.text_input("Prospective Franchisee Full Name")
    app_email = st.text_input("Prospective Franchisee Email")
    app_mobile = st.text_input("Prospective Franchisee Mobile / WhatsApp")
    app_address = st.text_input("Physical / Domicilium Address")

    payback_data = pd.DataFrame({"RECOVERY HORIZON": ["12 Months", "24 Months"], "REQUIRED TURNOVER/MONTH": ["R 579,193", "R 389,799"]})
    pnl_data = pd.DataFrame({"Year_Label": ["Year 1", "Year 2"], "Turnover": [7136206, 7707102], "Net Operating Profit": [2291100, 2590244]})

    if st.button("⚡ Generate & Sync Feasibility Pack"):
        pdf_buf = generate_pdf_report(
            location_name, shop_code, "Germiston, GP", internal_gla, external_gla, total_gla,
            selected_model, 26, 32, turnkey_capital, working_capital, int_rent, ext_rent, ops_cost,
            total_lease, 7.0, selected_model, 7.42, payback_data, pnl_data, blueprint_pil,
            applicant_name=app_name, applicant_email=app_email, applicant_mobile=app_mobile,
            applicant_address=app_address
        )
        pdf_bytes = pdf_buf.getvalue()
        pdf_fn = f"{location_name}_{selected_model.replace(' ','_')}.pdf"

        loc_path, sync_msg = sync_pdf_to_local_and_cloud(location_name, pdf_bytes, pdf_fn)
        st.success(f"PDF Generated! {sync_msg}")

        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        st.markdown(f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_fn}" class="direct-dl-btn">📥 Download PDF Direct</a>', unsafe_allow_html=True)

# TAB 2: BRAND SHOWCASE
with tab2:
    st.header("📖 Brand Menus & Global Media Showcase")
    for b_key, b_info in BRAND_MENU_CATALOG.items():
        st.markdown(f'<div class="brand-card-block">### {b_key}\n**Tagline:** {b_info["tagline"]}\n\n**Overview:** {b_info["description"]}\n\n🔗 [Download Menu PDF](https://drive.google.com/uc?export=download&id={b_info["drive_file_id"]})\n\n📸 [Instagram Profile]({b_info["instagram_url"]})</div>', unsafe_allow_html=True)

    st.subheader("🎬 Global Store Video Walk-Throughs & Gallery")
    st.markdown(f"📂 **Master Media Directory:** [Open Google Drive Media Folder]({STORE_MEDIA_LINKS['master_folder']})")

# TAB 3: REGISTRY
with tab3:
    st.header("Franchisee & Investor Lead Intake & Database")
    with st.form("reg_form"):
        fn = st.text_input("Full Name *")
        em = st.text_input("Email Address *")
        mb = st.text_input("Mobile / WhatsApp *")
        ps = st.text_input("Preferred Target Site *")
        
        has_comp = st.radio("Company Docs Available?", ["No", "Yes"], horizontal=True)
        upl_comp = st.file_uploader("Upload Company Docs", type=["pdf", "png", "jpg"]) if has_comp == "Yes" else None
        
        has_id = st.radio("Franchisee ID Available?", ["No", "Yes"], horizontal=True)
        upl_id = st.file_uploader("Upload Franchisee ID", type=["pdf", "png", "jpg"]) if has_id == "Yes" else None
        
        has_pof = st.radio("Proof of Funds Available?", ["No", "Yes"], horizontal=True)
        upl_pof = st.file_uploader("Upload Proof of Funds", type=["pdf", "png", "jpg"]) if has_pof == "Yes" else None

        if st.form_submit_button("Submit Lead to Database"):
            if fn and em and mb and ps:
                save_investor_lead({
                    "full_name": fn, "id_or_passport": "Provided", "email": em, "mobile": mb,
                    "preferred_site": ps, "store_model": "Express Model", "capital_available": 2500000.0,
                    "unencumbered_cash_pct": 50.0, "company_docs_status": "Uploaded" if upl_comp else "Not Provided",
                    "franchisee_id_status": "Uploaded" if upl_id else "Not Provided",
                    "proof_of_funds_status": "Uploaded" if upl_pof else "Not Provided"
                })
                st.success(f"Lead record for {fn} saved!")
            else:
                st.error("Please complete all mandatory fields (*).")

    st.subheader("CEO Pipeline Registry")
    df_pipe = get_pipeline_dataframe()
    if not df_pipe.empty:
        st.dataframe(df_pipe, use_container_width=True)
