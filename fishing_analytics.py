# fishing_analytics.py
import time
from talon import actions, cron
from . import fishing_state as state
from . import fishing_config as cfg
from . import fishing_vision as vision

def analytics_check_loop() -> None:
    """Synchronous background loop managing retrieve tracking and endpoint verification."""

    # ─── GENERATION GUARD ───
    # Capture the generation counter at the moment this tick starts running.
    # If fishing_enable_analytics_persistent() fires while we are mid-tick it
    # will increment loop_generation.  When we reach the finally block our
    # saved value will no longer match, so we simply do not reschedule —
    # killing the old loop cleanly without needing to cancel a cron handle.
    my_generation = state.loop_generation

    try:
        # ─── 1. ALWAYS READ TELEMETRY FIRST ───
        dist = vision.read_meter_distance()
        if dist is not None:
            if hasattr(state, 'distance_history'):
                state.distance_history.append((time.time(), dist))
                if len(state.distance_history) > 10:
                    state.distance_history.pop(0)
            state.current_distance = dist

        # Handle inline Keep screen buffering safely
        if getattr(state, 'current_mode', '') == "KEEP_SCREEN_WAIT":
            if time.time() - getattr(state, 'keep_detect_time', 0) >= 1.5:
                state.current_mode = "RECASTING"
                actions.user.fishing_process_catch_screen()
            return

        # ─── 2. CASTING PROTECTION ───
        is_recently_cast = (time.time() - getattr(state, 'cast_time', 0) < 5.0)
        if getattr(state, 'current_mode', '') in ["CASTING", "CAST FLIGHT"] or is_recently_cast:
            state.heavy_tension_start = None
            state.last_tension_time = time.time()
            return

        # Read line tension viewports safely
        low_tension, high_tension = vision.check_line_tension()
        state.low_tension = low_tension
        state.high_tension = high_tension
        
        if low_tension or high_tension:
            state.last_tension_time = time.time()

        # ─── 3. ACTIVE COMBAT STATE MACHINE ───
        if getattr(state, 'is_hooked', False) or getattr(state, 'current_mode', '') == "FIGHTING":
            if vision.check_orange_button():
                actions.user.fishing_stop_h_loop()
                state.current_mode = "KEEP_SCREEN_WAIT"
                state.keep_detect_time = time.time()
                return

            time_since_tension = time.time() - getattr(state, 'last_tension_time', time.time())
            if time_since_tension > 2.5:
                state.is_hooked = False
                state.is_pulling = False  # FIX: always clear pulling flag when fight ends
                actions.key("h:up")
                actions.user.fishing_resume_last_preset()
                return
            
            actions.user.fishing_handle_precise_fight_internal(low_tension, high_tension)
            return

        # ─── 4. GENUINE STRIKE VERIFICATION ───
        if high_tension:
            if not getattr(state, 'heavy_tension_start', None):
                state.heavy_tension_start = time.time()
            else:
                if time.time() - state.heavy_tension_start >= 0.8:
                    state.is_hooked = True
                    state.running = True
                    state.current_mode = "FIGHTING"
                    state.heavy_tension_start = None
                    actions.user.fishing_handle_precise_fight_internal(low_tension, high_tension)
                    return
        else:
            state.heavy_tension_start = None

        if not getattr(state, 'running', False) or getattr(state, 'current_mode', '') == "IDLE":
            return

        # ─── 5. RETRIEVE ENDPOINT LOGIC ───
        is_at_shoreline = (dist is not None and dist <= 1) or (dist is None and getattr(state, 'current_mode', '') == "REEL STEADY FAST")
        has_valid_action = getattr(state, 'valid_action_performed', False)

        if is_at_shoreline and has_valid_action:
            if vision.check_orange_button():
                print("[fishing] 0m Reached & Orange Screen verified! Transitioning to reader...")
                actions.user.fishing_stop_h_loop()
                state.current_mode = "KEEP_SCREEN_WAIT"
                state.keep_detect_time = time.time()
                return
            else:
                if not hasattr(state, 'shore_endpoint_ticks'):
                    state.shore_endpoint_ticks = 0
                state.shore_endpoint_ticks += 1
                
                # Force clean recast if we sit at shoreline dead-weight for 1.4 seconds
                if state.shore_endpoint_ticks >= 7:
                    state.shore_endpoint_ticks = 0
                    actions.user.fishing_stop_h_loop()
                    cron.after("1500ms", lambda: actions.user.fishing_smart_recast())
                return
        else:
            state.shore_endpoint_ticks = 0

        if dist is not None and 1 < dist <= 6:
            if getattr(state, 'current_mode', '') != "REEL STEADY FAST":
                actions.user.fishing_reel_steady_fast()

    except Exception as e:
        print(f"[fishing] Handled telemetry error safely: {e}")
    finally:
        # Only reschedule if we are still the active generation.
        # If fishing_enable_analytics_persistent() was called while this tick
        # was running, loop_generation will have been incremented and my_generation
        # will no longer match — so we silently drop this loop instead of
        # creating a second one running alongside the new one.
        if state.loop_generation == my_generation:
            state.recast_job = cron.after(cfg.ANALYTICS_FREQUENCY, analytics_check_loop)