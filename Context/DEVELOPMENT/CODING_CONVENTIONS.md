# Coding Conventions & Standards

This document establishes the code quality, architectural modularity, type safety, and documentation standards enforced across this repository.

---

## 1. Code Style & Formatting Standards

- **PEP-8 Adherence:** All code must conform strictly to Python PEP-8 styling standards.
- **Python Version Target:** Code must be compatible with **Python 3.11.x**.
- **Modern Typing Annotations:** Every Python module must include `from __future__ import annotations` at the top of the file to support concise union syntax (`int | None`, `tuple[str, ...]`).
- **Strict Type Hinting:** Function arguments, return values, and class attributes must be explicitly typed. Avoid defaulting to `Any`.

```python
from __future__ import annotations
import pathlib
import pandas as pd

def compute_lead_time(
    alarm_ts: pd.Timestamp | None,
    irrev_ts: pd.Timestamp | None,
) -> float | None:
    """Compute lead time in minutes between alarm and irreversibility."""
    if alarm_ts is None or irrev_ts is None:
        return None
    return (irrev_ts - alarm_ts).total_seconds() / 60.0
```

---

## 2. Architectural Modularity & Boundaries

1. **Separation of Concerns:**
   - **`src/`:** Contains core data acquisition, feature engineering, model training, and digital twin simulation logic. `src/` modules must have **zero dependencies** on UI libraries (`streamlit`, `altair`).
   - **`dashboard/`:** Contains UI layout, reactive controls, and visualization components. Models and monitors are imported directly from `src/` without duplicating logic.
2. **Centralization of Named Constants:**
   - Hardcoded magic numbers are strictly prohibited.
   - Core pipeline constants must be defined and imported from [`src/config.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/config.py).
   - UI visual constants and thresholds must be defined in [`dashboard/constants.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/dashboard/constants.py).
3. **Immutability & Non-Destructive Data Handling:**
   - Never mutate input DataFrames or numpy arrays in-place.
   - Create explicit copies (`df = df_clean.copy()`) before applying transformations or synthetic perturbations.

---

## 3. Contamination Guardrails & Defensive Assertions

Every script interacting with ground-truth reference tables must enforce defensive assertions:
- **Clean File Guard:**
  ```python
  assert "is_injected_anomaly" not in df_clean.columns, (
      "CONTAMINATION ERROR: Clean reference file contains injected anomaly columns! "
      "Re-run src/preprocessing.py to restore uncorrupted baseline."
  )
  ```
- **File Existence Guard:** Check file existence with clear remediation instructions before attempting I/O operations.

---

## 4. Logging & Diagnostic Output

- Use Python's built-in `logging` module rather than raw `print()` statements in pipeline scripts.
- Standard format string:
  ```python
  logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s [%(levelname)s] %(message)s",
      datefmt="%Y-%m-%d %H:%M:%S",
  )
  logger = logging.getLogger(__name__)
  ```
- Use parameterized logging (`logger.info("Processed %d rows", n)`) instead of string interpolation (`logger.info(f"...")`) to minimize unnecessary formatting overhead.

---

## 5. Documentation & Architectural Linking

- Every module must feature a comprehensive header docstring explaining:
  1. Module purpose and primary entry points.
  2. The structural proxy notice.
  3. The specific **Architectural Decisions (D1–D35)** implemented.
  4. Expected inputs and generated outputs.

