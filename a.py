# fishing_calibration_hud.py
from talon import Module, actions, canvas, ui
from talon.skia import Paint, Rect
from . import fishing_catch_reader as reader

mod = Module()
calibration_canvas = None

def draw_calibration_regions(canvas):
    """Draws visual bounding boxes directly over the target OCR screen regions."""
    paint = Paint()
    
    # Loop through the regions defined in your catch reader
    for name, region in reader.CATCH_REGIONS.items():
        x = region["x"]
        y = region["y"]
        w = region["w"]
        h = region["h"]
        
        rect = Rect(x, y, w, h)
        
        # 1. Draw a semi-transparent background fill to highlight the target text area
        paint.color = "ffffff22"  # Translucent white overlay
        paint.style = Paint.Style.FILL
        canvas.draw_rect(rect, paint)
        
        # 2. Draw a highly visible border around the perimeter
        paint.color = "ff0000ff"  # Solid red border
        paint.style = Paint.Style.STROKE
        paint.stroke_width = 2
        canvas.draw_rect(rect, paint)
        
        # 3. Label the box in the top-left corner so you know which region is which
        paint.color = "ffffffff"  # Solid white text
        paint.style = Paint.Style.FILL
        paint.textsize = 14
        canvas.draw_text(name.upper(), x + 5, y + 15, paint)

@mod.action_class
class Actions:
    def fishing_show_calibration_hud():
        """Displays the pixel-locked OCR calibration overlay."""
        global calibration_canvas
        if calibration_canvas is None:
            # Create a full-screen transparent canvas overlay
            calibration_canvas = canvas.Canvas(ui.main_screen().x, ui.main_screen().y, ui.main_screen().width, ui.main_screen().height)
            calibration_canvas.register("draw", draw_calibration_regions)
            print("[fishing] Calibration HUD Enabled.")

    def fishing_hide_calibration_hud():
        """Hides the OCR calibration overlay."""
        global calibration_canvas
        if calibration_canvas is not None:
            calibration_canvas.unregister("draw", draw_calibration_regions)
            calibration_canvas.close()
            calibration_canvas = None
            print("[fishing] Calibration HUD Disabled.")