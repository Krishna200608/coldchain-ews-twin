# Development Environment Setup

This document outlines the step-by-step procedure for configuring a local development environment for the Cold Chain Early Warning System Digital Twin project.

---

## 1. System Prerequisites

- **Operating System:** Windows 10/11, macOS (12.0+), or Ubuntu Linux (20.04/22.04 LTS).
- **Python:** **Python 3.11.x (64-bit)** is required. (Python 3.12+ may encounter binary wheel compatibility issues with older TensorFlow 2.15 builds).
- **Git:** Version 2.30+ installed.
- **Hardware Requirements:**
  - Minimum 8 GB RAM (16 GB recommended for full in-memory replay).
  - Multi-core CPU (quad-core or higher).
  - Dedicated GPU is **not required** for local development or inference; all models run locally on CPU.

---

## 2. Virtual Environment Setup

Always develop inside an isolated Python virtual environment to avoid package contamination.

### 2.1. Clone Repository & Initialize Environment
```bash
# Clone the repository
git clone https://github.com/Krishna200608/coldchain-ews-twin.git
cd coldchain-ews-twin

# Create virtual environment with Python 3.11
python -m venv .venv
```

### 2.2. Activate Environment
- **Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
  *(If execution policy blocks scripts, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*
- **Windows (Command Prompt):**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```
- **macOS / Linux (Bash/Zsh):**
  ```bash
  source .venv/bin/activate
  ```

---

## 3. Dependency Installation

Upgrade package management tools and install the frozen dependencies from `requirements.txt`:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 3.1. Verification of Critical Packages
Run the following verification snippet to confirm core frameworks are functioning:

```bash
python -c "import pandas, sklearn, tensorflow, simpy, streamlit; print('All core packages successfully imported.')"
```

---

## 4. Kaggle API Configuration

To enable automated dataset download via `src/data_acquisition.py`:

1. Log in to [Kaggle](https://www.kaggle.com) and navigate to **Account Settings** (`https://www.kaggle.com/settings`).
2. Scroll to the **API** section and click **"Create New Token"**.
3. Save the downloaded `kaggle.json` file to your user directory:
   - **Windows:** `C:\Users\<username>\.kaggle\kaggle.json`
   - **macOS / Linux:** `~/.kaggle/kaggle.json`
4. Secure permissions on Unix systems:
   ```bash
   chmod 600 ~/.kaggle/kaggle.json
   ```

---

## 5. IDE Configuration (VS Code)

To ensure smooth module imports without manual `sys.path` tampering:
1. Open the repository root in VS Code (`code .`).
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P`), search for **"Python: Select Interpreter"**, and choose the interpreter inside `./.venv`.
3. Set the terminal working directory to the repository root. All scripts and tests are designed to be executed from the root directory.

