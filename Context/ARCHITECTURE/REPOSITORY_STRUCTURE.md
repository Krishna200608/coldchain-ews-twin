# Repository Structure and Artifact Inventory

> **Single Source of Truth:** `Context/ARCHITECTURE/REPOSITORY_STRUCTURE.md`  
> **Related Documents:**  
> - [`SYSTEM_ARCHITECTURE.md`](SYSTEM_ARCHITECTURE.md)  
> - [`DATA_FLOW.md`](DATA_FLOW.md)  
> - [`MODULE_DEPENDENCIES.md`](MODULE_DEPENDENCIES.md)  
> - [`../DATA/DATA_DICTIONARY.md`](../DATA/DATA_DICTIONARY.md)

---

## 1. Top-Level Repository Directory Map

```text
coldchain-ews-twin/
├── .env                                # Local environment variable declarations
├── .gitignore                          # Git exclusion rules for caches, virtualenvs, and data
├── README.md                           # Project introduction and primary overview
├── requirements.txt                    # Pinned Python package dependencies
│
├── Context/                            # Single Source of Truth (SSOT) knowledge base for AI agents
│   ├── README.md                       # Knowledge base entry point, constraints & rules
│   ├── PROJECT/                        # Executive overview, problem statement, objectives
│   ├── ARCHITECTURE/                   # System design, repository layout, data flow, twin engine
│   ├── DATA/                           # Dataset ingestion, preprocessing, injection protocol
│   ├── MODELS/                         # Baseline, Isolation Forest, LSTM-Autoencoder specifications
│   ├── DIGITAL_TWIN/                   # SimPy simulation, streaming monitors, replay parity
│   ├── RESEARCH/                       # Methodology, experimental results, findings, limitations
│   ├── DEVELOPMENT/                    # Setup, execution, testing, coding conventions
│   └── MANAGEMENT/                     # Implementation status, AD log, known issues, roadmap
│
├── colab/                              # Cloud GPU model training notebooks
│   └── lstm_train.ipynb                # Google Colab T4 notebook for training LSTM-Autoencoders
│
├── dashboard/                          # Streamlit presentation and interactive simulation UI
│   ├── app.py                          # Application entry point, layout orchestrator, auto-play loop
│   ├── constants.py                    # UI constants, color palettes, icon mappings
│   ├── data_loader.py                  # Cached loaders, metadata mergers, D32 startup verification
│   ├── README.md                       # Comprehensive dashboard operator manual
│   ├── replay_engine.py                # D33 pre-warmed simulation and telemetry slicing
│   └── components/                     # Modular presentation components
│       ├── __init__.py                 # Package marker
│       ├── alert_log.py                # Real-time streaming alert log table & filters
│       ├── banners.py                  # D31 persistent proxy notice & train-side demo banners
│       ├── crosscheck_audit.py         # Milestone 5b live vs. batch parity verification card
│       ├── detector_cards.py           # Top KPI bar and 3 detector status cards
│       ├── showcase.py                 # D34 runtime-interpolated Guided Tour narrative cards
│       └── telemetry_chart.py          # Interactive Altair streaming chart & score diagnostics
│
├── data/                               # Data storage tiers
│   ├── raw/                            # Raw dataset directory (IOT-temp.csv; gitignored)
│   └── processed/                      # 30+ serialized evaluation summaries and CSV/JSON artifacts
│
├── docs/                               # Academic and technical documentation deliverables
│   ├── README.md                       # Documentation hub index
│   ├── AD_LOG.md                       # Architectural Decision Log (35 entries, D1–D35)
│   ├── understand.md                   # Plain-English conceptual walkthrough
│   ├── data_profile.md                 # Quantitative Milestone 1 EDA findings
│   ├── Presentation.md                 # Verbatim 16-slide presenter script for viva defense
│   ├── Project.md                      # Official academic project description
│   ├── Dataset_Submission/             # Packaged dataset submission directory with raw CSV
│   ├── figures/                        # High-resolution publication plots (300 DPI)
│   ├── Progress_Report/                # IEEE LaTeX progress report source, PDF, and bib
│   ├── Report/                         # 12-Chapter academic final report LaTeX package
│   └── Synopsis/                       # Initial academic project synopsis (.docx)
│
├── models/                             # Pre-trained model weight binaries and pipelines
│   ├── isolation_forest_out.joblib     # Fitted scikit-learn Isolation Forest (Out series; tracked)
│   ├── isolation_forest_in.joblib      # Fitted scikit-learn Isolation Forest (In series; tracked)
│   ├── lstm_out.h5                     # Trained Keras LSTM-Autoencoder weights (Out series; tracked)
│   └── lstm_in.h5                      # Trained Keras LSTM-Autoencoder weights (In series; tracked)
│
├── notebooks/                          # Milestone-by-milestone research and prototyping notebooks
│   ├── 01_eda.ipynb                    # Milestone 1: Exploratory data analysis & sampling profile
│   ├── 02_preprocessing_and_labeling.ipynb # Milestone 2: Feature engineering & anomaly injection
│   ├── 03_isolation_forest.ipynb       # Milestone 3: Classical unsupervised baseline detector
│   ├── 04_lstm_evaluation.ipynb        # Milestone 4b: Deep reconstruction error & lead-time evaluation
│   ├── 05_digital_twin_replay.ipynb    # Milestone 5a: SimPy simulation replay & fidelity verification
│   └── 06_digital_twin_live_monitors.ipynb # Milestone 5b: Live streaming monitors & batch cross-check
│
├── scripts/                            # Headless document generation and build automation utilities
│   ├── generate_presentation_pptx.py   # Programmatic PowerPoint (.pptx) compiler using python-pptx
│   ├── generate_presentation_html_pdf.py # HTML slide deck compiler and Chrome headless PDF export
│   └── generate_progress_pdf.py        # PDF compilation utility for progress documentation
│
├── src/                                # Core Python production package
│   ├── __init__.py                     # Package marker
│   ├── config.py                       # Global single source of truth for all named constants
│   ├── split_utils.py                  # Chronological train/test splitting utilities (D6)
│   ├── data_acquisition.py             # Authenticated Kaggle dataset download client
│   ├── preprocessing.py                # Timestamp parsing, deduplication, rolling features (D1, D2)
│   ├── anomaly_injection.py            # Controlled synthetic perturbation generator (D3)
│   ├── baseline_and_labels.py          # Naive 2-sigma threshold baseline and irreversibility (D4)
│   ├── isolation_forest_model.py       # Trailing rolling features and IF model training (D5, D7, D22)
│   ├── if_evaluation.py                # Point-wise metrics and lead-time evaluation for IF (D8, D35)
│   ├── lstm_prep.py                    # Bivariate sliding-window extraction & normalization (D9–D11)
│   ├── lstm_evaluation.py              # Causal last-timestep reconstruction MSE scoring (D13–D16, D35)
│   ├── three_way_comparison.py         # Merged comparative benchmark table (Baseline vs IF vs LSTM)
│   ├── digital_twin.py                 # SimPy 3-stage event-driven replay engine (D17–D19)
│   ├── twin_monitors.py                # Online streaming monitors for Baseline, IF, LSTM (D23, D24, D27)
│   ├── twin_verification.py            # Row-by-row simulation fidelity and SimTime validation
│   └── twin_crosscheck.py              # Live vs. batch cross-check audit & verification report
│
└── tests/                              # Automated testing and quality assurance
    └── test_d33_prewarm.py             # D32 startup verification and D33 buffer pre-warming test suite
```

---

## 2. Directory Responsibilities and Engineering Boundaries

### 1. `src/` (Core Logic)
* **Responsibility:** Contains all mathematical modeling, data transformations, simulation orchestration, and evaluation scoring.
* **Invariant:** Must never import from `dashboard/` or `notebooks/`. It is completely self-contained and imports constants strictly from `src/config.py`.

### 2. `dashboard/` (Presentation Layer)
* **Responsibility:** Multi-page Streamlit application providing interactive telemetry visualization, playhead scrubbing, Guided Tour walkthroughs, and audit reports.
* **Invariant (D27):** Contains **zero** new anomaly detection logic or threshold tuning. All monitors are imported directly from `src/twin_monitors.py`.

### 3. `data/processed/` (Serialized State Tier)
* **Responsibility:** Holds clean reference features, ground-truth injection logs, comparative lead-time tables, and machine-readable metrics JSONs.
* **Invariant (D3, D35):** Clean feature files (`out_features.csv`, `in_features.csv`) are permanent and read-only. Evaluation metrics are serialized once and never manually transcribed.

### 4. `models/` (Binary Assets)
* **Responsibility:** Pre-trained model weights.
* **Tracking Rules (D15):** 
  * `lstm_out.h5` and `lstm_in.h5` are tracked in git (~193 KB each) to enable out-of-the-box local CPU inference without requiring Colab training.
  * `isolation_forest_{out,in}.joblib` are tracked in git (~1.5 MB each) for immediate local dashboard deployment.

### 5. `tests/` (Automated Verification)
* **Responsibility:** Programmatic regression test suite executing pre-flight health assertions and verifying 100% bit-for-bit parity across all test injections.

---

## 3. Artifact Naming Conventions & File Formats

| File Format | Purpose in Repository | Representative Examples |
| :--- | :--- | :--- |
| `.csv` | Tabular telemetry streams, injection logs, and lead-time summaries. | `out_features.csv`, `three_way_comparison.csv`, `twin_crosscheck_report.csv` |
| `.json` | Structured single-source-of-truth metrics, normalization statistics, and training loss logs. | `if_pointwise_metrics.json`, `lstm_norm_stats_out.json`, `lstm_training_log_out.json` |
| `.npz` | Compressed NumPy binary archives storing multi-dimensional sliding-window tensors. | `lstm_windows_out_train.npz` (shape: $N \times 30 \times 2$) |
| `.joblib` | Serialized scikit-learn tree ensembles. | `isolation_forest_out.joblib` |
| `.h5` | Serialized Keras/TensorFlow model weights (HDF5 format). | `lstm_out.h5`, `lstm_in.h5` |
| `.py` | Production Python source code, utilities, tests, and build scripts. | `src/digital_twin.py`, `dashboard/app.py`, `tests/test_d33_prewarm.py` |
| `.ipynb` | Jupyter Notebooks for milestone prototyping and Colab GPU execution. | `notebooks/01_eda.ipynb`, `colab/lstm_train.ipynb` |
| `.tex` | Publication-ready LaTeX source for reports and slide presentations. | `docs/Progress_Report/main.tex`, `docs/Report/Krishna_Sikheriya_ColdChain_Report.tex` |
| `.pdf` | Compiled academic reports and presentation slides. | `docs/Progress_Report/Progress_Report.pdf`, `docs/Progress_Report/Presentation.pdf` |

---

## 4. Git Tracking Policy and `.gitignore` Rules

The repository strictly enforces clean version control practices via `.gitignore`:
* **Excluded:**
  * Virtual environments (`.venv/`, `env/`, `venv/`).
  * Python compiler bytecode (`__pycache__/`, `*.pyc`).
  * Raw datasets (`data/raw/*`, including `IOT-temp.csv`).
  * Credentials and tokens (`kaggle.json`, `.env`, GitHub PATs).
  * Build caches and temporary artifacts (`.ipynb_checkpoints/`, `*.egg-info/`).
* **Explicitly Tracked:**
  * Processed CSV and JSON artifacts under `data/processed/` (to maintain reproducible evaluation baselines).
  * Trained weights (`models/lstm_*.h5`, `models/isolation_forest_*.joblib`).
  * Full LaTeX source trees and compiled publication PDFs under `docs/`.

