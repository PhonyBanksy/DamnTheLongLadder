# fishing_catch_gui.py
from talon import Module, actions, imgui
from . import fishing_state as state

mod = Module()

@imgui.open()
def gui_catch_log(gui: imgui.GUI):
    gui.text("📋 Session Catch Ledger")
    gui.line()
    
    tot_fish = len(getattr(state, 'session_catch_log', []))
    tot_weight = getattr(state, 'session_total_weight', 0.0)
    tot_earn = getattr(state, 'session_total_earnings', 0.0)
    
    gui.text(f"Total Caught: {tot_fish}   |   Weight: {tot_weight:.2f} kg   |   Earnings: {tot_earn:.0f} cr")
    gui.line()
    gui.spacer()
    
    gui.text("Recent Catches:")
    log = getattr(state, 'session_catch_log', [])
    if not log:
        gui.text(" No fish logged this session yet.")
    else:
        for rec in reversed(log[-15:]):
            gui.text(f"[{rec['time']}] {rec['name']}  ──  ⚖️ {rec['weight']}   |   📏 {rec['length']}   |   💰 {rec['price']} cr")
            
    gui.line()
    if gui.button("Clear Session Log"):
        actions.user.fishing_clear_catch_log()
    if gui.button("Hide Log"):
        actions.user.fishing_hide_catch_log()

@mod.action_class
class Actions:
    def fishing_show_catch_log() -> None:
        """Displays the session catch tracker overlay."""
        gui_catch_log.show()

    def fishing_hide_catch_log() -> None:
        """Hides the session catch tracker overlay."""
        gui_catch_log.hide()

    def fishing_clear_catch_log() -> None:
        """Wipes current session metrics cleanly."""
        state.session_catch_log = []
        state.session_total_weight = 0.0
        state.session_total_earnings = 0.0
        print("[fishing] Session catch log cleared.")
