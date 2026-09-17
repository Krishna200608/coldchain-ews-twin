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
| 1 | Repo Scaffolding, Data Acquisition & EDA | ✅ Completed |
| 2 | Preprocessing, Injected Anomaly Protocol & Baseline Alarm | ✅ Completed |
| 3 | Isolation Forest Baseline Anomaly Detector | ✅ Completed |
| 4a| LSTM-Autoencoder Data Prep & Colab Notebook Authoring | ✅ Completed |
| 4b| Colab T4 Training & LSTM-Autoencoder Evaluation | ⏳ Awaiting Colab Run |
| 5 | SimPy Digital Twin & Integrated EWS | ⬜ Planned |

---

## Milestone 4a/4b Colab Workflow

Because training the LSTM-Autoencoder requires GPU acceleration (Google Colab T4 GPU), model training is partitioned into an authoring step (Milestone 4a) and an execution/evaluation step (Milestone 4b).

### 1. Files to Upload to Google Colab
Run `python src/lstm_prep.py` locally to generate the window arrays in `data/processed/`.
Upload these 4 `.npz` files to your Colab session under `data/processed/`:
- `data/processed/lstm_windows_out_train.npz`
- `data/processed/lstm_windows_out_val.npz`
- `data/processed/lstm_windows_in_train.npz`
- `data/processed/lstm_windows_in_val.npz`

### 2. Executing Training in Colab
Open `colab/lstm_train.ipynb` in Google Colab:
1. Ensure the runtime type is set to **T4 GPU** (`Runtime > Change runtime type > T4 GPU`).
2. Run all cells (`Runtime > Run all`).
3. Training will train separate Out and In models with early stopping and record loss curves and GPU hardware metadata.

### 3. Files to Download from Colab to Local Repository
Once training completes, download the following 4 files from Colab and place them in their respective local repository paths:
- `models/lstm_out.h5` → `coldchain-ews-twin/models/lstm_out.h5`
- `models/lstm_in.h5` → `coldchain-ews-twin/models/lstm_in.h5`
- `data/processed/lstm_training_log_out.json` → `coldchain-ews-twin/data/processed/lstm_training_log_out.json`
- `data/processed/lstm_training_log_in.json` → `coldchain-ews-twin/data/processed/lstm_training_log_in.json`

> **IMPORTANT**: Milestone 4b (test-set window extraction, reconstruction error scoring, PR curves, and EWS lead-time evaluation) **cannot proceed until this manual Colab GPU run is complete** and the trained weights are downloaded locally.
