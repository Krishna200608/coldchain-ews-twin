# Project Dataset Submission: Topic 21 — Digital Twin-Based Early Warning System for Cold Chain Disruption Detection

**Course:** Managing Corporate Entrepreneurship (B.Tech 2026, 7th Semester)  
**Institution:** Indian Institute of Information Technology, Allahabad (IIITA)  
**Instructor / Supervisor:** Dr. Netranand Pathak  
**Student Name:** Krishna Sikheriya  
**Roll Number:** IIT2023139  
**Submission Due Date:** September 27, 2026  

---

## 1. Dataset Identification and Source Information

| Attribute | Details |
|---|---|
| **Dataset Name** | IoT Temperature Sensor Readings (`IOT-temp.csv`) |
| **Primary File** | `IOT-temp.csv` (uncompressed: 6.63 MB / 6,948,127 bytes) |
| **Verifiable Repository Source** | Kaggle: `https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices` |
| **Original Data Provider** | Atulanand Jha (Data Scientist / Machine Learning Engineer) |
| **Data Collection Context** | Continuous environmental IoT temperature sensor installation logging physical enclosure and ambient surroundings |
| **License / Access** | Open Data / CC0: Public Domain |

---

## 2. Temporal Coverage and Parsing Specifications

- **Observation Date Range:** July 28, 2018 at 07:06:00 to December 8, 2018 at 09:30:00 (`2018-07-28 07:06:00` to `2018-12-08 09:30:00`).
- **Total Duration Covered:** **133 days, 2 hours, 24 minutes** (~4.4 continuous months of physical logging).
- **Unique Timestamps:** 27,920 distinct recording minute-intervals.
- **Critical Timestamp Parsing Protocol:** The timestamp format in the raw file is Day-First (`DD-MM-YYYY HH:MM`, e.g., `08-12-2018 09:30`). Default US-style month-first parsers silently fail on 47,662 rows (48.83% of data) where the day exceeds 12. Using strict `dayfirst=True` parses 100% of rows with zero failures across the true 133-day period.

---

## 3. Observation Volume and Partitioning Breakdown

- **Total Raw Observations:** **97,606 rows** (exactly 5 columns).
- **Unique Deduplicated Observations:** **97,605 rows** (1 exact duplicate row identified and removed during data hygiene cleaning).
- **Missing / Null Values:** **0 nulls across all columns** (100% complete).
- **Dual Environmental Spatial Streams:**
  - **`"Out"` (External Ambient Stream):** 77,260 observations (79.16% of dataset). Ambient environmental baseline with wider diurnal oscillations.
  - **`"In"` (Internal Enclosure Stream):** 20,345 observations (20.84% of dataset). Internal temperature monitoring representing cargo enclosure behavior.
- **Chronological Disjoint Partitioning:**
  To guarantee zero future look-ahead leakage in machine learning training, the dataset is partitioned chronologically using a 70% train / 30% test split (`cutoff_timestamp = 2018-10-29 11:10:48`):
  - **Training Partition (70%):** 63,887 Out rows, 16,577 In rows. Used exclusively for baseline threshold computation, Isolation Forest fitting, and LSTM-Autoencoder reconstruction manifold training.
  - **Test Partition (30%):** 13,372 Out rows, 3,767 In rows. Held out untouched for out-of-sample early-warning lead-time evaluation.

---

## 4. Variables and Data Dictionary

### A. Raw Columns in `IOT-temp.csv`

| Variable Name | Data Type | Missing Count | Unique Values | Description & Operational Role |
|---|---|---|---|---|
| `id` | String / Object | 0 | 97,605 | Unique transaction hash per sensor reading (`__export__.temp_log_<N>_<hash>`). |
| `room_id/id` | String / Object | 0 | 1 | Invariant monitoring room identifier (`"Room Admin"` across all records). Confirms single physical site boundary. |
| `noted_date` | String / Object | 0 | 27,920 | Day-first timestamp string (`DD-MM-YYYY HH:MM`). Converted to pandas `datetime64[ns]` with `dayfirst=True`. |
| `temp` | Integer (`int64`) | 0 | 31 | Recorded physical temperature in degrees Celsius (°C). Range: 21 °C to 51 °C. |
| `out/in` | String / Object | 0 | 2 | Binary location flag categorizing reading location (`"Out"` ambient vs. `"In"` internal enclosure). |

### B. Engineered Telemetry & Anomaly Variables (Derived for Project Methodology)

| Derived Variable | Mathematical Formulation | Operational Role in Project |
|---|---|---|
| `gap_seconds` | $\Delta t_k = t_k - t_{k-1}$ | Inter-arrival sampling interval in seconds, driving the SimPy virtual clock. |
| `rolling_mean` | Trailing 10-reading window mean | Causal moving central tendency (zero look-ahead leakage). |
| `rolling_std` | Trailing 10-reading window standard deviation | Causal moving volatility, detecting frozen signal variance collapse. |
| `temp_injected` | $x_k + \delta_k$ | Controlled synthetic perturbation stream (step, drift, flatline). |
| `is_injected_anomaly` | Boolean $\{0, 1\}$ | Explicit ground-truth indicator for evaluation lead times. |

---

## 5. Comprehensive Justification for Dataset Selection

### A. Direct Alignment with Prescribed Project Guidelines
This dataset was identified and selected in direct fulfillment of the supervisor's instruction for **Topic 21** (*"Please go ahead and download the dataset from Kaggle: atulanandjha/temperature-readings-iot-devices"*).

### B. Fulfillment of Research Objectives & Methodology
The central research question of this project is:
> *"How early and how accurately can an anomaly detection model embedded in a cold chain digital twin flag disruptions relative to when spoilage actually becomes irreversible?"*

`IOT-temp.csv` satisfies every empirical requirement necessary to answer this question:

1. **Realistic Irregular Arrival Dynamics for Digital Twin Simulation:**
   In real-world logistics, telemetry packets do not arrive at neat, uniform intervals; they suffer from network jitter, edge polling delays, and transmission dropouts. In this dataset, the inter-arrival gap exhibits severe irregularity:
   - Median gap: 0.0 seconds (due to simultaneous dual-tag logging).
   - Mean gap: 117.82 seconds; Standard deviation: 5,446.3 seconds.
   - **Coefficient of Variation ($\text{CoV} = \sigma / \mu$): 46.23**, quantitatively confirming extreme dispersion.
   - Maximum transmission blackout: 999,480 seconds (~11.57 days).
   This enables the **SimPy discrete-event digital twin** to operate on an event-driven virtual clock driven by real historical arrival gaps rather than synthetic artificial ticks.

2. **Structural Proxy for Cold-Chain Telemetry (Academic Rigor & Honesty):**
   Real, disruption-annotated refrigerated transport fleet data is commercially sensitive, proprietary, and unavailable in open research repositories. This dataset serves as a rigorous **structural proxy**:
   - It captures true physical sensor noise, diurnal cycling, and irregular edge polling.
   - By openly classifying it as a structural proxy rather than misrepresenting it as refrigerated cargo data, the study preserves strict scientific validity and makes zero ungrounded food-safety claims.

3. **Substantial Observation Scale for Deep Learning:**
   With 97,606 observations spanning 4.4 months, the dataset contains ample statistical depth to train deep sequential models (bivariate LSTM-Autoencoder) on normal operational behavior without overfitting or data exhaustion.

4. **Controlled Benchmark Baseline for Synthetic Disruption Injection:**
   Because raw IoT streams carry no verified ground-truth disruption annotations, the clean unperturbed stream provides the ideal neutral baseline for seeding 30 controlled disruption archetypes (abrupt step breaches, gradual linear drifts, and sensor flatline stiction). This allows exact mathematical measurement of early-warning lead times ($\Delta t_{\text{lead}} = t_{\text{irreversibility}} - t_{\text{alarm}}$).

5. **Verified Zero Silent Divergence in Digital Twin Replay:**
   The dataset was empirically validated to replay bit-for-bit through the 3-stage SimPy digital twin (`Source -> Transit -> Destination`) with **$0.00 \times 10^0$ seconds timing discrepancy** and 100% live/batch cross-check parity (42/42 valid test evaluations matching exactly).

---

## 6. Summary Checklist against Assignment Requirements

- [x] **Relevant to project topic:** Real IoT temperature telemetry directly supporting discrete-event digital twin replay and anomaly detection.
- [x] **Recent & up-to-date:** Comprehensive 4.4-month multi-thousand reading sensor log.
- [x] **Sufficient observations:** 97,606 raw readings; >63,000 training rows and >13,000 test rows.
- [x] **Differentiation:** Unique dataset identified and designated specifically for Topic 21.
- [x] **Verifiable and reliable source:** Hosted on Kaggle with public provenance, MD5 hash verification, and CC0 licensing.
- [x] **Quality checked:** 0 missing values, timestamp day-first format verified, single site boundary confirmed.
- [x] **Direct pipeline integration:** Fully integrated into published GitHub codebase (`https://github.com/Krishna200608/coldchain-ews-twin`) and public live dashboard (`https://coldchain-ews-twin.streamlit.app/`).
