# Streaming Anomaly Monitors

The streaming anomaly monitors (`src/twin_monitors.py`) provide stateful, incremental implementations of the three detection algorithms, executing online inference within the digital twin's Destination stage.

---

## 1. Streaming Architecture & State Management

In offline batch evaluation, entire matrices are sliced and evaluated simultaneously. In live operations, telemetry arrives sequentially:
- A live monitor must maintain **internal state** (rolling observation deques).
- Inference must be **incrementally computable** at $\mathcal{O}(1)$ time complexity per event.
- **Continuous Buffer Discipline (D23):** State deques persist continuously across the entire telemetry timeline (`train` $\to$ `val` $\to$ `test`) without artificial flushes, matching true production behavior.

```mermaid
flowchart TD
    Event["Incoming Telemetry Packet<br>(temp_injected, gap_seconds, ts)"]
    
    Event --> BaseMon["BaselineMonitor<br>Direct Scalar Comparison"]
    Event --> IFMon["IFMonitor<br>Rolling Deque (maxlen=10)"]
    Event --> LSTMMon["LSTMMonitor<br>Rolling Deque (maxlen=30)"]
    
    BaseMon -->|temp > threshold| BaseAlarm["Baseline Alarm Flag"]
    
    IFMon -->|Compute Incremental Stats| IFFeat["Vector: [temp, gap, mean, std]"]
    IFFeat -->|decision_function < 0.0| IFAlarm["IF Alarm Flag"]
    
    LSTMMon -->|Window Full (len=30)| Norm["Normalize with Train Stats<br>(temp_norm, log_gap_norm)"]
    Norm -->|Predict & Last-Step MSE| MSECalc["MSE(t=29) > Threshold"]
    MSECalc --> LSTMAlarm["LSTM Alarm Flag"]
```

---

## 2. Monitor Implementations

### 2.1. `BaselineMonitor`
- **State:** Stateless during runtime. Threshold $\tau_{\text{baseline}}$ is cached at initialization from clean feature data (`out_features.csv`, `in_features.csv`).
- **Algorithm:**
  ```python
  def process_event(self, event: dict[str, Any]) -> dict[str, Any]:
      temp = float(event["temp_injected"])
      is_alarm = bool(temp > self.threshold)
      return {
          "ts": event["ts"],
          "alarm": is_alarm,
          "score": temp,
          "threshold": self.threshold,
      }
  ```
- **Thresholds:** Out = $47.6710^\circ\text{C}$; In = $31.0573^\circ\text{C}$.

### 2.2. `IFMonitor`
- **State:** Double-ended queue (`collections.deque(maxlen=10)`) buffering recent `temp_injected` values.
- **Incremental Feature Calculation:**
  ```python
  self.temp_buffer.append(temp)
  rolling_mean = float(np.mean(self.temp_buffer))
  rolling_std = float(np.std(self.temp_buffer, ddof=1)) if len(self.temp_buffer) >= 2 else np.nan
  ```
- **Inference:**
  - If `rolling_std` is NaN (first reading), alarm is `False`.
  - Otherwise, passes `[[temp, gap_seconds, rolling_mean, rolling_std]]` to `model.decision_function()`.
  - Anomaly condition: `score < 0.0`.

### 2.3. `LSTMMonitor`
- **State:** Double-ended queue (`collections.deque(maxlen=30)`) buffering recent `(temp_injected, gap_seconds)` pairs.
- **Inference Pipeline:**
  1. If `len(buffer) < 30`, returns `score = NaN` and `alarm = False` (cold-start initialization).
  2. When `len(buffer) == 30`, extracts the array and normalizes:
     
     $$T_{\text{norm}} = \frac{T - \mu_T}{\sigma_T}, \quad \ln(\text{gap})_{\text{norm}} = \frac{\ln(1 + \text{gap}) - \mu_g}{\sigma_g}$$
     
     *(Parameters loaded from `data/processed/lstm_norm_stats_*.json`)*
  3. Feeds matrix of shape `(1, 30, 2)` into the pre-loaded Keras model:
     ```python
     pred = self.model.predict(X_window, verbose=0)
     ```
  4. Calculates causal MSE at the final timestep ($t = 29$):
     
     $$\text{MSE} = \frac{1}{2} \sum_{f=1}^2 (X_{0, 29, f} - \text{pred}_{0, 29, f})^2$$
     
  5. Anomaly condition: `MSE > threshold` ($1.0131$ for Out, $0.8350$ for In).

---

## 3. Buffer Pre-Warming Protocol (D33)

When simulating localized replay windows in the dashboard or testing framework, isolated data slices create cold-start transients:
- Isolation Forest requires 10 prior readings to stabilize `rolling_mean` and `rolling_std`.
- LSTM-Autoencoder requires 30 prior readings before generating its first inference score.

**The Protocol (D33):**
Before beginning replay at $t_{\text{start}}$, the system slices up to 30 historical readings immediately preceding $t_{\text{start}}$ and passes them silently through `IFMonitor` and `LSTMMonitor` with alarm generation disabled. This pre-warms internal buffers and ensures the very first replayed frame has full mathematical parity with offline batch scores.

