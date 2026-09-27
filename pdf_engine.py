import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_feasibility_pdf(data, blueprint_images=None):
    """
    Generates the true enterprise-grade 8-page Phatbuns Franchise Feasibility Report
    matching the exact Rondebuilt gold standard benchmark.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    primary_color = colors.HexColor("#1A1A1A")
    accent_color = colors.HexColor("#FF6600")
    bg_light = colors.HexColor("#F9F9F9")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=primary_color,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=accent_color,
        spaceAfter=10
    )
    
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=primary_color
    )

    cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=cell_style,
        fontName='Helvetica-Bold'
    )

    def add_header_footer(canvas, doc_obj):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 8)
        canvas.setFillColor(accent_color)
        canvas.drawString(36, 810, "PHAT buns")
        
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        header_text = "CONFIDENTIAL INFORMATION | Nisaar Ally: SA Master Rights Holder | Email: nisaar@fantastic1.com | Mobile: +27 (0)68 710 1939 | WhatsApp: +27 (0)82 786 7712"
        canvas.drawString(90, 810, header_text)
        
        canvas.drawRightString(559, 20, f"Page {doc_obj.page} of 8")
        canvas.restoreState()

    loc_name = data.get("location_name", "New Corner Northcliff (Shop RL 03)")
    footprint = data.get("store_footprint", 167.0)
    base_rent = data.get("base_net_rental", 350.0)
    turnkey_cap = data.get("turnkey_capital", 3100000.0)
    managing_agent = data.get("managing_agent", "Redefine Properties / Abcon")
    working_cap = turnkey_cap * 0.15

    # ================= PAGE 1: SITE PROFILE & CAPITAL SCHEDULE =================
    story.append(Paragraph(f"SITE EVALUATION & INVESTMENT ANALYSIS — {loc_name.upper()}", title_style))
    story.append(Paragraph(f"FULL SIT-DOWN MODEL ({footprint:.2f} M²) | MASTER FEASIBILITY PACK", subtitle_style))
    story.append(Spacer(1, 5))
    
    story.append(Paragraph("01. SITE PROFILE & CAPITAL SCHEDULE", cell_bold))
    story.append(Spacer(1, 3))
    
    table_data_1 = [
        [Paragraph("SITE PARAMETER", cell_bold), Paragraph("SPECIFICATION", cell_bold), Paragraph("TURNKEY CAPITAL SCHEDULE (EXCL. VAT)", cell_bold), Paragraph("AMOUNT", cell_bold)],
        [Paragraph("Location Name", cell_style), Paragraph(loc_name, cell_style), Paragraph("50% Deposit on Signing Agreement", cell_style), Paragraph(f"R {turnkey_cap * 0.5:,.2f}", cell_style)],
        [Paragraph("Address / Node", cell_style), Paragraph("High-Traffic Commercial Retail Node", cell_style), Paragraph("40% Beneficial Occupation (BO)", cell_style), Paragraph(f"R {turnkey_cap * 0.4:,.2f}", cell_style)],
        [Paragraph("Store Footprint", cell_style), Paragraph(f"{footprint:.2f} m² Full Sit-Down Model", cell_style), Paragraph("10% Prior to Store Opening", cell_style), Paragraph(f"R {turnkey_cap * 0.1:,.2f}", cell_style)],
        [Paragraph("Managing Agent", cell_style), Paragraph(managing_agent, cell_style), Paragraph("Total Turnkey Capital Outlay", cell_bold), Paragraph(f"R {turnkey_cap:,.2f}", cell_bold)],
        [Paragraph("Mall GLA Size", cell_style), Paragraph("Regional / Community Retail Node", cell_style), Paragraph("Working Capital Reserve", cell_style), Paragraph(f"R {working_cap:,.2f}", cell_style)],
        [Paragraph("Site Plan Attached", cell_style), Paragraph("Yes (Rendered on Page 6)", cell_style), Paragraph("Landlord Rental Deposit", cell_style), Paragraph(f"R {base_rent * footprint:,.2f}", cell_style)],
    ]
    t1 = Table(table_data_1, colWidths=[110, 150, 160, 103])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t1)
    story.append(Spacer(1, 10))

    story.append(Paragraph("02. LEASE STRUCTURE & PROPOSED LANDLORD OFFER TARGETS", cell_bold))
    story.append(Spacer(1, 3))
    table_data_2 = [
        [Paragraph("LEASE CLAUSE/PROVISION", cell_bold), Paragraph("TERMS & RATE STRUCTURE", cell_bold), Paragraph("FINANCIAL ALIGNMENT", cell_bold)],
        [Paragraph("Lease Period & Renewal", cell_style), Paragraph("5 Years Initial Period + 5-Year Renewal Option", cell_style), Paragraph("60 Months Base Amortization", cell_style)],
        [Paragraph("Base Net Rental Rate Target", cell_style), Paragraph(f"R {base_rent:.2f}/m²/month (Excl. VAT)", cell_style), Paragraph(f"R {base_rent * footprint:,.2f}/month", cell_style)],
        [Paragraph("Annual Rental Escalation", cell_style), Paragraph("7.5% per annum effective anniversary", cell_style), Paragraph("Predictable cost curve", cell_style)],
        [Paragraph("Monthly Turnover Rental Clause", cell_style), Paragraph("8.0% of net turnover vs Base Net Rental (whichever greater)", cell_style), Paragraph(f"Effective Threshold: > R {base_rent * footprint * 3:,.2f} p.m.", cell_style)],
        [Paragraph("Beneficial Occupation (BO)", cell_style), Paragraph("2 Month Rent-Free BO for Turnkey Store Fitout", cell_style), Paragraph("Fitout Schedule: 60 Days", cell_style)],
    ]
    t2 = Table(table_data_2, colWidths=[140, 203, 180])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t2)
    story.append(PageBreak())

    # ================= PAGE 2: CATCHMENT & RECOVERY MATRIX =================
    story.append(Paragraph("03. DYNAMIC CATCHMENT & LOCATION INTELLIGENCE", cell_bold))
    story.append(Spacer(1, 3))
    table_data_c = [
        [Paragraph("CATCHMENT METRIC", cell_bold), Paragraph("DATA POINT / LOCATION ANALYSIS (5KM & 10KM RADIUS)", cell_bold)],
        [Paragraph("LSM/ESM Profile", cell_style), Paragraph("LSM 8-10+ / High Disposable Income & Affluent Residential Node", cell_style)],
        [Paragraph("Monthly / Annual Footfall", cell_style), Paragraph("160,000–210,000 visits/month (~2.1M–2.5M Annually across node)", cell_style)],
        [Paragraph("Catchment Household Count", cell_style), Paragraph("110,000–135,000 Active Households (10 km Radius Core Demographic)", cell_style)],
        [Paragraph("In-Mall & 10km Competitors", cell_style), Paragraph("Woolworths Food, Checkers Hyper, Spur, RocoMamas, Burger King, KFC, McDonald's, Nando's", cell_style)],
    ]
    tc = Table(table_data_c, colWidths=[150, 373])
    tc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(tc)
    story.append(Spacer(1, 10))

    story.append(Paragraph("04. FINANCIAL RECOVERY & UNIT SALES TARGET MATRIX", cell_bold))
    story.append(Spacer(1, 3))
    
    table_data_3 = [
        [Paragraph("RECOVERY HORIZON", cell_bold), Paragraph("REQUIRED TURNOVER/MONTH", cell_bold), Paragraph("REQUIRED UNITS/MONTH", cell_bold), Paragraph("REQUIRED UNITS/DAY", cell_bold)],
        [Paragraph("Operational Breakeven", cell_style), Paragraph("R 310,000", cell_style), Paragraph("1,636 units", cell_style), Paragraph("55 units / day", cell_style)],
        [Paragraph("12 Months Recovery Target", cell_style), Paragraph("R 744,000", cell_style), Paragraph("3,980 units", cell_style), Paragraph("133 units / day", cell_style)],
        [Paragraph("24 Months Recovery Target", cell_style), Paragraph("R 527,000", cell_style), Paragraph("2,808 units", cell_style), Paragraph("94 units / day", cell_style)],
        [Paragraph("36 Months Recovery Target", cell_style), Paragraph("R 465,000", cell_style), Paragraph("2,417 units", cell_style), Paragraph("81 units / day", cell_style)],
        [Paragraph("48 Months Recovery Target", cell_style), Paragraph("R 410,000", cell_style), Paragraph("2,132 units", cell_style), Paragraph("71 units / day", cell_style)],
        [Paragraph("60 Months Recovery Target", cell_style), Paragraph("R 380,000", cell_style), Paragraph("1,975 units", cell_style), Paragraph("66 units / day", cell_style)],
    ]
    t3 = Table(table_data_3, colWidths=[140, 130, 130, 123])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t3)
    story.append(Spacer(1, 8))
    story.append(Paragraph("Detailed Investment Recovery Window: 12 to 24 Months Target Analysis with active daily unit velocity modeled against peak footfall conversion. (E&OE).", cell_style))
    story.append(PageBreak())

    # ================= PAGE 3: OPERATIONS & EQUIPMENT =================
    story.append(Paragraph("05. OPERATIONS, STAFFING & CHANNEL BREAKDOWN", cell_bold))
    story.append(Spacer(1, 3))
    story.append(Paragraph("• Revenue Channel Split: Online Deliveries (UberEats/Mr D): 45% | Takeaway & Counter: 30% | In-Store Express Dining: 25%", cell_style))
    story.append(Paragraph("• Staffing Structure (BCEA 8-Hour Shifts): 1 x Store Manager, 2 x Shift Supervisors (Floor Leads & POS), 3 x Line Grillers & Fryers, 2 x Till Operators/Runners, 2 x Cleaners & Scullery (SANHA Hygiene Compliance).", cell_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("06. TURNKEY KITCHEN EQUIPMENT MANIFEST", cell_bold))
    story.append(Spacer(1, 3))
    table_data_eq = [
        [Paragraph("STATION / CATEGORY", cell_bold), Paragraph("EQUIPMENT SPECIFICATION & DEPLOYMENT", cell_bold)],
        [Paragraph("Smash Grill Station", cell_style), Paragraph("Chrome Smash Griddle (3-Phase Heavy Duty), Bun Toaster & Pass-Through Heated Holding Cabinet.", cell_style)],
        [Paragraph("Frying & Prep Line", cell_style), Paragraph("Dual-Pan High-Recovery Deep Fryer, 3-Door Under-Counter Prep Fridge with Topping Rail.", cell_style)],
        [Paragraph("Extraction Canopy", cell_style), Paragraph("Stainless Steel Wall-Mounted Extraction Canopy complete with ANSUL Fire Suppression System.", cell_style)],
        [Paragraph("POS & Automation", cell_style), Paragraph("Dual-Screen Touch POS Terminal, Kitchen Display System (KDS), Thermal Printers & Router setup.", cell_style)],
        [Paragraph("Beverage & Shakes", cell_style), Paragraph("Heavy Duty Commercial Variable Speed Blender & Commercial Ice Machine (40kg/24hr capacity).", cell_style)],
        [Paragraph("Storage & Washup", cell_style), Paragraph("Stainless Steel Work Tables, Double Bowl Scullery Sink, Hand Wash Basin & Wall Shelving units.", cell_style)],
    ]
    teq = Table(table_data_eq, colWidths=[130, 393])
    teq.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(teq)
    story.append(PageBreak())

    # ================= PAGE 4: BRAND HERITAGE & MARKETING =================
    story.append(Paragraph("07. BRAND HERITAGE, USP & PRODUCT STANDARDS", cell_bold))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Founded in 2019, Phatbuns was built from a vision to reinvent the smash burger experience within the fast-casual market. Phatbuns brings a premier culinary disruption specializing in artisan smash burgers, proprietary secret sauces, and hand-crafted brioche buns. All ingredients and proteins adhere strictly to central supply chain quality assurance protocols, ensuring 100% consistency, Halal compliance (SANHA), and exceptional taste profiles.", cell_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("08. MARKETING, LAUNCH STRATEGY & DIGITAL ACQUISITION", cell_bold))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Franchisees benefit from a robust multi-channel marketing framework including pre-launch digital teaser campaigns, local influencer seeding, geo-fenced social media performance marketing targeting surrounding residential nodes, and integrated delivery aggregator partnerships (UberEats, Mr D).", cell_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("09. FRANCHISEE SUPPORT, TRAINING & OPERATIONAL GOVERNANCE", cell_bold))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Every Phatbuns franchise partner receives extensive onboarding and operational training covering a 4-week intensive program across back-of-house grill mastery, inventory control, and front-of-house guest hospitality.", cell_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("10. GOVERNANCE, COMPLIANCE & NEXT STEPS", cell_bold))
    story.append(Spacer(1, 3))
    story.append(Paragraph("To proceed with site allocation, prospective investors must: (1) Execute the attached NCNDA, (2) Submit verified proof of unencumbered cash equity, (3) Settle review administrative fees, and (4) Sign formal franchise agreements upon executive board approval.", cell_style))
    story.append(PageBreak())

    # ================= PAGE 5: 5-YEAR PRO FORMA P&L =================
    story.append(Paragraph("11. 5-YEAR PRO FORMA INCOME STATEMENT & P&L FORECAST", cell_bold))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Standard Model Parameters: 50% Debt Funding @ 11.75% Prime Rate | 35% COGS | 9% Royalties & Marketing | E&OE", cell_style))
    story.append(Spacer(1, 5))
    
    table_data_4 = [
        [Paragraph("FINANCIAL METRIC", cell_bold), Paragraph("YEAR 1", cell_bold), Paragraph("YEAR 2", cell_bold), Paragraph("YEAR 3", cell_bold), Paragraph("YEAR 4", cell_bold), Paragraph("YEAR 5", cell_bold)],
        [Paragraph("Gross Revenue", cell_style), Paragraph("R 8,500,000", cell_style), Paragraph("R 9,350,000", cell_style), Paragraph("R 10,285,000", cell_style), Paragraph("R 11,313,500", cell_style), Paragraph("R 12,444,850", cell_style)],
        [Paragraph("Cost of Sales (35%)", cell_style), Paragraph("R 2,975,000", cell_style), Paragraph("R 3,272,500", cell_style), Paragraph("R 3,599,750", cell_style), Paragraph("R 3,959,725", cell_style), Paragraph("R 4,355,698", cell_style)],
        [Paragraph("Gross Profit", cell_style), Paragraph("R 5,525,000", cell_style), Paragraph("R 6,077,500", cell_style), Paragraph("R 6,685,250", cell_style), Paragraph("R 7,353,775", cell_style), Paragraph("R 8,089,152", cell_style)],
        [Paragraph("Operating Expenses", cell_style), Paragraph("R 4,200,000", cell_style), Paragraph("R 4,536,000", cell_style), Paragraph("R 4,898,880", cell_style), Paragraph("R 5,290,790", cell_style), Paragraph("R 5,713,952", cell_style)],
        [Paragraph("Net Operating Profit", cell_style), Paragraph("R 1,325,000", cell_style), Paragraph("R 1,541,500", cell_style), Paragraph("R 1,786,370", cell_style), Paragraph("R 2,062,985", cell_style), Paragraph("R 2,375,200", cell_style)],
    ]
    t4 = Table(table_data_4, colWidths=[130, 78, 78, 78, 78, 81])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t4)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("11A. AGGREGATE 5-YEAR FINANCIAL RETURN (ROI) & MASTER RECOMMENDATION", cell_bold))
    story.append(Spacer(1, 3))
    table_data_roi = [
        [Paragraph("FINANCIAL METRIC / AGGREGATE CATEGORY", cell_bold), Paragraph("5-YEAR PROJECTED CUMULATIVE VALUE (ZAR)", cell_bold)],
        [Paragraph("Total Landlord Rentals Paid (5 Years)", cell_style), Paragraph(f"R {base_rent * footprint * 60:,.2f}", cell_style)],
        [Paragraph("Total Central Royalties Paid (9% over 5 Years)", cell_style), Paragraph("R 4,120,500.00", cell_style)],
        [Paragraph("Cumulative Net Operating Profit (After Debt Service)", cell_style), Paragraph("R 9,089,055.00", cell_style)],
        [Paragraph("Site Feasibility & Master Recommendation", cell_bold), Paragraph("Phatbuns South Africa advises this site as Feasible. Recommended Model: Full Sit-Down / Inline Store. (E&OE).", cell_bold)],
    ]
    troi = Table(table_data_roi, colWidths=[200, 323])
    troi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(troi)
    story.append(PageBreak())

    # ================= PAGE 6: BLUEPRINT & LAYOUT =================
    story.append(Paragraph("12. SITE DEVELOPMENT LEASING & FLOOR PLAN LAYOUT", cell_bold))
    story.append(Spacer(1, 5))
    if blueprint_images:
        for title, img in blueprint_images:
            story.append(Paragraph(f"Layout Ref: {title}", cell_bold))
            story.append(Spacer(1, 3))
            if img:
                img_path = f"/tmp/{title.replace(' ', '_')}.png"
                img.save(img_path)
                story.append(RLImage(img_path, width=450, height=280))
            else:
                story.append(Paragraph("[Blueprint Document Attached & Synchronized to Drive Folder]", cell_style))
            story.append(Spacer(1, 5))
    else:
        story.append(Paragraph("Standard modular kitchen layout engineered for SANHA Halal compliance, optimal customer throughput, and front-of-house seating capacity.", cell_style))
    story.append(PageBreak())

    # ================= PAGE 7: BRAND PORTFOLIO & MEDIA =================
    story.append(Paragraph("13. BRAND PORTFOLIO & GLOBAL MEDIA SHOWCASE", cell_bold))
    story.append(Spacer(1, 3))
    story.append(Paragraph("• Phatbuns Smash Burgers: Artisan Angus beef patties & signature sauces.", cell_style))
    story.append(Paragraph("• PhatVille Sliders & Sides: Nashville-style hot sliders & crinkle fries.", cell_style))
    story.append(Paragraph("• Butter Brûlée Desserts & Cookies: Gourmet freshly baked cookies & luxury shakes.", cell_style))
    story.append(Paragraph("• Doorstep Desserts: Warm waffles, dough tubs, and gelato sundaes.", cell_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Global Media Links: Phatbuns UK & Dubai Flagship store walk-through videos synchronized in master cloud repository.", cell_style))
    story.append(PageBreak())

    # ================= PAGE 8: LEGAL NCNDA =================
    story.append(Paragraph("14. NON-DISCLOSURE AND NON-CIRCUMVENTION AGREEMENT (NCNDA)", cell_bold))
    story.append(Spacer(1, 3))
    story.append(Paragraph("This Agreement is entered into between Phatbuns South Africa (Franchisor) and the undersigned Prospective Franchisee. All shared financial models, operational manuals, and layouts remain strictly confidential pursuant to FASA and POPIA frameworks.", cell_style))
    story.append(Spacer(1, 15))
    
    table_data_sig = [
        [Paragraph("For: PHATBUNS SOUTH AFRICA", cell_bold), Paragraph(f"For: {data.get('client_name', 'PROSPECTIVE INVESTOR')}", cell_bold)],
        [Paragraph("Authorized Signature: ______________________", cell_style), Paragraph("Authorized Signature: ______________________", cell_style)],
        [Paragraph("Name: Nisaar Ally", cell_style), Paragraph(f"Name: {data.get('client_name', 'Prospective Investor')}", cell_style)],
        [Paragraph("Title: SA Master Rights Holder", cell_style), Paragraph("Title: Prospective Franchisee", cell_style)],
        [Paragraph("Date: 2026-09-27 | Place: Johannesburg", cell_style), Paragraph("Date: ______________ | Place: _____________", cell_style)]
    ]
    tsig = Table(table_data_sig, colWidths=[250, 273])
    tsig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(tsig)

    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)
    return buffer.getvalue()
