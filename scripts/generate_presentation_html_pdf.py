"""Generate an interactive HTML slide deck and compile to a 16:9 Presentation.pdf.

Builds docs/Progress_Report/Presentation.html with keyboard navigation and speaker cues,
then renders it to docs/Progress_Report/Presentation.pdf via headless Chrome.
"""

import os
import subprocess

HTML_PATH = os.path.abspath("docs/Progress_Report/Presentation.html")
PDF_PATH = os.path.abspath("docs/Progress_Report/Presentation.pdf")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def build_deck():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Topic 21 Presentation — Digital Twin Cold Chain Early Warning System</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fira+Code:wght@400;600&display=swap');

  @page {
    size: 16in 9in;
    margin: 0;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #0b132b;
    color: #1e293b;
    overflow-x: hidden;
  }

  .slide {
    width: 16in;
    height: 9in;
    page-break-after: always;
    position: relative;
    background: #ffffff;
    display: flex;
    flex-direction: column;
    padding: 0.5in 0.8in;
    overflow: hidden;
  }

  /* Slide 1 Dark Theme */
  .slide-title-bg {
    background: linear-gradient(135deg, #07152f 0%, #0e264d 60%, #1e3a8a 100%);
    color: #ffffff;
    justify-content: center;
    align-items: center;
    text-align: center;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 2.5px solid #0284c7;
    padding-bottom: 12px;
    margin-bottom: 20px;
  }

  .header h1 {
    font-size: 26pt;
    font-weight: 800;
    color: #0e264d;
    line-height: 1.15;
  }

  .header p {
    font-size: 12pt;
    font-weight: 500;
    color: #0284c7;
    margin-top: 4px;
  }

  .header-logo {
    height: 60px;
  }

  .content-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    flex: 1;
    align-items: stretch;
  }

  .card {
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 22px 26px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  }

  .card-blue {
    background: #f0f7ff;
    border-color: #bae6fd;
  }

  .card-white {
    background: #ffffff;
    border: 2px solid #0284c7;
  }

  .card h2 {
    font-size: 16pt;
    font-weight: 700;
    color: #0e264d;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .card h2.accent {
    color: #0284c7;
  }

  ul.bullet-list {
    list-style: none;
    font-size: 12pt;
    line-height: 1.55;
    color: #334155;
  }

  ul.bullet-list li {
    margin-bottom: 12px;
    position: relative;
    padding-left: 20px;
  }

  ul.bullet-list li::before {
    content: "•";
    color: #0284c7;
    font-weight: bold;
    font-size: 16pt;
    position: absolute;
    left: 0;
    top: -2px;
  }

  ul.bullet-list strong {
    color: #0e264d;
  }

  .img-container {
    display: flex;
    flex-direction: column;
    gap: 14px;
    justify-content: center;
    align-items: center;
  }

  .img-container img {
    max-width: 100%;
    max-height: 5.6in;
    border-radius: 8px;
    border: 1px solid #cbd5e1;
    box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    object-fit: contain;
  }

  .img-half {
    max-height: 2.7in !important;
  }

  table.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11pt;
    margin-top: 6px;
  }

  table.styled-table th, table.styled-table td {
    border: 1px solid #cbd5e1;
    padding: 10px 12px;
    text-align: left;
    vertical-align: top;
  }

  table.styled-table th {
    background: #0e264d;
    color: #ffffff;
    font-weight: 600;
    font-size: 11pt;
  }

  table.styled-table tr:nth-child(even) td {
    background: #f8fafc;
  }

  .highlight-green {
    color: #16a34a;
    font-weight: 700;
    background-color: #dcfce7 !important;
  }

  .highlight-red {
    color: #dc2626;
    font-weight: 700;
    background-color: #fee2e2 !important;
  }

  .footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 9.5pt;
    color: #94a3b8;
    border-top: 1px solid #f1f5f9;
    padding-top: 8px;
    margin-top: auto;
  }

  .badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 9pt;
    font-weight: 600;
    background: #e0f2fe;
    color: #0369a1;
  }

  .cue-box {
    margin-top: 14px;
    background: #f1f5f9;
    border-left: 4px solid #0284c7;
    padding: 8px 14px;
    font-size: 10pt;
    color: #475569;
    font-style: italic;
    border-radius: 4px;
  }

  /* Presentation Mode Controls */
  #controls {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 9999;
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(8px);
    padding: 8px 16px;
    border-radius: 30px;
    display: flex;
    gap: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  }

  #controls button {
    background: #0284c7;
    color: white;
    border: none;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 10pt;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  #controls button:hover {
    background: #0369a1;
  }

  @media print {
    #controls {
      display: none !important;
    }
  }
</style>
</head>
<body>

<!-- SLIDE 1: TITLE SLIDE -->
<div class="slide slide-title-bg" id="slide-1">
  <img src="figures/iiit_allahabad_logo.png" style="height: 110px; margin-bottom: 24px;" alt="IIITA Crest">
  <h1 style="font-size: 34pt; font-weight: 800; max-width: 12.5in; line-height: 1.2; margin-bottom: 14px; color: #ffffff;">
    Digital Twin-Based Early Warning System for Cold Chain Disruption Detection
  </h1>
  <p style="font-size: 19pt; color: #bae6fd; font-weight: 500; margin-bottom: 32px;">
    Embedding Anomaly Detection Inside a Discrete-Event Simulation Loop (Topic 21)
  </p>
  <div style="font-size: 14pt; color: #e2e8f0; line-height: 1.6; margin-bottom: 26px;">
    <strong>Presenter:</strong> Krishna Sikheriya (Roll No: <strong>IIT2023139</strong>) — 7th Semester B.Tech (IT)<br>
    <strong>Course:</strong> Managing Corporate Entrepreneurship &nbsp;|&nbsp; <strong>Instructor:</strong> Dr. Netranand Pathak<br>
    <strong>Institution:</strong> Indian Institute of Information Technology, Allahabad (IIITA)
  </div>
  <div style="display: flex; gap: 16px; justify-content: center; font-size: 11pt; color: #38bdf8;">
    <span class="badge" style="background: rgba(2, 132, 199, 0.25); color: #bae6fd; font-size: 11pt; padding: 6px 16px;">Verified SimPy Twin</span>
    <span class="badge" style="background: rgba(2, 132, 199, 0.25); color: #bae6fd; font-size: 11pt; padding: 6px 16px;">Live Streamlit Cloud</span>
    <span class="badge" style="background: rgba(2, 132, 199, 0.25); color: #bae6fd; font-size: 11pt; padding: 6px 16px;">Open-Source GitHub</span>
  </div>
</div>

<!-- SLIDE 2: PROBLEM & OBJECTIVES -->
<div class="slide" id="slide-2">
  <div class="header">
    <div>
      <h1>Problem Statement, Research Gap & Core Objectives</h1>
      <p>Topic 21 — Managing Corporate Entrepreneurship</p>
    </div>
    <img src="figures/iiit_allahabad_logo.png" class="header-logo" alt="Logo">
  </div>
  <div class="content-grid">
    <div class="card card-blue">
      <h2>The Operational Challenge & Research Gap</h2>
      <ul class="bullet-list">
        <li><strong>Strict Thermal Range:</strong> Cold-chain cargo (vaccines, biologics, food) demands strict 2°C to 8°C adherence. A single excursion destroys batch viability.</li>
        <li><strong>The Traditional Status Quo:</strong> Commercial monitoring relies on <strong>static threshold alarms</strong> alerting only after temperatures exceed fixed limits for sustained periods (10–15 mins).</li>
        <li><strong>The Post-Hoc Problem:</strong> By the time a static threshold alarm sounds, cumulative heat exposure has already caused <strong>irreversible spoilage</strong>.</li>
        <li><strong>The Academic Gap:</strong> Prior research focuses on post-hoc shelf-life calculation. Proactive streaming anomaly detection inside a digital twin is underexplored.</li>
      </ul>
    </div>
    <div class="card card-white">
      <h2 class="accent">Core Objectives & Research Questions</h2>
      <ul class="bullet-list">
        <li><strong>Objective 1 (Digital Twin):</strong> Build an asynchronous discrete-event simulation (SimPy) modeling real multi-stage transit and network dropouts.</li>
        <li><strong>Objective 2 (Embedded Detectors):</strong> Embed Isolation Forest and deep LSTM-Autoencoder into the live streaming twin loop.</li>
        <li><strong>RQ1 (Lead Time Runway):</strong> How many minutes of early warning (&Delta;t<sub>lead</sub> = t<sub>irr</sub> - t<sub>alarm</sub>) can machine learning deliver before irreversible failure?</li>
        <li><strong>RQ2 (Model Comparison):</strong> How does classical tree isolation compare against sequential deep learning on irregular edge telemetry?</li>
        <li><strong>RQ3 (Simulation Fidelity):</strong> Can live streaming monitors achieve exact bit-for-bit parity with offline batch evaluations?</li>
      </ul>
    </div>
  </div>
  <div class="cue-box">
    <strong>Presenter Cue:</strong> "In cold-chain logistics, waiting for an alarm to cross a fixed threshold is fundamentally reactive—by the time it sounds, irreversible damage has occurred. Our digital twin catches subtle precursor symptoms before the failure boundary is crossed."
  </div>
  <div class="footer">
    <span>Slide 2 of 10</span>
    <span>Krishna Sikheriya (IIT2023139) | IIIT Allahabad</span>
  </div>
</div>

<!-- SLIDE 3: LITERATURE REVIEW -->
<div class="slide" id="slide-3">
  <div class="header">
    <div>
      <h1>Relevant Literature Review (Recent Benchmark Papers)</h1>
      <p>Peer-Reviewed Grounding Across Cold-Chain Digital Twins & Anomaly Detection (2023–2026)</p>
    </div>
    <img src="figures/iiit_allahabad_logo.png" class="header-logo" alt="Logo">
  </div>
  <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
    <table class="styled-table">
      <thead>
        <tr>
          <th style="width: 18%;">Paper Citation</th>
          <th style="width: 20%;">Publication Venue</th>
          <th style="width: 32%;">Core Contribution</th>
          <th style="width: 30%;">Direct Relevance to Topic 21</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Vukšić et al. (2026)</strong></td>
          <td><em>Applied Sciences</em><br>(MDPI)</td>
          <td>Hybrid physics-based digital twin + autoencoder for reefer maritime containers.</td>
          <td>Reports median lead time of <strong>~68 min</strong>; independently corroborates our empirical <strong>64 min</strong> drift early warning.</td>
        </tr>
        <tr>
          <td><strong>Xie et al. (2025)</strong></td>
          <td><em>PLOS ONE</em></td>
          <td>Improved Isolation Forest (subsampling + grouping) on cold-chain fleet streams.</td>
          <td>Primary benchmark for tree-based streaming anomaly detection; contextualizes single-sensor point-wise metrics.</td>
        </tr>
        <tr>
          <td><strong>Meng et al. (2024)</strong></td>
          <td><em>Journal of Food Engineering</em><br>(Elsevier)</td>
          <td>Box-level digital twin temperature model + static over-temperature alarms.</td>
          <td>Exemplifies the static threshold alarm baseline that our proactive anomaly-detection system benchmarks against.</td>
        </tr>
        <tr>
          <td><strong>Wu et al. (2023)</strong></td>
          <td><em>J. Industrial Information Integration</em> (Elsevier)</td>
          <td>IoE and Digital-Twin platform for cold-chain service logistics.</td>
          <td>Establishes architectural precedent for embedding AI inference into operational digital-twin pipelines.</td>
        </tr>
        <tr>
          <td><strong>Defraeye et al. (2023)</strong></td>
          <td><em>Comput. Electron. Agric.</em> /<br><em>J. Food Eng.</em></td>
          <td>Comprehensive review of food cold-chain digital twins and sensor dynamics.</td>
          <td>Identifies fundamental research gap: shifting from reactive quality loss to live event-driven early warning.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="cue-box">
    <strong>Presenter Cue:</strong> "Our research builds upon recent high-impact literature. Vukšić et al. in 2026 demonstrated a 68-minute lead time on reefer containers, which directly corroborates our finding of a 64-minute lead time on drift faults."
  </div>
  <div class="footer">
    <span>Slide 3 of 10</span>
    <span>Krishna Sikheriya (IIT2023139) | IIIT Allahabad</span>
  </div>
</div>

<!-- SLIDE 4: DATA STRATEGY -->
<div class="slide" id="slide-4">
  <div class="header">
    <div>
      <h1>Data Strategy & Structural Proxy Framing</h1>
      <p>Telemetry Dynamics, Irregular Sampling & Academic Integrity</p>
    </div>
    <img src="figures/iiit_allahabad_logo.png" class="header-logo" alt="Logo">
  </div>
  <div class="content-grid">
    <div class="card card-blue">
      <h2>Empirical Telemetry Properties</h2>
      <ul class="bullet-list">
        <li><strong>Dataset Source:</strong> Kaggle <code>IOT-temp.csv</code> (97,606 raw readings across 133 continuous days, July 28 to Dec 8, 2018).</li>
        <li><strong>Realistic Edge Irregularity:</strong> Mean arrival gap &Delta;t = 117.8 s, Median = 0.0 s, Std = 5446.3 s, Coefficient of Variation <strong>CoV = 46.23</strong>. Telemetry dropouts span up to 11.57 days.</li>
        <li><strong>Dual Streams:</strong> Ambient (<code>Out</code>, 77,260 rows) vs Container Enclosure proxy (<code>In</code>, 20,345 rows).</li>
      </ul>
      <div style="background: #fffbeb; border: 1.5px solid #fef3c7; border-left: 4px solid #d97706; padding: 12px; border-radius: 6px; margin-top: auto;">
        <strong style="color: #92400e; font-size: 11pt;">Scientific Honesty Notice:</strong>
        <p style="font-size: 10pt; color: #78350f; margin-top: 4px;">
          Originates from a generic IoT office installation (<code>Room Admin</code>). Framed strictly as an experimental <strong>structural proxy</strong> to evaluate irregular streaming pipelines and buffer mechanics without fabricating clinical claims.
        </p>
      </div>
    </div>
    <div class="img-container">
      <img src="figures/fig_temperature_distribution.png" class="img-half" alt="Temperature Distribution">
      <img src="figures/fig_sampling_intervals_corrected.png" class="img-half" alt="Sampling Interval Distribution">
    </div>
  </div>
  <div class="cue-box">
    <strong>Presenter Cue:</strong> "We used a 97,000-reading real IoT dataset. Real telemetry arrives irregularly due to network jitter, reflected in a high variance coefficient of 46.2. Importantly, we maintain complete academic honesty by framing this as a structural proxy."
  </div>
  <div class="footer">
    <span>Slide 4 of 10</span>
    <span>Krishna Sikheriya (IIT2023139) | IIIT Allahabad</span>
  </div>
</div>

<!-- SLIDE 5: SYSTEM ARCHITECTURE -->
<div class="slide" id="slide-5">
  <div class="header">
    <div>
      <h1>System Architecture & The Digital Twin</h1>
      <p>Discrete-Event Simulation Loop, Streaming Inference & Buffer Pre-Warming</p>
    </div>
    <img src="figures/iiit_allahabad_logo.png" class="header-logo" alt="Logo">
  </div>
  <div class="content-grid">
    <div class="card card-blue">
      <h2>Discrete-Event Simulation Architecture</h2>
      <ul class="bullet-list">
        <li><strong>Causal Preprocessing:</strong> Day-first timestamp parsing (preventing 48.8% silent parse failures). Derived trailing rolling statistics with zero look-ahead leakage (D22).</li>
        <li><strong>SimPy 3-Stage Pipeline:</strong> Models physical progression: <code>Source</code> &rarr; <code>Transit</code> &rarr; <code>Destination</code> driven by real inter-arrival gaps.</li>
        <li><strong>Embedded Streaming Monitors:</strong>
          <br>&bull; <code>BaselineMonitor</code>: Static 2&sigma; threshold ($47.7^\circ\text{C}$ Out, $34.9^\circ\text{C}$ In).
          <br>&bull; <code>IFMonitor</code>: Classical Isolation Forest ensemble.
          <br>&bull; <code>LSTMMonitor</code>: Deep sequence reconstruction MSE.
        </li>
        <li><strong>Silent Buffer Pre-Warming (D33):</strong> Priming sliding buffers before visible replay completely eliminates cold-start false negatives.</li>
      </ul>
    </div>
    <div class="card card-white" style="justify-content: space-around;">
      <h2 class="accent">Pipeline Process Flow</h2>
      <div style="display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #0e264d; color: white; padding: 10px 14px; border-radius: 8px; font-size: 11pt; font-weight: 600;">1. Raw Physical Stream (97,606 IoT readings)</div>
        <div style="text-align: center; color: #0284c7; font-size: 14pt;">&darr;</div>
        <div style="background: #f0f7ff; border: 1.5px solid #0284c7; color: #0e264d; padding: 10px 14px; border-radius: 8px; font-size: 11pt; font-weight: 600;">2. Causal Preprocessing & Chronological Train/Test Split</div>
        <div style="text-align: center; color: #0284c7; font-size: 14pt;">&darr;</div>
        <div style="background: #f0fdfa; border: 1.5px solid #0d9488; color: #0f766e; padding: 10px 14px; border-radius: 8px; font-size: 11pt; font-weight: 600;">3. SimPy Discrete-Event Digital Twin (Source &rarr; Transit &rarr; Dest)</div>
        <div style="text-align: center; color: #0284c7; font-size: 14pt;">&darr;</div>
        <div style="background: #f8fafc; border: 1.5px solid #cbd5e1; color: #1e293b; padding: 10px 14px; border-radius: 8px; font-size: 11pt; font-weight: 600;">4. Destination Sink: Baseline | Isolation Forest | LSTM-Autoencoder</div>
        <div style="text-align: center; color: #0284c7; font-size: 14pt;">&darr;</div>
        <div style="background: #e0f2fe; border: 1.5px solid #0284c7; color: #0369a1; padding: 10px 14px; border-radius: 8px; font-size: 11pt; font-weight: 600;">5. Live Verification Engine & Streamlit Cloud Dashboard</div>
      </div>
    </div>
  </div>
  <div class="cue-box">
    <strong>Presenter Cue:</strong> "Our digital twin replays events across Source, Transit, and Destination. When a reading reaches Destination, three parallel monitors score it. We implemented silent buffer pre-warming to eliminate cold-start false alarms."
  </div>
  <div class="footer">
    <span>Slide 5 of 10</span>
    <span>Krishna Sikheriya (IIT2023139) | IIIT Allahabad</span>
  </div>
</div>

<!-- SLIDE 6: EXPERIMENTAL SETUP -->
<div class="slide" id="slide-6">
  <div class="header">
    <div>
      <h1>Experimental Setup & Controlled Anomaly Protocol</h1>
      <p>Synthetic Perturbations, Failure Modes & Split Discipline</p>
    </div>
    <img src="figures/iiit_allahabad_logo.png" class="header-logo" alt="Logo">
  </div>
  <div class="content-grid">
    <div class="card card-blue">
      <h2>Controlled Perturbation Protocol (Seed 42)</h2>
      <ul class="bullet-list">
        <li><strong>30 Controlled Injections (15 Out / 15 In):</strong>
          <br>&bull; <em>Step Spikes (10):</em> +5°C to +15°C sudden jumps (door left open).
          <br>&bull; <em>Linear Drifts (10):</em> +0.05°C to +0.25°C/min ramps (refrigerant leak).
          <br>&bull; <em>Sensor Flatlines (10):</em> Zero variance stiction (frozen sensor).
        </li>
        <li><strong>Strict Chronological Split:</strong> 70% Train / 30% Test split at timestamp <code>2018-10-29 11:10:48</code>.</li>
        <li><strong>Out-of-Sample Evaluation:</strong> 24 injections fall in the train split (used only for development/previews). All headline claims are evaluated strictly on the <strong>6 untouched test injections</strong>.</li>
        <li><strong>Lead Time Metric:</strong> &Delta;t<sub>lead</sub> = t<sub>irreversibility</sub> - t<sub>alarm</sub> (where t<sub>irr</sub> is a sustained 10-minute upper threshold breach).</li>
      </ul>
    </div>
    <div class="img-container">
      <img src="figures/fig_injection_examples.png" alt="Injection Profiles">
    </div>
  </div>
  <div class="cue-box">
    <strong>Presenter Cue:</strong> "To test the system rigorously, we injected 30 controlled synthetic disruptions representing real failure modes: abrupt steps, gradual drifts, and flatlines. All our performance benchmarks are evaluated solely on the 6 untouched test-set injections."
  </div>
  <div class="footer">
    <span>Slide 6 of 10</span>
    <span>Krishna Sikheriya (IIT2023139) | IIIT Allahabad</span>
  </div>
</div>

<!-- SLIDE 7: RESULTS 1 - LEAD TIMES -->
<div class="slide" id="slide-7">
  <div class="header">
    <div>
      <h1>Core Result 1: Early-Warning Lead Times (Test Split)</h1>
      <p>Quantifying Operational Decision Runway (&Delta;t<sub>lead</sub> = t<sub>irr</sub> - t<sub>alarm</sub>)</p>
    </div>
    <img src="figures/iiit_allahabad_logo.png" class="header-logo" alt="Logo">
  </div>
  <div class="content-grid">
    <div style="display: flex; flex-direction: column; gap: 14px;">
      <table class="styled-table">
        <thead>
          <tr>
            <th>Injection ID</th>
            <th>Type</th>
            <th>Baseline</th>
            <th>IF Lead Time</th>
            <th>LSTM Lead Time</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>out_step_001</code></td>
            <td>Step</td>
            <td>0.0 min</td>
            <td>0.0 min</td>
            <td>0.0 min</td>
          </tr>
          <tr>
            <td><code>out_drift_009</code></td>
            <td>Drift</td>
            <td>0.0 min</td>
            <td class="highlight-green">+64.0 min (Early)</td>
            <td class="highlight-red">-14.0 min (Late)</td>
          </tr>
          <tr>
            <td><code>out_flatline_012</code></td>
            <td>Flatline</td>
            <td>Missed</td>
            <td class="highlight-green">Detected</td>
            <td class="highlight-green">Detected</td>
          </tr>
          <tr>
            <td><code>out_flatline_013</code></td>
            <td>Flatline</td>
            <td>Missed</td>
            <td class="highlight-green">Detected</td>
            <td class="highlight-red">Missed</td>
          </tr>
          <tr>
            <td><code>in_step_018</code></td>
            <td>Step</td>
            <td>0.0 min</td>
            <td>0.0 min</td>
            <td>0.0 min</td>
          </tr>
          <tr>
            <td><code>in_drift_023</code></td>
            <td>Drift</td>
            <td>0.0 min</td>
            <td class="highlight-green">+11.0 min (Early)</td>
            <td>0.0 min</td>
          </tr>
        </tbody>
      </table>
      <div class="card card-blue" style="padding: 14px 18px; margin-top: auto;">
        <strong style="color: #0e264d; font-size: 11pt;">Key Scientific Findings:</strong>
        <p style="font-size: 10pt; color: #334155; margin-top: 4px;">
          &bull; <strong>Drift Success:</strong> Isolation Forest delivers massive early warning (<strong>+64 min Out</strong>, <strong>+11 min In</strong>).<br>
          &bull; <strong>Step Synchrony:</strong> For abrupt jumps, all models alarm concurrently (0.0 min runway).<br>
          &bull; <strong>LSTM Lag:</strong> LSTM was late by 14 min on Out drift due to gradual sequence reconstruction adaptation.
        </p>
      </div>
    </div>
    <div class="img-container">
      <img src="figures/fig_m4b_three_way_lead_times.png" alt="Three-Way Lead Times">
    </div>
  </div>
  <div class="cue-box">
    <strong>Presenter Cue:</strong> "On gradual drift disruptions—which represent slow compressor failures—Isolation Forest wins decisively, providing an early warning 64 minutes ahead on Out and 11 minutes ahead on In. On sudden step breaches, all detectors fire concurrently at 0 minutes."
  </div>
  <div class="footer">
    <span>Slide 7 of 10</span>
    <span>Krishna Sikheriya (IIT2023139) | IIIT Allahabad</span>
  </div>
</div>

<!-- SLIDE 8: RESULTS 2 - TRADE-OFFS -->
<div class="slide" id="slide-8">
  <div class="header">
    <div>
      <h1>Core Result 2: Point-Wise Metrics & Trade-Offs</h1>
      <p>Point-Wise Classification Dynamics & Operational Roles (D35 Single Source of Truth)</p>
    </div>
    <img src="figures/iiit_allahabad_logo.png" class="header-logo" alt="Logo">
  </div>
  <div class="content-grid">
    <div class="card card-blue">
      <h2>Operational Model Roles</h2>
      <ul class="bullet-list">
        <li><strong>Isolation Forest — High-Recall Early Tripwire:</strong>
          <br>&bull; Recall: <strong>80.00%</strong> (Out), <strong>91.30%</strong> (In).
          <br>&bull; Trade-off: High False Positive Rate (45.59% Out, 26.98% In).
          <br>&bull; Role: Aggressive frontline tripwire where missing a breach is fatal.
        </li>
        <li><strong>LSTM-Autoencoder — Precision-Favoring Verifier:</strong>
          <br>&bull; On In series: <strong>13.11% Precision</strong>, <strong>2.85% FPR</strong>, 0.3852 AUC-PR.
          <br>&bull; Trade-off: Lower recall on Out series (20.00%, AUC-PR 0.0049).
          <br>&bull; Role: Conservative secondary verifier preventing operator alarm fatigue.
        </li>
        <li><strong>Extreme Rarity Context (~0.5% Anomaly Prevalence):</strong>
          <br>&bull; True anomalies represent only ~0.5% of rows. Under severe class imbalance, low absolute F1 is mathematically inevitable.
          <br>&bull; Operational Focus: Early warning runway (&Delta;t<sub>lead</sub>), not point-wise F1.
        </li>
      </ul>
    </div>
    <div class="img-container">
      <img src="figures/fig_m4b_pr_curves.png" alt="PR Curves">
    </div>
  </div>
  <div class="cue-box">
    <strong>Presenter Cue:</strong> "We see a classic engineering trade-off: Isolation Forest acts as an aggressive tripwire with recall over 80–90%, but higher false alarms. The LSTM is highly conservative on the In series with a 2.85% false-positive rate. Neither universally dominates."
  </div>
  <div class="footer">
    <span>Slide 8 of 10</span>
    <span>Krishna Sikheriya (IIT2023139) | IIIT Allahabad</span>
  </div>
</div>

<!-- SLIDE 9: DIGITAL TWIN PARITY & LIVE DASHBOARD -->
<div class="slide" id="slide-9">
  <div class="header">
    <div>
      <h1>Digital Twin Parity & Interactive Live Dashboard</h1>
      <p>Verification Audit & Deployed Public Streamlit Cloud Web Application</p>
    </div>
    <img src="figures/iiit_allahabad_logo.png" class="header-logo" alt="Logo">
  </div>
  <div class="content-grid">
    <div class="card card-blue">
      <h2>100% Bit-for-Bit Live/Batch Parity</h2>
      <ul class="bullet-list">
        <li><strong>High-Speed Discrete-Event Replay:</strong> SimPy digital twin replayed 97,603 readings in <strong>6.03 seconds</strong> of CPU execution (>1.9M&times; speedup) with exactly <strong>0.00 s</strong> virtual clock drift.</li>
        <li><strong>Zero Discrepancy Across All Tests:</strong> Across 30 injections &times; 3 monitors, all 42 applicable test evaluations matched offline batch results bit-for-bit (<strong>0 mismatches</strong>).</li>
        <li><strong>Automated Test Suite:</strong> Pre-flight verification (<code>test_d33_prewarm.py</code>) passes cleanly in 15.3 s.</li>
      </ul>
    </div>
    <div class="card card-white">
      <h2 class="accent">Deployed Streamlit Cloud UI</h2>
      <ul class="bullet-list">
        <li><strong>Public URL:</strong> <a href="https://coldchain-ews-twin.streamlit.app/" target="_blank" style="color: #0284c7; font-weight: 600;">coldchain-ews-twin.streamlit.app</a></li>
        <li><strong>Guided Tour Mode:</strong> 4-step sequence curated specifically for viva presentations.</li>
        <li><strong>Free Explore Mode:</strong> Interactive parameter inspection across all 30 injections with clear train/test tagging.</li>
        <li><strong>Single Source of Truth (D34):</strong> Narrative text dynamically interpolates metrics from verified CSVs; zero hardcoded UI numbers.</li>
        <li><strong>Zero Code Duplication:</strong> Directly imports verified monitors from <code>src/twin_monitors.py</code>.</li>
      </ul>
    </div>
  </div>
  <div class="cue-box">
    <strong>Presenter Cue:</strong> "Our automated cross-check report achieved a 100% exact match across all 42 comparisons. The entire system is deployed live on Streamlit Cloud, featuring an interactive Guided Tour designed specifically for viva examination walkthroughs."
  </div>
  <div class="footer">
    <span>Slide 9 of 10</span>
    <span>Krishna Sikheriya (IIT2023139) | IIIT Allahabad</span>
  </div>
</div>

<!-- SLIDE 10: CONCLUSION -->
<div class="slide" id="slide-10">
  <div class="header">
    <div>
      <h1>Conclusion & Corporate Entrepreneurship Relevance</h1>
      <p>Key Strategic Takeaways & Defense Readiness (Topic 21)</p>
    </div>
    <img src="figures/iiit_allahabad_logo.png" class="header-logo" alt="Logo">
  </div>
  <div class="card card-blue" style="flex: 1; justify-content: space-around;">
    <h2>Key Technical & Corporate Entrepreneurship Takeaways</h2>
    <ul class="bullet-list" style="font-size: 13pt; line-height: 1.6;">
      <li><strong>1. Evidence-First Engineering & Risk Management:</strong> Honest reporting of real trade-offs: We openly documented where deep learning lagged on drift and where classical ML excelled, avoiding superficial 99% accuracy claims.</li>
      <li><strong>2. Disciplined Architecture & Auditability:</strong> Maintained an append-only Architectural Decision Log (35 formal entries D1–D35), catching 4 critical bugs before they could compromise evaluation.</li>
      <li><strong>3. Technology Adoption Strategy:</strong> Proved that classical ML (Isolation Forest) can outperform deep neural networks for edge streaming early warning (+64 min lead time), providing high ROI at low compute overhead.</li>
      <li><strong>4. Complete Deliverable Portfolio:</strong> 100% complete and verified pipeline: Scaffolding, Models, Discrete-Event Twin, Automated Tests, Full 12-Chapter Report, and Live Web Dashboard.</li>
    </ul>
    <div style="background: #0e264d; color: white; padding: 14px 20px; border-radius: 8px; text-align: center; font-size: 14pt; font-weight: 700; border: 1.5px solid #0284c7;">
      Thank you for your time! | Open for Questions & Interactive Dashboard Demonstration
    </div>
  </div>
  <div class="cue-box">
    <strong>Presenter Cue:</strong> "To conclude: this project bridges machine learning, discrete-event digital twins, and disciplined corporate entrepreneurship. We demonstrated where classical ML provides real runway, where deep learning lags, and how to evaluate technology under uncertainty. Thank you!"
  </div>
  <div class="footer">
    <span>Slide 10 of 10</span>
    <span>Krishna Sikheriya (IIT2023139) | IIIT Allahabad</span>
  </div>
</div>

<!-- Presentation Controls for Browser -->
<div id="controls">
  <button onclick="prevSlide()">&larr; Prev</button>
  <button onclick="nextSlide()">Next &rarr;</button>
  <button onclick="toggleCues()">Toggle Cues</button>
</div>

<script>
  let currentSlide = 1;
  const totalSlides = 10;

  function showSlide(num) {
    if (num < 1) num = 1;
    if (num > totalSlides) num = totalSlides;
    currentSlide = num;
    const elem = document.getElementById('slide-' + currentSlide);
    if (elem) {
      elem.scrollIntoView({ behavior: 'smooth' });
    }
  }

  function nextSlide() { showSlide(currentSlide + 1); }
  function prevSlide() { showSlide(currentSlide - 1); }

  function toggleCues() {
    const cues = document.querySelectorAll('.cue-box');
    cues.forEach(c => {
      c.style.display = (c.style.display === 'none') ? 'block' : 'none';
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
      nextSlide();
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      prevSlide();
    } else if (e.key === 'c' || e.key === 'C') {
      toggleCues();
    }
  });
</script>

</body>
</html>
"""

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated HTML slide deck: {HTML_PATH} ({os.path.getsize(HTML_PATH):,} bytes)")

    # Render to PDF using Chrome Headless
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_PATH}",
        HTML_PATH
    ]
    subprocess.run(cmd, check=True)
    print(f"Compiled Presentation PDF: {PDF_PATH} ({os.path.getsize(PDF_PATH):,} bytes)")

if __name__ == "__main__":
    build_deck()
