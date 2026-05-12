
# ─── OVERLAY ─────────────────────────────────────────────────────────────────
help fishing: user.fishing_show_help()
hide fishing: user.fishing_hide_help()
hide help: user.fishing_hide_help()
# fishing.talon
show dashboard | open dashboard: 
    user.fishing_show_dashboard()
hide dashboard | close dashboard: 
    user.fishing_hide_dashboard()

# ─── ROD & UTILITIES ─────────────────────────────────────────────────────────
rod swap: 
    user.fishing_equip_rod()

cast it | toss it: user.fishing_cast_rod()

reel steady | reel slow: user.fishing_reel_steady()

relax now | stop now | stop it: user.fishing_emergency_stop()

watch it: user.fishing_enable_analytics_persistent()
show vision: user.fishing_show_vision_debug()
hide vision: user.fishing_hide_vision_debug()
stop tracking: user.fishing_disable_analytics_persistent()

# Trigger manual OCR extraction testr
test show reader: user.fishing_debug_catch_reader()

# Toggle the visible ledger GUI
show reader: user.fishing_show_catch_log()
# Show the visual bounding boxes directly on screen
show hud: user.fishing_show_calibration_hud()

# Hide the visual bounding boxes
hide hud: user.fishing_hide_calibration_hud()
# ─── RETRIEVE PRESETS ────────────────────────────────────────────────────────
reel it:
    user.fishing_start_preset("reel_it")

stop go:
    user.fishing_start_preset("stop_go")

stop go slow:
    user.fishing_start_preset("stop_go_slow")

walk it:
    user.fishing_start_preset("walk_it")

walk slow:
    user.fishing_start_preset("walk_slow")

wick it:
    user.fishing_start_preset("twitch_it")

wick slow:
    user.fishing_start_preset("twitch_slow")

# ─── SPEED ADJUSTERS ─────────────────────────────────────────────────────────
fishing faster:   user.fishing_speed_increase()
fishing slower:   user.fishing_speed_decrease()
fishing normal:   user.fishing_speed_reset()

# ─── DEBUGGING ───────────────────────────────────────────────────────────────
snap it: user.fishing_debug_snapshot()