# config.py - Central Configuration & Dictionaries
import os
import re

# Directory Setup
ASSETS_DIR = os.path.join(os.getcwd(), "assets")
MENUS_DIR = os.path.join(ASSETS_DIR, "menus")
LOCATIONS_DIR = os.path.join(os.getcwd(), "Locations")

# Brand Menus & Social Catalog
BRAND_MENU_CATALOG = {
    "Phatbuns Smash Burgers": {
        "logo_key": "phatbuns_sa",
        "filename": "Phatbuns_Smash_Burger_Main_Menu.pdf",
        "drive_file_id": "1Goe4yS1E5R0KiZt6N_cQ4HcCad9OUJgr",
        "tagline": "Artisan Smash Burgers & Signature Buns",
        "description": "Hand-pressed Angus beef smash patties served on seeded brioche, topped with proprietary secret sauces, Cheesy Doritos, Fiery Cheetos ranges, and buttermilk fried chicken.",
        "instagram_url": "https://www.instagram.com/phatbuns.uk?stkn=d2Q0MTEweDliOXhr"
    },
    "PhatVille Sliders & Sides": {
        "logo_key": "phatville",
        "filename": "Phatbuns_Menu_2_Sliders_and_Sides.pdf",
        "drive_file_id": "1lLGjL73SJeRfXXJKFl0a8ZnhfFQb1ich",
        "tagline": "Nashville Hot Sliders & Loaded Sides",
        "description": "Nashville-style sliders, crispy tender boxes, dusted crinkle fries, and specialized dipping sauces optimized for rapid kitchen assembly and delivery channels.",
        "instagram_url": "https://www.instagram.com/phatville?stkn=MTBoeDExOXFicDgybg=="
    },
    "Butter Brûlée Signature Drinks": {
        "logo_key": "butter_brulee",
        "filename": "Butter_Brulee_Signature_Drinks.pdf",
        "drive_file_id": "1dUxvPSZTyWfbjDXRxuBNFhFSOYc5ctWc",
        "tagline": "Signature Beverages & Artisanal Mocktails",
        "description": "Hand-crafted specialty iced teas, indulgent gourmet milkshakes, artisanal refresher coolers, and barista specialty coffees designed to complement sweet and savory offerings.",
        "instagram_url": "https://www.instagram.com/butterbrulee?stkn=dnZnMG1paGdoYW1k"
    },
    "Butter Brûlée Cookies & Desserts": {
        "logo_key": "butter_brulee",
        "filename": "Butter_Brulee_Classic_Exclusive_Cookies.pdf",
        "drive_file_id": "1nc1I7_-bLZkq4oJDE5wHwic8DZ8QCVxE",
        "tagline": "Classic & Exclusive Artisanal Cookies",
        "description": "Gourmet freshly baked classic cookies, stuffed exclusive artisan ranges, cookie caviar tiramisu, and specialty sweet pairings engineered for high average ticket yield.",
        "instagram_url": "https://www.instagram.com/butterbrulee?stkn=dnZnMG1paGdoYW1k"
    },
    "Butter Brûlée Seasonal Specials": {
        "logo_key": "butter_brulee",
        "filename": "Butter_Brulee_Seasonal_Menu_Item.pdf",
        "drive_file_id": "1OaWyRBwvoQQX-OZMQNlbdpXBgXQaFAZs",
        "tagline": "Luxury Milk Cakes, Seasonal Specials & Fine Shakes",
        "description": "Artisanal seasonal dessert offerings, caramelized french toast, pistachio kunafa treats, and high-margin signature drinks.",
        "instagram_url": "https://www.instagram.com/butterbrulee?stkn=dnZnMG1paGdoYW1k"
    },
    "Doorstep Desserts": {
        "logo_key": "doorstep",
        "filename": "Doorstep_Desserts_Artisan_Catalog.pdf",
        "drive_file_id": "1rghEVeNi5SRgy9NbTVp6UwbHgn_4pSHY",
        "tagline": "Gourmet Warm Desserts, Waffles & Sundaes",
        "description": "Indulgent double-stick waffle sticks, freshly baked dough tubs, Lotus Biscoff crunch cakes, gelato sundaes, and dessert delivery boxes.",
        "instagram_url": "https://www.instagram.com/doorstep.dessertsuk?stkn=MWFwd3gzaWQ3NGppNg=="
    }
}

STORE_MEDIA_LINKS = {
    "store_photos": "https://drive.google.com/file/d/1qbJ6kvaBxja2gBWoaoHLWme0MEA1omOH/view?usp=drivesdk",
    "uk_video_1": "https://drive.google.com/file/d/1txmElx_qkUeY6gJS8P5h7Diqoa_uRGr7/view?usp=drivesdk",
    "dubai_video": "https://drive.google.com/file/d/1mH-4NOQpqCv8oeft0FjOV-6JSjGfT1VK/view?usp=drivesdk",
    "uk_video_2": "https://drive.google.com/file/d/1XYpOF-_aKlzcEgaUouhE8Ewlvdpn7nFI/view?usp=drivesdk",
    "master_folder": "https://drive.google.com/drive/folders/1ql6WibMHHNn_EeEpfB7ol8u9n3LdPImZ"
}

LOCATION_LOOKUP = {
    "Custom / Other Site...": "",
    "Rondebuilt Centre": "Germiston, Ekurhuleni, Gauteng",
    "Cedar Square": "Fourways, Johannesburg, Gauteng",
    "Clearwater Mall": "Strubensvalley, Roodepoort, Gauteng",
    "Campus Square": "Auckland Park, Johannesburg, Gauteng",
    "Sandton City Shopping Centre": "Sandton Central, Johannesburg, Gauteng",
    "Mall of Africa": "Waterfall City, Midrand, Gauteng"
}

SITE_PROFILES = {
    "Rondebuilt Centre": {
        "suburb": "Germiston, Ekurhuleni, Gauteng",
        "shop": "79",
        "landlord": "Vegieland Properties (Pty) Ltd",
        "mall_size": "23,275 m² Community Centre",
        "footfall": "~380,000 visits/month (~4.5M Annually)",
        "households": "24,061 Active Households / ~76,995 Area Population",
        "competitors": "Shoprite, Boxer, Build-It Flagship, Debonairs, Wimpy, Pedro's, Hungry Lion, Clicks, Pep, Ackermans, Capitec",
        "lsm_profile": "LSM 6–9 / Established Commercial & Industrial Corridor",
        "default_rent": 220.0,
        "default_ops": 32.50,
        "default_gla": 98.0,
        "model": "Express Model",
        "turnover_clause_pct": 7.0
    },
    "Cedar Square": {
        "suburb": "Fourways, Johannesburg, Gauteng",
        "shop": "CS12",
        "landlord": "Redefine Properties",
        "mall_size": "12,000 m² Lifestyle & Entertainment Centre",
        "footfall": "~550,000 visits/month (~6.6 Million Annually)",
        "households": "95,000 Active Households (10 km Radius)",
        "competitors": "Tiger's Milk, Panarottis, Mugg & Bean, Nando's, Salsa Mexican Grill",
        "lsm_profile": "LSM 8–10+ / Upscale Lifestyle Precinct",
        "default_rent": 300.0,
        "default_ops": 45.0,
        "default_gla": 80.0,
        "model": "Express Model",
        "turnover_clause_pct": 7.0
    },
    "Clearwater Mall": {
        "suburb": "Strubensvalley, Roodepoort, Gauteng",
        "shop": "UM017B",
        "landlord": "Hyprop Investments Ltd",
        "mall_size": "86,000 m² Regional Flagship",
        "footfall": "~700,000 visits/month (~9.8 Million Annually)",
        "households": "125,000–145,000 Active Households (10 km Radius)",
        "competitors": "Burger King, Panarottis, Steers, Debonairs, Mochachos, Ocean Basket",
        "lsm_profile": "LSM 8–10+ / High Purchasing Power Suburb",
        "default_rent": 181.0,
        "default_ops": 50.0,
        "default_gla": 252.0,
        "model": "Multi-Brand Kitchen Model",
        "turnover_clause_pct": 6.0
    }
}

STORE_MODELS = {
    "Kiosk Model": {
        "size_range": "20 - 60 sqm",
        "turnkey_capital": 850000.0,
        "working_capital": 250000.0,
        "est_monthly_turnover": 350000.0,
        "labor_monthly": 45000.0,
        "foh_pct": 0.00,
        "default_gla": 40.0,
        "min_footfall_req": 300000,
        "ideal_lsm": "LSM 6-10+"
    },
    "Express Model": {
        "size_range": "40 - 90 sqm",
        "turnkey_capital": 2500000.0,
        "working_capital": 450000.0,
        "est_monthly_turnover": 650000.0,
        "labor_monthly": 85000.0,
        "foh_pct": 0.10,
        "default_gla": 70.0,
        "min_footfall_req": 500000,
        "ideal_lsm": "LSM 7-10+"
    },
    "Full Sit-Down Model": {
        "size_range": "100 - 160 sqm",
        "turnkey_capital": 3250000.0,
        "working_capital": 750000.0,
        "est_monthly_turnover": 950000.0,
        "labor_monthly": 125000.0,
        "foh_pct": 0.40,
        "default_gla": 120.0,
        "min_footfall_req": 650000,
        "ideal_lsm": "LSM 8-10+"
    },
    "Multi-Brand Kitchen Model": {
        "size_range": "100 - 160 sqm",
        "turnkey_capital": 3500000.0,
        "working_capital": 700000.0,
        "est_monthly_turnover": 1100000.0,
        "labor_monthly": 135000.0,
        "foh_pct": 0.40,
        "default_gla": 130.0,
        "min_footfall_req": 700000,
        "ideal_lsm": "LSM 8-10+"
    },
}

SEASONAL_FACTORS = [0.90, 1.00, 1.00, 1.15, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.05, 1.25]
