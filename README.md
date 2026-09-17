# Digital Twin-Based Early Warning System for Cold Chain Disruption Detection

> **Milestone 1 — Repo Scaffolding, Data Acquisition & EDA**

## Project Overview

This project develops a **Digital Twin-based Early Warning System (EWS)** for
cold-chain logistics. The system models a refrigerated-transport environment as
a SimPy-based digital twin and detects anomalies using a combination of
Isolation Forest (classical baseline) and an LSTM-Autoencoder (deep learning).

### Dataset — Structural Proxy Notice

> ⚠️ The dataset used in this milestone (`atulanandjha/temperature-readings-iot-devices`
> on Kaggle) is a **generic IoT temperature sensor log — it is NOT real
> refrigerated-transport telemetry**. It is being used exclusively as a
> **structural proxy** to validate ingestion pipelines, characterise irregular
> sampling behaviour, and develop anomaly-detection scaffolding before
> real cold-chain data is available.
> Every output file, notebook, and module that touches this dataset must
> repeat this caveat.

---

## Repository Layout

```
coldchain-ews-twin/
├── .gitignore              # excludes data/raw/, data/processed/, venvs, etc.
├── README.md
├── requirements.txt
│
├── data/
│   ├── raw/                # ← gitignored; place downloaded CSV here
│   └── processed/          # ← gitignored; cleaned/feature-engineered files
│
├── notebooks/
│   └── 01_eda.ipynb        # Milestone 1 EDA
│
├── src/
│   └── data_acquisition.py # Downloads the Kaggle dataset to data/raw/
│
├── docs/
│   ├── AD_LOG.md           # Architecture Decision Log
│   └── data_profile.md     # Plain-prose EDA findings (actual numbers)
│
└── colab/                  # Placeholder — LSTM milestone notebooks land here
```

---

## Quick-Start

### 1 — Install dependencies

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2 — One-time Kaggle API setup

The data-acquisition script authenticates using the **Kaggle API credentials
file** that Kaggle provides in your account settings.

1. Go to <https://www.kaggle.com/settings> → "API" → "Create New Token".
2. Save the downloaded `kaggle.json` to `~/.kaggle/kaggle.json`  
   (Windows: `C:\Users\<you>\.kaggle\kaggle.json`).
3. Restrict permissions: `chmod 600 ~/.kaggle/kaggle.json` (Linux/macOS).

The script reads these credentials automatically — **do not hardcode them**
in any source file and never commit `kaggle.json` to git (it is gitignored).

### 3 — Download the dataset

```bash
python src/data_acquisition.py
```

This places the raw CSV in `data/raw/` without modification.

### 4 — Run the EDA notebook

```bash
jupyter notebook notebooks/01_eda.ipynb
```

---

## Milestones

| # | Milestone | Status |
|---|-----------|--------|
| 1 | Repo Scaffolding, Data Acquisition & EDA | ✅ In progress |
| 2 | SimPy Digital Twin skeleton | ⬜ Planned |
| 3 | Isolation Forest baseline | ⬜ Planned |
| 4 | LSTM-Autoencoder | ⬜ Planned |
| 5 | EWS integration & alerting | ⬜ Planned |

---

## Notes

- **No modeling code** is present in this milestone. Anomaly detection
  (Isolation Forest, LSTM-Autoencoder) and the SimPy digital twin are
  implemented in later milestones.
- `data/raw/` and `data/processed/` are gitignored to keep the raw CSV
  out of version control.
