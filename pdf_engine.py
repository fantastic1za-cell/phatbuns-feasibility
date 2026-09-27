# pdf_engine.py - Production PDF Engine (Fail-Safe Site Profile Fallbacks)
import os
import io
import math
import re
from PIL import Image, ImageDraw

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from config import ASSETS_DIR, SITE_PROFILES, BRAND_MENU_CATALOG, STORE_MEDIA_LINKS

def find_file_in_assets(target_names):
    search_dirs = [ASSETS_DIR, os.getcwd()]
    targets_clean = [t.lower() for t in target_names]
    for d in search_dirs:
        if os.path.exists(d):
            for file in os.listdir(d):
                if file.lower() in targets_clean:
                    return os.path.join(d, file)
    return None

def get_asset_images_map():
    return {
        "phatbuns_sa": find_file_in_assets(["Phatbuns_SA.PNG", "phatbuns_sa.png"]),
        "phatville": find_file_in_assets(["Phatville.PNG", "phatville.png"]),
        "phatbuns": find_file_in_assets(["Phatbuns.PNG", "phatbuns.png"]),
        "butter_brulee": find_file_in_assets(["ButterBruleeLogo.PNG", "butterbrulee.png"]),
        "doorstep": find_file_in_assets(["Doorstep Logo.PNG", "doorstep.png"]),
        "sa_flag": find_file_in_assets(["SAFlag.PNG", "saflag.png", "sa_flag.png"]),
        "cover_bg": find_file_in_assets(["coverSA.JPG", "coversa.jpg", "cover.jpg", "Cover.JPG"])
    }

def create_cover_page_image():
    asset_map = get_asset_images_map()
    bg_path = asset_map.get("cover_bg")
    target_w, target_h = 2480, 3508 # A4 @ 300 DPI
    
    if bg_path and os.path.exists(bg_path):
        try:
            orig = Image.open(bg_path).convert("RGB")
            orig_w, orig_h = orig.size
            target_ratio = target_w / float(target_h)
            orig_ratio = orig_w / float(orig_h)
            
            if orig_ratio > target_ratio:
                new_w = int(orig_h * target_ratio)
                left = (orig_w - new_w) // 2
                crop_box = (left, 0, left + new_w, orig_h)
            else:
                new_h = int(orig_w / target_ratio)
                top = (orig_h - new_h) // 2
                crop_box = (0, top, orig_w, top + new_h)
                
            cropped = orig.crop(crop_box)
            bg_img = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
        except Exception:
            bg_img = Image.new("RGB", (target_w, target_h), color=(235, 120, 35))
    else:
        bg_img = Image.new("RGB", (target_w, target_h), color=(235, 120, 35))

    img_byte_arr = io.BytesIO()
    bg_img.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr.seek(0)
    return img_byte_arr

def create_aspect_ratio_rl_image(pil_img, max_width=500, max_height=320):
    orig_w, orig_h = pil_img.size
    aspect = orig_w / float(orig_h)

    if orig_w > orig_h:
        new_w = min(orig_w, max_width)
        new_h = new_w / aspect
        if new_h > max_height:
            new_h = max_height
            new_w = new_h * aspect
    else:
        new_h = min(orig_h, max_height)
        new_w = new_h * aspect
        if new_w > max_width:
            new_w = max_width
            new_h = new_w / aspect

    img_byte_arr = io.BytesIO()
    pil_img.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr.seek(0)
    return RLImage(io.BytesIO(img_byte_arr.getvalue()), width=new_w, height=new_h)

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            selfThe traceback in your screenshot points to a pandas `KeyError` happening right inside `pdf_engine.py` when building `sec3_banner` or reading `SITE_PROFILES`.

Specifically, `SITE_PROFILES` is being queried using `location_name` as a key. When an uploaded legacy file (or typed custom location) produces a site name string that doesn't match an exact dictionary key in `SITE_PROFILES`, looking it up directly raises a `KeyError`.

To fix this once and for all across the application, we will replace the lookup logic with fail-safe dictionary methods (`.get()`) and ensure pandas DataFrames use safe column checks.

---

### Step 1: Update `pdf_engine.py`

Open **`pdf_engine.py`** on GitHub, edit the file, and replace its contents with this updated script:

```python
# pdf_engine.py - Fail-Safe PDF Report Engine
import os
import io
import math
import re
from PIL import Image, ImageDraw

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from config import ASSETS_DIR, SITE_PROFILES, BRAND_MENU_CATALOG, STORE_MEDIA_LINKS

def find_file_in_assets(target_names):
    search_dirs = [ASSETS_DIR, os.getcwd()]
    targets_clean = [t.lower() for t in target_names]
    for d in search_dirs:
        if os.path.exists(d):
            for file in os.listdir(d):
                if file.lower() in targets_clean:
                    return os.path.join(d, file)
    return None

def get_asset_images_map():
    return {
        "phatbuns_sa": find_file_in_assets(["Phatbuns_SA.PNG", "phatbuns_sa.png"]),
        "phatville": find_file_in_assets(["Phatville.PNG", "phatville.png"]),
        "phatbuns": find_file_in_assets(["Phatbuns.PNG", "phatbuns.png"]),
        "butter_brulee": find_file_in_assets(["ButterBruleeLogo.PNG", "butterbrulee.png"]),
        "doorstep": find_file_in_assets(["Doorstep Logo.PNG", "doorstep.png"]),
        "sa_flag": find_file_in_assets(["SAFlag.PNG", "saflag.png", "sa_flag.png"]),
        "cover_bg": find_file_in_assets(["coverSA.JPG", "coversa.jpg", "cover.jpg", "Cover.JPG"])
    }

def create_cover_page_image():
    asset_map = get_asset_images_map()
    bg_path = asset_map.get("cover_bg")
    target_w, target_h = 2480, 3508 # A4 @ 300 DPI
    
    if bg_path and os.path.exists(bg_path):
        try:
            orig = Image.open(bg_path).convert("RGB")
            orig_w, orig_h = orig.size
            target_ratio = target_w / float(target_h)
            orig_ratio = orig_w / float(orig_h)
            
            if orig_ratio > target_ratio:
                new_w = int(orig_h * target_ratio)
                left = (orig_w - new_w) // 2
                crop_box = (left, 0, left + new_w, orig_h)
            else:
                new_h = int(orig_w / target_ratio)
                top = (orig_h - new_h) // 2
                crop_box = (0, top, orig_w, top + new_h)
                
            cropped = orig.crop(crop_box)
            bg_img = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
        except Exception:
            bg_img = Image.new("RGB", (target_w, target_h), color=(235, 120, 35))
    else:
        bg_img = Image.new("RGB", (target_w, target_h), color=(235, 120, 35))

    img_byte_arr = io.BytesIO()
    bg_img.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr.seek(0)
    return img_byte_arr

def create_aspect_ratio_rl_image(pil_img, max_width=500, max_height=320):
    orig_w, orig_h = pil_img.size
    aspect = orig_w / float(orig_h)

    if orig_w > orig_h:
        new_w = min(orig_w, max_width)
        new_h = new_w / aspect
        if new_h > max_height:
            new_h = max_height
            new_w = new_h * aspect
    else:
        new_h = min(orig_h, max_height)
        
