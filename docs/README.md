# Cold Chain EWS Digital Twin — Documentation Hub

**Course:** Managing Corporate Entrepreneurship (B.Tech 7th Semester, 2026)  
**Institution:** Indian Institute of Information Technology, Allahabad (IIITA)  
**Supervisor / Instructor:** Dr. Netranand Pathak  
**Topic 21:** Digital Twin-Based Early Warning System for Cold Chain Disruption Detection Using Anomaly Detection  
**Author:** Krishna Sikheriya (Roll No: IIT2023139)  
**Repository:** [https://github.com/Krishna200608/coldchain-ews-twin](https://github.com/Krishna200608/coldchain-ews-twin)  
**Live Deployed Dashboard:** [https://coldchain-ews-twin.streamlit.app/](https://coldchain-ews-twin.streamlit.app/)  

---

## Directory Organization & Deliverables Map

The `docs/` folder contains all academic publications, slide decks, architectural logs, dataset submissions, and technical documentation generated for Topic 21.

```
docs/
├── README.md                       # This navigation index and documentation guide
├── AD_LOG.md                       # Architectural Decision Log (formal entries D1 through D35)
├── understand.md                   # Comprehensive plain-English project walkthrough (less jargon)
├── data_profile.md                 # Quantitative EDA findings on 97,606 raw IoT sensor readings
├── Project.md                      # Official Topic 21 prompt & problem brief from course supervisor
│
├── Progress_Report/                # Progress Report, Overleaf LaTeX package & Presentation deck
│   ├── Presentation.pptx           # PowerPoint 16:9 widescreen presentation with figures & speaker notes
│   ├── Presentation.pdf            # Compiled 16:9 widescreen presentation PDF ready for projection
│   ├── Presentation.html           # Interactive browser presentation deck with keyboard navigation & cues
│   ├── presentation.tex            # Overleaf-compilable LaTeX Beamer deck with TikZ vector diagrams
│   ├── Presentation_Overleaf.zip   # 1-Click ready-to-upload archive for Overleaf Beamer slides (2.11 MB)
│   ├── Presentation.md             # 10-slide presentation deck with spoken presenter cues
│   ├── Progress_Report.pdf         # Compiled publication-ready progress report document (310 KB)
│   ├── Progress_Report.md          # Markdown progress report with lead-time tables & literature review
│   ├── main.tex                    # Overleaf-compilable LaTeX source with custom TikZ flowcharts
│   ├── references.bib              # BibTeX literature citations (recent papers 2023–2026)
│   ├── Progress_Report_Overleaf.zip# 1-Click ready-to-upload archive for Overleaf report (2.11 MB)
│   └── figures/                    # High-res report figures, TikZ assets & IIITA emblem
│
├── Report/                         # Comprehensive Academic Final Report
│   ├── Krishna_Sikheriya_ColdChain_Report.pdf  # Compiled 12-chapter IEEE/Springer report (2.2 MB)
│   ├── Krishna_Sikheriya_ColdChain_Report.tex  # Complete LaTeX manuscript source code
│   ├── references.bib              # Full bibliography
│   └── figures/                    # Vector plots, PR curves, and IIITA branding
│
├── Dataset_Submission/             # Official assignment dataset submission
│   ├── IOT-temp.csv                # Raw sensor telemetry (97,606 rows; structural proxy)
│   └── README.md                   # Submission metadata, schema definition & integrity notices
│
├── Synopsis/                       # Initial Research Proposal
│   └── Krishna_Sikheriya_Topic21_Synopsis.docx # Research synopsis submitted at project launch
│
└── figures/                        # Central visual repository for EDA & evaluation plots
    ├── fig_injection_examples.png              # Synthetic fault profiles (step, drift, flatline)
    ├── fig_inout_diff_match_rate.png           # Timestamp alignment cross-check plot
    ├── fig_inout_distribution.png              # Ambient vs enclosure temperature density
    ├── fig_m4b_pr_curves.png                   # Precision-Recall curves (IF vs LSTM)
    ├── fig_m4b_reconstruction_error_drift.png  # LSTM temporal reconstruction lag on drift
    ├── fig_m4b_three_way_lead_times.png        # Comparative early-warning lead-time bar chart
    ├── fig_readings_per_room_id_id.png         # Room Admin invariant verification
    ├── fig_representative_stretch.png          # High-resolution time-series snippet
    ├── fig_sampling_intervals.png              # Raw inter-arrival gap histogram
    ├── fig_sampling_intervals_corrected.png    # Corrected day-first arrival gap distribution
    ├── fig_temp_by_tag.png                     # Box plots of temperature by device tag
    └── fig_temperature_distribution.png        # Overall empirical temperature distribution
```

---

## Deliverables Summary

### 1. Progress Report & Defense Deck ([`docs/Progress_Report/`](Progress_Report/))
- **PowerPoint Presentation:** [`Presentation.pptx`](Progress_Report/Presentation.pptx) — Professional 16:9 widescreen presentation with embedded figures, styled tables, and native PowerPoint speaker notes matching spoken cues verbatim.
- **Compiled Slide PDF:** [`Presentation.pdf`](Progress_Report/Presentation.pdf) — Ready-to-project 16:9 widescreen presentation PDF (3.41 MB).
- **Interactive Browser Deck:** [`Presentation.html`](Progress_Report/Presentation.html) — Standalone presentation with keyboard controls (Arrow Keys, Space) and presenter cue toggle ('C').
- **Overleaf Beamer Source:** [`presentation.tex`](Progress_Report/presentation.tex) — Complete LaTeX Beamer deck with custom IIITA theme and TikZ vector flowcharts.
- **1-Click Beamer Overleaf Zip:** [`Presentation_Overleaf.zip`](Progress_Report/Presentation_Overleaf.zip) — Ready to import into Overleaf for instant Beamer compilation.
- **Slide Script & Spoken Cues:** [`Presentation.md`](Progress_Report/Presentation.md) — 10-slide outline with slide content and spoken cues.
- **Progress Report PDF:** [`Progress_Report.pdf`](Progress_Report/Progress_Report.pdf) — Publication-grade technical progress report document (310 KB).
- **Progress Report Overleaf Source:** [`main.tex`](Progress_Report/main.tex) & [`references.bib`](Progress_Report/references.bib) — Formal LaTeX progress report with TikZ flowcharts.
- **1-Click Report Overleaf Zip:** [`Progress_Report_Overleaf.zip`](Progress_Report/Progress_Report_Overleaf.zip) — Ready to upload directly to Overleaf for instant report compilation.

### 2. Final Academic Report ([`docs/Report/`](Report/))
- **Compiled PDF:** [`Krishna_Sikheriya_ColdChain_Report.pdf`](Report/Krishna_Sikheriya_ColdChain_Report.pdf) — Comprehensive 12-chapter monograph detailing the theoretical foundations of cold-chain thermodynamics, tree partition algorithms, recurrent autoencoders, discrete-event SimPy simulation, and empirical single-source-of-truth evaluations.

### 3. Core Project Guides & Architectural Audit
- **Plain-English Guide:** [`understand.md`](understand.md) — Simple, accessible explanation of the entire project without heavy jargon.
- **Architectural Decision Log:** [`AD_LOG.md`](AD_LOG.md) — Immutable audit trail of 35 formal engineering decisions (D1–D35) tracking bug fixes, pipeline refactors, and design choices.
- **Data Profiling:** [`data_profile.md`](data_profile.md) — Rigorous statistical analysis of the Kaggle IoT temperature dataset, documenting the high variance ($\text{CoV} = 46.23$) and structural proxy rationale.
- **Supervisor Topic Brief:** [`Project.md`](Project.md) — Original course topic specifications assigned by Dr. Netranand Pathak.

### 4. Dataset Archive ([`docs/Dataset_Submission/`](Dataset_Submission/))
- Contains the physical IoT telemetry dataset (`IOT-temp.csv`, 6.63 MB) paired with a formal dataset `README.md` defining schema columns, timestamp parsing protocols, and structural-proxy integrity notices.

### 5. Visual Figures Repository ([`docs/figures/`](figures/))
- Stores all high-resolution charts generated across EDA and milestone evaluation scripts, referenced throughout the main `README.md` and project publications.
