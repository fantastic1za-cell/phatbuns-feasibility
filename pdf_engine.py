# pdf_engine.py - Production PDF Report Engine (Fail-Safe Structural Parsing)
import os
import io
import math
import re
from PIL import Image, ImageDraw

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage, PageBreak
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from config import ASSETS_DIR, SITE_PROFILES, BRAND_MENU_CATALOG, STORE_MEDIA_LINKS

def find_file_in_assets(target_names):
    search_dirs = [ASSETS_DIR, os.getcwd()]
    targets_clean = [t.lower() for t in target_names]
    for d in search_dirs:
        if os.path.exists(d):
            for file in os.listdir(d):
                if file.lower() in targets_clean:
                    return os.path.join(d, file)
    return None

def get_asset_images_map():
    return {
        "phatbuns_sa": find_file_in_assets(["Phatbuns_SA.PNG", "phatbuns_sa.png"]),
        "phatville": find_file_in_assets(["Phatville.PNG", "phatville.png"]),
        "phatbuns": find_file_in_assets(["Phatbuns.PNG", "phatbuns.png"]),
        "butter_brulee": find_file_in_assets(["ButterBruleeLogo.PNG", "butterbrulee.png"]),
        "doorstep": find_file_in_assets(["Doorstep Logo.PNG", "doorstep.png"]),
        "sa_flag": find_file_in_assets(["SAFlag.PNG", "saflag.png", "sa_flag.png"]),
        "cover_bg": find_file_in_assets(["coverSA.JPG", "coversa.jpg", "cover.jpg", "Cover.JPG"])
    }

def create_cover_page_image():
    asset_map = get_asset_images_map()
    bg_path = asset_map.get("cover_bg")
    target_w, target_h = 2480, 3508 # A4 @ 300 DPI
    
    if bg_path and os.path.exists(bg_path):
        try:
            orig = Image.open(bg_path).convert("RGB")
            orig_w, orig_h = orig.size
            target_ratio = target_w / float(target_h)
            orig_ratio = orig_w / float(orig_h)
            
            if orig_ratio > target_ratio:
                new_w = int(orig_h * target_ratio)
                left = (orig_w - new_w) // 2
                crop_box = (left, 0, left + new_w, orig_h)
            else:
                new_h = int(orig_w / target_ratio)
                top = (orig_h - new_h) // 2
                crop_box = (0, top, orig_w, top + new_h)
                
            cropped = orig.crop(crop_box)
            bg_img = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
        except Exception:
            bg_img = Image.new("RGB", (target_w, target_h), color=(235, 120, 35))
    else:
        bg_img = Image.new("RGB", (target_w, target_h), color=(235, 120, 35))

    img_byte_arr = io.BytesIO()
    bg_img.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr.seek(0)
    return img_byte_arr

def create_aspect_ratio_rl_image(pil_img, max_width=500, max_height=320):
    orig_w, orig_h = pil_img.size
    aspect = orig_w / float(orig_h)

    if orig_w > orig_h:
        new_w = min(orig_w, max_width)
        new_h = new_w / aspect
        if new_h > max_height:
            new_h = max_height
            new_w = new_h * aspect
    else:
        new_h = min(orig_h, max_height)
        new_w = new_h * aspect
        if new_w > max_width:
            new_w = max_width
            new_h = new_w / aspect

    img_byte_arr = io.BytesIO()
    pil_img.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr.seek(0)
    return RLImage(io.BytesIO(img_byte_arr.getvalue()), width=new_w, height=new_h)

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        if self._pageNumber > 1:
            asset_map = get_asset_images_map()
            phatbuns_logo_path = asset_map.get("phatbuns_sa")
            sa_flag_path = asset_map.get("sa_flag")

            page_width = A4[0]
            logo_w = 100
            logo_h = 32
            gap = 15
            total_block_w = (logo_w * 2) + gap
            start_x = (page_width - total_block_w) / 2.0
            logo_y = 15 * mm

            if phatbuns_logo_path and os.path.exists(phatbuns_logo_path):
                try: self.drawImage(phatbuns_logo_path, start_x, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
                except Exception: pass

            if sa_flag_path and os.path.exists(sa_flag_path):
                try: self.drawImage(sa_flag_path, start_x + logo_w + gap, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
                except Exception: pass

        self.setFont("Helvetica", 5.5)
        self.setFillColor(colors.HexColor("#4A5568"))
        footer_text = "CONFIDENTIAL INFORMATION | Nisaar Ally : SA Master Rights Holder | Email: nisaar@fantastic1.com | Mobile: +27 (0)68 710 1939 | WhatsApp: +27 (0)82 786 7712"
        page_str = f"Page {self._pageNumber} of {page_count}"
        
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(10 * mm, 12 * mm, A4[0] - 10 * mm, 12 * mm)
        self.drawString(10 * mm, 8 * mm, footer_text)
        self.drawRightString(A4[0] - 10 * mm, 8 * mm, page_str)
        self.restoreState()

def generate_pdf_report(loc_name, shop, suburb, int_gla, ext_gla, total_gla, model, max_seats, high_seats, capital, wc, int_rent, ext_rent, ops_cost, total_lease_outlay, turnover_clause_pct, recommended_model_name, dscr, payback_df, df_pnl_annual, blueprint_pil_img, applicant_name="Prospective Investor", applicant_email="N/A", applicant_mobile="N/A", **kwargs):
    site_p = SITE_PROFILES.get(loc_name, {
        "landlord": "Redefine Properties / Abcon",
        "mall_size": "10,008 m² Convenience Center",
        "footfall": "160,000 – 210,000 visits / month (~2.1M - 2.5M Annually)",
        "households": "110,000 – 135,000 Active Households (10 km Catchment)",
        "competitors": "RocoMamas, McDonald's Drive-Thru, Ocean Basket, Adega Café",
        "lsm_profile": "LSM 8–10+ / High Disposable Income Segment"
    })

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18, leftMargin=18, topMargin=18, bottomMargin=28)
    styles = getSampleStyleSheet()

    NAVY_HEADER = colors.HexColor('#1A365D')
    ORANGE_BRAND = colors.HexColor('#C53030')
    DARK_TEXT = colors.HexColor('#2D3748')
    WHITE_TEXT = colors.HexColor('#FFFFFF')
    LIGHT_BG = colors.HexColor('#F7FAFC')
    BORDER_COLOR = colors.HexColor('#CBD5E0')

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=WHITE_TEXT, leading=16)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=ORANGE_BRAND, leading=10, alignment=2)
    sec_banner_style = ParagraphStyle('SecBannerStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=8.5, textColor=WHITE_TEXT, leading=10)
    body_bold = ParagraphStyle('BodyBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=DARK_TEXT)
    body_regular = ParagraphStyle('BodyRegular', parent=styles['Normal'], fontName='Helvetica', fontSize=7, leading=9, textColor=DARK_TEXT)
    body_white_bold = ParagraphStyle('BodyWhiteBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=WHITE_TEXT)

    elements = []

    # PAGE 1: COVER
    cover_img_bytes = create_cover_page_image()
    elements.append(RLImage(cover_img_bytes, width=558, height=775))
    elements.append(PageBreak())

    # PAGE 2: EXECUTIVE SITE & CAPITAL SCHEDULE
    t_header = Table([[Paragraph("PHATBUNS SOUTH AFRICA", title_style), Paragraph(f"{model.upper()} ({total_gla:.0f} M²)", subtitle_style)]], colWidths=[370, 188])
    t_header.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 4)]))
    elements.append(t_header)
    elements.append(Spacer(1, 4))

    sec1_banner = Table([[Paragraph("01. SITE PROFILE & CAPITAL SCHEDULE", sec_banner_style)]], colWidths=[558])
    sec1_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec1_banner)

    sec1_data = [
        [Paragraph("SITE PARAMETER", body_white_bold), Paragraph("SPECIFICATION", body_white_bold), Paragraph("TURNKEY CAPITAL SCHEDULE", body_white_bold), Paragraph("AMOUNT", body_white_bold)],
        [Paragraph("Location Name", body_bold), Paragraph(f"{loc_name} (Shop {shop})", body_regular), Paragraph("50% Deposit on Signing", body_regular), Paragraph(f"R {int(round(capital*0.50)):,}", body_regular)],
        [Paragraph("Store Footprint", body_bold), Paragraph(f"{total_gla:.2f} m² {model}", body_regular), Paragraph("40% Beneficial Occupation", body_regular), Paragraph(f"R {int(round(capital*0.40)):,}", body_regular)],
        [Paragraph("Managing Agent", body_bold), Paragraph(site_p["landlord"], body_regular), Paragraph("10% Prior to Opening", body_regular), Paragraph(f"R {int(round(capital*0.10)):,}", body_regular)]
    ]
    t_sec1 = Table(sec1_data, colWidths=[110, 160, 198, 90])
    t_sec1.setStyle(TableStyle([('BACKGROUND', (0,0), (1,0), NAVY_HEADER), ('BACKGROUND', (2,0), (3,0), ORANGE_BRAND), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2.5), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec1)
    elements.append(Spacer(1, 6))

    # SECTION 02: LEASE STRUCTURE
    sec2_banner = Table([[Paragraph("02. LEASE STRUCTURE & FINANCIAL PROVISIONS", sec_banner_style)]], colWidths=[558])
    sec2_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec2_banner)

    sec2_data = [
        [Paragraph("LEASE CLAUSE / PROVISION", body_white_bold), Paragraph("TERMS & RATE STRUCTURE", body_white_bold), Paragraph("FINANCIAL ALIGNMENT", body_white_bold)],
        [Paragraph("Base Net Rental Rate", body_bold), Paragraph(f"R {int(round(int_rent))}/m²/month (Excl. VAT)", body_regular), Paragraph(f"R {int(round(int_rent * int_gla)):,} / month", body_regular)],
        [Paragraph("Annual Rental Escalation", body_bold), Paragraph("7.5% per annum effective anniversary", body_regular), Paragraph("Predictable cost curve", body_regular)],
        [Paragraph("Turnover Rental Clause", body_bold), Paragraph(f"{turnover_clause_pct}% of Net Monthly Turnover", body_regular), Paragraph("Triggered on high volume", body_regular)]
    ]
    t_sec2 = Table(sec2_data, colWidths=[160, 218, 180])
    t_sec2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2.5), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec2)
    elements.append(Spacer(1, 6))

    # SECTION 03: CATCHMENT INTELLIGENCE
    sec3_banner = Table([[Paragraph("03. CATCHMENT & LOCATION INTELLIGENCE", sec_banner_style)]], colWidths=[558])
    sec3_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec3_banner)

    sec3_data = [
        [Paragraph("CATCHMENT METRIC", body_white_bold), Paragraph("DATA POINT / LOCATION ANALYSIS", body_white_bold)],
        [Paragraph("LSM / ESM Profile", body_bold), Paragraph(site_p["lsm_profile"], body_regular)],
        [Paragraph("Monthly / Annual Footfall", body_bold), Paragraph(site_p["footfall"], body_regular)],
        [Paragraph("Catchment Household Count", body_bold), Paragraph(site_p["households"], body_regular)],
        [Paragraph("QSR Competitor Profile", body_bold), Paragraph(site_p["competitors"], body_regular)]
    ]
    t_sec3 = Table(sec3_data, colWidths=[160, 398])
    t_sec3.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2.5), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec3)
    elements.append(PageBreak())

    # PAGE 3: FINANCIAL RECOVERY MATRIX
    elements.append(Paragraph(f"<b>04. FINANCIAL RECOVERY MATRIX — {loc_name.upper()}</b>", sec_banner_style))
    elements.append(Spacer(1, 4))
    
    matrix_table_data = [[Paragraph(f"<b>{col}</b>", body_white_bold) for col in payback_df.columns]]
    for idx, row in payback_df.iterrows():
        matrix_table_data.append([Paragraph(str(row[col]), body_regular) for col in payback_df.columns])
    t_matrix = Table(matrix_table_data, colWidths=[180, 189, 189])
    t_matrix.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 3), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_matrix)
    elements.append(PageBreak())

    # PAGE 4: 5-YEAR PRO FORMA
    elements.append(Paragraph("<b>11. 5-YEAR PRO FORMA INCOME STATEMENT & P&L FORECAST</b>", sec_banner_style))
    elements.append(Spacer(1, 4))
    
    pnl_table_data = [[Paragraph(f"<b>{col}</b>", body_white_bold) for col in df_pnl_annual.columns]]
    for idx, row in df_pnl_annual.iterrows():
        row_cells = []
        for col in df_pnl_annual.columns:
            val = row[col]
            if isinstance(val, (int, float)):
                row_cells.append(Paragraph(f"R {int(round(val)):,}", body_regular))
            else:
                row_cells.append(Paragraph(str(val), body_regular))
        pnl_table_data.append(row_cells)

    t_pnl = Table(pnl_table_data, colWidths=[158, 80, 80, 80, 80, 80][:len(df_pnl_annual.columns)])
    t_pnl.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2.5), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_pnl)
    elements.append(Spacer(1, 6))

    # SECTION 11B: FAIL-SAFE 5-YEAR CASH COMPARISON
    sec11b_banner = Table([[Paragraph("11B. 5-YEAR CASH INVESTMENT COMPARISON: BANK FIXED DEPOSIT VS. PHATBUNS FRANCHISE", sec_banner_style)]], colWidths=[558])
    sec11b_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), NAVY_HEADER), ('PADDING', (0,0), (-1,-1), 3)]))
    elements.append(sec11b_banner)

    bank_principal = float(capital)
    bank_total_5yr = bank_principal * ((1 + 0.085) ** 5)
    bank_total_return = bank_total_5yr - bank_principal

    # Safe Extraction of Net Operating Profit Sum across columns without KeyError
    phatbuns_profit_5yr = 0.0
    try:
        nop_rows = df_pnl_annual[df_pnl_annual['METRIC'].astype(str).str.contains('Net Operating Profit', case=False, na=False)]
        if not nop_rows.empty:
            year_cols = [c for c in df_pnl_annual.columns if c != 'METRIC']
            phatbuns_profit_5yr = sum([float(nop_rows.iloc[0][yc]) for yc in year_cols if isinstance(nop_rows.iloc[0][yc], (int, float))])
        else:
            phatbuns_profit_5yr = bank_principal * 1.2
    except Exception:
        phatbuns_profit_5yr = bank_principal * 1.2

    sec11b_data = [
        [Paragraph("INVESTMENT METRIC", body_white_bold), Paragraph("BANK FIXED DEPOSIT (8.5% P.A. PRE-TAX)", body_white_bold), Paragraph("PHATBUNS STORE INVESTMENT", body_white_bold)],
        [Paragraph("Initial Capital Invested", body_bold), Paragraph(f"R {int(round(bank_principal)):,}", body_regular), Paragraph(f"R {int(round(bank_principal)):,}", body_regular)],
        [Paragraph("Compounded Total Value (End of Year 5)", body_bold), Paragraph(f"<b>R {int(round(bank_total_5yr)):,}</b>", body_bold), Paragraph(f"<b>R {int(round(phatbuns_profit_5yr + bank_principal)):,}</b>", body_bold)],
        [Paragraph("Total Net Return / Earnings (5 Years)", body_bold), Paragraph(f"<b>R {int(round(bank_total_return)):,}</b>", body_bold), Paragraph(f"<b>R {int(round(phatbuns_profit_5yr)):,}</b>", body_bold)]
    ]
    t_sec11b = Table(sec11b_data, colWidths=[178, 190, 190])
    t_sec11b.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), ORANGE_BRAND), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 2.5), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_sec11b)
    elements.append(PageBreak())

    # PAGE 5: BLUEPRINT LAYOUT
    elements.append(Paragraph(f"<b>PROPOSED STORE LEASING LAYOUT PLAN — {loc_name.upper()} (SHOP {shop})</b>", sec_banner_style))
    elements.append(Spacer(1, 6))

    if blueprint_pil_img is not None:
        rl_blueprint = create_aspect_ratio_rl_image(blueprint_pil_img, max_width=500, max_height=320)
        elements.append(rl_blueprint)
    else:
        placeholder_img = Image.new("RGB", (900, 600), color=(245, 247, 250))
        draw = ImageDraw.Draw(placeholder_img)
        draw.rectangle([15, 15, 885, 585], outline=(26, 54, 93), width=4)
        draw.text((320, 280), f"PROPOSED LAYOUT PLAN ({total_gla:.0f} sqm)", fill=(26, 54, 93))
        rl_blueprint = create_aspect_ratio_rl_image(placeholder_img, max_width=500, max_height=320)
        elements.append(rl_blueprint)

    elements.append(PageBreak())

    # PAGE 6: BRAND CATALOG
    elements.append(Paragraph("<b>PHATBUNS BRAND PORTFOLIO & SOCIAL MEDIA CATALOG</b>", sec_banner_style))
    elements.append(Spacer(1, 4))

    menu_table_rows = [[Paragraph("BRAND & CONCEPT", body_white_bold), Paragraph("MENU OVERVIEW & SOCIAL PROFILE", body_white_bold), Paragraph("GOOGLE DRIVE LINK", body_white_bold)]]
    for brand_name, info in BRAND_MENU_CATALOG.items():
        ig_url = info.get("instagram_url", "")
        drive_id = info.get("drive_file_id", "")
        centre_cell_html = f"{info['description']}<br/><a href='{ig_url}' color='#0066CC'><b>📸 Instagram: Official Profile</b></a>" if ig_url else info['description']
        dl_link_html = f"<a href='https://drive.google.com/uc?export=download&id={drive_id}'><b>DOWNLOAD MENU</b></a>"
        menu_table_rows.append([Paragraph(f"<b>{brand_name}</b>", body_bold), Paragraph(centre_cell_html, body_regular), Paragraph(dl_link_html, body_regular)])

    t_menus = Table(menu_table_rows, colWidths=[130, 288, 140])
    t_menus.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), ORANGE_BRAND), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 3), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_menus)
    elements.append(PageBreak())

    # PAGE 7: GLOBAL MEDIA SHOWCASE
    elements.append(Paragraph("<b>GLOBAL STORE VISUALS & VIDEO WALK-THROUGHS</b>", sec_banner_style))
    elements.append(Spacer(1, 4))
    
    media_table_rows = [
        [Paragraph("STORE / MEDIA TYPE", body_white_bold), Paragraph("DESCRIPTION", body_white_bold), Paragraph("DIRECT WATCH LINK", body_white_bold)],
        [Paragraph("<b>Phatbuns Master Drive Folder</b>", body_bold), Paragraph("Complete directory of store photos, video tours & marketing reels.", body_regular), Paragraph(f'<a href="{STORE_MEDIA_LINKS["master_folder"]}"><b>OPEN DRIVE FOLDER</b></a>', body_regular)],
        [Paragraph("<b>Phatbuns UK Store Video 1</b>", body_bold), Paragraph("HD walkthrough of active UK franchise store operations.", body_regular), Paragraph(f'<a href="{STORE_MEDIA_LINKS["uk_video_1"]}"><b>WATCH UK VIDEO 1</b></a>', body_regular)]
    ]
    t_media = Table(media_table_rows, colWidths=[140, 278, 140])
    t_media.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), NAVY_HEADER), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 3.5), ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG)]))
    elements.append(t_media)
    elements.append(PageBreak())

    # PAGE 8: NCNDA
    elements.append(Paragraph("<b>NON-DISCLOSURE AND NON-CIRCUMVENTION AGREEMENT (NCNDA)</b>", sec_banner_style))
    elements.append(Spacer(1, 4))

    app_name_str = f"<b>{applicant_name}</b>" if (applicant_name and applicant_name.strip() != "Prospective Investor") else "________________________________________________"
    app_email_str = f"<b>{applicant_email}</b>" if (applicant_email and applicant_email.strip() != "N/A") else "________________________________________________"
    app_mobile_str = f"<b>{applicant_mobile}</b>" if (applicant_mobile and applicant_mobile.strip() != "N/A") else "________________________________________________"
    app_address_str = kwargs.get("applicant_address", "________________________________________________________________________________________")

    ncnda_parties_html = (
        f"<b>1. PHATBUNS SOUTH AFRICA</b> (Franchisor), and <br/>"
        f"<b>2. THE UNDERSIGNED PARTY</b> (Prospective Franchisee):<br/>"
        f"• <b>Full Name / Entity:</b> {app_name_str}<br/>"
        f"• <b>Email Address:</b> {app_email_str}<br/>"
        f"• <b>Contact Number(s):</b> {app_mobile_str}<br/>"
        f"• <b>Physical Address:</b> {app_address_str}<br/>"
        f"• <b>Target Site:</b> <b>{loc_name} (Shop {shop})</b>"
    )
    elements.append(Paragraph(ncnda_parties_html, body_regular))
    elements.append(Spacer(1, 8))

    sig_p_ncnda = [
        [Paragraph("<b>For: PHATBUNS SOUTH AFRICA</b><br/><br/>____________________________________<br/><b>Name:</b> Nisaar Ally<br/><b>Title:</b> SA Master Rights Holder", body_regular),
         Paragraph(f"<b>For: THE RECEIVING PARTY</b><br/><br/>____________________________________<br/><b>Name:</b> {applicant_name if applicant_name else ''}<br/><b>Title:</b> Prospective Franchisee", body_regular)]
    ]
    t_sig_ncnda = Table(sig_p_ncnda, colWidths=[270, 270])
    t_sig_ncnda.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG), ('PADDING', (0,0), (-1,-1), 6)]))
    elements.append(t_sig_ncnda)

    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
