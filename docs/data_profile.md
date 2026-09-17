# Data Profile — IOT-temp.csv
## Cold Chain EWS Digital Twin — Milestone 1

---

> **⚠ STRUCTURAL PROXY NOTICE (mandatory restatement)**  
> The dataset profiled in this document (`atulanandjha/temperature-readings-iot-devices`,
> Kaggle — file: `IOT-temp.csv`, 6.63 MB) is a **generic IoT temperature sensor log.
> It is NOT real refrigerated-transport telemetry.** It is used exclusively as a
> structural proxy to exercise the ingestion and EDA pipeline while real cold-chain
> data is unavailable. Every statistic below describes the proxy dataset and makes no
> claim about operational cold-chain temperature behaviour.

---

## 1. File Identity

| Field | Value |
|-------|-------|
| Filename | `IOT-temp.csv` |
| File size | 6.63 MB |
| Kaggle slug | `atulanandjha/temperature-readings-iot-devices` |
| Version downloaded | v1 (via kagglehub) |

---

## 2. Row Count

| Metric | Value |
|--------|-------|
| Actual rows | **97,606** |
| Project-brief estimate | ~97,600 |
| Delta | **+6 rows (+0.01%)** |
| Status | ✅ MATCH (within 1%) |

The estimate in the project brief is accurate to within 6 rows. No discrepancy.

---

## 3. Column Names and Dtypes

Exact column list as read by `pd.read_csv()`:

| Column | dtype | Unique values | Nulls | Notes |
|--------|-------|---------------|-------|-------|
| `id` | object | 97,605 | 0 | Per-row UUID, format `__export__.temp_log_<N>_<hash>`. **Not a sensor device ID.** One duplicate row gives 97,605 unique IDs for 97,606 rows. |
| `room_id/id` | object | **1** | 0 | Single constant value: `"Room Admin"`. All readings belong to a single named room. No multi-sensor topology exists beyond the Out/In tag. |
| `noted_date` | object (string) | 27,920 | 0 | Timestamp strings in `DD-MM-YYYY HH:MM` format (day-first). Must be parsed with `dayfirst=True`. |
| `temp` | int64 | 31 | 0 | Integer temperature values, range 21–51. |
| `out/in` | object | **2** | 0 | Binary location tag: `"Out"` (77,261 rows, 79.16%) and `"In"` (20,345 rows, 20.84%). |

**Columns: `['id', 'room_id/id', 'noted_date', 'temp', 'out/in']`**

---

## 4. In/Out Tag Distribution

| Tag | Count | Percentage |
|-----|-------|-----------|
| `Out` | 77,261 | 79.16% |
| `In` | 20,345 | 20.84% |

The `"Out"` tag dominates with approximately 4× the row count of `"In"`. The dataset description on Kaggle characterises these as readings from inside and outside a room. In the cold-chain proxy context, `"Out"` would correspond to an external (ambient) sensor and `"In"` to an internal (cargo) sensor — but this mapping is not validated against real cold-chain semantics.

---

## 5. Timestamp Parsing

### Format

The `noted_date` column uses the format `DD-MM-YYYY HH:MM` (e.g., `08-12-2018 09:30`). This is **day-first**, not the US-style month-first format.

### Critical Parsing Issue

Pandas' default `pd.to_datetime()` without `dayfirst=True` incorrectly applies `MM-DD-YYYY` interpretation. For any date where the day value exceeds 12 (i.e., days 13–31), pandas cannot interpret the value in MM-DD format and silently produces `NaT`. This causes **47,662 rows (~48.8%) to fail parsing** and shifts the inferred date range by approximately 5 months (reporting Jan–Dec 2018 instead of the correct Jul–Dec 2018).

| Parse mode | Failures | Date range |
|------------|----------|-----------|
| Default (MM-DD-YYYY) | **47,662** | 2018-01-11 → 2018-12-10 (WRONG) |
| `dayfirst=True` ✅ | **0** | 2018-07-28 → 2018-12-08 (CORRECT) |

All downstream analysis uses `dayfirst=True`.

### Date Range (Correct)

| Field | Value |
|-------|-------|
| Earliest record | 2018-07-28 07:06 |
| Latest record | 2018-12-08 09:30 |
| Total span | **133 days, 2 hours, 24 minutes** (roughly 4.4 months) |
| Unique timestamps | 27,920 distinct `noted_date` strings |

---

## 6. Sampling Interval Analysis

> This section directly tests the "irregular sampling" claim from the project brief.

All statistics computed after sorting by correctly-parsed timestamp (`dayfirst=True`). A "gap" is the time in seconds between consecutive records in the full sorted dataset.

### Overall (All 97,606 records)

| Statistic | Value (seconds) | Value (minutes) |
|-----------|-----------------|-----------------|
| n gaps | 97,605 | — |
| min | 0.0 | 0.00 |
| p25 | 0.0 | 0.00 |
| **median** | **0.0** | **0.00** |
| p75 | 60.0 | 1.00 |
| **mean** | **117.82** | **1.96** |
| **std** | **5,446.3** | **90.8** |
| p95 | 240.0 | 4.00 |
| p99 | 600.0 | 10.00 |
| max | 999,480.0 | 16,658 (277.6 h) |
| **CoV (std/mean)** | **46.23** | — |

### Interpretation

**The "irregular sampling" claim holds — strongly and quantitatively.**

- The **median inter-reading gap is 0 seconds** because 71.40% of consecutive record pairs (69,686 of 97,605 gaps) have a zero gap. This occurs because `"Out"` and `"In"` readings are logged at the same minute-resolution timestamp — so when both sensors fire at the same minute, the gap between consecutive rows is 0.
- The **coefficient of variation (CoV) is 46.23**, far exceeding the 0.5 threshold for "irregular." Even excluding zero-gaps, the CoV remains extreme due to gaps ranging from 60 seconds to 277.6 hours.
- The **maximum gap of 999,480 seconds (≈277.6 hours ≈ 11.6 days)** indicates significant data collection outages, which is material for anomaly-detection modelling.
- The p75 is 60 s and p95 is 240 s (4 minutes), so the bulk of non-zero readings occur at roughly 1–4 minute intervals.

### Per out/in Tag

| Tag | n readings | median (s) | mean (s) | std (s) | max (s) | CoV |
|-----|-----------|-----------|---------|--------|--------|-----|
| `In` | 20,345 | 0.0 | 565.3 | 13,811 | 1,003,380 | 24.43 |
| `Out` | 77,261 | 0.0 | 148.8 | 6,190 | 999,480 | 41.59 |

Both tags show the same pattern: zero median (same-minute pairing), high mean driven by long outage gaps, and very high CoV. The `"In"` sensor has a higher mean gap (565 s vs. 149 s), meaning it was sampled less frequently than `"Out"`.

> **Important caveat**: The per-tag intervals computed above treat each tag's series as independent and sort globally. Because the dataset has only one room (`room_id/id = "Room Admin"`), there is no genuine per-sensor-device breakdown — the `"Out"` and `"In"` labels are the only topology available.

---

## 7. Missing Values

**No missing values in any column.**

| Column | Null count | Null % |
|--------|-----------|--------|
| `id` | 0 | 0.0000% |
| `room_id/id` | 0 | 0.0000% |
| `noted_date` | 0 | 0.0000% |
| `temp` | 0 | 0.0000% |
| `out/in` | 0 | 0.0000% |
| **Total** | **0** | **0.0000%** |

The dataset is complete — no imputation or forward-fill will be needed before modelling.

---

## 8. Duplicate Rows

| Metric | Value |
|--------|-------|
| Exact duplicate rows | **1** |
| Duplicate % | 0.0010% |

One exact duplicate row exists. It is negligible in proportion (0.001%) but should be removed in preprocessing to avoid double-counting in any aggregation or anomaly-detection window.

---

## 9. Temperature Value Distribution

All 97,606 temperature values are present (no nulls). The values are integers.

| Statistic | Value |
|-----------|-------|
| count | 97,606 |
| min | **21** |
| mean | **35.054** |
| median | **35** |
| std | **5.700** |
| max | **51** |
| n distinct values | 31 |
| value range | 21–51 (integer steps) |

### Sentinel / Implausible Value Check

| Check | Count |
|-------|-------|
| Values < −50 | **0** |
| Values > 100 | **0** |
| Values == −99 | **0** |
| Values == 999 | **0** |
| Values == 0 | **0** |

**No sentinel values or implausible readings found.** The range 21–51°C is internally consistent with a room-temperature logger in a subtropical environment. It is, however, far outside the cold-chain operating range (typically −25°C to +5°C for frozen, 2–8°C for pharmaceutical). This is expected: the dataset is a structural proxy and does not represent cold-chain temperatures.

---

## 10. Sensor / Room ID Cardinality

### `room_id/id` column

- **1 unique value**: `"Room Admin"`
- All 97,606 readings originate from a single named room/location.
- **There is no multi-sensor/multi-room topology in this dataset.** The only structural distinction between readings is the `"Out"` / `"In"` tag.

### `id` column

- **97,605 unique values** across 97,606 rows (1 non-unique pair → the duplicate row)
- Format: `__export__.temp_log_<integer>_<8-char hex hash>`
- This is a **per-record UUID**, not a sensor device ID. It cannot be used to group readings by sensor.

### Reading counts by `out/in` tag

| Tag | n readings | % of total |
|-----|-----------|-----------|
| `Out` | 77,261 | 79.16% |
| `In` | 20,345 | 20.84% |

---

## 11. Summary of Data Quality Issues

| Issue | Severity | Count | Notes |
|-------|----------|-------|-------|
| Timestamp ambiguity (day-first format) | ⚠ High | affects 47,662 rows if parsed incorrectly | Fixed by using `dayfirst=True`; zero parse failures with correct parser |
| Duplicate rows | Low | 1 | Drop before modelling |
| Missing values | None | 0 | Dataset is complete |
| Sentinel/error temperatures | None | 0 | All values in plausible proxy range |
| Zero-duration gaps (same-minute pairs) | Informational | 69,686 pairs | Expected: Out+In readings at same minute |
| Long outage gaps | Informational | max 277.6 h | Material for window-based anomaly detection |
| Degenerate room_id | Informational | 1 unique room | No multi-sensor topology beyond Out/In tag |

---

## 12. Proxy Limitation — Final Restatement

This dataset (`IOT-temp.csv`) is a generic IoT temperature sensor log from a
residential/office-type environment. Its temperature range (21–51°C), single-room
topology, and out/in binary sensor tag are **structurally similar** to a cold-chain
sensor log in terms of the data engineering challenges (irregular sampling, paired
sensor readings, timestamp parsing issues) but are **not representative** of real
cold-chain telemetry in any of the following respects:

- Temperature range is 21–51°C vs. cold-chain ranges of −25°C to +8°C
- There is no cargo identity, shipment metadata, or GPS context
- The "out/in" tag does not map directly to cargo vs. ambient sensor semantics
- The data covers 4.4 months from a single anonymous room

Any anomaly threshold, distribution parameter, or feature derived from this
dataset must be re-validated against real cold-chain telemetry before the EWS
can be considered operationally meaningful.
