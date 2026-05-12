# fishing_detect_engine.py
from talon import canvas
from talon.types import Rect
from PIL import ImageGrab
import os

# ─── CAST BAR REGION ─────────────────────────────────────────────────────────
CAST_REGION = {"x": 3234, "y": 653, "w": 60, "h": 465}
RELEASE_AT_FILL = 0.80  # 80% full = release

# ─── COLOR DETECTION RANGES ──────────────────────────────────────────────────
FILL_COLOR_RANGES = [
    (120, 255, 120, 255,   0, 100),  # Top Amber / Olive / Yellow
    (  0, 160, 140, 255,   0, 120),  # Mid Green to Lime
    (  0, 100, 120, 255, 100, 255),  # Cyan / Teal gradient
    (  0,  80,   0, 180, 150, 255),  # Bottom Blue
]

overlay_canvas = None

def _draw_cast_box(c):
    c.paint.color = "00FF00"
    c.paint.style = c.paint.Style.STROKE
    c.paint.stroke_width = 3
    c.draw_rect(Rect(0, 0, CAST_REGION["w"], CAST_REGION["h"]))

def show_overlay():
    global overlay_canvas
    if overlay_canvas is None:
        x, y, w, h = CAST_REGION["x"], CAST_REGION["y"], CAST_REGION["w"], CAST_REGION["h"]
        overlay_canvas = canvas.Canvas(x, y, w, h)
        overlay_canvas.register("draw", _draw_cast_box)

def hide_overlay():
    global overlay_canvas
    if overlay_canvas:
        overlay_canvas.unregister("draw", _draw_cast_box)
        overlay_canvas.close()
        overlay_canvas = None

def is_fill_pixel(r, g, b) -> bool:
    """Returns True if an RGB pixel falls within the broad fill spectrum."""
    for (rmin, rmax, gmin, gmax, bmin, bmax) in FILL_COLOR_RANGES:
        if rmin <= r <= rmax and gmin <= g <= gmax and bmin <= b <= bmax:
            return True
    return False

def capture_bar():
    """Captures the defined bar region from the screen."""
    x, y, w, h = CAST_REGION["x"], CAST_REGION["y"], CAST_REGION["w"], CAST_REGION["h"]
    return ImageGrab.grab(bbox=(x, y, x + w, y + h), all_screens=True).convert("RGB")

def measure_fill(img) -> float:
    """Counts total filled rows based on a 30% row-width threshold."""
    width, height = img.size
    pixels = img.load()

    filled_rows = 0
    for row in range(height):
        fill_count = sum(
            1 for col in range(width)
            if is_fill_pixel(*pixels[col, row])
        )
        if fill_count / width >= 0.30:
            filled_rows += 1

    return filled_rows / height