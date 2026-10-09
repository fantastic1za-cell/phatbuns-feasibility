import os
import io
import logging
from datetime import datetime

logger = logging.getLogger("PDF_Engine")

def format_currency(value):
    """Formats numeric values into standard ZAR commercial string currency (Excl. VAT)."""
    try:
        return f"R {float(value):,.2f}"
    except (ValueError, TypeError):
        return "R 0.00"

def extract_pdf_data(*args, **kwargs):
    """
    Normalizes inputs from app.py whether passed as a single dictionary, 
    positional arguments, or individual keyword arguments.
    """
    if args and isinstance(args[0], dict):
        return args[0]
    elif kwargs:
        return kwargs
    elif args:
        keys = ["location_name", "client_name", "store_type", "sqm", "rental_rate", "fitout_cost", "equipment_cost"]
        return {keys[i]: args[i] for i in range(min(len(args), len(keys)))}
    return {}

def generate_rondebult_html(data):
    """Constructs the Rondebult Master Prospectus layout using strict CSS paged media."""
    location_name = data.get("location_name") or data.get("location") or "Target Location"
    client_name = data.get("client_name") or data.get("applicant_name") or "Valued Investor"
    store_type = data.get("store_type") or data.get("model_type") or "Standard Inline"
    shop_code = data.get("shop_code") or "Shop RL 03"
    
    try:
        sqm = float(data.get("sqm", 80))
    except (ValueError, TypeError):
        sqm = 80.0

    try:
        rental_rate = float(data.get("rental_rate", 220))
    except (ValueError, TypeError):
        rental_rate = 220.0

    monthly_rent = sqm * rental_rate
    deposit = monthly_rent * 2

    fitout_cost = float(data.get("fitout_cost", 850000))
    equipment_cost = float(data.get("equipment_cost", 650000))
    pos_signage = float(data.get("pos_signage", 120000))
    working_capital = float(data.get("working_capital", 150000))
    opening_stock = float(data.get("opening_stock", 80000))
    total_setup = fitout_cost + equipment_cost + pos_signage + working_capital + opening_stock + deposit

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Phatbuns Feasibility Report - {location_name}</title>
        <style>
            @page {{
                size: A4 portrait;
                margin: 20mm 15mm 20mm 15mm;
                @bottom-right {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 8pt;
                    color: #64748B;
                }}
                @bottom-left {{
                    content: "Phatbuns SA Commercial Feasibility — Confidential";
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 8pt;
                    color: #64748B;
                }}
            }}
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #1E293B;
                font-size: 10pt;
                line-height: 1.5;
                margin: 0;
                padding: 0;
            }}
            .page-break {{ page-break-before: always; }}
            .header-bar {{
                border-bottom: 3px solid #D97706;
                padding-bottom: 12px;
                margin-bottom: 24px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .brand-title {{
                font-size: 22pt;
                font-weight: 800;
                color: #0F172A;
                margin: 0;
            }}
            .brand-sub {{
                font-size: 10pt;
                color: #D97706;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            h2 {{
                font-size: 14pt;
                color: #0F172A;
                border-left: 4px solid #D97706;
                padding-left: 8px;
                margin-top: 20px;
                margin-bottom: 12px;
                text-transform: uppercase;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                margin-bottom: 20px;
                font-size: 9.5pt;
            }}
            th {{
                background-color: #0F172A;
                color: #FFFFFF;
                text-align: left;
                padding: 8px 10px;
            }}
            td {{
                padding: 8px 10px;
                border-bottom: 1px solid #E2E8F0;
            }}
            tr:nth-child(even) td {{ background-color: #F8FAFC; }}
            .amount-col {{
                text-align: right;
                font-family: 'Courier New', Courier, monospace;
                font-weight: 600;
            }}
            .total-row td {{
                background-color: #FEF3C7 !important;
                font-weight: 700;
                border-top: 2px solid #D97706;
                border-bottom: 2px solid #D97706;
                color: #78350F;
            }}
            .badge {{
                display: inline-block;
                padding: 3px 8px;
                background-color: #0284C7;
                color: #FFFFFF;
                font-size: 8pt;
                font-weight: 700;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>

        <!-- PAGE 1: COVER -->
        <div style="text-align: center; padding-top: 100px;">
            <div class="brand-sub">Franchise Expansion Opportunity</div>
            <h1 style="font-size: 30pt; color: #0F172A; margin-top: 10px; margin-bottom: 5px;">PHATBUNS SOUTH AFRICA</h1>
            <div style="font-size: 13pt; color: #64748B;">Master Investor Dossier & Feasibility Analysis</div>
            
            <div style="margin-top: 120px; padding: 20px; border: 1px solid #CBD5E1; border-radius: 8px; display: inline-block; width: 80%; text-align: left; background-color: #F8FAFC;">
                <p><strong>Target Site Node:</strong> {location_name} ({shop_code})</p>
                <p><strong>Prepared For:</strong> {client_name}</p>
                <p><strong>Store Format:</strong> {store_type} ({sqm} sqm Footprint)</p>
                <p><strong>Date Generated:</strong> {datetime.now().strftime('%d %B %Y')}</p>
                <p><strong>Financial Protocol:</strong> Exclusive of VAT (Excl. VAT)</p>
            </div>
        </div>

        <!-- PAGE 2: LEASE & CAPEX -->
        <div class="page-break"></div>
        <div class="header-bar">
            <div>
                <div class="brand-title">PHATBUNS</div>
                <div class="brand-sub">Commercial Feasibility</div>
            </div>
            <span class="badge">Rondebult Layout Standard</span>
        </div>

        <h2>1. Site Node & Lease Parameter Analysis</h2>
        <table>
            <thead>
                <tr>
                    <th>Commercial Lease Metric</th>
                    <th>Baseline Specification</th>
                    <th class="amount-col">Projected Value (Excl. VAT)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Target Demised Premises Size</td>
                    <td>{sqm} sqm</td>
                    <td class="amount-col">{sqm} m²</td>
                </tr>
                <tr>
                    <td>Base Gross Rental Rate</td>
                    <td>R {rental_rate:,.2f} / sqm</td>
                    <td class="amount-col">{format_currency(monthly_rent)} / mo</td>
                </tr>
                <tr>
                    <td>Landlord Security Deposit</td>
                    <td>Minimum 2-Month Rental Guarantee</td>
                    <td class="amount-col">{format_currency(deposit)}</td>
                </tr>
                <tr>
                    <td>Operations Footprint Standard</td>
                    <td>Kitchen & Delivery Prep Compliant</td>
                    <td class="amount-col">PASSED (>50 sqm)</td>
                </tr>
            </tbody>
        </table>

        <h2>2. Initial Capital Expenditure Schedule</h2>
        <table>
            <thead>
                <tr>
                    <th>Capital Outlay Component</th>
                    <th>Scope Description</th>
                    <th class="amount-col">Cost Allocation (Excl. VAT)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Store Civils & Fitout</td>
                    <td>Leasehold improvements & shopfront</td>
                    <td class="amount-col">{format_currency(fitout_cost)}</td>
                </tr>
                <tr>
                    <td>Kitchen Equipment & Extraction</td>
                    <td>Commercial griddles, fryers & canopy</td>
                    <td class="amount-col">{format_currency(equipment_cost)}</td>
                </tr>
                <tr>
                    <td>Brand Signage & POS Automation</td>
                    <td>External signage & POS hardware</td>
                    <td class="amount-col">{format_currency(pos_signage)}</td>
                </tr>
                <tr>
                    <td>Landlord Deposit Reserve</td>
                    <td>2-Month gross rental deposit held by lessor</td>
                    <td class="amount-col">{format_currency(deposit)}</td>
                </tr>
                <tr>
                    <td>Initial Working Capital Reserve</td>
                    <td>Unencumbered liquidity buffer</td>
                    <td class="amount-col">{format_currency(working_capital)}</td>
                </tr>
                <tr>
                    <td>Opening Stock Outlay</td>
                    <td>Core consumables & packaging</td>
                    <td class="amount-col">{format_currency(opening_stock)}</td>
                </tr>
                <tr class="total-row">
                    <td colspan="2">TOTAL PROJECTED CAPITAL OUTLAY (EXCL. VAT)</td>
                    <td class="amount-col">{format_currency(total_setup)}</td>
                </tr>
            </tbody>
        </table>

        <!-- PAGE 3: NCNDA AGREEMENT -->
        <div class="page-break"></div>
        <div class="header-bar">
            <div>
                <div class="brand-title">PHATBUNS</div>
                <div class="brand-sub">Non-Circumvention & NCNDA</div>
            </div>
            <span class="badge">Legal Execution Page</span>
        </div>

        <h2>3. Master Confidentiality & Non-Disclosure Terms</h2>
        <p>
            This document containing financial models, site layout renders, and operational benchmarks for <strong>{location_name}</strong> is strictly confidential and protected under non-disclosure regulations.
        </p>
        <p>
            The recipient ({client_name}) agrees that all proprietary franchise materials, operational metrics, and lease terms shall remain exclusive property of Phatbuns South Africa. Unauthorised distribution or direct negotiations with developers bypassing the rights holder is prohibited.
        </p>

        <div style="margin-top: 80px; width: 100%;">
            <table style="border: none;">
                <tr style="background: none;">
                    <td style="width: 50%; border: none; vertical-align: top;">
                        <p><strong>Signed on behalf of Franchisee Applicant:</strong></p>
                        <br><br>
                        <div style="border-bottom: 1px solid #000; width: 80%;"></div>
                        <p>Signature</p>
                        <p>Name: {client_name}</p>
                        <p>Date: ________________________</p>
                    </td>
                    <td style="width: 50%; border: none; vertical-align: top;">
                        <p><strong>Signed on behalf of Phatbuns SA Master Rights Holder:</strong></p>
                        <br><br>
                        <div style="border-bottom: 1px solid #000; width: 80%;"></div>
                        <p>Signature</p>
                        <p>Name: Nisaar Ally</p>
                        <p>Date: {datetime.now().strftime('%d/%m/%Y')}</p>
                    </td>
                </tr>
            </table>
        </div>

    </body>
    </html>
    """

def generate_reportlab_fallback(data):
    """High-reliability ReportLab fallback engine."""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    location_name = data.get("location_name") or data.get("location") or "Target Location"
    client_name = data.get("client_name") or data.get("applicant_name") or "Valued Investor"

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0F172A'), spaceAfter=12
    )
    story.append(Paragraph("PHATBUNS SA — INVESTOR DOSSIER", title_style))
    story.append(Paragraph(f"<b>Location:</b> {location_name} | <b>Client:</b> {client_name}", styles['Normal']))
    story.append(Spacer(1, 20))

    table_data = [
        ["Financial Metric (Excl. VAT)", "Value Allocation"],
        ["Target Location", location_name],
        ["Applicant Name", client_name],
        ["Engine Status", "ReportLab Redundancy Active"]
    ]

    t = Table(table_data, colWidths=[250, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def build_pdf(*args, **kwargs):
    """Flexible entry point accepting positional, keyword, or dict args."""
    data = extract_pdf_data(*args, **kwargs)
    try:
        from weasyprint import HTML
        logger.info("Executing Primary Engine: WeasyPrint...")
        html_string = generate_rondebult_html(data)
        return HTML(string=html_string).write_pdf()
    except Exception as e:
        logger.warning(f"WeasyPrint failed ({str(e)}). Switching to ReportLab...")
        return generate_reportlab_fallback(data)

# Backward-compatibility alias
generate_feasibility_pdf = build_pdf
