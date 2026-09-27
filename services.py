def extract_legacy_pdf_parameters(pdf_file_bytes):
    extracted_data = {}
    if not HAS_PYPDF:
        return extracted_data
    
    try:
        reader = PdfReader(io.BytesIO(pdf_file_bytes))
        full_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
            
        # Flexible Regex matchers for legacy layouts
        loc_match = re.search(r"(?:Location|Site|Mall)\s*(?:Name)?[:\|\-]?\s*([^\n\(]+)", full_text, re.IGNORECASE)
        if loc_match:
            extracted_data["location_name"] = loc_match.group(1).strip()
            
        shop_match = re.search(r"(?:Shop|Unit|Store)\s*([0-9A-Za-z\-]+)", full_text, re.IGNORECASE)
        if shop_match:
            extracted_data["shop_code"] = shop_match.group(1).strip()

        gla_match = re.search(r"(\d+(?.\d+)?)\s*(?:m²|sqm|sq m)", full_text, re.IGNORECASE)
        if gla_match:
            extracted_data["internal_gla"] = float(gla_match.group(1))

        rent_match = re.search(r"R\s*([\d,]+(?:\.\d+)?)\s*/\s*(?:m²|sqm)", full_text, re.IGNORECASE)
        if rent_match:
            extracted_data["int_rent"] = float(rent_match.group(1).replace(",", ""))

        cap_match = re.search(r"(?:Turnkey|Capital|Setup)\s*(?:Cost)?[:\|\-]?\s*R\s*([\d,]+)", full_text, re.IGNORECASE)
        if cap_match:
            extracted_data["turnkey_capital"] = float(cap_match.group(1).replace(",", ""))

        wc_match = re.search(r"(?:Working Capital)\s*[:\|\-]?\s*R\s*([\d,]+)", full_text, re.IGNORECASE)
        if wc_match:
            extracted_data["working_capital"] = float(wc_match.group(1).replace(",", ""))

    except Exception as e:
        print(f"PDF Parsing Exception: {e}")
        
    return extracted_data
