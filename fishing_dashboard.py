# fishing_dashboard.py
from talon import Module, actions, imgui
from . import fishing_state as state

mod = Module()

@imgui.open()
def gui_fishing_dashboard(gui: imgui.GUI):
    gui.text("🎣 Live Telemetry")
    gui.line()

    gui.text(f"Action:  {state.current_mode}")
    gui.text(f"Speed:   {state.speed_multiplier}x")
    gui.spacer()
    
    dist_display = f"{state.current_distance}m" if state.current_distance is not None else "Searching..."
    gui.text(f"Distance: {dist_display}")

    if len(state.distance_history) >= 2 and state.current_distance is not None:
        oldest_time, oldest_dist = state.distance_history[0]
        latest_time, latest_dist = state.distance_history[-1]
        time_delta = latest_time - oldest_time
        
        if time_delta > 0:
            velocity = (latest_dist - oldest_dist) / time_delta
            gui.text(f"Velocity: {velocity:+.1f} m/s")
        else:
            gui.text("Velocity: -- m/s")
    else:
        gui.text("Velocity: -- m/s")

    gui.spacer()
    gui.line()

    tension_label = "None (Slack Line)"
    if getattr(state, 'high_tension', False):
        tension_label = "HIGH (Heavy Pull)"
    elif getattr(state, 'low_tension', False):
        tension_label = "NORMAL (Good Pressure)"
    gui.text(f"Tension:  {tension_label}")

    gui.spacer()
    gui.line()

    if state.is_hooked:
        gui.text("⚠️ FISH HOOKED! (Fighting)")
    elif state.current_distance == 0:
        gui.text("🔄 0m Reached (Recasting)")
    else:
        gui.text("Status: Normal Retrieve")

    gui.spacer()
    if gui.button("Hide Telemetry"):
        actions.user.fishing_hide_dashboard()

@mod.action_class
class Actions:
    def fishing_show_dashboard() -> None:
        """Show the live telemetry dashboard"""
        gui_fishing_dashboard.show()

    def fishing_hide_dashboard() -> None:
        """Hide the live telemetry dashboard"""
        gui_fishing_dashboard.hide()

    def fishing_toggle_dashboard() -> None:
        """Toggle dashboard visibility"""
        if gui_fishing_dashboard.showing:
            gui_fishing_dashboard.hide()
        else:
            gui_fishing_dashboard.show()
