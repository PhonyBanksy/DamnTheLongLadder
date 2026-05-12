# fishing_controls.py
from talon import Module, actions, cron
from . import fishing_state as state

mod = Module()

@mod.action_class
class Actions:
    def fishing_emergency_stop() -> None:
        """Instantly purges scheduled routines, cancels internal loop flags, and un-keys inputs."""
        print("[fishing] *** ABSOLUTE EMERGENCY STOP ENFORCED. CANCELING OPERATIONS. ***")
        
        # 1. Force state logic gates down globally
        state.is_running = False
        state.running = False
        state.detecting = False
        state.is_hooked = False
        state.is_pulling = False

        # 2. Iterate and annihilate orphaned memory jobs
        if hasattr(state, 'active_cron_jobs'):
            for job in state.active_cron_jobs:
                try:
                    cron.cancel(job)
                except Exception:
                    pass
            state.active_cron_jobs.clear()

        # Direct explicit cancellations against native module attributes
        for attr in ['loop_job', 'detect_job', 'recast_job']:
            job_ref = getattr(state, attr, None)
            if job_ref:
                try:
                    cron.cancel(job_ref)
                except Exception:
                    pass
                setattr(state, attr, None)

        # 3. Purge physical keyboard/mouse input states forcefully
        actions.key("space:up")
        actions.key("shift:up")
        actions.key("h:up")
        actions.mouse_release(0)
        actions.mouse_release(1)
