# Testing & Quality Assurance Guide

This document details the automated testing framework, test suite organization, assertion criteria, and quality assurance procedures for the repository.

---

## 1. Testing Philosophy & Regression Boundaries

The testing philosophy is designed around mathematical determinism and architectural invariants:
- **No Flaky Tests:** Tests avoid wall-clock sleep assertions or non-deterministic network calls.
- **Invariant Protection:** Unit tests explicitly verify that modular abstractions (such as isolated window replays in the UI) do not deviate from verified full-stream calculations.
- **Contamination Guards:** Pre-flight assertions verify that ground-truth clean reference tables remain uncorrupted by synthetic anomaly injection code.

---

## 2. Test Suite Inventory (`tests/`)

### `tests/test_d33_prewarm.py`
Validates the **D33 Buffer Pre-Warming Protocol** used in the interactive dashboard:
- **Test Case 1 (`test_if_monitor_prewarm`):** Tests that an `IFMonitor` pre-warmed with 10 trailing historical readings generates instantaneous rolling statistics (`rolling_mean_if`, `rolling_std_if`) and decision scores that identically match the continuous, un-sliced stream from frame index 0.
- **Test Case 2 (`test_lstm_monitor_prewarm`):** Tests that an `LSTMMonitor` pre-warmed with 30 trailing pairs generates valid causal reconstruction MSE scores without triggering cold-start `NaN` blind spots.
- **Test Case 3 (`test_zero_alarm_during_prewarm`):** Confirms that pre-warming feeds historical data silently, emitting zero alarms during the priming phase.

---

## 3. Running the Test Suite

Execute tests using Python's built-in `unittest` runner from the repository root:

### 3.1. Run Specific Test Module
```bash
python -m unittest tests/test_d33_prewarm.py
```

### 3.2. Run in Verbose Mode
```bash
python -m unittest -v tests/test_d33_prewarm.py
```

Expected output:
```text
test_if_monitor_prewarm (tests.test_d33_prewarm.TestD33Prewarming) ... ok
test_lstm_monitor_prewarm (tests.test_d33_prewarm.TestD33Prewarming) ... ok
test_zero_alarm_during_prewarm (tests.test_d33_prewarm.TestD33Prewarming) ... ok

----------------------------------------------------------------------
Ran 3 tests in 1.482s

OK
```

### 3.3. Discover All Tests Across Repository
```bash
python -m unittest discover tests
```

---

## 4. Contributor Pre-Commit Verification Checklist

Before opening a pull request or committing changes, verify the following 4 gates:

1. **Clean Data Integrity Gate:** Verify clean reference files are untouched:
   ```bash
   python -c "import pandas as pd; df = pd.read_csv('data/processed/out_features.csv'); assert 'is_injected_anomaly' not in df.columns, 'Clean file contaminated!'"
   ```
2. **Pre-Warming Regression Gate:** Run `python -m unittest tests/test_d33_prewarm.py`. All tests must pass.
3. **Startup Verification Gate (D32):** Run `python -c "from dashboard.data_loader import run_d32_startup_check; assert len(run_d32_startup_check()) == 0, 'Missing artifacts!'"`
4. **Cross-Check Parity Gate (M5b):** Run `python src/twin_crosscheck.py` and ensure mismatches (`match == 'False'`) remain **0**.

