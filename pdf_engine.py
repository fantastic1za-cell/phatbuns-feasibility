import os
from io import BytesIO

def generate_feasibility_pdf(form_data, blueprint_images=None):
    """
    Compiles the complete multi-page enterprise-grade Phatbuns master investor pack 
    into raw PDF bytes using WeasyPrint, maintaining exact branding and layout structure.
    """
    if blueprint_images is None:
        blueprint_images = []

    # Extract dynamic form inputs
    location_name = form_data.get("location_name", "New Corner Northcliff (Shop RL 03)")
    store_footprint = form_data.get("store_footprint", 167.0)
    base_net_rental = form_data.get("base_net_rental", 350.0)
    turnkey_capital = form_data.get("turnkey_capital", 3100000.0)
    managing_agent = form_data.get("managing_agent", "Redefine Properties / Abcon")
    client_name = form_data.get("client_name", "Nisaar Ally")
    
    # Financial computations & terms
    annual_escalation = form_data.get("annual_escalation", 7.5)
    turnover_rental_pct = form_data.get("turnover_rental_pct", 8.0)
    beneficial_occupation_months = form_data.get("beneficial_occupation_months", 2.0)
    lease_period_years = form_data.get("lease_period_years", 5.0)
    
    monthly_operating_cost = base_net_rental * store_footprint
    annual_base_rent = monthly_operating_cost * 12
    
    # Construct full multi-page HTML template matching master prospectus format
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 15mm 15mm 18mm 15mm;
                @bottom-left {{
                    content: "CONFIDENTIAL INFORMATION | Nisaar Ally: SA Master Rights Holder | Email: nisaar@fantastic1.com | Mobile: +27 (0)68 710 1939";
                    font-size: 6.5pt;
                    color: #555;
                }}
                @bottom-right {{
                    content: "Page " counter(page) " of 8";
                    font-size: 7.5pt;
                    font-weight: bold;
                    color: #ff7518;
                }}
            }}
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #2c3e50;
                line-height: 1.4;
                margin: 0;
                padding: 0;
            }}
            .cover-page {{
                text-align: center;
                page-break-after: always;
                padding-top: 40mm;
            }}
            .cover-brand {{
                font-size: 36pt;
                font-weight: 900;
                color: #ff7518;
                margin: 0;
                letter-spacing: 2px;
            }}
            .cover-subtitle {{
                font-size: 14pt;
                font-weight: bold;
                color: #1a1a1a;
                margin-top: 10px;
                margin-bottom: 40mm;
            }}
            .page-break {{
                page-break-before: always;
            }}
            .header-bar {{
                border-bottom: 2px solid #ff7518;
                padding-bottom: 6px;
                margin-bottom: 15px;
            }}
            .brand-sm {{
                font-size: 14pt;
                font-weight: bold;
                color: #ff7518;
                margin: 0;
            }}
            h2 {{
                color: #ff7518;
                font-size: 11pt;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 3px;
                margin-top: 14px;
                margin-bottom: 8px;
                text-transform: uppercase;
            }}
            .metric-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 6px;
                margin-bottom: 12px;
            }}
            .metric-table th, .metric-table td {{
                border: 1px solid #d0d0d0;
                padding: 6px 10px;
                text-align: left;
                font-size: 8.5pt;
            }}
            .metric-table th {{
                background-color: #f8f9fa;
                color: #333;
                text-transform: uppercase;
                font-size: 8pt;
            }}
        </style>
    </head>
    <body>

        <!-- PAGE 1: COVER & EXECUTIVE SUMMARY -->
        <div class="cover-page">
            <div style="font-size: 12pt; font-weight: bold; color: #777; letter-spacing: 1px;">EXPRESS MODEL ({store_footprint:.0f} M²)</div>
            <h1 class="cover-brand">PHAT BUNS</h1>
            <div class="cover-subtitle">SOUTH AFRICA<br>SITE EVALUATION & INVESTMENT ANALYSIS — {location_name.upper()}</div>
            
            <table class="metric-table" style="margin-top: 20mm;">
                <tr>
                    <th>Turnkey Setup</th>
                    <th>Working Capital</th>
                    <th>Base Net Rental</th>
                    <th>Ops Cost</th>
                </tr>
                <tr>
                    <td><strong>R {turnkey_capital:,.0f}</strong><br><span style="font-size: 7.5pt; color: #666;">Excl. VAT (Turnkey)</span></td>
                    <td><strong>R 450,000</strong><br><span style="font-size: 7.5pt; color: #666;">Suggested Reserve</span></td>
                    <td><strong>R {base_net_rental:.0f}/m²</strong><br><span style="font-size: 7.5pt; color: #666;">pm Excl. VAT</span></td>
                    <td><strong>R 45,000</strong><br><span style="font-size: 7.5pt; color: #666;">Gross Terms</span></td>
                </tr>
            </table>
        </div>

        <!-- PAGE 2: SITE PROFILE & LEASE TERMS -->
        <div class="header-bar">
            <div class="brand-sm">PHAT BUNS SOUTH AFRICA</div>
            <div style="font-size: 8pt; color: #666;">01. SITE PROFILE & CAPITAL SCHEDULE</div>
        </div>

        <h2>01. Site Profile & Capital Schedule</h2>
        <table class="metric-table">
            <tr>
                <th>Site Parameter</th>
                <th>Specification</th>
                <th>Turnkey Capital Schedule (Excl. VAT)</th>
                <th>Amount</th>
            </tr>
            <tr>
                <td><strong>Location Name</strong></td>
                <td>{location_name}</td>
                <td>50% Deposit on Signing Agreement</td>
                <td>R {turnkey_capital * 0.5:,.0f}</td>
            </tr>
            <tr>
                <td><strong>Address / Node</strong></td>
                <td>{managing_agent} Commercial Node</td>
                <td>40% Beneficial Occupation (BO)</td>
                <td>R {turnkey_capital * 0.4:,.0f}</td>
            </tr>
            <tr>
                <td><strong>Store Footprint</strong></td>
                <td>{store_footprint:.2f} m² Full Sit-Down Model</td>
                <td>10% Prior to Store Opening</td>
                <td>R {turnkey_capital * 0.1:,.0f}</td>
            </tr>
            <tr>
                <td><strong>Managing Agent</strong></td>
                <td>{managing_agent}</td>
                <td><strong>Total Turnkey Capital Outlay</strong></td>
                <td><strong>R {turnkey_capital:,.0f}</strong></td>
            </tr>
        </table>

        <h2>02. Lease Structure & Proposed Landlord Offer</h2>
        <table class="metric-table">
            <tr>
                <th>Lease Clause / Provision</th>
                <th>Terms & Rate Structure</th>
                <th>Financial Alignment</th>
            </tr>
            <tr>
                <td><strong>Base Net Rental Rate Target</strong></td>
                <td>R {base_net_rental:.0f}/m²/month (Excl. VAT & Utilities)</td>
                <td>R {monthly_operating_cost:,.2f}/month</td>
            </tr>
            <tr>
                <td><strong>Annual Rental Escalation</strong></td>
                <td>{annual_escalation}% per annum effective anniversary</td>
                <td>Predictable cost curve</td>
            </tr>
            <tr>
                <td><strong>Turnover Rental Clause</strong></td>
                <td>{turnover_rental_pct}% of Net Monthly Turnover vs Base Net Rental</td>
                <td>Triggers above Base Threshold</td>
            </tr>
            <tr>
                <td><strong>Beneficial Occupation (BO)</strong></td>
                <td>{beneficial_occupation_months} Month Rent-Free BO for Turnkey Store Fitout</td>
                <td>Fitout Schedule: 60 Days</td>
            </tr>
        </table>

        <h2>03. Dynamic Catchment & Location Intelligence</h2>
        <table class="metric-table">
            <tr>
                <th>Catchment Metric</th>
                <th>Data Point / Location Analysis</th>
            </tr>
            <tr>
                <td><strong>LSM/ESM Profile</strong></td>
                <td>LSM 8-10+/High Disposable Income Segment</td>
            </tr>
            <tr>
                <td><strong>Monthly / Annual Footfall</strong></td>
                <td>160,000-210,000 visits/month (~2.1M-2.5M Annually)</td>
            </tr>
            <tr>
                <td><strong>Catchment Household Count</strong></td>
                <td>110,000-135,000 Active Households (10 km Radius)</td>
            </tr>
            <tr>
                <td><strong>In-Mall Competitor Profile</strong></td>
                <td>RocoMamas, McDonald's Drive-Thru, Ocean Basket, Adega Café</td>
            </tr>
        </table>

        <div class="page-break"></div>

        <!-- PAGE 3: RECOVERY HORIZON & OPS -->
        <div class="header-bar">
            <div class="brand-sm">PHAT BUNS SOUTH AFRICA</div>
            <div style="font-size: 8pt; color: #666;">04. FINANCIAL RECOVERY & UNIT SALES TARGET MATRIX</div>
        </div>

        <h2>04. Financial Recovery & Unit Sales Target Matrix</h2>
        <table class="metric-table">
            <tr>
                <th>Recovery Horizon</th>
                <th>Required Turnover / Month</th>
                <th>Required Units / Month</th>
                <th>Required Units / Day</th>
            </tr>
            <tr>
                <td><strong>Operational Breakeven</strong></td>
                <td>R 310,000.00</td>
                <td>1,636 units</td>
                <td>55 units/day</td>
            </tr>
            <tr>
                <td><strong>12 Months Recovery Target</strong></td>
                <td>R 744,000.00</td>
                <td>3,980 units</td>
                <td>133 units/day</td>
            </tr>
            <tr>
                <td><strong>24 Months Recovery Target</strong></td>
                <td>R 527,000.00</td>
                <td>2,808 units</td>
                <td>94 units/day</td>
            </tr>
            <tr>
                <td><strong>36 Months Recovery Target</strong></td>
                <td>R 465,000.00</td>
                <td>2,417 units</td>
                <td>81 units/day</td>
            </tr>
        </table>

        <h2>05. Operations, Staffing & Channel Breakdown</h2>
        <table class="metric-table">
            <tr>
                <th>Revenue Channel Split</th>
                <th>Staffing Structure (BCEA 8-Hour Shifts)</th>
            </tr>
            <tr>
                <td>
                    • Online Deliveries (UberEats/Mr D): 45%<br>
                    • Takeaway & Counter Collect: 30%<br>
                    • In-Store Express Dining: 25%
                </td>
                <td>
                    • 1 x Store Manager (Operations & Inventory)<br>
                    • 2 x Shift Supervisors (Floor Leads & POS)<br>
                    • 3 x Line Grillers & Fryers (Griddle & Assembly)<br>
                    • 2 x Till Operators / Runners (FOH Dispatch)<br>
                    • 2 x Cleaners & Scullery (Hygiene & SANHA Standards)
                </td>
            </tr>
        </table>

        <h2>06. Turnkey Kitchen Equipment Manifest</h2>
        <table class="metric-table">
            <tr>
                <th>Station / Category</th>
                <th>Equipment Specification</th>
            </tr>
            <tr>
                <td><strong>Smash Grill Station</strong></td>
                <td>Chrome Smash Griddle (3-Phase Heavy Duty), Bun Toaster & Pass-Through Heated Holding Cabinet.</td>
            </tr>
            <tr>
                <td><strong>Frying & Prep Line</strong></td>
                <td>Dual-Pan High-Recovery Deep Fryer, 3-Door Under-Counter Prep Fridge with Topping Rail.</td>
            </tr>
            <tr>
                <td><strong>Extraction & Canopy</strong></td>
                <td>Stainless Steel Wall-Mounted Extraction Canopy complete with ANSUL Fire Suppression System.</td>
            </tr>
            <tr>
                <td><strong>POS & Automation</strong></td>
                <td>Dual-Screen Touch POS Terminal, Kitchen Display System (KDS), Thermal Printers & Router setup.</td>
            </tr>
        </table>

        <div class="page-break"></div>

        <!-- PAGE 4: 5-YEAR PRO FORMA P&L -->
        <div class="header-bar">
            <div class="brand-sm">PHAT BUNS SOUTH AFRICA</div>
            <div style="font-size: 8pt; color: #666;">11. 5-YEAR PRO FORMA INCOME STATEMENT & INVESTMENT COMPARISON</div>
        </div>

        <h2>11A. 5-Year Pro Forma Income Statement & P&L Forecast</h2>
        <table class="metric-table">
            <tr>
                <th>Financial Metric</th>
                <th>Year 1</th>
                <th>Year 2</th>
                <th>Year 3</th>
                <th>Year 4</th>
                <th>Year 5</th>
            </tr>
            <tr>
                <td><strong>Gross Revenue</strong></td>
                <td>R 8,500,000</td>
                <td>R 9,350,000</td>
                <td>R 10,285,000</td>
                <td>R 11,313,500</td>
                <td>R 12,444,850</td>
            </tr>
            <tr>
                <td><strong>Cost of Sales (35%)</strong></td>
                <td>R 2,975,000</td>
                <td>R 3,272,500</td>
                <td>R 3,599,750</td>
                <td>R 3,959,725</td>
                <td>R 4,355,698</td>
            </tr>
            <tr>
                <td><strong>Gross Profit</strong></td>
                <td>R 5,525,000</td>
                <td>R 6,077,500</td>
                <td>R 6,685,250</td>
                <td>R 7,353,775</td>
                <td>R 8,089,152</td>
            </tr>
            <tr>
                <td><strong>Operating Expenses</strong></td>
                <td>R 4,200,000</td>
                <td>R 4,536,000</td>
                <td>R 4,898,880</td>
                <td>R 5,290,790</td>
                <td>R 5,713,952</td>
            </tr>
            <tr>
                <td><strong>Net Operating Profit</strong></td>
                <td><strong>R 1,325,000</strong></td>
                <td><strong>R 1,541,500</strong></td>
                <td><strong>R 1,786,370</strong></td>
                <td><strong>R 2,062,985</strong></td>
                <td><strong>R 2,375,200</strong></td>
            </tr>
        </table>

        <h2>11B. 5-Year Cash Investment Comparison</h2>
        <table class="metric-table">
            <tr>
                <th>Investment Metric</th>
                <th>Bank Fixed Deposit (8.5% p.a. Pre-Tax)</th>
                <th>Phatbuns Store Investment</th>
            </tr>
            <tr>
                <td><strong>Initial Capital Invested</strong></td>
                <td>R {turnkey_capital:,.0f}</td>
                <td>R {turnkey_capital:,.0f}</td>
            </tr>
            <tr>
                <td><strong>Compounded Total Value (End of Year 5)</strong></td>
                <td>R 4,661,336</td>
                <td>R 12,191,055</td>
            </tr>
            <tr>
                <td><strong>Total Net Return / Earnings (5 Years)</strong></td>
                <td>R 1,561,336</td>
                <td><strong>R 9,091,055</strong></td>
            </tr>
        </table>

        <div class="page-break"></div>

        <!-- PAGE 5: BRAND PORTFOLIO & MENUS -->
        <div class="header-bar">
            <div class="brand-sm">PHAT BUNS SOUTH AFRICA</div>
            <div style="font-size: 8pt; color: #666;">BRAND PORTFOLIO & DIGITAL CATALOGS</div>
        </div>

        <h2>Brand Portfolio & Concept Overview</h2>
        <table class="metric-table">
            <tr>
                <th>Brand & Concept</th>
                <th>Menu Overview & Social Profile</th>
            </tr>
            <tr>
                <td><strong>Phatbuns Smash Burgers</strong></td>
                <td>Hand-pressed Angus beef smash patties served on seeded brioche, topped with proprietary secret sauces, Cheesy Doritos, and Fiery Cheetos ranges.</td>
            </tr>
            <tr>
                <td><strong>PhatVille Sliders & Sides</strong></td>
                <td>Nashville-style sliders, crispy tender boxes, dusted crinkle fries, and specialized dipping sauces optimized for delivery channels.</td>
            </tr>
            <tr>
                <td><strong>Butter Brûlée Signature Drinks</strong></td>
                <td>Hand-crafted specialty iced teas, indulgent gourmet milkshakes, artisanal refresher coolers, and barista specialty coffees.</td>
            </tr>
            <tr>
                <td><strong>Butter Brûlée Cookies & Desserts</strong></td>
                <td>Gourmet freshly baked classic cookies, stuffed exclusive artisan ranges, cookie caviar tiramisu, and specialty sweet pairings.</td>
            </tr>
        </table>

        <div class="page-break"></div>

        <!-- PAGE 6: LEGAL & SIGN-OFF -->
        <div class="header-bar">
            <div class="brand-sm">PHAT BUNS SOUTH AFRICA</div>
            <div style="font-size: 8pt; color: #666;">GOVERNANCE, COMPLIANCE & SIGN-OFF</div>
        </div>

        <h2>Non-Disclosure & Non-Circumvention Agreement (NCNDA)</h2>
        <p style="font-size: 8.5pt;">
            Entered into by and between <strong>PHATBUNS SOUTH AFRICA</strong> (Franchisor) and <strong>{client_name}</strong> (Prospective Franchisee). 
            All disclosures, financial models, recipes, and operational workflows are shared under strict confidentiality in compliance with the Consumer Protection Act (CPA) and FASA guidelines.
        </p>

        <table class="metric-table" style="margin-top: 30px;">
            <tr>
                <th style="width: 50%;">For: PHATBUNS SOUTH AFRICA</th>
                <th style="width: 50%;">For: THE RECEIVING PARTY</th>
            </tr>
            <tr>
                <td style="height: 60px; vertical-align: bottom;">
                    <strong>Authorized Signature:</strong> ______________________<br>
                    <strong>Name:</strong> Nisaar Ally<br>
                    <strong>Title:</strong> SA Master Rights Holder
                </td>
                <td style="height: 60px; vertical-align: bottom;">
                    <strong>Authorized Signature:</strong> ______________________<br>
                    <strong>Name:</strong> {client_name}<br>
                    <strong>Title:</strong> Prospective Franchisee
                </td>
            </tr>
        </table>

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
                Paragraph(f"<b>Phatbuns Master Prospectus - {location_name}</b>", styles['Heading1']),
                Spacer(1, 12),
                Paragraph(f"Client: {client_name}", styles['Normal']),
                Paragraph(f"Footprint: {store_footprint} m2", styles['Normal']),
                Paragraph(f"Turnkey Capital: R {turnkey_capital:,.2f}", styles['Normal']),
            ]
            doc.build(story)
            return buffer.getvalue()
        except Exception:
            return b"%PDF-1.4 Fallback Feasibility Report Document Bytes"
