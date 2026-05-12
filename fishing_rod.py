# fishing_rod.py
import time
import os
from talon import Module, actions, cron
from . import fishing_state as state
from . import fishing_analytics as analytics
from . import fishing_vision as vision

mod = Module()

def _cancel_local_timers():
    """Locally purges active cadences to stabilize hardware control interfaces."""
    state.running = False
    state.is_pulling = False
    if getattr(state, 'loop_job', None):
        try: cron.cancel(state.loop_job)
        except Exception: pass
        state.loop_job = None


@mod.action_class
class Actions:
    def fishing_cast_rod() -> None:
        """Executes core physical casting deployment phases from a clean stance."""
        _cancel_local_timers()
        try: actions.user.fishing_stop_color_detect()
        except Exception: pass
        
        # Forcefully release right-click aiming states alongside keyboard triggers
        actions.mouse_release(1)
        actions.mouse_release(0)
        for k in ["h", "space", "shift", "e"]:
            actions.key(f"{k}:up")

        state.current_distance = None
        state.valid_action_performed = True  
        if hasattr(state, 'distance_history'):
            state.distance_history.clear()

        state.cast_time = time.time()
        state.current_mode = "CASTING"
        state.running = True
        state.is_running = True
        
        # Tiny physical buffer to ensure interface drops aim before holding space
        time.sleep(0.1)
        
        try: actions.user.fishing_start_color_detect()
        except Exception: pass

        # Analytics started AFTER cast begins so it cannot re-trigger reel_steady_fast
        actions.user.fishing_enable_analytics_persistent()
        print("[fishing] Deployed physical line cast sequence cleanly.")

    def fishing_smart_recast() -> None:
        """Evaluates operational phases to conditionally fire line casting commands."""
        if getattr(state, 'current_mode', '') in ["KEEP_SCREEN_WAIT", "RECASTING"]:
            return
        actions.user.fishing_cast_rod()

    def fishing_hook_fish_event() -> None:
        """Executes physical hook set mechanics natively."""
        actions.key("h:down")
        cron.after("400ms", lambda: actions.key("h:up"))
        state.running = True
        state.is_running = True
        state.is_hooked = True
        state.valid_action_performed = True

    def fishing_stop_h_loop() -> None:
        """Executes targeted state and physical loop cancelations with absolute mouse un-keying."""
        _cancel_local_timers()
        state.is_hooked = False
        state.auto_resume = False
        state.heavy_tension_start = None
        state.current_mode = "IDLE"
        
        actions.mouse_release(1)
        actions.mouse_release(0)
        
        for k in ["h", "space", "shift", "e"]:
            actions.key(f"{k}:up")
            
        try: actions.user.fishing_stop_color_detect()
        except Exception: pass

    def fishing_enable_analytics_persistent() -> None:
        """Authorizes telemetry tracking logic over interface routines."""
        if getattr(state, 'recast_job', None):
            try: cron.cancel(state.recast_job)
            except Exception: pass
            
        state.shore_endpoint_ticks = 0
        state.heavy_tension_start = None
        state.recast_job = cron.after("100ms", analytics.analytics_check_loop)

    def fishing_disable_analytics_persistent() -> None:
        """Terminates active metrics scanning tasks directly."""
        if getattr(state, 'recast_job', None):
            try: cron.cancel(state.recast_job)
            except Exception: pass
            state.recast_job = None

    def fishing_debug_ocr_region() -> None:
        """Captures distance mapping bounding coordinates cleanly to disk."""
        from PIL import ImageGrab
        l, t, w, h = vision.METER_REGION["x"], vision.METER_REGION["y"], vision.METER_REGION["w"], vision.METER_REGION["h"]
        img = ImageGrab.grab(bbox=(l, t, l+w, t+h), all_screens=True)
        img.save(os.path.join(os.path.dirname(__file__), "debug_ocr_region.png"))
        print("[fishing] Debug distance telemetry snapshot saved.")

    def fishing_show_vision_debug() -> None:
        """Renders HUD visualization mappings globally."""
        try: vision.toggle_vision_debug(True)
        except Exception: pass

    def fishing_hide_vision_debug() -> None:
        """Hides HUD visualization mappings globally."""
        try: vision.toggle_vision_debug(False)
        except Exception: pass
