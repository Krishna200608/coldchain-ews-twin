"""Generate a polished 16:9 PowerPoint presentation deck (Presentation.pptx).

Reads content and spoken cues from docs/Progress_Report/Presentation.md, incorporates
figures from docs/Progress_Report/figures/, and applies a refined academic theme.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ------------------------------------------------------------------------------
# COLOR PALETTE CONSTANTS
# ------------------------------------------------------------------------------
COLOR_NAVY = RGBColor(14, 38, 77)       # #0E264D (Primary Header)
COLOR_BLUE = RGBColor(2, 132, 199)      # #0284C7 (Accent Blue)
COLOR_DARK = RGBColor(30, 41, 59)       # #1E293B (Body Text)
COLOR_LIGHT_BG = RGBColor(240, 247, 255)# #F0F7FF (Card Fill)
COLOR_WHITE = RGBColor(255, 255, 255)   # #FFFFFF
COLOR_BORDER = RGBColor(203, 213, 225)  # #CBD5E1 (Card Border)
COLOR_HEADER_BG = RGBColor(241, 245, 249)# #F1F5F9 (Table Header Fill)
COLOR_GREEN = RGBColor(22, 163, 74)     # #16A34A (Positive Highlight)
COLOR_RED = RGBColor(220, 38, 38)       # #DC2626 (Warning/Late Highlight)
COLOR_AMBER = RGBColor(217, 119, 6)     # #D97706 (Limitation)
COLOR_TEAL = RGBColor(13, 148, 136)     # #0D9488 (Cold-chain accent)

FIG_DIR = os.path.abspath("docs/Progress_Report/figures")

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_base_slide(title_text, subtitle_text="Topic 21 — Digital Twin Early Warning System"):
        slide = prs.slides.add_slide(blank_layout)
        
        # Header banner shape
        header_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
        header_box.fill.solid()
        header_box.fill.fore_color.rgb = COLOR_NAVY
        header_box.line.color.rgb = COLOR_BLUE
        header_box.line.width = Pt(2.5)

        # Header Title
        tf = header_box.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title_text
        p1.font.name = "Calibri"
        p1.font.size = Pt(22)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_WHITE
        p1.alignment = PP_ALIGN.LEFT
        p1.space_after = Pt(2)

        # Header Subtitle
        p2 = tf.add_paragraph()
        p2.text = subtitle_text
        p2.font.name = "Calibri"
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(186, 230, 253)
        p2.alignment = PP_ALIGN.LEFT

        # Header Logo (if present)
        logo_path = os.path.join(FIG_DIR, "iiit_allahabad_logo.png")
        if os.path.exists(logo_path):
            slide.shapes.add_picture(logo_path, Inches(12.35), Inches(0.12), height=Inches(0.85))

        # Bottom footer bar
        footer = slide.shapes.add_textbox(Inches(0.8), Inches(7.15), Inches(11.733), Inches(0.3))
        ftf = footer.text_frame
        ftf.vertical_anchor = MSO_ANCHOR.MIDDLE
        fp = ftf.paragraphs[0]
        fp.text = "Managing Corporate Entrepreneurship (B.Tech 7th Sem) | Krishna Sikheriya (IIT2023139) | IIIT Allahabad"
        fp.font.name = "Calibri"
        fp.font.size = Pt(9.5)
        fp.font.color.rgb = RGBColor(148, 163, 184)
        fp.alignment = PP_ALIGN.LEFT

        return slide

    def set_speaker_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # ==========================================================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    bg = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_NAVY
    bg.line.fill.background()

    # Top accent line
    top_line = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.15))
    top_line.fill.solid()
    top_line.fill.fore_color.rgb = COLOR_BLUE
    top_line.line.fill.background()

    # IIITA Crest
    logo_path = os.path.join(FIG_DIR, "iiit_allahabad_logo.png")
    if os.path.exists(logo_path):
        slide1.shapes.add_picture(logo_path, Inches(5.8), Inches(0.8), height=Inches(1.5))

    # Title Card
    tb = slide1.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(11.333), Inches(3.2))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Digital Twin-Based Early Warning System for Cold Chain Disruption Detection"
    p.font.name = "Calibri"
    p.font.size = Pt(27)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(8)

    p_sub = tf.add_paragraph()
    p_sub.text = "Using Anomaly Detection inside a Discrete-Event Simulation Loop (Topic 21)"
    p_sub.font.name = "Calibri"
    p_sub.font.size = Pt(17)
    p_sub.font.color.rgb = RGBColor(186, 230, 253)
    p_sub.alignment = PP_ALIGN.CENTER
    p_sub.space_after = Pt(20)

    p_meta = tf.add_paragraph()
    p_meta.text = "Presenter: Krishna Sikheriya (Roll No: IIT2023139) — 7th Semester B.Tech (IT)\nCourse: Managing Corporate Entrepreneurship | Instructor: Dr. Netranand Pathak\nIndian Institute of Information Technology, Allahabad (IIITA)"
    p_meta.font.name = "Calibri"
    p_meta.font.size = Pt(13)
    p_meta.font.color.rgb = RGBColor(226, 232, 240)
    p_meta.alignment = PP_ALIGN.CENTER
    p_meta.space_after = Pt(16)

    p_links = tf.add_paragraph()
    p_links.text = "GitHub: github.com/Krishna200608/coldchain-ews-twin   |   Live Web App: coldchain-ews-twin.streamlit.app"
    p_links.font.name = "Calibri"
    p_links.font.size = Pt(11)
    p_links.font.color.rgb = RGBColor(56, 189, 248)
    p_links.alignment = PP_ALIGN.CENTER

    set_speaker_notes(slide1, (
        "Good morning, Professor and peers. Today I am presenting our project on Topic 21: "
        "A Digital Twin-Based Early Warning System for Cold Chain Disruption Detection. "
        "We set out to investigate whether embedding streaming machine learning detectors directly inside "
        "a digital twin can flag dangerous temperature breaches before irreversible spoilage occurs, "
        "rather than waiting for reactive alarms after the damage is already done."
    ))

    # ==========================================================================
    # SLIDE 2: PROBLEM STATEMENT & CORE OBJECTIVES
    # ==========================================================================
    slide2 = add_base_slide("Problem Statement, Research Gap & Core Objectives")

    # Left Card: The Problem
    card1 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4))
    card1.fill.solid()
    card1.fill.fore_color.rgb = COLOR_LIGHT_BG
    card1.line.color.rgb = COLOR_BORDER
    card1.line.width = Pt(1.2)
    tf1 = card1.text_frame
    tf1.word_wrap = True
    tf1.vertical_anchor = MSO_ANCHOR.TOP

    p = tf1.paragraphs[0]
    p.text = "The Operational Problem & Research Gap"
    p.font.name = "Calibri"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(12)

    bullets1 = [
        ("The Cold Chain Reality: ", "Vaccines, biologics, and premium perishables demand unbroken temperature control (e.g., 2°C to 8°C). A single excursion destroys cargo value."),
        ("The Traditional Failure Mode: ", "Existing logistics systems rely on static upper-bound threshold alarms that trigger only after temperature breaches a fixed limit for sustained durations (10–15 mins)."),
        ("The Post-Hoc Problem: ", "By the time a static threshold alarm sounds, cumulative thermal exposure has already caused irreversible biochemical spoilage."),
        ("The Literature Gap: ", "Prior cold-chain research focuses predominantly on post-hoc quality loss modeling. Real-time anomaly detection embedded in a digital twin for early warning is underexplored.")
    ]
    for b_title, b_desc in bullets1:
        bp = tf1.add_paragraph()
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.color.rgb = COLOR_DARK
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.color.rgb = COLOR_DARK
        bp.font.size = Pt(11.5)
        bp.space_after = Pt(10)

    # Right Card: Objectives & Research Questions
    card2 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4))
    card2.fill.solid()
    card2.fill.fore_color.rgb = COLOR_WHITE
    card2.line.color.rgb = COLOR_BLUE
    card2.line.width = Pt(1.5)
    tf2 = card2.text_frame
    tf2.word_wrap = True
    tf2.vertical_anchor = MSO_ANCHOR.TOP

    p = tf2.paragraphs[0]
    p.text = "Core Objectives & Research Questions"
    p.font.name = "Calibri"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE
    p.space_after = Pt(12)

    bullets2 = [
        ("Objective 1 (Digital Twin): ", "Build an event-driven SimPy simulation replicating the asynchronous streaming and network dropouts of real transit."),
        ("Objective 2 (Embedded Anomaly Detection): ", "Embed unsupervised Isolation Forest and deep LSTM-Autoencoder into the twin loop."),
        ("RQ1 (Early Warning Runway): ", "How many minutes of lead time (Δt_lead = t_irr - t_alarm) can machine learning provide before irreversible failure?"),
        ("RQ2 (Model Trade-off): ", "How does classical tree isolation compare against deep recurrent reconstruction on irregular edge telemetry?"),
        ("RQ3 (Simulation Fidelity): ", "Can live streaming monitors run without silent divergence or cold-start lag relative to offline batch evaluation?")
    ]
    for b_title, b_desc in bullets2:
        bp = tf2.add_paragraph()
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.color.rgb = COLOR_NAVY
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.color.rgb = COLOR_DARK
        bp.font.size = Pt(11)
        bp.space_after = Pt(8)

    set_speaker_notes(slide2, (
        "In cold-chain logistics, waiting for an alarm to cross a fixed threshold is fundamentally reactive—"
        "by the time it sounds, irreversible damage has often already occurred. Our research tackles this gap by asking: "
        "can an event-driven digital twin catch the subtle precursor symptoms, such as compressor drift or variance loss, "
        "before the failure boundary is crossed? We evaluate exactly how many minutes of early warning we can gain, "
        "compare classical vs deep learning detectors, and verify simulation fidelity."
    ))

    # ==========================================================================
    # SLIDE 3: RELEVANT LITERATURE REVIEW
    # ==========================================================================
    slide3 = add_base_slide("Relevant Literature Review (Recent Key Papers 2023–2026)")

    # Literature Table
    rows = 6
    cols = 4
    left = Inches(0.8)
    top = Inches(1.4)
    width = Inches(11.7)
    height = Inches(5.4)

    table_shape = slide3.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(2.4)
    table.columns[2].width = Inches(3.6)
    table.columns[3].width = Inches(3.5)

    headers = ["Paper Citation", "Journal / Venue", "Core Contribution", "Direct Relevance to Topic 21"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        p = cell.text_frame.paragraphs[0]
        p.font.name = "Calibri"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

    lit_data = [
        ("Vukšić et al. (2026)", "Applied Sciences\n(MDPI)", "Hybrid physics-based digital twin + autoencoder for reefer maritime containers.", "Reports median lead time of ~68 min; independently corroborates our 64-minute early warning on drift."),
        ("Xie et al. (2025)", "PLOS ONE", "Improved Isolation Forest (subsampling + feature grouping) for streaming cold-chain fleet data.", "Benchmarks tree-based streaming anomaly detection; contextualizes single-sensor point-wise metrics."),
        ("Meng et al. (2024)", "Journal of Food Engineering\n(Elsevier)", "Cost-effective box-level digital twin temperature modeling + static pallet alarms.", "Exemplifies the traditional static threshold alarm paradigm that our proactive system benchmarks against."),
        ("Wu et al. (2023)", "J. Industrial Information\nIntegration (Elsevier)", "Internet-of-Everything and Digital-Twin platform for cold-chain service logistics.", "Establishes architectural precedent for embedding AI inference into operational digital-twin pipelines."),
        ("Defraeye et al. (2023)", "Comput. Electron. Agric. /\nJ. Food Eng.", "Comprehensive review of food cold-chain digital twins and sensor dynamics.", "Identifies fundamental gap: transitioning from post-hoc quality loss to live event-driven early warning.")
    ]

    for row_idx, data in enumerate(lit_data, start=1):
        for col_idx, text in enumerate(data):
            cell = table.cell(row_idx, col_idx)
            cell.text = text
            cell.fill.solid()
            if row_idx % 2 == 1:
                cell.fill.fore_color.rgb = COLOR_LIGHT_BG
            else:
                cell.fill.fore_color.rgb = COLOR_WHITE
            p = cell.text_frame.paragraphs[0]
            p.font.name = "Calibri"
            p.font.size = Pt(10)
            if col_idx == 0:
                p.font.bold = True
                p.font.color.rgb = COLOR_NAVY
            else:
                p.font.color.rgb = COLOR_DARK

    set_speaker_notes(slide3, (
        "Our work is grounded in recent literature from top journals in food engineering and industrial systems. "
        "Crucially, Vukšić et al. in 2026 demonstrated a 68-minute lead time using deep learning on maritime reefer containers, "
        "which independently corroborates our finding of a 64-minute lead time on drift faults. "
        "Furthermore, Xie et al. in 2025 benchmarked Isolation Forest on cold-chain fleets, while Meng et al. in 2024 "
        "in the Journal of Food Engineering and Wu et al. in 2023 established the digital twin framework we build upon."
    ))

    # ==========================================================================
    # SLIDE 4: DATA STRATEGY & STRUCTURAL PROXY FRAMING
    # ==========================================================================
    slide4 = add_base_slide("Data Strategy & Structural Proxy Framing")

    # Left Column Text
    card_data = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.4))
    card_data.fill.solid()
    card_data.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_data.line.color.rgb = COLOR_BORDER
    tf = card_data.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Dataset Characteristics & Scientific Rigor"
    p.font.name = "Calibri"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(10)

    bullets_data = [
        ("Kaggle IoT Dataset: ", "97,606 raw readings across 133 continuous days (July 28 to Dec 8, 2018), 27,920 unique minute timestamps."),
        ("Realistic Sampling Dynamics: ", "High inter-arrival irregularity (Mean = 117.8 s, Median = 0.0 s, Std = 5446.3 s, CoV = 46.23). Dropouts span up to 11.57 days, accurately reflecting edge IoT transmission challenges."),
        ("Dual Sensor Streams: ", "Separated into ambient (Out, 77,260 rows) and internal enclosure proxy (In, 20,345 rows)."),
        ("Structural-Proxy Data Notice: ", "In adherence to strict academic honesty, this dataset originates from an office installation ('Room Admin'), not live pharmaceutical reefer vehicles. We frame it exclusively as an engineering structural proxy to validate asynchronous streaming pipelines and model integration without making ungrounded food-safety claims.")
    ]
    for b_title, b_desc in bullets_data:
        bp = tf.add_paragraph()
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.color.rgb = COLOR_NAVY
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.color.rgb = COLOR_DARK
        bp.font.size = Pt(11)
        bp.space_after = Pt(8)

    # Right Column: Two figures
    fig1 = os.path.join(FIG_DIR, "fig_temperature_distribution.png")
    fig2 = os.path.join(FIG_DIR, "fig_sampling_intervals_corrected.png")
    if os.path.exists(fig1):
        slide4.shapes.add_picture(fig1, Inches(6.9), Inches(1.4), width=Inches(5.6))
    if os.path.exists(fig2):
        slide4.shapes.add_picture(fig2, Inches(6.9), Inches(4.1), width=Inches(5.6))

    set_speaker_notes(slide4, (
        "We used a 97,000-reading real IoT dataset covering over 4 months. In real supply chains, sensor packets arrive "
        "irregularly due to network jitter and dropouts—our data reflects this with a high variance coefficient of 46.2. "
        "Importantly, we maintain complete academic honesty: we explicitly treat this as a structural proxy for sensor streaming, "
        "rather than fabricating claims of live pharmaceutical field testing."
    ))

    # ==========================================================================
    # SLIDE 5: SYSTEM ARCHITECTURE & DIGITAL TWIN
    # ==========================================================================
    slide5 = add_base_slide("System Architecture & SimPy Digital Twin")

    card_arch = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4))
    card_arch.fill.solid()
    card_arch.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_arch.line.color.rgb = COLOR_BORDER
    tf = card_arch.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Discrete-Event Simulation Architecture"
    p.font.name = "Calibri"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(10)

    arch_bullets = [
        ("Causal Preprocessing: ", "Corrected day-first timestamp parsing (preventing 48.8% silent parse failures). Derived trailing rolling means and stds with zero look-ahead leakage (D22)."),
        ("SimPy 3-Stage Transit: ", "Source -> Transit -> Destination event-driven virtual clock, replaying real inter-arrival gaps with zero timing discrepancy."),
        ("Embedded Streaming Monitors: ", "Destination sink embeds three parallel monitors:\n• BaselineMonitor (Static 2σ threshold)\n• IFMonitor (Isolation Forest partition score)\n• LSTMMonitor (Sliding-window reconstruction MSE)"),
        ("Silent Buffer Pre-Warming (D33): ", "Sliding window buffers are silently primed with preceding historical observations, completely eliminating cold-start false negatives during windowed replay.")
    ]
    for b_title, b_desc in arch_bullets:
        bp = tf.add_paragraph()
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.color.rgb = COLOR_NAVY
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.color.rgb = COLOR_DARK
        bp.font.size = Pt(11)
        bp.space_after = Pt(8)

    # Right Column: Visual Flowchart Blocks
    flow_steps = [
        ("1. Physical IoT Stream", "Raw telemetry (97,606 rows, IOT-temp.csv)", COLOR_WHITE, COLOR_NAVY),
        ("2. Causal Preprocessing", "dayfirst=True, Δt_k, trailing rolling features", COLOR_LIGHT_BG, COLOR_BLUE),
        ("3. SimPy Discrete-Event Twin", "3-Stage Pipeline: Source -> Transit -> Destination", RGBColor(240, 253, 250), COLOR_TEAL),
        ("4. Embedded Streaming Monitors", "Baseline (2σ) | IF Monitor | LSTM Monitor", COLOR_HEADER_BG, COLOR_NAVY),
        ("5. Silent Buffer Pre-Warming (D33)", "History pre-loaded -> 100% live/batch parity", RGBColor(254, 243, 199), COLOR_AMBER),
        ("6. Cloud Analytics & Dashboard", "Streamlit UI: Guided Tour & Free Explore", RGBColor(224, 242, 254), COLOR_BLUE)
    ]
    y_start = 1.4
    for title, desc, f_color, b_color in flow_steps:
        box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(y_start), Inches(5.7), Inches(0.75))
        box.fill.solid()
        box.fill.fore_color.rgb = f_color
        box.line.color.rgb = b_color
        box.line.width = Pt(1.5)
        btf = box.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp1 = btf.paragraphs[0]
        bp1.text = title
        bp1.font.bold = True
        bp1.font.size = Pt(12)
        bp1.font.color.rgb = b_color
        bp2 = btf.add_paragraph()
        bp2.text = desc
        bp2.font.size = Pt(10)
        bp2.font.color.rgb = COLOR_DARK
        y_start += 0.88

    set_speaker_notes(slide5, (
        "Our architecture consists of three stages: data ingestion, machine learning detectors, and an event-driven SimPy digital twin "
        "modeling Source, Transit, and Destination. When a telemetry event reaches Destination, our three monitors score it in real time. "
        "We implemented silent buffer pre-warming so the rolling buffers have history, eliminating cold-start errors."
    ))

    # ==========================================================================
    # SLIDE 6: EXPERIMENTAL SETUP & ANOMALY PROTOCOL
    # ==========================================================================
    slide6 = add_base_slide("Experimental Setup & Controlled Anomaly Protocol")

    card_exp = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4))
    card_exp.fill.solid()
    card_exp.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_exp.line.color.rgb = COLOR_BORDER
    tf = card_exp.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Controlled Perturbation Injection (Seed 42)"
    p.font.name = "Calibri"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(10)

    exp_bullets = [
        ("30 Controlled Injections: ", "Seeded across chronological timeline representing 3 canonical failure modes:\n• Step Spikes (10): Abrupt +5°C to +15°C jumps (door left open).\n• Linear Drifts (10): Gradual ramps (compressor refrigerant leak).\n• Sensor Flatlines (10): Zero variance persistence (stiction)."),
        ("Strict Chronological Split: ", "70% Train / 30% Test split at cutoff timestamp 2018-10-29 11:10:48."),
        ("Out-of-Sample Discipline: ", "24 injections fall in the train split (used only for development/previews). All formal headline claims are evaluated strictly on the 6 untouched test injections."),
        ("Lead Time Metric Definition: ", "Δt_lead = t_irreversibility - t_alarm (where t_irr is a sustained 10-minute breach). Positive = early warning; Negative = late alarm.")
    ]
    for b_title, b_desc in exp_bullets:
        bp = tf.add_paragraph()
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.color.rgb = COLOR_NAVY
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.color.rgb = COLOR_DARK
        bp.font.size = Pt(11)
        bp.space_after = Pt(8)

    # Right Column: Figure
    fig_inj = os.path.join(FIG_DIR, "fig_injection_examples.png")
    if os.path.exists(fig_inj):
        slide6.shapes.add_picture(fig_inj, Inches(6.8), Inches(1.5), width=Inches(5.7))

    set_speaker_notes(slide6, (
        "To test the system rigorously, we injected 30 controlled synthetic disruptions representing real failure modes: "
        "abrupt steps, gradual drifts, and flatlines. We enforced a strict chronological 70/30 train/test split. "
        "To ensure scientific validity, all our performance benchmarks are evaluated solely on the 6 untouched test-set injections."
    ))

    # ==========================================================================
    # SLIDE 7: CORE RESULT 1 — EARLY-WARNING LEAD TIMES
    # ==========================================================================
    slide7 = add_base_slide("Core Result 1: Early-Warning Lead Times (Test Split)")

    # Table on Left
    t_shape = slide7.shapes.add_table(7, 5, Inches(0.8), Inches(1.4), Inches(6.5), Inches(3.6))
    tbl = t_shape.table
    tbl.columns[0].width = Inches(1.6)
    tbl.columns[1].width = Inches(1.0)
    tbl.columns[2].width = Inches(1.2)
    tbl.columns[3].width = Inches(1.35)
    tbl.columns[4].width = Inches(1.35)

    headers7 = ["Injection ID", "Type", "Baseline", "IF Lead Time", "LSTM Lead Time"]
    for i, h in enumerate(headers7):
        cell = tbl.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_WHITE

    res_data = [
        ("out_step_001", "Step", "0.0 min", "0.0 min", "0.0 min"),
        ("out_drift_009", "Drift", "0.0 min", "+64.0 min (Early)", "-14.0 min (Late)"),
        ("out_flatline_012", "Flatline", "Missed", "Detected", "Detected"),
        ("out_flatline_013", "Flatline", "Missed", "Detected", "Missed"),
        ("in_step_018", "Step", "0.0 min", "0.0 min", "0.0 min"),
        ("in_drift_023", "Drift", "0.0 min", "+11.0 min (Early)", "0.0 min")
    ]
    for r_idx, row in enumerate(res_data, start=1):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            if "+64.0" in val or "+11.0" in val:
                cell.fill.fore_color.rgb = RGBColor(220, 252, 231)
            elif "-14.0" in val:
                cell.fill.fore_color.rgb = RGBColor(254, 226, 226)
            elif r_idx % 2 == 1:
                cell.fill.fore_color.rgb = COLOR_LIGHT_BG
            else:
                cell.fill.fore_color.rgb = COLOR_WHITE
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(9.5)
            if "+64.0" in val or "+11.0" in val:
                p.font.bold = True
                p.font.color.rgb = COLOR_GREEN
            elif "-14.0" in val:
                p.font.bold = True
                p.font.color.rgb = COLOR_RED
            else:
                p.font.color.rgb = COLOR_DARK

    # Bottom Callout under table
    c_box = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.2), Inches(6.5), Inches(1.6))
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = COLOR_LIGHT_BG
    c_box.line.color.rgb = COLOR_BLUE
    ctf = c_box.text_frame
    ctf.word_wrap = True
    cp = ctf.paragraphs[0]
    cp.text = "Key Scientific Observations"
    cp.font.bold = True
    cp.font.size = Pt(12)
    cp.font.color.rgb = COLOR_NAVY
    cp.space_after = Pt(4)
    c_bullets = [
        ("Decisive Drift Lead Time: ", "Isolation Forest flags subtle variance change 64 minutes (Out) and 11 minutes (In) before irreversibility."),
        ("Step Synchrony: ", "For abrupt spikes, all models trigger simultaneously at 0.0 min."),
        ("LSTM Adaptation Lag: ", "LSTM was late by 14 min on Out drift due to error adaptation.")
    ]
    for t1, t2 in c_bullets:
        bp = ctf.add_paragraph()
        r1 = bp.add_run()
        r1.text = t1
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = COLOR_DARK
        r2 = bp.add_run()
        r2.text = t2
        r2.font.size = Pt(10)
        r2.font.color.rgb = COLOR_DARK

    # Right Column: Lead Time Bar Chart
    fig_lt = os.path.join(FIG_DIR, "fig_m4b_three_way_lead_times.png")
    if os.path.exists(fig_lt):
        slide7.shapes.add_picture(fig_lt, Inches(7.5), Inches(1.4), width=Inches(5.0))

    set_speaker_notes(slide7, (
        "Here is our primary research finding: On gradual drift disruptions—which represent slow compressor failures—"
        "Isolation Forest wins decisively, providing an early warning 64 minutes ahead on Out and 11 minutes ahead on In. "
        "On abrupt step breaches, all detectors trigger concurrently at 0 minutes. And for sensor flatlines, "
        "the traditional threshold completely fails to fire, while Isolation Forest catches both."
    ))

    # ==========================================================================
    # SLIDE 8: CORE RESULT 2 — CLASSIFICATION TRADE-OFFS
    # ==========================================================================
    slide8 = add_base_slide("Core Result 2: Point-Wise Metrics & Trade-Offs")

    card_trade = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.4))
    card_trade.fill.solid()
    card_trade.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_trade.line.color.rgb = COLOR_BORDER
    tf = card_trade.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Operational Role Trade-Offs (D35 Data)"
    p.font.name = "Calibri"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(8)

    t_bullets = [
        ("Isolation Forest — High-Recall Early Tripwire:", "\n• Recall: 80.00% (Out), 91.30% (In)\n• Trade-off: High False Positive Rate (45.59% Out, 26.98% In)\n• Role: Aggressive frontline tripwire where missing a breach is fatal."),
        ("LSTM-Autoencoder — Precision-Favoring Verifier:", "\n• On In series: 13.11% Precision, 2.85% FPR, 0.3852 AUC-PR\n• Trade-off: Lower recall on Out series (20.00%, AUC-PR 0.0049)\n• Role: Conservative secondary verifier to prevent false alarm fatigue."),
        ("Extreme Prevalence Context (~0.5% Anomaly Rate):", "\n• True anomaly rows represent only 65/13,372 (0.48%) on Out and 23/3,767 (0.61%) on In.\n• Under severe class imbalance, low absolute F1 scores are mathematically inevitable, not a defect.\n• Primary Metric: Lead time runway (Δt_lead), not point-wise F1.")
    ]
    for b_title, b_desc in t_bullets:
        bp = tf.add_paragraph()
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.color.rgb = COLOR_NAVY
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.color.rgb = COLOR_DARK
        bp.font.size = Pt(10.5)
        bp.space_after = Pt(6)

    # Right Column: PR Curves
    fig_pr = os.path.join(FIG_DIR, "fig_m4b_pr_curves.png")
    if os.path.exists(fig_pr):
        slide8.shapes.add_picture(fig_pr, Inches(6.8), Inches(1.4), width=Inches(5.7))

    set_speaker_notes(slide8, (
        "When looking at point-wise metrics, we see a classic engineering trade-off: Isolation Forest acts as an aggressive tripwire "
        "with high recall over 80–90%, but at the cost of a higher false-alarm rate. In contrast, the LSTM is highly conservative "
        "on the In series with a 2.85% false-positive rate and higher precision. Neither detector universally dominates, "
        "showing why hybrid architectures are valuable."
    ))

    # ==========================================================================
    # SLIDE 9: DIGITAL TWIN PARITY & LIVE DASHBOARD
    # ==========================================================================
    slide9 = add_base_slide("Digital Twin Parity & Interactive Live Dashboard")

    card_dt = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4))
    card_dt.fill.solid()
    card_dt.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_dt.line.color.rgb = COLOR_BORDER
    tf = card_dt.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Simulation Fidelity & Live/Batch Parity"
    p.font.name = "Calibri"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(10)

    dt_bullets = [
        ("100% Bit-for-Bit Verification: ", "SimPy simulation replayed 97,603 readings in 6.03 s CPU time (>1.9M× real-time speedup) with exactly 0.00 s virtual clock drift."),
        ("Zero Discrepancy Across All Tests: ", "Across 30 injections × 3 monitors, all 42 applicable test evaluations matched batch results bit-for-bit (0 mismatches)."),
        ("Buffer Pre-Warming Proven: ", "Pre-flight checks and automated tests (test_d33_prewarm.py) pass cleanly in 15.3 s, guaranteeing reliable cold-chain simulation without state lag.")
    ]
    for b_title, b_desc in dt_bullets:
        bp = tf.add_paragraph()
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.color.rgb = COLOR_NAVY
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.color.rgb = COLOR_DARK
        bp.font.size = Pt(11)
        bp.space_after = Pt(10)

    # Right Card: Streamlit Cloud
    card_dash = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4))
    card_dash.fill.solid()
    card_dash.fill.fore_color.rgb = COLOR_WHITE
    card_dash.line.color.rgb = COLOR_BLUE
    card_dash.line.width = Pt(1.5)
    tf2 = card_dash.text_frame
    tf2.word_wrap = True

    p2 = tf2.paragraphs[0]
    p2.text = "Deployed Streamlit Cloud Application"
    p2.font.name = "Calibri"
    p2.font.size = Pt(16)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_BLUE
    p2.space_after = Pt(10)

    dash_bullets = [
        ("Public URL: ", "coldchain-ews-twin.streamlit.app"),
        ("Dual Interaction Modes: ", "\n• Guided Tour: 4-step narrated demonstration designed for viva presentations.\n• Free Explore: Interactive parameter tuning and inspection of all 30 injections."),
        ("Single Source of Truth: ", "No hardcoded numbers in presentation layer (D34). Narrative text interpolates dynamically from verified evaluation CSVs."),
        ("Zero Code Duplication: ", "Dashboard directly imports verified detection logic from src/twin_monitors.py.")
    ]
    for b_title, b_desc in dash_bullets:
        bp = tf2.add_paragraph()
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.color.rgb = COLOR_NAVY
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.color.rgb = COLOR_DARK
        bp.font.size = Pt(11)
        bp.space_after = Pt(8)

    set_speaker_notes(slide9, (
        "To prove that embedding these models in a simulation loop doesn't cause silent discrepancies, "
        "our automated cross-check report achieved a 100% exact match across all 42 applicable comparisons. "
        "Furthermore, the entire system is deployed live on Streamlit Cloud, featuring an interactive Guided Tour "
        "designed specifically for viva examination walkthroughs."
    ))

    # ==========================================================================
    # SLIDE 10: CONCLUSION & CORPORATE ENTREPRENEURSHIP RELEVANCE
    # ==========================================================================
    slide10 = add_base_slide("Conclusion & Corporate Entrepreneurship Relevance")

    card_conc = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(11.733), Inches(4.3))
    card_conc.fill.solid()
    card_conc.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_conc.line.color.rgb = COLOR_BORDER
    tf = card_conc.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Corporate Entrepreneurship & Technical Takeaways"
    p.font.name = "Calibri"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(12)

    conc_bullets = [
        ("1. Evidence-First Engineering & Risk Management: ", "Honest reporting of real trade-offs: We openly documented where deep learning lagged on drift and where classical ML excelled, avoiding the common corporate trap of fabricating artificial 99% accuracy claims."),
        ("2. Disciplined Architecture & Auditability: ", "Maintained an append-only Architectural Decision Log (35 formal entries D1–D35). This rigorous audit process caught 4 critical bugs (timestamp parse inversion, rolling leakage, cold starts) before they could compromise evaluation."),
        ("3. Technology Adoption Strategy: ", "Demonstrated that classical ML (Isolation Forest) can outperform deep neural networks for edge streaming early warning (+64 min lead time), providing high ROI at low compute overhead."),
        ("4. Complete Deliverable Portfolio: ", "100% technically complete: Scaffolding, Models, Discrete-Event Twin, Automated Tests, Full 12-Chapter Report, and Live Web Dashboard.")
    ]
    for b_title, b_desc in conc_bullets:
        bp = tf.add_paragraph()
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.color.rgb = COLOR_NAVY
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.color.rgb = COLOR_DARK
        bp.font.size = Pt(11.5)
        bp.space_after = Pt(8)

    # Bottom Banner
    banner = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.9), Inches(11.733), Inches(0.95))
    banner.fill.solid()
    banner.fill.fore_color.rgb = COLOR_NAVY
    banner.line.color.rgb = COLOR_BLUE
    banner.line.width = Pt(1.5)
    btf = banner.text_frame
    btf.vertical_anchor = MSO_ANCHOR.MIDDLE
    bp = btf.paragraphs[0]
    bp.text = "Thank you for your time! | Open for Questions & Interactive Dashboard Demonstration"
    bp.font.bold = True
    bp.font.size = Pt(14)
    bp.font.color.rgb = COLOR_WHITE
    bp.alignment = PP_ALIGN.CENTER

    set_speaker_notes(slide10, (
        "To conclude: this project bridges machine learning, discrete-event digital twins, and disciplined corporate entrepreneurship. "
        "We did not cherry-pick our data or claim artificial perfection—we demonstrated exactly where classical ML provides real "
        "operational runway, where deep learning lags, and how an organization can rigorously evaluate technology under uncertainty. "
        "Thank you, and I look forward to your questions."
    ))

    # ==========================================================================
    # SLIDE 11: REFERENCES & BENCHMARK LITERATURE
    # ==========================================================================
    slide11 = add_base_slide("References & Benchmark Literature")

    # Left Card: Recent Papers
    card_ref1 = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4))
    card_ref1.fill.solid()
    card_ref1.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_ref1.line.color.rgb = COLOR_BORDER
    tf_r1 = card_ref1.text_frame
    tf_r1.word_wrap = True

    p = tf_r1.paragraphs[0]
    p.text = "Recent Cold-Chain Benchmarks (2023–2026)"
    p.font.name = "Calibri"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(8)

    refs1 = [
        "1. Vukšić, M., Ćelić, J., Ogrizović, D., & Perić Hadžić, A. (2026). Early Anomaly Detection in Maritime Refrigerated Containers Using a Hybrid Digital Twin and Deep Learning Framework. Applied Sciences, 16(4), 1887.",
        "2. Xie, Z., Long, H., Ling, C., Zhou, Y., & Luo, Y. (2025). An Anomaly Detection Scheme for Data Stream in Cold Chain Logistics. PLOS ONE, 20(3), e0315322.",
        "3. Meng, X., Xie, R., Liao, J., Shen, X., & Yang, S. (2024). A Cost-Effective Over-Temperature Alarm System for Cold Chain Delivery. Journal of Food Engineering, 368, 111914.",
        "4. Wu, W., Shen, L., Zhao, Z., Harish, A. R., Zhong, R. Y., & Huang, G. Q. (2023). Internet of Everything and Digital Twin Enabled Service Platform for Cold Chain Logistics. Journal of Industrial Information Integration, 33, 100443.",
        "5. Defraeye, T., Shrivastava, C., Berry, T., Verboven, P., Onwude, D., Schudel, S., et al. (2023). Digital Twins of Food Cold Chains: Advances, Challenges, and Opportunities. Computers and Electronics in Agriculture, 214, 108252."
    ]
    for r in refs1:
        bp = tf_r1.add_paragraph()
        bp.text = r
        bp.font.size = Pt(9.5)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(6)

    # Right Card: Foundational Algorithms & Links
    card_ref2 = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4))
    card_ref2.fill.solid()
    card_ref2.fill.fore_color.rgb = COLOR_WHITE
    card_ref2.line.color.rgb = COLOR_BLUE
    card_ref2.line.width = Pt(1.5)
    tf_r2 = card_ref2.text_frame
    tf_r2.word_wrap = True

    p = tf_r2.paragraphs[0]
    p.text = "Foundational Algorithms & Project Assets"
    p.font.name = "Calibri"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE
    p.space_after = Pt(8)

    refs2 = [
        "6. Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation Forest. 2008 Eighth IEEE International Conference on Data Mining (ICDM), 413–422.",
        "7. Malhotra, P., Ramakrishnan, A., Anand, G., Vig, L., Agarwal, P., & Shroff, G. (2016). LSTM-based Encoder-Decoder for Multi-sensor Anomaly Detection. ICML 2016 Anomaly Detection Workshop.",
        "8. Anand Jha, A. (2018). Temperature Readings: IoT Devices Telemetry Dataset. Kaggle Datasets (Structural Proxy Dataset).",
        "\n• Live Deployed Dashboard: https://coldchain-ews-twin.streamlit.app/",
        "• Open-Source Code Repository: https://github.com/Krishna200608/coldchain-ews-twin",
        "• Institution: Department of Information Technology, IIIT Allahabad"
    ]
    for r in refs2:
        bp = tf_r2.add_paragraph()
        bp.text = r
        bp.font.size = Pt(10)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(6)

    set_speaker_notes(slide11, (
        "Finally, our research is thoroughly grounded in contemporary peer-reviewed literature across food engineering, "
        "industrial digital twins, and machine learning. Here are the core benchmark references supporting our methodology "
        "and empirical findings. Thank you, and I am now happy to take any questions."
    ))

    # Save Presentation
    output_path = os.path.abspath("docs/Progress_Report/Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path} (Size: {os.path.getsize(output_path):,} bytes)")

if __name__ == "__main__":
    create_deck()
