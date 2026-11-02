# PRIMER — Boot Context for New AI Agent Session
## Cold Chain EWS Digital Twin — GPU Research Phase

> **Paste this entire file as your first message in the new Antigravity chat.**  
> It gives the AI agent complete project context so it can continue immediately.

---

## Who You Are and What You Are Doing

You are an AI coding agent (Antigravity / Claude) helping a B.Tech 7th semester student at IIITA (Indian Institute of Information Technology, Allahabad) implement novel machine learning research improvements on a Cold Chain Early Warning System Digital Twin project.

**Student:** Krishna Sikheriya — Roll No: `IIT2023139`  
**Course:** Managing Corporate Entrepreneurship  
**Supervisor:** Netranand Pathak | Instructor: Dr. Shashi Kant Rai  
**Repository:** `https://github.com/Krishna200608/coldchain-ews-twin`  
**Current working directory on GPU server:** `~/coldchain-ews-twin`  
**GPU:** NVIDIA RTX 5000 Ada Generation, 32 GB VRAM — SSH access, already connected  
**Deadline:** Less than 2 weeks from today  
**Goal:** Implement 4–5 novel ML improvements for a course demo + viva presentation  

---

## Mandatory Reading Before Any Code

The project has a centralized documentation system at `Context/`. Read in this order before touching any code:

```bash
cat Context/README.md
cat Context/MANAGEMENT/ARCHITECTURAL_DECISIONS.md
cat docs/RESEARCH_HANDOFF.md    # ← THE MASTER PLAN — read this carefully
```

The `docs/RESEARCH_HANDOFF.md` file is the single most important document. It contains:
- Complete current system state (verified metrics, model architectures, file inventory)
- All 35 immutable architectural constraints (D1–D35)
- Full implementation plans with working Python code skeletons for every proposal
- 14-day execution timeline

---

## The Problem This Project Solves

Commercial cold-chain refrigerated logistics uses **static threshold alarms** that only fire after temperature exceeds a limit — by definition, post-hoc. This project builds an **Early Warning System** that detects subtle precursor signatures (sensor variance collapse, slow thermal drift) *before* a threshold breach, using:

1. **Naive Baseline Detector** — 2σ threshold exceedance (reference)
2. **Isolation Forest** — multivariate density-based anomaly detection
3. **LSTM-Autoencoder** — sequence reconstruction error anomaly detection
4. **SimPy Digital Twin** — replays historical telemetry through live streaming monitors
5. **Streamlit Dashboard** — interactive viva demo with guided tour + free explore modes

**Dataset:** IoT temperature sensor log (`IOT-temp.csv`, 97,605 records from Kaggle) used as a structural proxy — not real cold-chain data. All anomalies are synthetic.

---

## Verified Current Performance (Ground Truth — DO NOT FABRICATE)

These numbers come from `data/processed/*_pointwise_metrics.json` and `data/processed/three_way_comparison.csv`:

| Model | Series | Recall | Precision | FPR | PR-AUC |
|-------|--------|--------|-----------|-----|--------|
| Isolation Forest | Out | 80.0% | 0.85% | **45.59%** | 0.0676 |
| Isolation Forest | In | 91.30% | 2.04% | 26.98% | 0.2371 |
| LSTM-AE | Out | 20.0% | 0.48% | 20.50% | 0.0049 |
| LSTM-AE | In | 69.57% | **13.11%** | 2.85% | **0.3852** |

**Key lead times (test injections only):**
- `out_drift_009`: IF = **+64.0 min** early, LSTM = **−14.0 min** LATE (sequence lag problem)
- `in_drift_023`: IF = +11.0 min early, LSTM = 0.0 min

**What this means:** IF has catastrophic false positive rate on the Out series (45.59%). LSTM has a sequence inertia lag on drift events (−14 min). Both problems are the primary targets for improvement.

---

## Existing LSTM-AE Architecture (Keras, on disk as `.h5`)

```
Encoder:  LSTM(2→32)        → (batch, 32)       — takes [temp_norm, log_gap_norm]
Bottleneck: RepeatVector(30) → (batch, 30, 32)
Decoder:  LSTM(32→32)       → (batch, 30, 32)
Output:   TimeDistributed(Dense(2)) → (batch, 30, 2)
Total: 12,866 parameters
```

- Input features: `[temp_injected_norm, log_gap_seconds_norm]` (2 features only)
- Window: 30 readings × 2 features (count-based, NOT time-based — see D1)
- Thresholds: `Out = 1.010091`, `In = 1.512753` (train causal mean + 2σ — D13)
- Files: `models/lstm_out.h5`, `models/lstm_in.h5`

---

## The 5 Research Proposals (Priority Order)

All proposals have full code skeletons in `docs/RESEARCH_HANDOFF.md`. This is a summary:

### P4 — Adaptive Threshold via Kalman + CUSUM (Start Here — CPU, 2–3 days)
- **Problem:** Fixed 2σ threshold never adapts to distributional shift across seasons
- **Solution:** Kalman filter tracks running anomaly score statistics; CUSUM detects drift
- **Files:** `src/adaptation/adaptive_threshold.py` (new), modify `src/twin_monitors.py`
- **Novelty:** Online self-calibrating threshold for irregular-interval (count-based) IoT stream
- **GPU needed:** No — implement immediately

### P2 — Physics-Informed LSTM-AE (2–3 days, PyTorch)
- **Problem:** MSE loss cannot distinguish electrical sensor spike from real temperature excursion
- **Solution:** Add Newton's Law of Cooling as soft loss penalty: `L = L_MSE + λ‖dT/dt_pred - (-k(T-T_amb))‖²`
- **Files:** `src/models/pilstm_ae.py` (new), `colab/pilstm_ae_train.ipynb` (new)
- **Novelty:** First PINN (Physics-Informed Neural Network) for cold-chain IoT anomaly detection
- **GPU needed:** Yes — use RTX 5000 Ada

### P1 — Variational LSTM-AE with Uncertainty (3–4 days, PyTorch)
- **Problem:** Single-point alarm with no confidence level; model can't express "I'm unsure"
- **Solution:** VAE encoder outputs μ and log σ² → reparameterization → stochastic z; MC dropout for uncertainty
- **Anomaly score:** Decomposed into aleatoric (sensor noise) + epistemic (model ignorance)
- **Files:** `src/models/vlstm_ae.py` (new), `colab/vlstm_ae_train.ipynb` (new)
- **Novelty:** First uncertainty-quantified VAE for streaming cold-chain early warning
- **GPU needed:** Yes — RTX 5000 Ada; ~200 epochs with KL annealing

### P5 — Evidential Fusion (EDL) (3–4 days, after P1+P2)
- **Problem:** 3 detectors operate independently; their complementary strengths are never combined
- **Solution:** Dempster-Shafer evidence theory + small MLP fuses all detector scores into fused alarm probability + conflict mass K
- **Files:** `src/fusion/evidential_fusion.py` (new), `colab/fusion_train.ipynb` (new)
- **Novelty:** Evidence-theoretic multi-detector fusion for cold-chain IoT alarm triage
- **Depends on:** P1 + P2 producing anomaly scores first

### P3 — TFT Forecaster (Stretch goal — only if days 1–11 finish early)
- **Problem:** LSTM detects anomalies reactively; TFT predicts future trajectory
- **Skip for now** — largest effort (5–7 days), not essential for 2-week deadline

---

## Immutable Constraints (Non-Negotiable — D1–D35)

Violating these invalidates the project's scientific integrity. Key ones:

| Rule | What It Means |
|------|---------------|
| **D1** | Never resample to fixed time grid. All windowing is count-based (30 readings, not 30 minutes) |
| **D2** | Out (ambient) and In (enclosure proxy) series are always processed separately |
| **D3/D4** | `out_features.csv` and `in_features.csv` must never be overwritten |
| **D6** | Train/test split is always chronological at `cutoff_ts = "2018-10-29 11:10:48"`. No k-fold. No random shuffle |
| **D7/D13** | IF `contamination='auto'`. LSTM threshold from train causal mean + 2σ only. Never from test labels |
| **D26** | Only 6 test-side injections constitute the scientific benchmark. 24 train-side = demo only |
| **D27** | No model logic in `dashboard/` — always import monitors from `src/twin_monitors.py` |
| **D33** | Buffer pre-warming required: IF gets 10 readings, LSTM gets 30 readings before any visible window |

Full list with rationale: `docs/AD_LOG.md` and `Context/MANAGEMENT/ARCHITECTURAL_DECISIONS.md`

---

## Repository Structure (Key Files)

```
coldchain-ews-twin/
├── Context/                        # SSOT — 44 markdown files (read before coding)
│   └── README.md                   # ← START HERE for project rules
├── src/
│   ├── config.py                   # ALL named constants — import from here
│   ├── twin_monitors.py            # BaselineMonitor, IFMonitor, LSTMMonitor
│   ├── lstm_prep.py                # Sliding window builder (30×2 arrays)
│   └── digital_twin.py            # SimPy simulation engine
├── dashboard/
│   ├── app.py                      # Streamlit entry point
│   ├── replay_engine.py            # D33 pre-warmed playback
│   └── components/                 # UI modules
├── models/
│   ├── lstm_out.h5                 # Existing Keras LSTM-AE (12,866 params)
│   ├── lstm_in.h5
│   ├── isolation_forest_out.joblib
│   └── isolation_forest_in.joblib
├── data/processed/                 # Pre-computed CSVs/JSONs/NPZs — do not delete
├── tests/
│   └── test_d33_prewarm.py        # Must pass after any monitor change
├── docs/
│   ├── RESEARCH_HANDOFF.md        # ← MASTER PLAN with full code skeletons
│   ├── GPU_SERVER_SETUP.md        # Server setup guide (you already did this)
│   └── AD_LOG.md                  # Architecture decisions D1–D35
└── requirements.txt
```

---

## Config Constants (from `src/config.py`)

```python
ROLLING_WINDOW          = 10      # IF rolling buffer (count-based)
LSTM_WINDOW_LENGTH      = 30      # LSTM sliding window (count-based)
LSTM_WINDOW_STRIDE      = 5       # Window stride
TRAIN_FRACTION          = 0.7     # Chronological split
RANDOM_SEED             = 42      # All reproducible ops
K_SIGMA                 = 2.0     # Baseline/threshold sigma
cutoff_ts               = "2018-10-29 11:10:48"
LSTM_THRESH_OUT         = 1.010091
LSTM_THRESH_IN          = 1.512753
```

---

## Normalization Stats (saved in JSON — do not change)

**Out series** (`data/processed/lstm_norm_stats_out.json`):
```json
{
  "temp_injected_mean": 35.68003853096587,
  "temp_injected_std": 5.950910598500125,
  "log_gap_seconds_mean": 0.9894990680764548,
  "log_gap_seconds_std": 1.9985174353346589
}
```

---

## Environment Verification (Run These First)

```bash
cd ~/coldchain-ews-twin
source .venv/bin/activate

# 1. Run parity tests (must all pass before any new work)
python -m unittest tests/test_d33_prewarm.py -v

# 2. Quick smoke test
python -c "
import torch, tensorflow as tf, joblib, pandas, numpy
tf.get_logger().setLevel('ERROR')
m = tf.keras.models.load_model('models/lstm_out.h5', compile=False)
print('LSTM params:', m.count_params())
print('CUDA:', torch.cuda.is_available())
print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none')
print('ALL OK')
"
```

---

## Where to Start

**First task for this session:** Implement **P4 — Adaptive Threshold** (Kalman + CUSUM).

1. Create `src/adaptation/__init__.py` (empty)
2. Create `src/adaptation/adaptive_threshold.py` — see full code skeleton in `docs/RESEARCH_HANDOFF.md` Part 4 → P4
3. Integrate into `src/twin_monitors.py` — add `KalmanCUSUMAdapter` to both `IFMonitor` and `LSTMMonitor`
4. Run parity tests to ensure D33 still passes
5. Show before/after FPR comparison

The code skeleton is already written in `docs/RESEARCH_HANDOFF.md`. Read it before implementing.

---

## Academic Novelty Claims (for Report/Viva)

1. **P2:** First application of Newton's Law of Cooling as a PINN loss regularizer for cold-chain LSTM-AE
2. **P1:** First uncertainty-decomposed VAE (aleatoric + epistemic) for streaming IoT cold-chain EWS
3. **P4:** First online Kalman+CUSUM adaptive threshold for irregular-interval (count-based, non-i.i.d.) IoT anomaly detectors
4. **P5:** First Dempster-Shafer evidence-theoretic multi-detector fusion for cold-chain alarm triage

---

## Commit Convention

```bash
git add -A
git commit -m "research(p4): implement KalmanCUSUMAdapter for adaptive thresholding"
git push origin main
```

Format: `research(p#): description` for research proposals  
Also update relevant `Context/` files after each proposal and add entries to `docs/AD_LOG.md`.

---

*This primer was generated on 2026-11-02. The project SSOT is `Context/README.md`. The full improvement plan is `docs/RESEARCH_HANDOFF.md`. Everything is in the GitHub repo at `https://github.com/Krishna200608/coldchain-ews-twin`.*

