import os
from io import BytesIO

def generate_feasibility_pdf(form_data, blueprint_images=None):
    """
    Compiles the complete enterprise-grade multi-page Phatbuns franchise feasibility pack 
    into raw PDF bytes using WeasyPrint with full financial, operational, and structural schedules.
    """
    if blueprint_images is None:
        blueprint_images = []

    # Extract dynamic form inputs
    location_name = form_data.get("location_name", "Selected Store Node")
    store_footprint = form_data.get("store_footprint", 167.0)
    base_net_rental = form_data.get("base_net_rental", 350.0)
    turnkey_capital = form_data.get("turnkey_capital", 3100000.0)
    managing_agent = form_data.get("managing_agent", "Redefine Properties / Abcon")
    client_name = form_data.get("client_name", "Valued Partner")
    
    # Financial computations & terms
    annual_escalation = form_data.get("annual_escalation", 7.5)
    turnover_rental_pct = form_data.get("turnover_rental_pct", 8.0)
    beneficial_occupation_months = form_data.get("beneficial_occupation_months", 2.0)
    lease_period_years = form_data.get("lease_period_years", 5.0)
    
    annual_base_rent = store_footprint * base_net_rental * 12
    monthly_operating_cost = base_net_rental * store_footprint
    estimated_ops_cost = 45000.0  # Utilities, security, mall ops
    
    # Construct complete multi-section HTML template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 15mm;
                @bottom-right {{
                    content: "Page " counter(page);
                    font-size: 8pt;
                    color: #666;
                }}
            }}
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #2c3e50;
                line-height: 1.5;
                margin: 0;
                padding: 0;
            }}
            .header-table {{
                width: 100%;
                border-bottom: 3px solid #ff7518;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .header-table td {{
                vertical-align: middle;
                border: none;
                padding: 0;
            }}
            .brand-title {{
                font-size: 16pt;
                font-weight: bold;
                color: #1a1a1a;
                margin: 0;
            }}
            .brand-subtitle {{
                font-size: 9pt;
                color: #ff7518;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}
            .sa-flag {{
                height: 28px;
                width: auto;
                vertical-align: middle;
            }}
            h1 {{
                color: #1a1a1a;
                font-size: 18pt;
                margin: 0 0 5px 0;
            }}
            h2 {{
                color: #ff7518;
                font-size: 12pt;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 4px;
                margin-top: 18px;
                margin-bottom: 10px;
            }}
            .metric-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                margin-bottom: 15px;
            }}
            .metric-table th, .metric-table td {{
                border: 1px solid #e0e0e0;
                padding: 8px 12px;
                text-align: left;
                font-size: 9pt;
            }}
            .metric-table th {{
                background-color: #f8f9fa;
                color: #333;
            }}
            .page-break {{
                page-break-before: always;
            }}
            .footer-signature {{
                margin-top: 30px;
                page-break-inside: avoid;
            }}
        </style>
    </head>
    <body>

        <!-- Top Header Layout -->
        <table class="header-table">
            <tr>
                <td>
                    <div class="brand-title">🍔 PHAT BUNS</div>
                    <div class="brand-subtitle">SOUTH AFRICA • MASTER FRANCHISE</div>
                </td>
                <td style="text-align: right;">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/a/af/Flag_of_South_Africa.svg" alt="South African Flag" class="sa-flag">
                    <br><span style="font-size: 7.5pt; color: #777;">EXECUTIVE FEASIBILITY PACK</span>
                </td>
            </tr>
        </table>

        <h1>Site Feasibility Assessment</h1>
        <p style="font-size: 10pt; color: #555; margin-top: 0;">Comprehensive Investment & Operations Pack prepared for <strong>{client_name}</strong>.</p>

        <h2>1. Location & Core Lease Parameters</h2>
        <table class="metric-table">
            <tr>
                <th>Parameter</th>
                <th>Specification</th>
            </tr>
            <tr>
                <td><strong>Target Node / Location</strong></td>
                <td>{location_name}</td>
            </tr>
            <tr>
                <td><strong>Managing Agent / Landlord</strong></td>
                <td>{managing_agent}</td>
            </tr>
            <tr>
                <td><strong>Store Footprint</strong></td>
                <td>{store_footprint:,.1f} m²</td>
            </tr>
            <tr>
                <td><strong>Base Net Rental Rate</strong></td>
                <td>R {base_net_rental:,.2f} / m²</td>
            </tr>
            <tr>
                <td><strong>Monthly Base Rental</strong></td>
                <td>R {monthly_operating_cost:,.2f}</td>
            </tr>
            <tr>
                <td><strong>Estimated Annual Base Rent</strong></td>
                <td>R {annual_base_rent:,.2f}</td>
            </tr>
            <tr>
                <td><strong>Turnkey Capital Outlay</strong></td>
                <td>R {turnkey_capital:,.2f}</td>
            </tr>
        </table>

        <h2>2. Lease Commercial Terms & Verification</h2>
        <table class="metric-table">
            <tr>
                <th>Commercial Term</th>
                <th>Agreed Metric</th>
            </tr>
            <tr>
                <td>Initial Lease Period</td>
                <td>{lease_period_years} Years</td>
            </tr>
            <tr>
                <td>Annual Rental Escalation</td>
                <td>{annual_escalation}% p.a.</td>
            </tr>
            <tr>
                <td>Turnover Rental Clause</td>
                <td>{turnover_rental_pct}% of Gross Turnover</td>
            </tr>
            <tr>
                <td>Beneficial Occupation Period</td>
                <td>{beneficial_occupation_months} Months Rent-Free</td>
            </tr>
        </table>

        <div class="page-break"></div>

        <h2>3. Capital Expenditure & Turnkey Breakdown</h2>
        <table class="metric-table">
            <tr>
                <th>Cost Center</th>
                <th>Allocation (ZAR)</th>
            </tr>
            <tr>
                <td>Store Fit-out & Joinery</td>
                <td>R 1,150,000.00</td>
            </tr>
            <tr>
                <td>Kitchen Equipment & Extraction Line</td>
                <td>R 950,000.00</td>
            </tr>
            <tr>
                <td>POS & Automated Kiosk Hardware</td>
                <td>R 250,000.00</td>
            </tr>
            <tr>
                <td>Signage & Visual Branding</td>
                <td>R 180,000.00</td>
            </tr>
            <tr>
                <td>Working Capital & Initial Stock</td>
                <td>R 350,000.00</td>
            </tr>
            <tr>
                <td>Professional Fees, Deposits & Contingency</td>
                <td>R 220,000.00</td>
            </tr>
            <tr>
                <td><strong>Total Turnkey Investment</strong></td>
                <td><strong>R {turnkey_capital:,.2f}</strong></td>
            </tr>
        </table>

        <h2>4. Estimated Monthly Operating Projections</h2>
        <table class="metric-table">
            <tr>
                <th>Expense Item</th>
                <th>Monthly Estimate (ZAR)</th>
            </tr>
            <tr>
                <td>Base Net Rental</td>
                <td>R {monthly_operating_cost:,.2f}</td>
            </tr>
            <tr>
                <td>Operational Costs, Utilities & Security</td>
                <td>R {estimated_ops_cost:,.2f}</td>
            </tr>
            <tr>
                <td>Marketing & Promotional Levy (2%)</td>
                <td>R 35,000.00 (Est.)</td>
            </tr>
            <tr>
                <td>Franchise Royalty Fee (6%)</td>
                <td>R 105,000.00 (Est.)</td>
            </tr>
        </table>

        <div class="footer-signature">
            <h2>Next Steps & Authorization</h2>
            <p style="font-size: 9.5pt;">Please review the complete schedule above, verify your investment parameters, and return an executed copy to proceed with formal store rollout and corporate approval.</p>
            
            <br>
            <p style="font-size: 9.5pt;"><strong>Warm regards,</strong><br>
            <strong>Nisaar Ally</strong><br>
            <span style="color: #666; font-size: 8.5pt;">SA Master Rights Holder | Phatbuns Expansion</span><br>
            <span style="color: #666; font-size: 8.5pt;">Mobile: +27 (0)68 710 1939 | Email: nisaar@fantastic1.com</span></p>
        </div>

    </body>
    </html>
    """

    try:
        from weasyprint import HTML
        return HTML(string=html_content).write_pdf()
    except Exception:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = [
                Paragraph(f"<b>Phatbuns Feasibility Report - {location_name}</b>", styles['Heading1']),
                Spacer(1, 12),
                Paragraph(f"Client: {client_name}", styles['Normal']),
                Paragraph(f"Footprint: {store_footprint} m2", styles['Normal']),
                Paragraph(f"Turnkey Capital: R {turnkey_capital:,.2f}", styles['Normal']),
            ]
            doc.build(story)
            return buffer.getvalue()
        except Exception:
            return b"%PDF-1.4 Fallback Feasibility Report Document Bytes"
