# fishing_detect_actions.py
from talon import Module, actions, cron
import time
import os
from . import fishing_state as state
from . import fishing_config as cfg
from . import fishing_detect_engine as engine

mod = Module()

def _scan_frame():
    if not getattr(state, 'detecting', False):
        return

    img = engine.capture_bar()
    fill = engine.measure_fill(img)

    if fill >= engine.RELEASE_AT_FILL: 
        actions.key("space:up")
        state.detecting = False
        engine.hide_overlay()
        
        state.cast_release_time = time.time()
        state.current_mode = "CAST FLIGHT"
        print(f"[fishing] RELEASED Spacebar at {fill*100:.1f}% fill")

        if getattr(state, 'last_preset', None):
            cron.after("2000ms", lambda: actions.user.fishing_resume_last_preset())
        else:
            cron.after("4500ms", lambda: setattr(state, 'current_mode', 'IDLE'))
        return

    cron.after("4ms", _scan_frame)

@mod.action_class
class Actions:
    def fishing_start_color_detect() -> None:
        """Holds space, shows overlay, and starts scanning the cast bar."""
        if getattr(state, 'detecting', False):
            return
        state.detecting = True
        state.current_mode = "CASTING"
        actions.key("space:down")
        engine.show_overlay()
        _scan_frame()

    def fishing_stop_color_detect() -> None:
        """Cancels detection, hides overlay, and releases spacebar cleanly."""
        state.detecting = False
        actions.key("space:up")
        engine.hide_overlay()

    def fishing_debug_snapshot() -> None:
        """Saves current bar capture to debug_cast_dump.png."""
        try:
            img = engine.capture_bar()
            fill = engine.measure_fill(img)
            save_path = os.path.join(os.path.dirname(__file__), "debug_cast_dump.png")
            img.save(save_path)
            print(f"[fishing] Snapshot saved. Fill: {fill*100:.1f}%")
        except Exception as e:
            print(f"[fishing] Snapshot failed: {e}")
