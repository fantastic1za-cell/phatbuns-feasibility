# app.py - Main Streamlit Interface (Full Feasibility Layout + Custom Header Branding)
import os
import io
import re
import math
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
    send_investor_lead_notification,
    get_drive_service, get_or_create_drive_folder, upload_pdf_to_drive
)
from pdf_engine import generate_pdf_report, get_asset_images_map

# Initialize SQLite Database
init_db()

# Helper function to convert logo images to Base64 HTML strings safely
def get_base64_image(image_path):
    if image_path and os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception:
            return None
    return None

# Load Header Assets
asset_images = get_asset_images_map()
sa_app_logo_path = asset_images.get("phatbuns_sa")
sa_flag_path = asset_images.get("sa_flag")

b64_phatbuns_sa = get_base64_image(sa_app_logo_path)
b64_sa_flag = get_base64_image(sa_flag_path)

# Streamlit Page Configuration
app_favicon = Image.open(sa_app_logo_path) if sa_app_logo_path and os.path.exists(sa_app_logo_path) else "🍔"

st.set_page_config(
    page_title="Phatbuns SA Feasibility Engine",
    page_icon=app_favicon,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling for Dark Theme, Header Banner & Cards
st.markdown("""
<style>
.stApp { background-color: #111111; color: #FFFFFF; }

/* Dynamic Dual Logo Banner */
.brand-banner { 
    background: linear-gradient(135deg, #1f1f1f 0%, #0a0a0a 100%); 
    padding: 22px; 
    border-radius: 12px; 
    text-align: center; 
    border: 1px solid #333; 
    margin-bottom: 10px; 
}
.banner-header-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    margin-bottom: 8px;
}
.header-logo-phatbuns {
    height: 40px;
    width: auto;
    object-fit: contain;
}
.header-logo-flag {
    height: 32px;
    width: auto;
    object-fit: contain;
}
.brand-title { 
    color: #FFFFFF; 
    font-size: 24px; 
    font-weight: 800; 
    margin: 0; 
    line-height: 1.25;
    letter-spacing: 0.8px;
}
.banner-subtitle {
    font-size: 13px;
    color: #CBD5E0;
    margin-top: 6px;
}
.green-divider { border: none; height: 3px; background-color: #72BF44; border-radius: 2px; margin: 15px 0; }

.calc-box {
    background-color: #1A202C;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #2D3748;
    margin-bottom: 15px;
}
.calc-title {
    font-size: 13px;
    font-weight: 700;
    color: #72BF44;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.calc-val {
    font-size: 20px;
    font-weight: 800;
    color: #FFFFFF;
}

.brand-card-block {
    background-color: #1A1A1A;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #333333;
    margin-bottom: 25px;
}
.brand-logo-img {
    max-height: 55px;
    width: auto;
    margin-bottom: 12px;
    display: block;
}
.brand-card-header { font-size: 20px; font-weight: 800; color: #FFFFFF; margin-bottom: 4px; }
.brand-tagline { font-size: 13px; font-weight: 700; color: #C53030; margin-bottom: 12px; }
.brand-overview { font-size: 13.5px; line-height: 1.6; color: #E2E8F0; margin-bottom: 16px; }
.brand-link-row { margin-top: 10px; font-size: 14px; }
.brand-link-row a { color: #63B3ED !important; text-decoration: none; font-weight: 600; }
.direct-dl-btn {
    display: block;
    width: 100%;
    background-color: #0066CC;
    color: white !important;
    text-align: center;
    padding: 12px;
    border-radius: 8px;
    font-weight: bold;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

# Generate HTML string for Header Icons
phatbuns_img_html = f'<img src="data:image/png;base64,{b64_phatbuns_sa}" class="header-logo-phatbuns" alt="Phatbuns SA"/>' if b64_phatbuns_sa else ''
flag_img_html = f'<img src="data:image/png;base64,{b64_sa_flag}" class="header-logo-flag" alt="SA Flag"/>' if b64_sa_flag else ''

st.markdown(f'''
<div class="brand-banner">
    <div class="banner-header-row">
        {phatbuns_img_html}
        <div class="brand-title">PHATBUNS<br/>SOUTH AFRICA</div>
        {flag_img_html}
    </div>
    <div class="banner-subtitle">Bankable Commercial Feasibility, Financial Modeling & Automated Lease Extraction</div>
</div>
''', unsafe_allow_html=True)
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
            "1. I have a Landlord Proposal / Offer Sheet (OCR Auto-Extract)", 
            "2. No Proposal — Check Mall Viability & Propose Target Rates",
            "3. Update Old/Legacy Franchisee Pack to New Format"
        ],
        index=0
    )

    if "1. I have a Landlord Proposal" in analysis_mode:
        st.subheader("📄 Landlord Offer Sheet / Proposal Extraction")
        proposal_file = st.file_uploader("Upload Landlord Proposal / Offer Sheet (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"])
        if proposal_file:
            st.success("Proposal ingested. Review auto-populated lease metrics below.")

    elif "3. Update Old/Legacy" in analysis_mode:
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

    st.subheader("📐 Store Footprint & Seating Capacity Calculator")
    col_int, col_ext = st.columns(2)
    with col_int: internal_gla = st.number_input("Internal Area (sqm)", value=float(model_data["default_gla"]))
    with col_ext: external_gla = st.number_input("External / Patio Area (sqm)", value=0.0)
    total_gla = internal_gla + external_gla

    # Dynamic Seating Calculation
    foh_ratio = model_data.get("foh_pct", 0.10)
    foh_area = (internal_gla * foh_ratio) + external_gla
    est_standard_seats = int(math.floor((foh_area * 0.70) / 1.4)) if foh_area > 0 else 0
    est_hightop_seats = int(math.floor((foh_area * 0.30) / 1.0)) if foh_area > 0 else 0
    total_est_seats = est_standard_seats + est_hightop_seats

    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        st.markdown(f'<div class="calc-box"><div class="calc-title">Standard Dining Seats</div><div class="calc-val">{est_standard_seats} Seats</div></div>', unsafe_allow_html=True)
    with s_col2:
        st.markdown(f'<div class="calc-box"><div class="calc-title">High-Top / Counter Seats</div><div class="calc-val">{est_hightop_seats} Seats</div></div>', unsafe_allow_html=True)
    with s_col3:
        st.markdown(f'<div class="calc-box"><div class="calc-title">Total Seating Capacity</div><div class="calc-val">{total_est_seats} Seats</div></div>', unsafe_allow_html=True)

    blueprint_file = st.file_uploader("Upload Store Blueprint / Layout Plan", type=["pdf", "png", "jpg", "jpeg"])
    blueprint_pil = Image.open(blueprint_file).convert("RGB") if blueprint_file and not blueprint_file.name.endswith('.pdf') else None

    st.divider()
    st.header("Commercial Capital & Detailed Lease Modeling")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1: turnkey_capital = st.number_input("Turnkey Capital (Excl. VAT)", value=float(model_data["turnkey_capital"]))
    with col_c2: working_capital = st.number_input("Working Capital", value=float(model_data["working_capital"]))

    st.subheader("🏢 Landlord Rental & Operational Cost Schedule")
    l_col1, l_col2, l_col3 = st.columns(3)
    with l_col1:
        int_rent = st.number_input("Internal Base Rent (R / sqm)", value=220.0)
        ext_rent = st.number_input("External Base Rent (R / sqm)", value=0.0)
    with l_col2:
        rates_cost = st.number_input("Rates & Taxes (R / sqm)", value=18.50)
        ops_cost = st.number_input("Ops Cost (R / sqm)", value=32.50)
    with l_col3:
        generator_cost = st.number_input("Generator / Utility Recovery (R / sqm)", value=15.00)
        marketing_pct = st.number_input("Marketing Levy (% of Base Rental)", value=5.0)

    st.subheader("📈 Turnover Rent Clause")
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        turnover_clause_pct = st.number_input("Annual Turnover Clause (%)", value=7.0)
    with t_col2:
        turnover_threshold = st.number_input("Monthly Turnover Threshold (R / month)", value=650000.0)

    # Monthly Lease Outlay Calculation
    base_rent_total = (internal_gla * int_rent) + (external_gla * ext_rent)
    ops_total = total_gla * ops_cost
    rates_total = total_gla * rates_cost
    gen_total = total_gla * generator_cost
    mktg_total = base_rent_total * (marketing_pct / 100.0)
    total_lease_monthly = base_rent_total + ops_total + rates_total + gen_total + mktg_total

    st.markdown(f'<div class="calc-box"><div class="calc-title">Total Monthly Lease Outlay (Excl. VAT)</div><div class="calc-val">R {int(round(total_lease_monthly)):,} / month</div></div>', unsafe_allow_html=True)

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
            selected_model, est_standard_seats, est_hightop_seats, turnkey_capital, working_capital, int_rent, ext_rent, ops_cost,
            total_lease_monthly, turnover_clause_pct, selected_model, 7.42, payback_data, pnl_data, blueprint_pil,
            applicant_name=app_name, applicant_email=app_email, applicant_mobile=app_mobile,
            applicant_address=app_address
        )
        pdf_bytes = pdf_buf.getvalue()
        pdf_fn = f"{location_name}_{selected_model.replace(' ','_')}.pdf"

        loc_path, sync_msg = sync_pdf_to_local_and_cloud(location_name, pdf_bytes, pdf_fn)
        st.success(f"PDF Generated! {sync_msg}")

        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        st.markdown(f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_fn}" class="direct-dl-btn">📥 Download PDF Direct</a>', unsafe_allow_html=True)


# TAB 2: BRAND MENUS & GLOBAL MEDIA SHOWCASE
with tab2:
    st.header("📖 Brand Menus & Global Media Showcase")
    st.markdown("Individual brand catalogs and global store walk-throughs below are configured with dedicated Google Drive Download & Streaming Links.")
    st.write("")

    for b_key, b_info in BRAND_MENU_CATALOG.items():
        logo_file_path = asset_images.get(b_info.get("logo_key", "phatbuns_sa"))
        b64_logo_str = get_base64_image(logo_file_path)
        
        logo_html = f'<img src="data:image/png;base64,{b64_logo_str}" class="brand-logo-img"/>' if b64_logo_str else ''
        drive_dl_url = f"https://drive.google.com/uc?export=download&id={b_info['drive_file_id']}"
        ig_url = b_info.get("instagram_url", "")

        card_html = f"""
        <div class="brand-card-block">
            {logo_html}
            <div class="brand-card-header">{b_key}</div>
            <div class="brand-tagline">Tagline: {b_info['tagline']}</div>
            <div class="brand-overview"><b>Overview:</b> {b_info['description']}</div>
            <div class="brand-link-row">🔗 <b>Google Drive Direct Download Link:</b> <a href="{drive_dl_url}" target="_blank">{b_info['filename']}</a></div>
            <div class="brand-link-row" style="margin-top:6px;">📸 <b>Official Instagram Profile:</b> <a href="{ig_url}" target="_blank">{ig_url}</a></div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

    st.subheader("🎬 Global Store Video Walk-Throughs & Visual Gallery")
    
    st.markdown(f"""
    <a href="{STORE_MEDIA_LINKS['master_folder']}" target="_blank" style="text-decoration:none;">
        <div style="background-color:#1A365D; color:white; padding:12px; border-radius:8px; text-align:center; font-weight:bold; margin-bottom:15px; border:1px solid #3182CE;">
            📂 Open Phatbuns Master Google Drive Media Repository (All Videos & Photos)
        </div>
    </a>
    """, unsafe_allow_html=True)

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown(f"🖼️ **Sample Store Photos Gallery:** [View Google Drive Gallery]({STORE_MEDIA_LINKS['store_photos']})")
        st.markdown(f"🎬 **Phatbuns UK Walk-Through 1:** [Watch Video]({STORE_MEDIA_LINKS['uk_video_1']})")
        st.markdown(f"🎬 **Phatbuns UK Walk-Through 2:** [Watch Video]({STORE_MEDIA_LINKS['uk_video_2']})")

    with m_col2:
        st.markdown(f"🎬 **Phatbuns Dubai Flagship Video:** [Watch Video]({STORE_MEDIA_LINKS['dubai_video']})")
        st.markdown(f"🎬 **Store Opening Event & Reels:** [Watch Collection]({STORE_MEDIA_LINKS['master_folder']})")
        st.markdown(f"🎬 **Kitchen & Pass Operations Line:** [Watch Video Clip]({STORE_MEDIA_LINKS['master_folder']})")


# TAB 3: INVESTOR & FRANCHISEE REGISTRY
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
                lead_payload = {
                    "full_name": fn, 
                    "id_or_passport": "Provided" if upl_id else "Pending", 
                    "email": em, 
                    "mobile": mb,
                    "preferred_site": ps, 
                    "store_model": "Express Model", 
                    "capital_available": 2500000.0,
                    "unencumbered_cash_pct": 50.0, 
                    "company_docs_status": "Uploaded" if upl_comp else "Not Provided",
                    "franchisee_id_status": "Uploaded" if upl_id else "Not Provided",
                    "proof_of_funds_status": "Uploaded" if upl_pof else "Not Provided"
                }
                
                # 1. Save Lead to SQLite Database
                save_investor_lead(lead_payload)
                
                # 2. Dispatch Executive Email Notification to Both Recipients
                email_sent, email_msg = send_investor_lead_notification(lead_payload)
                
                if email_sent:
                    st.success(f"✅ Lead for {fn} saved to database & dispatched to fantastic1za@gmail.com and nisaar@fantastic1.com!")
                else:
                    st.warning(f"✅ Lead saved to database, but email dispatch notification failed: {email_msg}")
            else:
                st.error("Please complete all mandatory fields (*).")

    st.subheader("CEO Pipeline Registry")
    try:
        df_pipe = get_pipeline_dataframe()
        if not df_pipe.empty:
            st.dataframe(df_pipe, use_container_width=True)
        else:
            st.info("No franchisee applications logged in database yet.")
    except Exception:
        st.warning("Database initializing...")
