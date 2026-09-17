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

## Milestone 4a/4b Colab Workflow (Automated via GitHub PAT)

Because training the LSTM-Autoencoder requires GPU acceleration (Google Colab T4 GPU), model training is partitioned into an authoring step (Milestone 4a) and an execution/evaluation step (Milestone 4b).

### 1. Colab Secrets Setup (One-Time)
1. Open Google Colab and open `colab/lstm_train.ipynb`.
2. On the left sidebar, click the **Secrets** icon (🔑).
3. Add a new secret named `GITHUB_TOKEN` (or `GH_TOKEN`), paste your GitHub Personal Access Token (PAT with `repo` / contents write permissions), and toggle on **Notebook access**.
4. Set the runtime to **T4 GPU** (`Runtime > Change runtime type > T4 GPU`).

### 2. Execution & Automated Push in Colab
1. Run all cells in `colab/lstm_train.ipynb`.
2. The notebook will automatically:
   - Authenticate and clone `https://github.com/Krishna200608/coldchain-ews-twin` directly into the Colab environment using your PAT.
   - Automatically load the 4 preprocessed window files (`lstm_windows_{out,in}_{train,val}.npz`) directly from `data/processed/` in the cloned repository (zero manual upload required).
   - Train the D12 LSTM-Autoencoder models for Series Out and Series In on the T4 GPU with early stopping.
   - Automatically commit and push `models/lstm_out.h5`, `models/lstm_in.h5`, `data/processed/lstm_training_log_out.json`, and `data/processed/lstm_training_log_in.json` directly back to the GitHub repository's `main` branch!

### 3. Sync to Local Repository
Once the Colab run finishes and pushes the artifacts, run in your local repository:
```bash
git pull origin main
```
to pull the trained models and training logs locally.
Then proceed to Milestone 4b (evaluating test-side reconstruction errors and early-warning lead times).
