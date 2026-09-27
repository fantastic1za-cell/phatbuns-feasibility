import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_feasibility_pdf(data, blueprint_images=None):
    """
    Generates the enterprise-grade 8-page Phatbuns Franchise Feasibility Report
    matching the Rondebuilt Centre benchmark.
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
    
    # Custom Corporate Styles
    primary_color = colors.HexColor("#1A1A1A") # Dark Charcoal / Black
    accent_color = colors.HexColor("#FF6600")  # Phatbuns Orange
    bg_light = colors.HexColor("#F9F9F9")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary_color,
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#666666"),
        spaceAfter=15
    )
    
    header_footer_style = ParagraphStyle(
        'HeaderFooter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#444444")
    )

    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
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

    # ================= PAGE 1: SITE PROFILE & CAPITAL SCHEDULE =================
    story.append(Paragraph("PHATBUNS SOUTH AFRICA", title_style))
    story.append(Paragraph(f"SITE EVALUATION & INVESTMENT ANALYSIS — {loc_name.upper()}", subtitle_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("01. SITE PROFILE & CAPITAL SCHEDULE", cell_bold))
    story.append(Spacer(1, 5))
    
    table_data_1 = [
        [Paragraph("SITE PARAMETER", cell_bold), Paragraph("SPECIFICATION", cell_bold), Paragraph("TURNKEY CAPITAL SCHEDULE", cell_bold), Paragraph("AMOUNT", cell_bold)],
        [Paragraph("Location Name", cell_style), Paragraph(loc_name, cell_style), Paragraph("50% Deposit on Signing", cell_style), Paragraph(f"R {turnkey_cap * 0.5:,.2f}", cell_style)],
        [Paragraph("Store Footprint", cell_style), Paragraph(f"{footprint:.2f} m² Full Sit-Down Model", cell_style), Paragraph("40% Beneficial Occupation", cell_style), Paragraph(f"R {turnkey_cap * 0.4:,.2f}", cell_style)],
        [Paragraph("Managing Agent", cell_style), Paragraph(managing_agent, cell_style), Paragraph("10% Prior to Opening", cell_style), Paragraph(f"R {turnkey_cap * 0.1:,.2f}", cell_style)],
    ]
    t1 = Table(table_data_1, colWidths=[120, 160, 150, 93])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))

    story.append(Paragraph("02. LEASE STRUCTURE & FINANCIAL PROVISIONS", cell_bold))
    story.append(Spacer(1, 5))
    table_data_2 = [
        [Paragraph("LEASE CLAUSE / PROVISION", cell_bold), Paragraph("TERMS & RATE STRUCTURE", cell_bold), Paragraph("FINANCIAL ALIGNMENT", cell_bold)],
        [Paragraph("Base Net Rental Rate", cell_style), Paragraph(f"R {base_rent:.2f}/m²/month (Excl. VAT)", cell_style), Paragraph(f"R {base_rent * footprint:,.2f}/month", cell_style)],
        [Paragraph("Annual Rental Escalation", cell_style), Paragraph("7.5% per annum effective anniversary", cell_style), Paragraph("Predictable cost curve", cell_style)],
        [Paragraph("Turnover Rental Clause", cell_style), Paragraph("8.0% of Net Monthly Turnover", cell_style), Paragraph("Triggered on high volume", cell_style)],
    ]
    t2 = Table(table_data_2, colWidths=[150, 183, 190])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t2)
    story.append(PageBreak())

    # ================= PAGES 2 TO 8 (Structured Master Pack) =================
    # Page 2: Catchment & Recovery Horizon
    story.append(Paragraph("03. CATCHMENT & LOCATION INTELLIGENCE", cell_bold))
    story.append(Spacer(1, 5))
    story.append(Paragraph("• LSM/ESM Profile: LSM 8-10+/High Disposable Income Segment", cell_style))
    story.append(Paragraph("• Monthly / Annual Footfall: 160,000–210,000 visits/month (~2.1M–2.5M Annually)", cell_style))
    story.append(Paragraph("• Catchment Household Count: 110,000–135,000 Active Households (10 km Radius)", cell_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("04. FINANCIAL RECOVERY HORIZON & UNIT TARGETS", cell_bold))
    story.append(Spacer(1, 5))
    
    table_data_3 = [
        [Paragraph("RECOVERY HORIZON", cell_bold), Paragraph("REQUIRED TURNOVER/MONTH", cell_bold), Paragraph("REQUIRED UNITS/MONTH", cell_bold)],
        [Paragraph("Operational Breakeven", cell_style), Paragraph("R 310,000", cell_style), Paragraph("1,636 units", cell_style)],
        [Paragraph("12 Months Target", cell_style), Paragraph("R 744,000", cell_style), Paragraph("3,980 units", cell_style)],
        [Paragraph("24 Months Target", cell_style), Paragraph("R 527,000", cell_style), Paragraph("2,808 units", cell_style)],
        [Paragraph("36 Months Target", cell_style), Paragraph("R 465,000", cell_style), Paragraph("2,417 units", cell_style)],
    ]
    t3 = Table(table_data_3, colWidths=[173, 175, 175])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t3)
    story.append(PageBreak())

    # Page 3: Operations & Equipment Manifest
    story.append(Paragraph("05. OPERATIONS, STAFFING & CHANNEL BREAKDOWN", cell_bold))
    story.append(Spacer(1, 5))
    story.append(Paragraph("• Online Deliveries (UberEats/Mr D): 45% | Takeaway & Counter: 30% | In-Store Express: 25%", cell_style))
    story.append(Paragraph("• Staffing: 1 x Store Manager, 2 x Shift Supervisors, 3 x Line Grillers, 2 x Till Operators, 2 x Scullery/Cleaners.", cell_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("06. TURNKEY KITCHEN EQUIPMENT MANIFEST", cell_bold))
    story.append(Spacer(1, 5))
    story.append(Paragraph("• Smash Grill Station: Chrome Smash Griddle (3-Phase Heavy Duty), Bun Toaster & Pass-Through Heated Holding Cabinet.", cell_style))
    story.append(Paragraph("• Frying & Prep Line: Dual-Pan High-Recovery Deep Fryer, 3-Door Under-Counter Prep Fridge with Topping Rail.", cell_style))
    story.append(Paragraph("• Extraction & Safety: Stainless Steel Wall-Mounted Canopy complete with ANSUL Fire Suppression System.", cell_style))
    story.append(PageBreak())

    # Page 4: Brand Standards & Marketing
    story.append(Paragraph("07. BRAND HERITAGE, USP & PRODUCT STANDARDS", cell_bold))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Founded in 2019, Phatbuns reinvents the smash burger experience with artisan beef patties, secret sauces, and hand-crafted brioche buns. 100% SANHA Halal compliant central supply chain quality assurance.", cell_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("08. MARKETING & DIGITAL ACQUISITION", cell_bold))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Multi-channel pre-launch teaser campaigns, local influencer seeding, geo-fenced social media marketing, and integrated aggregator delivery partnerships.", cell_style))
    story.append(PageBreak())

    # Page 5: 5-Year P&L Forecast
    story.append(Paragraph("11. 5-YEAR PRO FORMA INCOME STATEMENT & P&L FORECAST", cell_bold))
    story.append(Spacer(1, 5))
    table_data_4 = [
        [Paragraph("FINANCIAL METRIC", cell_bold), Paragraph("YEAR 1", cell_bold), Paragraph("YEAR 2", cell_bold), Paragraph("YEAR 3", cell_bold), Paragraph("YEAR 5", cell_bold)],
        [Paragraph("Gross Revenue", cell_style), Paragraph("R 8,500,000", cell_style), Paragraph("R 9,350,000", cell_style), Paragraph("R 10,285,000", cell_style), Paragraph("R 12,444,850", cell_style)],
        [Paragraph("Cost of Sales (35%)", cell_style), Paragraph("R 2,975,000", cell_style), Paragraph("R 3,272,500", cell_style), Paragraph("R 3,599,750", cell_style), Paragraph("R 4,355,698", cell_style)],
        [Paragraph("Gross Profit", cell_style), Paragraph("R 5,525,000", cell_style), Paragraph("R 6,077,500", cell_style), Paragraph("R 6,685,250", cell_style), Paragraph("R 8,089,152", cell_style)],
        [Paragraph("Operating Expenses", cell_style), Paragraph("R 4,200,000", cell_style), Paragraph("R 4,536,000", cell_style), Paragraph("R 4,898,880", cell_style), Paragraph("R 5,713,952", cell_style)],
        [Paragraph("Net Operating Profit", cell_style), Paragraph("R 1,325,000", cell_style), Paragraph("R 1,541,500", cell_style), Paragraph("R 1,786,370", cell_style), Paragraph("R 2,375,200", cell_style)],
    ]
    t4 = Table(table_data_4, colWidths=[130, 93, 93, 93, 114])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t4)
    story.append(PageBreak())

    # Page 6: Site Blueprint & Layout Plans
    story.append(Paragraph("12. SITE DEVELOPMENT LEASING & FLOOR PLAN LAYOUT", cell_bold))
    story.append(Spacer(1, 10))
    if blueprint_images:
        for title, img in blueprint_images:
            story.append(Paragraph(f"Layout Ref: {title}", cell_bold))
            story.append(Spacer(1, 5))
            if img:
                # Save temp or draw PIL image
                img_path = f"/tmp/{title.replace(' ', '_')}.png"
                img.save(img_path)
                story.append(RLImage(img_path, width=450, height=300))
            else:
                story.append(Paragraph("[Blueprint Document Attached & Synchronized to Drive Folder]", cell_style))
            story.append(Spacer(1, 10))
    else:
        story.append(Paragraph("Standard modular kitchen layout engineered for SANHA Halal compliance and optimal customer throughput.", cell_style))
    story.append(PageBreak())

    # Page 7: Brand Portfolio & Media Links
    story.append(Paragraph("13. BRAND PORTFOLIO & GLOBAL MEDIA SHOWCASE", cell_bold))
    story.append(Spacer(1, 5))
    story.append(Paragraph("• Phatbuns Smash Burgers: Artisan Angus beef patties & signature sauces.", cell_style))
    story.append(Paragraph("• PhatVille Sliders & Sides: Nashville-style hot sliders & crinkle fries.", cell_style))
    story.append(Paragraph("• Butter Brûlée Desserts & Cookies: Gourmet freshly baked cookies & luxury shakes.", cell_style))
    story.append(Paragraph("• Doorstep Desserts: Warm waffles, dough tubs, and gelato sundaes.", cell_style))
    story.append(PageBreak())

    # Page 8: Legal NCNDA
    story.append(Paragraph("14. NON-DISCLOSURE AND NON-CIRCUMVENTION AGREEMENT (NCNDA)", cell_bold))
    story.append(Spacer(1, 5))
    story.append(Paragraph("This Agreement is entered into between Phatbuns South Africa (Franchisor) and the undersigned Prospective Franchisee. All shared financial models, operational manuals, and layouts remain strictly confidential pursuant to FASA and POPIA frameworks.", cell_style))

    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)
    return buffer.getvalue()
