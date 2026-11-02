# GPU Server Setup Guide
## Cold Chain EWS Digital Twin — RTX 5000 Ada (SSH)

> **Purpose:** Complete, self-contained guide to clone, configure, and verify the project on the college GPU server via SSH. Follow every step in order.
>
> **Repository:** `https://github.com/Krishna200608/coldchain-ews-twin`  
> **GPU:** NVIDIA RTX 5000 Ada Generation, 32 GB VRAM  
> **Python:** 3.11  
> **Framework:** Existing code = TensorFlow/Keras; new research models = PyTorch

---

## Phase 0 — Connect to the GPU Server

```bash
# Connect (replace with actual college server IP and your username)
ssh <your-username>@<college-gpu-server-ip>

# Verify you are on the right machine
hostname
whoami

# Verify GPU is accessible
nvidia-smi
```

**Expected `nvidia-smi` output:**
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI ...   Driver Version: ...   CUDA Version: 12.x                  |
+-----------------------------------------------------------------------------+
| GPU  Name        ...    Memory-Usage           GPU-Util  ...                |
|   0  NVIDIA RTX 5000 Ada Generation   32520MiB / 32768MiB  ...             |
+-----------------------------------------------------------------------------+
```

If `nvidia-smi` fails → contact college IT before proceeding.

---

## Phase 1 — System Dependencies Check

```bash
# Check Python availability (need 3.11)
python3 --version           # May show 3.10 or 3.12 — either is fine to start
python3.11 --version        # Prefer 3.11 specifically

# If Python 3.11 not installed:
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Check git
git --version               # Need >= 2.30

# Check available disk space (need at least 5 GB for data + models + venv)
df -h ~
```

---

## Phase 2 — Clone the Repository

```bash
# Navigate to your home or preferred work directory
cd ~

# Clone the repository
git clone https://github.com/Krishna200608/coldchain-ews-twin.git
cd coldchain-ews-twin

# Verify you are on main branch at the latest commit
git log --oneline -5
```

**Expected latest commits (as of 2026-11-02):**
```
be8bb8b docs: add comprehensive AI agent research handoff document
2732953 docs: establish centralized /Context Single Source of Truth directory (M7)
12662a9 feat(ui): upgrade telemetry chart legend into modern colored badge pills
```

---

## Phase 3 — Create Python Virtual Environment

```bash
# Inside the cloned repo
cd ~/coldchain-ews-twin

# Create venv with Python 3.11
python3.11 -m venv .venv

# Activate venv (Linux/macOS — this is what you use on SSH)
source .venv/bin/activate

# Verify correct Python inside venv
python --version          # Should show Python 3.11.x
which python              # Should point inside .venv/
```

---

## Phase 4 — Install PyTorch with CUDA (RTX 5000 Ada)

> [!IMPORTANT]
> Install PyTorch **before** `requirements.txt` to get the correct CUDA build. RTX 5000 Ada = Ada Lovelace architecture = CUDA Compute Capability 8.9.

```bash
# Activate venv (if not already active)
source ~/.venv/bin/activate
# or: source ~/coldchain-ews-twin/.venv/bin/activate

# Check CUDA version on the server (pick the matching PyTorch build)
nvcc --version             # Shows CUDA toolkit version
# OR check driver CUDA version:
nvidia-smi | grep "CUDA Version"

# Install PyTorch for CUDA 12.1 (most common on modern servers with RTX 5000 Ada)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# --- ALTERNATIVE: if server has CUDA 11.8 ---
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# --- ALTERNATIVE: if server has CUDA 12.4 ---
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Verify PyTorch CUDA works
python -c "
import torch
print('PyTorch version:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
print('CUDA version:', torch.version.cuda)
print('GPU name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE')
print('VRAM (GB):', torch.cuda.get_device_properties(0).total_memory / 1e9 if torch.cuda.is_available() else 0)
"
```

**Expected output:**
```
PyTorch version: 2.x.x+cu121
CUDA available: True
CUDA version: 12.1
GPU name: NVIDIA RTX 5000 Ada Generation
VRAM (GB): 32.xx
```

If `CUDA available: False` → the wrong PyTorch build was installed. Re-run with correct CUDA version.

---

## Phase 5 — Install Project Dependencies (requirements.txt)

```bash
cd ~/coldchain-ews-twin
source .venv/bin/activate

# Install all project dependencies
pip install -r requirements.txt

# Install additional research packages (not yet in requirements.txt)
pip install pytorch-forecasting pytorch-lightning optuna

# Verify key packages
python -c "
import tensorflow as tf
import sklearn
import simpy
import streamlit
import pandas as pd
import numpy as np
print('TensorFlow:', tf.__version__)
print('scikit-learn:', sklearn.__version__)
print('SimPy:', simpy.__version__)
print('Streamlit:', streamlit.__version__)
print('Pandas:', pd.__version__)
print('NumPy:', np.__version__)
"
```

**Known issue:** TensorFlow on Linux may show CUDA-related warnings at import. These are safe to ignore as long as the import succeeds. The existing LSTM models run on CPU during inference (fast enough for the 12,866-parameter model).

---

## Phase 6 — Verify Pre-built Model Files (from GitHub LFS or local transfer)

The following model files must exist. **They are NOT regenerated from scratch — they come from the repo or are transferred from local machine.**

```bash
ls -lh ~/coldchain-ews-twin/models/
```

**Required files:**
```
models/
├── isolation_forest_out.joblib    (~1 MB)
├── isolation_forest_in.joblib     (~830 KB)
├── lstm_out.h5                    (~193 KB)  ← Keras LSTM-AE, Out series
└── lstm_in.h5                     (~193 KB)  ← Keras LSTM-AE, In series
```

If any `.h5` or `.joblib` file is missing, transfer from local Windows machine:

```powershell
# Run this on your LOCAL Windows machine (PowerShell):
$GPU_SERVER = "<your-username>@<college-gpu-server-ip>"
$REPO = "d:\Lab\Managing Corporate Entrepreneurship\coldchain-ews-twin"

# Transfer model files
scp "$REPO\models\lstm_out.h5" "${GPU_SERVER}:~/coldchain-ews-twin/models/"
scp "$REPO\models\lstm_in.h5" "${GPU_SERVER}:~/coldchain-ews-twin/models/"
scp "$REPO\models\isolation_forest_out.joblib" "${GPU_SERVER}:~/coldchain-ews-twin/models/"
scp "$REPO\models\isolation_forest_in.joblib" "${GPU_SERVER}:~/coldchain-ews-twin/models/"
```

---

## Phase 7 — Transfer Pre-processed Data Files

These CSV/JSON/NPZ files take hours to regenerate. Transfer them directly.

```powershell
# Run on LOCAL Windows machine (PowerShell):
$GPU_SERVER = "<your-username>@<college-gpu-server-ip>"
$DATA = "d:\Lab\Managing Corporate Entrepreneurship\coldchain-ews-twin\data\processed"
$DEST = "${GPU_SERVER}:~/coldchain-ews-twin/data/processed/"

# Transfer all processed data at once (scp recursive)
scp -r "$DATA" "${GPU_SERVER}:~/coldchain-ews-twin/data/"
```

**Verify on server:**
```bash
ls -lh ~/coldchain-ews-twin/data/processed/ | wc -l   # Should show ~35 files
ls ~/coldchain-ews-twin/data/processed/*.json          # Should list 6 JSON files
ls ~/coldchain-ews-twin/data/processed/*.npz           # Should list 4 NPZ files
```

**Critical files that MUST be present:**
```
data/processed/
├── out_features.csv              (clean, ~9.5 MB — NEVER overwrite)
├── in_features.csv               (clean, ~2.5 MB — NEVER overwrite)
├── out_labeled.csv               (~10 MB)
├── in_labeled.csv                (~2.7 MB)
├── lstm_norm_stats_out.json      (normalization constants)
├── lstm_norm_stats_in.json
├── lstm_windows_out_train.npz    (pre-built training windows)
├── lstm_windows_out_val.npz
├── lstm_windows_in_train.npz
├── lstm_windows_in_val.npz
├── if_pointwise_metrics.json     (verified benchmark metrics)
├── lstm_pointwise_metrics.json
├── three_way_comparison.csv      (lead time table)
├── twin_crosscheck_report.csv    (batch vs. live parity)
└── injection_log.csv             (30 injection audit trail)
```

---

## Phase 8 — Run Verification Tests

```bash
cd ~/coldchain-ews-twin
source .venv/bin/activate

# Run the parity test suite (must all pass before any new development)
python -m unittest tests/test_d33_prewarm.py -v
```

**Expected output:**
```
test_all_detectors_have_correct_prewarm_count ... ok
test_lstm_prewarm_reproduces_alarm_timestamps ... ok
test_if_prewarm_reproduces_alarm_timestamps ... ok
----------------------------------------------------------------------
Ran 3 tests in ~16s
OK
```

If any test fails → data transfer was incomplete. Re-transfer the relevant CSV files.

---

## Phase 9 — Quick Smoke Test (End-to-End)

```bash
cd ~/coldchain-ews-twin
source .venv/bin/activate

python -c "
import pathlib, json, numpy as np, pandas as pd

# 1. Verify processed data
data_dir = pathlib.Path('data/processed')
required = [
    'lstm_norm_stats_out.json', 'lstm_norm_stats_in.json',
    'lstm_windows_out_train.npz', 'lstm_windows_in_train.npz',
    'out_labeled.csv', 'in_labeled.csv',
    'if_pointwise_metrics.json', 'lstm_pointwise_metrics.json',
]
for f in required:
    p = data_dir / f
    assert p.exists(), f'MISSING: {f}'
    print(f'  OK: {f}')

# 2. Verify models load
import joblib
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

m_out = tf.keras.models.load_model('models/lstm_out.h5', compile=False)
m_in  = tf.keras.models.load_model('models/lstm_in.h5', compile=False)
if_out = joblib.load('models/isolation_forest_out.joblib')
if_in  = joblib.load('models/isolation_forest_in.joblib')
print(f'  OK: lstm_out.h5 ({m_out.count_params()} params)')
print(f'  OK: lstm_in.h5  ({m_in.count_params()} params)')
print(f'  OK: isolation_forest_out.joblib')
print(f'  OK: isolation_forest_in.joblib')

# 3. Verify normalization stats
stats = json.load(open('data/processed/lstm_norm_stats_out.json'))
assert abs(stats['temp_injected_mean'] - 35.68) < 0.01
print(f'  OK: norm_stats_out.json (temp_mean={stats[\"temp_injected_mean\"]:.4f})')

# 4. Verify benchmark metrics
lm = json.load(open('data/processed/lstm_pointwise_metrics.json'))
assert abs(lm['In']['auc_pr'] - 0.3852) < 0.01
print(f'  OK: lstm_pointwise_metrics.json (In PR-AUC={lm[\"In\"][\"auc_pr\"]:.4f})')

# 5. Verify PyTorch
import torch
print(f'  OK: PyTorch {torch.__version__}, CUDA={torch.cuda.is_available()}, GPU={torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')

print()
print('ALL CHECKS PASSED. Environment is ready.')
"
```

---

## Phase 10 — Configure Jupyter for GPU Notebooks

```bash
cd ~/coldchain-ews-twin
source .venv/bin/activate

# Install Jupyter kernel for this venv
python -m ipykernel install --user --name coldchain-gpu --display-name "ColdChain GPU (3.11)"

# Start Jupyter on the server (port-forwarded to local browser)
# On SERVER — run in a tmux session:
tmux new -s jupyter
jupyter lab --no-browser --port=8888 --ip=0.0.0.0
# Ctrl+B, D to detach from tmux

# On LOCAL machine (PowerShell) — SSH tunnel:
ssh -L 8888:localhost:8888 <your-username>@<college-gpu-server-ip> -N
# Then open: http://localhost:8888 in local browser
# Use token shown in tmux session
```

---

## Phase 11 — Optional: Install Antigravity CLI on the Server

> This allows you to start a new Antigravity chat session directly from the GPU server terminal.

```bash
# Install the Antigravity CLI (agy)
curl -sSL https://storage.googleapis.com/antigravity-releases/install.sh | bash
# Or via pip if available:
# pip install antigravity-cli

# Verify installation
agy --version

# Start a new Antigravity session in the repo directory
cd ~/coldchain-ews-twin
agy chat
```

When the new Antigravity chat opens, paste the contents of `PRIMER.md` (see below) as your first message. This bootstraps the AI agent with full project context.

---

## Summary: What Each Phase Accomplishes

| Phase | What It Does | Required? |
|-------|-------------|-----------|
| 0 | SSH connect + GPU verify | ✅ Always |
| 1 | System dependency check | ✅ Always |
| 2 | Clone repo | ✅ Always |
| 3 | Create Python venv | ✅ Always |
| 4 | Install PyTorch + CUDA | ✅ For GPU training |
| 5 | Install requirements.txt | ✅ Always |
| 6 | Transfer model files | ✅ If not in git |
| 7 | Transfer processed data | ✅ Always (large files) |
| 8 | Run parity tests | ✅ Before any code changes |
| 9 | Smoke test | ✅ Confirm all assets intact |
| 10 | Jupyter setup | Optional (for notebooks) |
| 11 | Install Antigravity CLI | Optional (for AI-assisted dev) |

---

## Troubleshooting

### `nvidia-smi: command not found`
```bash
export PATH=$PATH:/usr/local/cuda/bin
sudo apt install -y nvidia-utils-<version>
```

### `ModuleNotFoundError: No module named 'src'`
```bash
# Always run from repo root, not from inside src/
cd ~/coldchain-ews-twin
python src/twin_monitors.py  # not: cd src && python twin_monitors.py
```

### TensorFlow CUDA warnings at import
Safe to ignore. Add `export TF_CPP_MIN_LOG_LEVEL=3` to `~/.bashrc`.

### `torch.cuda.is_available()` returns False
PyTorch CUDA build doesn't match server CUDA version. Check `nvcc --version` and reinstall PyTorch with matching `cu###` index.

### scp transfer too slow
```bash
# Use rsync instead (much faster for many small files)
rsync -avz --progress \
  "d:\Lab\Managing Corporate Entrepreneurship\coldchain-ews-twin\data\processed\\" \
  "<username>@<ip>:~/coldchain-ews-twin/data/processed/"
```

### Disk quota exceeded
```bash
# Check quota
quota -s
# Clear pip cache
pip cache purge
# Remove __pycache__ directories
find ~/coldchain-ews-twin -type d -name __pycache__ -exec rm -rf {} +
```

