# fishing_catch_reader.py 
import os
import time
import re
from PIL import ImageGrab
import numpy as np
import cv2
from talon import Module, actions, cron
import pytesseract
from . import fishing_state as state
from . import fishing_config as cfg

mod = Module()

TESS_CMD = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
if os.path.exists(TESS_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESS_CMD

CATCH_REGIONS = {
    "name":   {"x": 1264, "y": 934,  "w": 904, "h": 51},
    "weight": {"x": 1280, "y": 1006, "w": 250, "h": 72},
    "length": {"x": 1595, "y": 1006, "w": 238, "h": 72},
    "price":  {"x": 1897, "y": 1006, "w": 285, "h": 72},
}

FP_DISCARD_KEYWORDS = [
    "horn", "wort", "lily", "pad", "pond", "salv", "pistia", "victoria", "amazon",
    "reed", "sedge", "bulrush", "sawgrass", "moss", "coral", "backlash",
    "boot", "shoe", "rag", "bag", "stick", "bark", "shell", "turtle",
    "crayfish", "weed", "trash", "snag", "object", "item"
]

if not hasattr(state, 'session_catch_log'):
    state.session_catch_log = []
if not hasattr(state, 'session_total_earnings'):
    state.session_total_earnings = 0.0
if not hasattr(state, 'session_total_weight'):
    state.session_total_weight = 0.0

def clean_and_read_text(region_box: dict, debug_name: str = "") -> str:
    try:
        x, y, w, h = region_box["x"], region_box["y"], region_box["w"], region_box["h"]
        cap = ImageGrab.grab(bbox=(x, y, x + w, y + h), all_screens=True).convert("L")
        img = np.array(cap)
        
        img_resized = cv2.resize(img, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        _, thresh = cv2.threshold(img_resized, 120, 255, cv2.THRESH_BINARY_INV)
        
        if debug_name:
            dump_path = os.path.join(os.path.dirname(__file__), f"debug_catch_{debug_name}.png")
            cv2.imwrite(dump_path, thresh)

        text = pytesseract.image_to_string(thresh, config="--psm 6").strip()
        return text
    except Exception as e:
        print(f"[fishing] OCR Extraction failed for {debug_name}: {e}")
        return ""

def parse_numeric_value(text: str) -> float:
    if not text:
        return 0.0
    clean_str = re.sub(r"[A-Za-z:;\|\n\r]", " ", text.replace(",", ""))
    matches = re.findall(r"[-+]?\d*\.\d+|\d+", clean_str)
    if matches:
        return float(matches[-1])
    return 0.0

@mod.action_class
class Actions:
    def fishing_process_catch_screen() -> None:
        """Extracts text and executes Keep/Discard."""
        print("[fishing] Processing Catch Screen Text inline...")
        
        name_text = clean_and_read_text(CATCH_REGIONS["name"], debug_name="name")
        weight_text = clean_and_read_text(CATCH_REGIONS["weight"], debug_name="weight")
        length_text = clean_and_read_text(CATCH_REGIONS["length"], debug_name="length")
        price_text = clean_and_read_text(CATCH_REGIONS["price"], debug_name="price")
        
        fish_name = name_text.replace("\n", " ").strip() if name_text else "Unknown Fish"
        weight_val = parse_numeric_value(weight_text)
        length_val = parse_numeric_value(length_text)
        price_val = parse_numeric_value(price_text)
        
        record = {
            "time": time.strftime("%H:%M:%S"),
            "name": fish_name,
            "weight": f"{weight_val:.3f} kg" if weight_val > 0 else "0.000 kg",
            "length": f"{length_val:.1f} cm" if length_val > 0 else "0.0 cm",
            "price": price_val
        }
        
        state.session_catch_log.append(record)
        if len(state.session_catch_log) > 50:
            state.session_catch_log.pop(0)
            
        state.session_total_weight += weight_val
        state.session_total_earnings += price_val
        
        print(f"[fishing] Logged Catch: {fish_name} | {record['weight']} | {record['length']} | {price_val} cr")
        
        is_discard_keyword = any(kw in fish_name.lower() for kw in FP_DISCARD_KEYWORDS)
        is_zero_price = (price_val == 0)

        if is_discard_keyword or is_zero_price:
            print(f"[fishing] Trash detected ({fish_name}). Hitting backspace to discard...")
            actions.key("backspace")
        else:
            print(f"[fishing] Valid catch ({fish_name}). Hitting space to collect...")
            actions.key("space:down")
            cron.after("80ms", lambda: actions.key("space:up"))
            cron.after("1500ms", lambda: actions.key("space"))
        
        if hasattr(state, 'valid_action_performed'):
            state.valid_action_performed = False
            
        delay = getattr(cfg, 'POST_KEEP_DELAY', "5000ms")
        cron.after(delay, lambda: actions.user.fishing_cast_rod())

    def fishing_debug_catch_reader() -> None:
        """Manual test trigger."""
        print("\n─── Executing Manual Catch Screen OCR Test ───")
        name_text = clean_and_read_text(CATCH_REGIONS["name"], debug_name="name")
        weight_text = clean_and_read_text(CATCH_REGIONS["weight"], debug_name="weight")
        length_text = clean_and_read_text(CATCH_REGIONS["length"], debug_name="length")
        price_text = clean_and_read_text(CATCH_REGIONS["price"], debug_name="price")
        
        print(f"Extracted Raw Name:   '{name_text.strip()}'")
        w_val = parse_numeric_value(weight_text)
        l_val = parse_numeric_value(length_text)
        p_val = parse_numeric_value(price_text)
        print(f"Parsed -> Weight: {w_val} | Length: {l_val} | Price: {p_val}")
        
        fish_name = name_text.replace("\n", " ").strip() if name_text else "Unknown"
        is_kw = any(kw in fish_name.lower() for kw in FP_DISCARD_KEYWORDS)
        print(f"Action -> {'DISCARD (backspace)' if (is_kw or p_val == 0) else 'KEEP (space)'}")
        print("──────────────────────────────────────────────\n")
