# fishing_gui.py
# ─── Imgui overlay ──────────────────────────────────────────────────────────

from talon import Module, actions, imgui
from . import fishing_state as state
mod = Module()

@imgui.open()
def gui_fishing(gui: imgui.GUI):
    gui.text("Fishing Bot")
    gui.line()

    gui.text(f"Status: {state.current_mode}")
    gui.text(f"Speed:  {state.speed_multiplier}x")
    gui.line()
    gui.spacer()

    gui.text("RETRIEVES:")
    gui.text("walk it / slow   -  Walking topwater glide")
    gui.text("wick it / slow   -  Twitching retrieve")
    gui.text("pop it / slow    -  Popping topwater splash")
    gui.text("stop go / slow   -  Stop and go retrieve")
    gui.text("reel it          -  Straight looped retrieve")
    gui.text("reel steady      -  Hold space steady")
    gui.spacer()
    
    gui.text("SPEED CONTROLS:")
    gui.text("fishing faster   -  quicker cadence (+10%)")
    gui.text("fishing slower   -  slower cadence (-10%)")
    gui.text("fishing normal   -  reset to 1.0x")
    gui.spacer()

    gui.text("UTILITIES:")
    gui.text("cast it          -  auto-release cast on full charge")
    gui.text("watch it         -  manual image detector start")
    gui.text("stop watch       -  cancel detector")
    gui.text("relax now        -  stop all actions completely")
    gui.text("keep it          -  tap space once")
    gui.text("rod swap         -  equip rod (E)")

    gui.spacer()
    if gui.button("Hide Menu"):
        actions.user.hide_fishing_help()

@mod.action_class
class Actions:
    def fishing_show_help() -> None:
        """Show the fishing overlay"""
        gui_fishing.show()

    def fishing_hide_help() -> None:
        """Hide the fishing overlay"""
        gui_fishing.hide()

    def fishing_toggle_help() -> None:
        """Toggle the fishing overlay"""
        if gui_fishing.showing:
            gui_fishing.hide()
        else:
            gui_fishing.show()
