# fishing_state.py

# Execution Flags
current_mode      = "IDLE"
speed_multiplier  = 1.0
last_preset       = None
auto_resume       = False

# Telemetry
current_distance  = None
distance_history  = []      
is_hooked         = False
is_pulling        = False   

# Loop Controls & Task Registry
running           = False
is_running        = False  # Used globally to authorize hardware inputs
loop_job          = None
loop_generation   = 0       # Incremented every time a new analytics loop is started.
                            # Each loop instance captures this value on entry and checks
                            # it before rescheduling — if it no longer matches, the loop
                            # knows it has been superseded and quietly stops itself.
detect_job        = None
detecting         = False
recast_job        = None
active_cron_jobs  = []     # Central registry to track and terminate cron jobs

# Preset Profiles
active_hold       = 0
active_interval   = 0
active_variation  = 0
active_stop_go    = False

FISHING_PRESETS = {
    "walk_it":      {"hold": 95,   "interval": 520,  "variation": 5},
    "walk_slow":    {"hold": 115,  "interval": 680,  "variation": 5},
    "twitch":       {"hold": 140,  "interval": 780,  "variation": 10},
    "twitch_slow":  {"hold": 160,  "interval": 1050, "variation": 15},
    "stop_go":      {"hold": 1400, "interval": 500,  "variation": 20, "stop_go": True},
    "stop_go_slow": {"hold": 1200, "interval": 300,  "variation": 20, "stop_go": True},
    "reel_it":      {"hold": 800,  "interval": 200,  "variation": 50},
    "fight_fish":   {"hold": 2000, "interval": 100,  "variation": 50} 
}