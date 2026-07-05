# CANORIS

**CANORIS (CAN-Oriented Risk Intelligence System)** is an Edge AI Automotive Risk Assessment Platform that detects anomalous behaviour on a vehicle's Controller Area Network (CAN) and assists engineers in assessing cyber threats through layered risk analysis and actionable recommendations.

This project is being developed for the Tata Technologies InnoVent Hackathon 2026 under **Category 3.2.1.6 – Edge AI for Automotive Cybersecurity**.

---

## Architecture

```
Virtual CAN Traffic → Feature Extraction → Isolation Forest → Consistency Checks
                    → Risk Assessment → Response Engine → Streamlit Dashboard
```

## Current State

✅ **Done:**
- `backend/simulator/` — generates realistic, evolving telemetry for 5 simulated ECUs (Speed, RPM, Steering, Brake, Battery), configured via `can_profiles.json`. Values evolve smoothly over time with natural timing jitter; no real CAN hardware is used yet.
- `dashboard/app.py` — The Streamlit dashboard currently uses placeholder data shaped to match the planned backend API, allowing the frontend to be developed independently before integration.

🚧 **Not yet built:**
- Feature extraction
- Isolation Forest detection model
- Rule-based consistency checks
- Risk fusion (weighted scoring)
- Response engine (real lookup table, wired to backend)
- FastAPI backend tying it all together
- Connection between the simulator, backend, and dashboard

P.S. : The simulator and dashboard were deliberately built in parallel and are **not yet connected to each other** — the dashboard currently shows placeholder/random data shaped the same way real data eventually will be, so the swap later is small.

---

## Repository Structure

```text
canoris/
├── backend/
│   ├── simulator/          # Vehicle telemetry generation
│   │   ├── traffic_generator.py
│   │   └── can_profiles.json
│   ├── features/           # Feature extraction from CAN traffic
│   ├── consistency/        # Rule-based signal consistency checks
│   ├── model/              # Isolation Forest training & inference
│   ├── fusion/             # Risk Fusion Engine
│   ├── response/           # Attack classification & recommendations
│   └── main.py             # FastAPI backend
│
├── dashboard/
│   └── app.py              # Streamlit dashboard
│
├── data/                   # Public datasets & generated logs
│
├── config.yaml             # Project configuration
├── README.md
└── .gitignore
```
---

## Tech Stack

- Python 3.12+
- Streamlit
- FastAPI
- python-can
- CAN-utils (planned)
- scikit-learn
- Pandas
- NumPy
- Docker (deployment)
---

## Roadmap

1. **Feature extraction** — packet count/frequency, inter-arrival time (mean + variance), payload entropy, unique CAN ID count, sequence rarity score.
2. **Isolation Forest** — train on normal simulator/public-dataset traffic, evaluate with precision/recall/ROC-AUC/false-positive rate.
3. **Consistency checks** — rule-based cross-signal checks (e.g., speed vs. brake, RPM vs. gear/speed, wheel speed consistency).
4. **Risk Fusion Engine** — fixed weighted fusion: `0.5 × ML score + 0.3 × Consistency score + 0.2 × Rule score`.
5. **Attack-type identification** — rule-based classification into Spoofing / Replay / Flooding / Unauthorized ID Injection.
6. **Response engine** — real lookup table mapping attack type → affected ECU, impact, recommended action.
7. **FastAPI backend** — owns the simulator in-process, exposes `/risk/current`, `/alert/current`, `/traffic/current`, `/simulator/attack`.
8. **Connect the dashboard** — swap placeholder functions in `dashboard/app.py` for real backend calls (no layout/session-state changes needed).
9. **Docker** — containerize once everything works locally.
10. **Public dataset validation** — validate feature distributions and model performance against a real-vehicle CAN dataset (e.g., HCRL Car-Hacking Dataset or ROAD dataset).

### Stretch goals (only after the above is stable)
- Model bake-off (One-Class SVM, LOF, autoencoder) vs. Isolation Forest
- Additional ECUs / attack types
- Persistence (JSON log → optionally SQLite)
- Raspberry Pi proof-of-concept with a real CAN transceiver

---

## Running Locally

```bash
# Simulator
python backend/simulator/traffic_generator.py

# Dashboard
streamlit run dashboard/app.py
```

## Status

This repository is under active development for the Tata Technologies InnoVent Hackathon 2026.
