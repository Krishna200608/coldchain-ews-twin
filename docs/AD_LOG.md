# Architecture Decision Log — Cold Chain EWS Digital Twin

All significant design/data decisions for this project are recorded here in
reverse-chronological order. Each entry states *what* was decided and *why*.

---

## 2026-09-17 — Dataset selection

**Decision:** `atulanandjha/temperature-readings-iot-devices` (Kaggle) is used
as the structural proxy for cold-chain telemetry throughout Milestone 1.

**Rationale:** This dataset was selected at the project synopsis stage
(*not* a new decision made during implementation). It is a generic IoT
temperature sensor log, not real refrigerated-transport data. It was chosen
solely because it exhibits the structural properties — irregular sampling
intervals and an in/out room sensor tag — that allow the ingestion pipeline
and anomaly-detection scaffolding to be developed before real cold-chain data
is available.

**Limitation:** Any statistics derived from this dataset (sampling intervals,
temperature distributions, row counts) describe the proxy dataset, *not*
operational cold-chain telemetry. All downstream modules must carry this
caveat explicitly.

---
