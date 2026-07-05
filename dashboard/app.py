import time
import random
import streamlit as st

# Placeholder data functions
ECU_NAMES = ["speed", "RPM", "Steering", "Brake", "Battery"]

PLACEHOLDER_RESPONSES = {
    "Spoofing": {
        "affected_ecu": "Brake",
        "possible_impact": "A forged brake signal could mask a real braking event.",
        "recommended_action": "Flag the source CAN ID and cross-check with consistency rules.",
        "reason": "Known CAN ID reporting an implausible payload.",
    },
    "Replay": {
        "affected_ecu": "Speed",
        "possible_impact": "A replayed message could misrepresent current vehicle speed.",
        "recommended_action": "Compare message sequence against recent history.",
        "reason": "Repeated sequence matching a recently observed window.",
    },
    "Flooding": {
        "affected_ecu": "Steering",
        "possible_impact": "Excess traffic could delay legitimate steering messages.",
        "recommended_action": "Rate-limit or isolate the offending CAN ID.",
        "reason": "Packet frequency significantly above baseline.",
    },
    "Unauthorised ID Injection": {
        "affected_ecu": "Battery",
        "possible_impact": "An unrecognized ID could indicate a rogue device on the bus.",
        "recommended_action": "Block unknown IDs and log for review.",
        "reason": "CAN ID not present in the authorized ID list.",
    },
}

ATTACK_TYPES = list(PLACEHOLDER_RESPONSES.keys())

def get_current_reading(prev_value, active_value):
    """ Placeholder for the simulator backend"""
    max_step = 25 if active_value else 6
    step = random.uniform(-max_step, max_step)
    new_value = max(0, min(120, prev_value + step))
    return {
        "ecu" : random.choice(ECU_NAMES),
        "value" : round(new_value, 1),
        "timestamp" : time.time(),
    }

def compute_risk_assessment(active_attack):
    """ Placeholder for the risk assessment stage """ 
    if active_attack is None:
        score = round(random.uniform(0.05, 0.25), 2)
        band = "Normal"
    else:
        score = round(random.uniform(0.7, 0.95), 2)
        band = "Attack"
    return {"risk_score" : score, "band" : band}


# Page 
st.set_page_config(page_title="CANORIS", page_icon="🛡️", layout="wide")
st.title("CANORIS | Automotive Risk Assessment Dashboard")

with st.sidebar:
    st.header("System Status")
    st.write("Mode: Simulation")
    st.write("Backend connection: Not yet connected")

# Session state init to survive re-runs
if "traffic_history" not in st.session_state:
    st.session_state.traffic_history = [60.0]

if "active_attack" not in st.session_state:
    st.session_state.active_attack = None

if "risk" not in st.session_state:
    st.session_state.risk = compute_risk_assessment(st.session_state.active_attack)

col1,col2 = st.columns([1,2])

with col1:
    st.subheader("Current risk")
    st.metric(
        label = "Risk score",
        value = f"{st.session_state.risk['risk_score']:.2f}",
        delta = st.session_state.risk["band"],
    )

with col2:
    st.subheader("Live traffic")
    last_value = st.session_state.traffic_history[-1]
    new_reading = get_current_reading(last_value, st.session_state.active_attack)

    st.session_state.traffic_history.append(new_reading["value"])
    st.session_state.traffic_history = st.session_state.traffic_history[-30:]

    st.line_chart(st.session_state.traffic_history)
    st.caption(f"Last reading: {new_reading['ecu']} = {new_reading['value']}")

st.divider()

# Attack buttons
st.subheader("Simulate an attack scenario")

cols = st.columns(len(ATTACK_TYPES))
for col, attack in zip(cols, ATTACK_TYPES):
    if col.button(attack, use_container_width = True):
        st.session_state.active_attack = attack
        st.session_state.risk = compute_risk_assessment(attack)

if st.button("Clear alert"):
    st.session_state.active_attack = None
    st.session_state.risk = compute_risk_assessment(None)
st.divider()

# Alert panel
st.subheader("Alert")
if st.session_state.active_attack:
    attack = st.session_state.active_attack
    info = PLACEHOLDER_RESPONSES[attack]

    st.error(f"⚠️ {attack} detected on {info['affected_ecu']} ECU")
    st.write(f"Reason {info['reason']}")

    st.subheader("Recommendation")
    st.write(f"Possible impact : {info['possible_impact']}")
    st.write(f"Recommended action : {info['recommended_action']}")
else:
    st.success("No active alerts.")
