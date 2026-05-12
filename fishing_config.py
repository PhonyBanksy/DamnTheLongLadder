# fishing_config.py

# ─── RECAST TIMERS ──────────────────────────────────────────────────────────
UI_SCAN_INITIAL_DELAY = "150ms" 
UI_SCAN_FREQUENCY = "150ms"
POST_KEEP_DELAY = "5000ms"
LOOP_UPDATE_INTERVAL = "50ms"
ANALYTICS_START_DELAY = "100ms"
UI_MAX_ATTEMPTS = 25
# ─── OCR & VISION ───────────────────────────────────────────────────────────
OCR_CONFIDENCE_THRESHOLD = 0.7 
# Highly responsive but safe for the main thread
ANALYTICS_FREQUENCY = "200ms"

# ─── TENSION & FIGHTING ─────────────────────────────────────────────────────
TENSION_ACTIVE_RGB = (0, 210, 50) 
TENSION_TOLERANCE = 85 
FIGHT_PULL_DURATION = "1000ms" 

HEAVY_TENSION_RGB = (255, 120, 0) 
HEAVY_TENSION_TOLERANCE = 60
FIGHT_HEAVY_PULL_DURATION = "1200ms" 

# ─── DETECTION & LOOPS ──────────────────────────────────────────────────────
SPLASHDOWN_DELAY = "1200ms"
GOLD_SCAN_FREQUENCY = "4ms"
CAST_CHARGE_DELAY = "250ms"
REEL_STEADY_DELAY = "150ms"