import os
from io import BytesIO
from weasyprint import HTML

def generate_feasibility_pdf(form_data, blueprint_images=None):
    """
    Compiles the enterprise-grade multi-page Phatbuns franchise feasibility pack 
    into raw PDF bytes using WeasyPrint, ensuring uniform logo and flag scaling.
    """
    if blueprint_images is None:
        blueprint_images = []

    # Extract dynamic form inputs
    location_name = form_data.get("location_name", "Selected Store Node")
    store_footprint = form_data.get("store_footprint", 0.0)
    base_net_rental = form_data.get("base_net_rental", 0.0)
    turnkey_capital = form_data.get("turnkey_capital", 0.0)
    managing_agent = form_data.get("managing_agent", "N/A")
    client_name = form_data.get("client_name", "Valued Partner")
    
    # Financial computations
    annual_escalation = form_data.get("annual_escalation", 7.5)
    turnover_rental_pct = form_data.get("turnover_rental_pct", 8.0)
    beneficial_occupation_months = form_data.get("beneficial_occupation_months", 2.0)
    lease_period_years = form_data.get("lease_period_years", 5.0)
    
    annual_base_rent = store_footprint * base_net_rental * 12
    
    # Construct HTML template with uniform image dimensions for logo and flag
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 20mm;
                @bottom-right {{
                    content: "Page " counter(page);
                    font-size: 9pt;
                    color: #666;
                }}
            }}
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #2c3e50;
                line-height: 1.6;
                margin: 0;
                padding: 0;
            }}
            .header-container {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                border-bottom: 3px solid #ff7518;
                padding-bottom: 15px;
                margin-bottom: 25px;
            }}
            .brand-group {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            /* Uniform sizing for logo and flag to match perfectly */
            .brand-logo, .sa-flag {{
                height: 40px;
                width: auto;
                object-fit: contain;
            }}
            h1 {{
                color: #1a1a1a;
                font-size: 22pt;
                margin: 0;
            }}
            h2 {{
                color: #ff7518;
                font-size: 14pt;
                border-bottom: 1px solid #eee;
                padding-bottom: 5px;
                margin-top: 20px;
            }}
            .metric-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                margin-bottom: 25px;
            }}
            .metric-table th, .metric-table td {{
                border: 1px solid #e0e0e0;
                padding: 10px 14px;
                text-align: left;
                font-size: 10pt;
            }}
            .metric-table th {{
                background-color: #f8f9fa;
                color: #333;
            }}
            .footer-signature {{
                margin-top: 40px;
                page-break-inside: avoid;
            }}
        </style>
    </head>
    <body>

        <!-- Header with Logo and Flag aligned side-by-side at identical heights -->
        <div class="header-container">
            <div class="brand-group">
                <!-- Phatbuns SA Brand Logo -->
                <img src="https://i.ibb.co/1Z92138/phatbuns-logo.png" alt="Phatbuns SA Logo" class="brand-logo" onerror="this.style.display='none'">
                <!-- South African Flag scaled to match the exact height -->
                <img src="https://upload.wikimedia.org/wikipedia/commons/a/af/Flag_of_South_Africa.svg" alt="South African Flag" class="sa-flag">
            </div>
            <div style="text-align: right;">
                <span style="font-size: 10pt; font-weight: bold; color: #ff7518;">EXECUTIVE FEASIBILITY PACK</span><br>
                <span style="font-size: 8pt; color: #777;">Mr Mobile SA PTY LTD</span>
            </div>
        </div>

        <h1>Site Feasibility Assessment</h1>
        <p style="font-size: 11pt; color: #555;">Prepared for <strong>{client_name}</strong> regarding retail space expansion opportunities.</p>

        <h2>1. Location & Lease Parameters</h2>
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
                <td><strong>Estimated Annual Base Rent</strong></td>
                <td>R {annual_base_rent:,.2f}</td>
            </tr>
            <tr>
                <td><strong>Turnkey Capital Outlay</strong></td>
                <td>R {turnkey_capital:,.2f}</td>
            </tr>
        </table>

        <h2>2. Lease Commercial Terms</h2>
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

        <div class="footer-signature">
            <h2>Next Steps:</h2>
            <p>Please review the attached documentation, verify the financial metrics on page 1, and return an executed copy to proceed with formal store rollout and corporate approval.</p>
            <p>Should you have any questions or require modifications to the layout footprint, please feel free to reach out directly.</p>
            
            <br>
            <p><strong>Warm regards,</strong></p>
            <p>
                <strong>Nisaar Ally</strong><br>
                <span style="color: #666; font-size: 9pt;">SA Master Rights Holder | Phatbuns Expansion</span><br>
                <span style="color: #666; font-size: 9pt;">Mobile: +27 (0)68 710 1939 | Email: nisaar@fantastic1.com</span>
            </p>
        </div>

    </body>
    </html>
    """

    # Generate PDF bytes via WeasyPrint
    pdf_file_bytes = HTML(string=html_content).write_pdf()
    return pdf_file_bytes
