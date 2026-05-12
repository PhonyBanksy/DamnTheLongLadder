# fishing_loops.py
import time
from talon import Module, actions, cron
from . import fishing_state as state

mod = Module()

def _run_cadence_loop():
    """Executes continuous looping inputs for complex mechanical retrieve cadences."""
    if not getattr(state, 'running', False) or not getattr(state, 'is_running', False):
        return

    # ─── ABSOLUTE 0-METER LOCKOUT GUARD ───
    if getattr(state, 'current_distance', None) is not None and state.current_distance <= 0:
        actions.user.fishing_stop_h_loop()
        return

    excluded_modes = [
        "IDLE", "CASTING", "CAST FLIGHT", "RECASTING", 
        "KEEP_SCREEN_WAIT", "FIGHTING"
    ]
    if state.current_mode in excluded_modes:
        return

    mode = getattr(state, 'current_mode', '').replace("_", " ")
    speed = getattr(state, 'speed_multiplier', 1.0)
    
    if mode.startswith("WALK"):
        actions.key("space:down")
        actions.key("h:down")
        cron.after("100ms", lambda: actions.key("h:up"))
        interval = int(520 / speed)
        
    elif mode.startswith("TWITCH") or mode.startswith("WICK"):
        actions.key("space:down")
        actions.key("h:down")
        cron.after("80ms", lambda: actions.key("h:up"))
        interval = int(500 / speed)
        
    elif mode.startswith("POP"):
        actions.key("space:down")
        actions.key("h:down")
        cron.after("150ms", lambda: actions.key("h:up"))
        interval = int(800 / speed)
        
    elif mode.startswith("STOP GO"):
        actions.key("space:down")
        cron.after("400ms", lambda: actions.key("space:up"))
        interval = int(1000 / speed)
        
    elif mode.startswith("REEL IT"):
        actions.key("space:down")
        cron.after("500ms", lambda: actions.key("space:up"))
        interval = int(600 / speed)
    else:
        return

    state.loop_job = cron.after(f"{interval}ms", _run_cadence_loop)
    if hasattr(state, 'active_cron_jobs') and state.loop_job:
        state.active_cron_jobs.append(state.loop_job)


@mod.action_class
class Actions:
    def fishing_handle_precise_fight_internal(low_tension: bool, high_tension: bool) -> None:
        """Manages dynamic line tension logic natively during automated fights."""
        # ─── ABSOLUTE 0-METER LOCKOUT GUARD ───
        if getattr(state, 'current_distance', None) is not None and state.current_distance <= 0:
            actions.user.fishing_stop_h_loop()
            return
            
        actions.key("space:down")
        current_time = time.time()
        
        if high_tension:
            if not getattr(state, 'is_pulling', False):
                state.is_pulling = True
                state.pull_start_time = current_time
                actions.key("h:down")
            else:
                if current_time - getattr(state, 'pull_start_time', current_time) > 1.2:
                    actions.key("h:up")
                    state.is_pulling = False
        elif not low_tension:
            if not getattr(state, 'is_pulling', False):
                state.is_pulling = True
                state.pull_start_time = current_time
                actions.key("h:down")
        else:
            if getattr(state, 'is_pulling', False):
                actions.key("h:up")
                state.is_pulling = False

    def fishing_trigger_cadence_loop() -> None:
        """Public endpoint to initialize continuous execution loops safely."""
        _run_cadence_loop()
