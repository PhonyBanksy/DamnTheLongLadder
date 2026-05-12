# fishing_vision.py
import ctypes
from PIL import ImageGrab
import numpy as np
import cv2
import os
from typing import Optional, Tuple

try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception: 
    pass

# ─── SCREEN REGIONS ─────────────────────────────────────────────────────────
METER_REGION = {"x": 2913, "y": 1241, "w": 160, "h": 110}
KEEP_REGION = {"x": 1350, "y": 1100, "w": 650, "h": 350}

# Sub-region coordinates mapping specific indicator windows (40x10 each)
BAR_COORDS = {
    "bottom-left":   {"x": 3035, "y": 1018, "w": 40, "h": 10},
    "bottom-center": {"x": 3167, "y": 1018, "w": 40, "h": 10},
    "bottom-right":  {"x": 3300, "y": 1019, "w": 40, "h": 10},
    "top-left":      {"x": 3035, "y": 676,  "w": 40, "h": 10},
    "top-center":    {"x": 3167, "y": 676,  "w": 40, "h": 10},
    "top-right":     {"x": 3300, "y": 676,  "w": 40, "h": 10},
}

# Standard Line Tension (Cyan / Green spectrum)
CYAN_HSV_LOWER = np.array([40, 80, 80])
CYAN_HSV_UPPER = np.array([110, 255, 255])

# Heavy Tension Spikes (Bright Yellow / Warm Orange / Warm Red spectrum)
YELLOW_HSV_LOWER = np.array([0, 100, 100])
YELLOW_HSV_UPPER = np.array([35, 255, 255])

WHITE_THRESHOLD = 150  
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "fishing_debug")
templates: dict[str, np.ndarray] = {}

def load_templates() -> None:
    if templates: 
        return
    for i in range(10):
        t_path = os.path.join(TEMPLATE_DIR, f"{i}.png")
        if os.path.exists(t_path):
            img = cv2.imread(t_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                if img.shape[-1] == 4:
                    alpha = img[:, :, 3]
                    gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
                    gray[alpha == 0] = 0 
                    _, thresh_temp = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
                else:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    _, thresh_temp = cv2.threshold(gray, WHITE_THRESHOLD, 255, cv2.THRESH_BINARY)
                templates[str(i)] = thresh_temp

def read_meter_distance() -> Optional[int]:
    load_templates()
    try:
        l, t, w, h = METER_REGION["x"], METER_REGION["y"], METER_REGION["w"], METER_REGION["h"]
        cap = ImageGrab.grab(bbox=(l, t, l+w, t+h), all_screens=True).convert("L")
        img = np.array(cap)
        _, thresh = cv2.threshold(img, WHITE_THRESHOLD, 255, cv2.THRESH_BINARY)
        
        matches = []
        for d, temp in templates.items():
            res = cv2.matchTemplate(thresh, temp, cv2.TM_CCOEFF_NORMED)
            locs = np.where(res >= 0.80)
            for pt in zip(*locs[::-1]):
                matches.append({"digit": d, "x": pt[0], "score": res[pt[1], pt[0]]})
        
        if not matches: 
            return None
        matches = sorted(matches, key=lambda m: m["score"], reverse=True)
        clean = []
        for m in matches:
            if not any(abs(m["x"] - c["x"]) < 15 for c in clean): 
                clean.append(m)
        
        num_str = "".join(m["digit"] for m in sorted(clean, key=lambda m: m["x"]))
        if num_str:
            val = int(num_str)
            return val if val < 200 else None
        return None
    except Exception: 
        return None

def check_specific_bar(coords: dict[str, int], hsv_lower: np.ndarray, hsv_upper: np.ndarray) -> bool:
    try:
        x, y, w, h = coords["x"], coords["y"], coords["w"], coords["h"]
        cap = ImageGrab.grab(bbox=(x, y, x + w, y + h), all_screens=True).convert("RGB")
        img_bgr = cv2.cvtColor(np.array(cap), cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(img_hsv, hsv_lower, hsv_upper)
        total_pixels = w * h
        matching_pixels = cv2.countNonZero(mask)
        
        return bool((matching_pixels / total_pixels) >= 0.15)
    except Exception:
        return False

def check_line_tension() -> Tuple[bool, bool]:
    try:
        low_tension = (
            check_specific_bar(BAR_COORDS["bottom-left"],   CYAN_HSV_LOWER, CYAN_HSV_UPPER) or
            check_specific_bar(BAR_COORDS["bottom-center"], CYAN_HSV_LOWER, CYAN_HSV_UPPER) or
            check_specific_bar(BAR_COORDS["bottom-right"],  CYAN_HSV_LOWER, CYAN_HSV_UPPER)
        )
        
        high_tension = (
            check_specific_bar(BAR_COORDS["top-left"],   YELLOW_HSV_LOWER, YELLOW_HSV_UPPER) or
            check_specific_bar(BAR_COORDS["top-center"], YELLOW_HSV_LOWER, YELLOW_HSV_UPPER) or
            check_specific_bar(BAR_COORDS["top-right"],  YELLOW_HSV_LOWER, YELLOW_HSV_UPPER)
        )
        
        return low_tension, high_tension
    except Exception:
        return False, False

def check_orange_button() -> bool:
    try:
        l, t, w, h = KEEP_REGION["x"], KEEP_REGION["y"], KEEP_REGION["w"], KEEP_REGION["h"]
        cap = ImageGrab.grab(bbox=(l, t, l+w, t+h), all_screens=True).convert("RGB")
        img = np.array(cap)
        
        r_match = np.abs(img[..., 0].astype(int) - 240) <= 35
        g_match = np.abs(img[..., 1].astype(int) - 130) <= 35
        b_match = np.abs(img[..., 2].astype(int) - 20) <= 35
        
        return bool(np.sum(r_match & g_match & b_match) >= 200)
    except Exception:
        return False

def toggle_vision_debug(show: bool) -> None:
    pass