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

