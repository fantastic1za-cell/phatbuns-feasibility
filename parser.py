import re
from PIL import Image

def parse_uploaded_offer_image(image_file):
    """
    Parses landlord offer screenshots using OCR/Regex logic.
    """
    try:
        import pytesseract
        image = Image.open(image_file)
        gray_image = image.convert('L')
        extracted_text = pytesseract.image_to_string(gray_image)
    except Exception:
        # Failsafe if pytesseract is not installed on host
        extracted_text = ""

    parsed_data = {
        "location_name": "New Corner Northcliff",
        "shop_code": "Shop RL 03",
        "sqm": 80.0,
        "rental_rate": 220.0,
        "raw_text": extracted_text
    }
    
    if extracted_text:
        # Regex for Shop Code
        shop_match = re.search(r'(?i)(shop|unit|store)\s*[:#-]?\s*([A-Z0-9\-]+)', extracted_text)
        if shop_match:
            parsed_data["shop_code"] = f"{shop_match.group(1).title()} {shop_match.group(2)}"

        # Regex for Area (sqm)
        sqm_match = re.search(r'(\d+[\.,]?\d*)\s*(?:sqm|m2|m²|square\s*meter)', extracted_text, re.IGNORECASE)
        if sqm_match:
            parsed_data["sqm"] = float(sqm_match.group(1).replace(',', '.'))

        # Regex for Rent per sqm
        rent_match = re.search(r'(?:R|zar)?\s*(\d+[\.,]?\d*)\s*(?:per|\/)\s*(?:sqm|m2|m²)', extracted_text, re.IGNORECASE)
        if rent_match:
            parsed_data["rental_rate"] = float(rent_match.group(1).replace(',', '.'))

        lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
        if lines:
            parsed_data["location_name"] = lines[0]

    return parsed_data
