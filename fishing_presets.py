# fishing_presets.py
from talon import Module, actions
from . import fishing_state as state

mod = Module()

@mod.action_class
class Actions:
    def fishing_start_preset(name: str) -> None:
        """Initializes targeted retrieval profile profiles cleanly."""
        actions.user.fishing_stop_h_loop()
        
        state.current_mode = name.upper().replace("_", " ")
        state.last_preset = name
        state.auto_resume = True 
        state.running = True
        state.is_running = True
        state.valid_action_performed = True  
        
        if not state.current_mode.startswith("STOP GO"):
            actions.key("space:down")
            
        actions.user.fishing_enable_analytics_persistent()
        print(f"[fishing] Preset Active: {state.current_mode}")
        actions.user.fishing_trigger_cadence_loop()

    def fishing_reel_steady() -> None:
        """Enables standard automated slow/steady retrieve profiles."""
        actions.user.fishing_stop_h_loop()
        state.current_mode = "REEL STEADY"
        state.last_preset = "reel steady"
        state.auto_resume = True
        state.running = True
        state.is_running = True
        state.valid_action_performed = True  
        
        actions.user.fishing_enable_analytics_persistent()
        print("[fishing] Preset Active: REEL STEADY")
        actions.key("space:down")

    def fishing_reel_steady_fast() -> None:
        """Enables high-speed surface retrieval profile macros."""
        # Guard: don't engage if we're already transitioning away from a retrieve
        if getattr(state, 'current_mode', '') in ["CASTING", "CAST FLIGHT", "RECASTING", "IDLE", "KEEP_SCREEN_WAIT"]:
            return

        actions.user.fishing_stop_h_loop()
        state.current_mode = "REEL STEADY FAST"
        state.running = True
        state.is_running = True
        state.valid_action_performed = True
        
        actions.key("space:down")
        actions.key("shift:down")
        actions.key("h:down")

    def fishing_resume_last_preset() -> None:
        """Restores recent operational retrieve macros programmatically."""
        preset = getattr(state, 'last_preset', None)
        if not preset:
            setattr(state, 'current_mode', 'IDLE')
            return
            
        if preset == "reel steady":
            actions.user.fishing_reel_steady()
        else:
            actions.user.fishing_start_preset(preset)

    def fishing_speed_increase() -> None:
        """Increments underlying execution frequency metrics."""
        state.speed_multiplier = round(getattr(state, 'speed_multiplier', 1.0) + 0.1, 1)
        print(f"[fishing] Speed modifier set to: {state.speed_multiplier}x")

    def fishing_speed_decrease() -> None:
        """Decrements underlying execution frequency metrics."""
        state.speed_multiplier = round(max(0.1, getattr(state, 'speed_multiplier', 1.0) - 0.1), 1)
        print(f"[fishing] Speed modifier set to: {state.speed_multiplier}x")

    def fishing_speed_reset() -> None:
        """Normalizes runtime execution rates directly."""
        state.speed_multiplier = 1.0
        print("[fishing] Speed modifier reset to base standard.")
