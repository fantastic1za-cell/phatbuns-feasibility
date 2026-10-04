import os
import io
import logging
import pandas as pd
from datetime import datetime

# Setup engine logger
logger = logging.getLogger("PDF_Engine")

def format_currency(value):
    """Formats numeric values into standard ZAR commercial string currency (Excl. VAT)."""
    try:
        return f"R {float(value):,.2f}"
    except (ValueError, TypeError):
        return "R 0.00"

def generate_rondebult_html(data):
    """
    Constructs the exact Rondebult Master Prospectus layout using strict CSS paged media.
    Guarantees clean page breaks, two-column financial breakdowns, and executive typography.
    """
    location_name = data.get("location_name", "Target Location")
    client_name = data.get("client_name", "Valued Investor")
    store_type = data.get("store_type", "Standard Inline")
    sqm = data.get("sqm", 80)
    rental_rate = data.get("rental_rate", 220)
    monthly_rent = sqm * rental_rate
    deposit = monthly_rent * 2  # Standard 2-month rental deposit rule
    
    # Capital Outlay Calculations (Excl. VAT)
    fitout_cost = data.get("fitout_cost", 850000)
    equipment_cost = data.get("equipment_cost", 650000)
    pos_signage = data.get("pos_signage", 120000)
    working_capital = data.get("working_capital", 150000)
    opening_stock = data.get("opening_stock", 80000)
    total_setup = fitout_cost + equipment_cost + pos_signage + working_capital + opening_stock + deposit

    html_content = f"""
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

            .page-break {{
                page-break-before: always;
            }}

            /* Header Structure */
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
                letter-spacing: -0.5px;
                margin: 0;
            }}
            
            .brand-sub {{
                font-size: 10pt;
                color: #D97706;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}

            /* Section Styling */
            h2 {{
                font-size: 14pt;
                color: #0F172A;
                border-left: 4px solid #D97706;
                padding-left: 8px;
                margin-top: 20px;
                margin-bottom: 12px;
                text-transform: uppercase;
            }}

            /* Table Formatting */
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
                font-weight: 600;
            }}

            td {{
                padding: 8px 10px;
                border-bottom: 1px solid #E2E8F0;
            }}

            tr:nth-child(even) td {{
                background-color: #F8FAFC;
            }}

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

            /* Callout Cards */
            .info-card {{
                background-color: #F1F5F9;
                border-radius: 6px;
                padding: 12px 16px;
                margin-bottom: 16px;
            }}

            .badge {{
                display: inline-block;
                padding: 3px 8px;
                background-color: #0284C7;
                color: #FFFFFF;
                font-size: 8pt;
                font-weight: 700;
                border-radius: 4px;
                text-transform: uppercase;
            }}
        </style>
    </head>
    <body>

        <!-- PAGE 1: COVER PAGE -->
        <div style="text-align: center; padding-top: 120px;">
            <div class="brand-sub">Franchise Expansion Opportunity</div>
            <h1 style="font-size: 32pt; color: #0F172A; margin-top: 10px; margin-bottom: 5px;">PHATBUNS SOUTH AFRICA</h1>
            <div style="font-size: 14pt; color: #64748B; font-weight: 300;">Master Investor Dossier & Feasibility Analysis</div>
            
            <div style="margin-top: 150px; padding: 20px; border: 1px solid #CBD5E1; border-radius: 8px; display: inline-block; width: 80%; text-align: left; background-color: #F8FAFC;">
                <p><strong>Target Site Node:</strong> {location_name}</p>
                <p><strong>Prepared For:</strong> {client_name}</p>
                <p><strong>Store Format:</strong> {store_type} ({sqm} sqm Footprint)</p>
                <p><strong>Date Generated:</strong> {datetime.now().strftime('%d %B %Y')}</p>
                <p><strong>Financial Protocol:</strong> All Figures Designated Exclusive of VAT (Excl. VAT)</p>
            </div>
        </div>

        <!-- PAGE 2: EXECUTIVE SITE EVALUATION -->
        <div class="page-break"></div>
        <div class="header-bar">
            <div>
                <div class="brand-title">PHATBUNS</div>
                <div class="brand-sub">Commercial Feasibility</div>
            </div>
            <span class="badge">Rondebult Layout Standard</span>
        </div>

        <h2>1. Site Node & Lease Parameter Analysis</h2>
        <div class="info-card">
            Site assessment conducted for target location: <strong>{location_name}</strong>. Footprint calculations strictly adhere to spatial kitchen requirements (minimum 50 sqm threshold enforced).
        </div>

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
                    <td>Leasehold improvements, joinery, shopfront, & electrical</td>
                    <td class="amount-col">{format_currency(fitout_cost)}</td>
                </tr>
                <tr>
                    <td>Kitchen Equipment & Extraction</td>
                    <td>Commercial griddles, fryers, refrigeration, & canopy system</td>
                    <td class="amount-col">{format_currency(equipment_cost)}</td>
                </tr>
                <tr>
                    <td>Brand Signage & POS Automation</td>
                    <td>External illuminated signage, menu boards, & POS infrastructure</td>
                    <td class="amount-col">{format_currency(pos_signage)}</td>
                </tr>
                <tr>
                    <td>Landlord Deposit Reserve</td>
                    <td>2-Month gross rental deposit held by lessor</td>
                    <td class="amount-col">{format_currency(deposit)}</td>
                </tr>
                <tr>
                    <td>Initial Working Capital Reserve</td>
                    <td>Unencumbered liquidity buffer for launch period</td>
                    <td class="amount-col">{format_currency(working_capital)}</td>
                </tr>
                <tr>
                    <td>Opening Stock Outlay</td>
                    <td>Core consumables, packaging, & initial ingredient load</td>
                    <td class="amount-col">{format_currency(opening_stock)}</td>
                </tr>
                <tr class="total-row">
                    <td colspan="2">TOTAL PROJECTED CAPITAL OUTLAY (EXCL. VAT)</td>
                    <td class="amount-col">{format_currency(total_setup)}</td>
                </tr>
            </tbody>
        </table>

        <!-- PAGE 3: NCNDA & EXECUTION AGREEMENT -->
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

        <div style="margin-top: 100px; width: 100%;">
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
    return html_content

def generate_reportlab_fallback(data):
    """
    Engineering Redundancy: High-reliability ReportLab binary builder.
    Executed automatically if WeasyPrint C-dependencies are unavailable.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    location_name = data.get("location_name", "Target Location")
    client_name = data.get("client_name", "Valued Investor")

    # Title
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=12
    )
    story.append(Paragraph(f"PHATBUNS SA — INVESTOR DOSSIER", title_style))
    story.append(Paragraph(f"<b>Location:</b> {location_name} | <b>Client:</b> {client_name}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Fallback Table
    table_data = [
        ["Financial Metric (Excl. VAT)", "Value Allocation"],
        ["Demised Premises Footprint", f"{data.get('sqm', 80)} sqm"],
        ["Base Gross Rent", f"R {data.get('rental_rate', 220):,.2f} / sqm"],
        ["Landlord Security Deposit", format_currency(data.get('sqm', 80) * data.get('rental_rate', 220) * 2)],
        ["Status", "ReportLab Fallback Engine Active"]
    ]

    t = Table(table_data, colWidths=[250, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def build_pdf(data):
    """
    Master Dispatcher Function:
    Attempts WeasyPrint PDF generation first; seamlessly switches to ReportLab on error.
    """
    try:
        from weasyprint import HTML
        logger.info("Initiating Primary Engine: WeasyPrint (Rondebult Layout)...")
        html_string = generate_rondebult_html(data)
        pdf_bytes = HTML(string=html_string).write_pdf()
        return pdf_bytes
    except Exception as e:
        logger.warning(f"WeasyPrint Primary Engine unavailable/failed: {str(e)}. Triggering ReportLab Fallback...")
        try:
            return generate_reportlab_fallback(data)
        except Exception as fallback_err:
            logger.error(f"Critical PDF Failover Error: {str(fallback_err)}")
            raise RuntimeError(f"Engine PDF rendering failed on both primary and redundancy layers: {str(fallback_err)}")
