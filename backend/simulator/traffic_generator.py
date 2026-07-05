"""
Generates relialistic, evolving vehicle telemetry as plain Python dictionaries, meant to simulate CAN bus traffic before any real CAN transport is added. 

For now not implementing any attacks, no python-can/vCAN, no FastAPI, no threading, no ML. 
Just believable stream of Speed / RPM / Steering / Brake / Battery readings that evolve smoothly over time from the ECU profiles defined in can_profile.json.
"""

import json 
import random 
import time
from pathlib import Path
from typing import Any, IO, Optional

# type aliases
Profile = dict[str, Any]
Profiles = dict[str, Profile]
ECUState = dict[str, float]
State = dict[str, ECUState]
Message = dict[str, Any]

def load_profiles(path: Path = Path("backend/simulator/can_profiles.json")) -> Profiles:
    """ Load the ECU configs from json file """

    with open(path, "r") as f:
        return json.load(f)

def init_state(profiles: Profiles) -> State:
    """ 
    Build the inital in-memory state for every ECU: its starting value and a last_sent timestamp of 0.0 (so every ECU is immediately eligible to send on the very first loop check).
    """

    state: State = {}
    for ecu_name, profile in profiles.items():
        state[ecu_name] = {
                "value": profile["start_value"],
                "last_sent": 0.0,
                }

    return state

def evolve_value(current_value: float, profile: Profile) -> float:
    """
    Nudge the current value by a small random step (a random walk), then clamp it to the profile's realistic min/max bounds.
    This is what makes readings drift naturally instead of teleporting — e.g. Speed gradually climbing from 40 to 45 km/h, never jumping straight to 150.
    """

    step = random.uniform(-profile["max_change_per_update"], profile["max_change_per_update"])
    new_value = current_value + step 

    return max(
            profile["min"], min(
                profile["max"], new_value
                )
            )

def is_due(ecu_name: str, state: State, profile: Profile, now: float) -> bool:
    """
    Decide whether this ECU should send a new reading right now.
    Jitter is recalculated fresh on every check, which is what gives us "roughly every period_seconds, with natural wobble" instead of a perfectly fixed, suspiciously robotic interval.
    """

    period = profile["period_seconds"]
    jitter = random.uniform(-profile["jitter_ms"], profile["jitter_ms"]) / 1000.0
    elapsed = now - state[ecu_name]["last_sent"]

    return elapsed >= (period + jitter)

def build_message(ecu_name: str, profile: Profile, value: float) -> Message:
    """
    Build a flat, consistent message dictionary. Every ECU produces the exact same five fields — only the values differ. Later modules (feature extraction, dashboard) depend on this schema staying identical across all ECUs.
    """

    return {
            "timestamp": time.time(),
            "ecu": ecu_name,
            "can_id": profile["can_id"],
            "value": round(value, 2),
            "unit": profile["unit"],
            }

def generate_traffic(duration_seconds: float = 30, save_to_file: bool = False) -> None:
    """
    Main generation loop. For the configured duration, repeatedly checks every ECU; any ECU that is "due" gets its value evolved and a new message emitted (printed, and optionally appended to a JSON Lines log).
    """
    profiles: Profiles = load_profiles()
    state: State = init_state(profiles)
    log_file: Optional[IO[str]] = (
            open("backend/simulator/traffic_log.jsonl", "a") if save_to_file else None
            )

    start_time = time.time()
    try:
        while time.time() - start_time < duration_seconds:
            now = time.time()
            for ecu_name, profile in profiles.items():
                if is_due(ecu_name, state, profile, now):
                    state[ecu_name]["value"] = evolve_value(state[ecu_name]["value"], profile)
                    message = build_message(ecu_name, profile, state[ecu_name]["value"])
                    state[ecu_name]["last_sent"] = now

                    print(message)
                    if log_file:
                        log_file.write(json.dumps(message) + "\n")

            time.sleep(0.01)
    finally:
        if log_file:
            log_file.close()


if __name__ == "__main__":
    generate_traffic(duration_seconds=30, save_to_file=True)
