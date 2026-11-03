"""Generate a polished 16:9 Final Presentation PowerPoint deck (Presentation.pptx).

Reads content from docs/Report/Presentation.md, incorporates figures from
docs/Report/figures/, and applies a refined academic and corporate theme.
Saves the completed presentation to docs/Report/Presentation.pptx.
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
COLOR_NAVY = RGBColor(14, 38, 77)        # #0E264D (Primary Header & Identity)
COLOR_BLUE = RGBColor(2, 132, 199)       # #0284C7 (Accent Blue)
COLOR_DARK = RGBColor(30, 41, 59)        # #1E293B (Body Text)
COLOR_LIGHT_BG = RGBColor(240, 247, 255) # #F0F7FF (Card Fill)
COLOR_WHITE = RGBColor(255, 255, 255)    # #FFFFFF
COLOR_BORDER = RGBColor(203, 213, 225)   # #CBD5E1 (Card Border)
COLOR_HEADER_BG = RGBColor(241, 245, 249)# #F1F5F9 (Table Header Fill)
COLOR_GREEN = RGBColor(22, 163, 74)      # #16A34A (Positive / Verified Highlight)
COLOR_RED = RGBColor(220, 38, 38)        # #DC2626 (Warning / Late Highlight)
COLOR_AMBER = RGBColor(217, 119, 6)      # #D97706 (Limitation / Structural Proxy)
COLOR_TEAL = RGBColor(13, 148, 136)      # #0D9488 (Cold-Chain Accent)

FIG_DIR = os.path.abspath("docs/Report/figures")

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

    top_line = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.15))
    top_line.fill.solid()
    top_line.fill.fore_color.rgb = COLOR_BLUE
    top_line.line.fill.background()

    logo_path = os.path.join(FIG_DIR, "iiit_allahabad_logo.png")
    if os.path.exists(logo_path):
        slide1.shapes.add_picture(logo_path, Inches(5.8), Inches(0.8), height=Inches(1.5))

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
    p_sub.text = "Physics-Informed Deep Learning, Multi-Horizon Forecasting & Evidential Fusion in a Discrete-Event Simulation Loop (Topic 21)"
    p_sub.font.name = "Calibri"
    p_sub.font.size = Pt(16)
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
        "Good morning, Professor and peers. Today I am presenting our capstone project for Topic 21: "
        "A Digital Twin-Based Early Warning System for Cold Chain Disruption Detection. Our objective is "
        "to answer a crucial operational question: Can we move beyond reactive temperature alarms by "
        "embedding physics-informed deep learning, uncertainty quantification, and predictive multi-horizon "
        "forecasting directly inside an event-driven digital twin, warning operators hours before irreversible "
        "spoilage occurs?"
    ))

    # ==========================================================================
    # SLIDE 2: INDUSTRIAL CONTEXT & THE COLD CHAIN DILEMMA
    # ==========================================================================
    slide2 = add_base_slide(
        "Introduction: The Cold Chain Reality & The Reactive Flaw",
        "Topic 21: Cold Chain EWS Twin | Industrial Context & The Operational Dilemma"
    )

    card1 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.6), Inches(4.3))
    card1.fill.solid()
    card1.fill.fore_color.rgb = COLOR_LIGHT_BG
    card1.line.color.rgb = COLOR_BORDER
    tf1 = card1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "The Cold Chain Reality & High Stakes"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(12)

    bullets1 = [
        "Strict Thermal Bounds: Cold-chain cargo (vaccines, biologics, perishable foods) demands strict, unbroken temperature control (e.g., 2°C to 8°C).",
        "High Economic Impact: Over $35 billion in biopharma products and one-third of global food supplies are lost annually due to temperature excursions during transit.",
        "Public Health Risk: Temperature abuse compromises drug potency and vaccine efficacy, creating severe risks for patients and triggering massive recalls."
    ]
    for b in bullets1:
        bp = tf1.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(12)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(10)

    card2 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.4), Inches(5.7), Inches(4.3))
    card2.fill.solid()
    card2.fill.fore_color.rgb = COLOR_LIGHT_BG
    card2.line.color.rgb = COLOR_BORDER
    tf2 = card2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Traditional Failure Mode: Static Alarms"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(12)

    bullets2 = [
        "Status Quo: Commercial cold chains rely on static threshold alarms (alerting only if temperature breaches 8°C for >10–15 minutes).",
        "The Post-Hoc Flaw: Alarms only fire after the thermal boundary has already been breached.",
        "Irreversible Damage: By the time an operator or driver is notified, cumulative thermal exposure has already caused irreversible biochemical degradation."
    ]
    for b in bullets2:
        bp = tf2.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(12)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(10)

    alert_box = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(5.9), Inches(11.7), Inches(1.0))
    alert_box.fill.solid()
    alert_box.fill.fore_color.rgb = RGBColor(254, 242, 242)
    alert_box.line.color.rgb = COLOR_RED
    atf = alert_box.text_frame
    atf.word_wrap = True
    ap = atf.paragraphs[0]
    ap.text = "The Core Flaw: Waiting for an absolute threshold breach is fundamentally reactive—by the time alarms fire, product damage is already irreversible!"
    ap.font.size = Pt(13)
    ap.font.bold = True
    ap.font.color.rgb = COLOR_RED
    ap.alignment = PP_ALIGN.CENTER

    set_speaker_notes(slide2, (
        "In pharmaceutical and food cold chains, thermal stability is critical. Over 35 billion dollars of vaccines "
        "and biopharmaceuticals are discarded every year due to temperature breaches. Yet today, commercial logistics "
        "still relies on static threshold alarms that fire only after temperatures have exceeded limits for 10 or 15 minutes. "
        "By that time, cumulative heat exposure has already degraded the product. Traditional monitoring is fundamentally post-hoc and reactive."
    ))

    # ==========================================================================
    # SLIDE 3: RESEARCH GAPS & CORE OBJECTIVES
    # ==========================================================================
    slide3 = add_base_slide(
        "Research Gaps & Core Formulation",
        "Topic 21: Cold Chain EWS Twin | Research Objectives & Formal Questions"
    )

    card_gap = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.4), Inches(5.5))
    card_gap.fill.solid()
    card_gap.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_gap.line.color.rgb = COLOR_BORDER
    tg = card_gap.text_frame
    tg.word_wrap = True
    p = tg.paragraphs[0]
    p.text = "The Academic Gap & Proposed Paradigm Shift"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(10)

    gap_bullets = [
        "Prior Literature Focus: Academic studies focus predominantly on post-hoc shelf-life kinetics (calculating Arrhenius microbial or enzyme decay after the excursion has completed).",
        "The Missing Capability: Proactive, real-time early warning embedded within an event-driven digital twin that flags developing thermal failures hours before irreversible breach.",
        "Proposed Solution: Build an end-to-end discrete-event digital twin hosting physics-informed deep learning, multi-horizon quantile forecasting, and evidential fusion."
    ]
    for b in gap_bullets:
        bp = tg.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(11.5)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(10)

    rqs = [
        ("RQ1: Early Warning Runway (Lead Time)", "How many minutes of actionable early warning (Δt_lead = t_irr - t_alarm) can machine learning deliver relative to when spoilage becomes irreversible?"),
        ("RQ2: Classical vs. Deep Learning Trade-offs", "How do tree ensembles (Isolation Forest) compare against deep sequence autoencoders on irregular, real-world edge telemetry?"),
        ("RQ3: Digital Twin Simulation Fidelity", "Can an event-driven SimPy simulation loop process streaming telemetry in real time without cold-start divergence compared to offline batch evaluation?"),
        ("RQ4: Physics & Uncertainty Integration", "Can incorporating Newton cooling laws and epistemic uncertainty quantification eliminate false alarms while extending early-warning lead times?")
    ]
    y_pos = 1.4
    for title, desc in rqs:
        rq_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.5), Inches(y_pos), Inches(6.0), Inches(1.25))
        rq_box.fill.solid()
        rq_box.fill.fore_color.rgb = RGBColor(255, 255, 255)
        rq_box.line.color.rgb = COLOR_BLUE
        rtf = rq_box.text_frame
        rtf.word_wrap = True
        rp = rtf.paragraphs[0]
        rp.text = title
        rp.font.size = Pt(12)
        rp.font.bold = True
        rp.font.color.rgb = COLOR_BLUE
        rp.space_after = Pt(2)

        rp2 = rtf.add_paragraph()
        rp2.text = desc
        rp2.font.size = Pt(10)
        rp2.font.color.rgb = COLOR_DARK
        y_pos += 1.4

    set_speaker_notes(slide3, (
        "This brings us to the research gap: most academic literature focuses on post-hoc damage modeling—calculating "
        "how much product was ruined after the excursion ended. Our work shifts the paradigm to real-time proactive early warning. "
        "We formulated four concrete research questions: First, how much early warning lead time can we gain before irreversible breach? "
        "Second, what are the true trade-offs between classical tree models and deep sequence models? Third, can a digital twin run these models "
        "in live streaming without cold-start lag? And fourth, can physics-informed loss and uncertainty quantification eliminate the false alarms "
        "that plague edge deployments?"
    ))

    # ==========================================================================
    # SLIDE 4: THEORETICAL FOUNDATIONS & LITERATURE REVIEW
    # ==========================================================================
    slide4 = add_base_slide(
        "Theoretical Foundations: Literature Review (2023–2026)",
        "Grounded in Recent Peer-Reviewed Literature across Food Systems, Logistics & AI"
    )

    rows, cols = 7, 4
    table_shape = slide4.shapes.add_table(rows, cols, Inches(0.8), Inches(1.4), Inches(11.733), Inches(4.7))
    table = table_shape.table
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(2.5)
    table.columns[2].width = Inches(4.0)
    table.columns[3].width = Inches(3.033)

    headers = ["Paper Citation", "Publication Venue", "Core Contribution", "Direct Relevance to Topic 21"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

    lit_data = [
        ("Vukšić et al. (2026)", "Applied Sciences (MDPI)", "Hybrid physics-based digital twin + autoencoder for reefer maritime containers.", "Reports median lead time ~68 min; independently corroborates our empirical early warning."),
        ("Xie et al. (2025)", "PLOS ONE", "Improved Isolation Forest (subsampling + feature grouping) for cold-chain fleet streams.", "Primary tree-ensemble streaming benchmark; contextualizes point-wise F1 metrics under extreme rarity."),
        ("Meng et al. (2024)", "Journal of Food Engineering", "Box-level digital twin thermal model + static over-temperature alarms.", "Exemplifies the static threshold baseline that our proactive predictive system benchmarks against."),
        ("Wu et al. (2023)", "J. Ind. Inf. Integration", "Internet-of-Everything and Digital-Twin platform for cold-chain service logistics.", "Establishes architectural precedent for embedding AI inference into operational digital twins."),
        ("Defraeye et al. (2023)", "Comput. Electron. Agric.", "State-of-the-art review on food cold-chain digital twins and sensor dynamics.", "Identifies core research gap: shifting from reactive quality loss to live event-driven early warning."),
        ("Sensoy et al. (2018)", "NeurIPS", "Evidential Deep Learning for quantifying classification uncertainty without sampling.", "Theoretical foundation for our Dempster-Shafer multimodal evidence fusion module (P5).")
    ]
    for row_idx, data in enumerate(lit_data, start=1):
        for col_idx, text in enumerate(data):
            cell = table.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(255, 255, 255) if row_idx % 2 != 0 else COLOR_HEADER_BG
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_DARK

    takeaway = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.25), Inches(11.733), Inches(0.65))
    takeaway.fill.solid()
    takeaway.fill.fore_color.rgb = RGBColor(240, 253, 244)
    takeaway.line.color.rgb = COLOR_GREEN
    ttf = takeaway.text_frame
    tp = ttf.paragraphs[0]
    tp.text = "Key Literature Alignment: Vukšić et al. (2026) report ~68 min lead time on maritime reefers, independently corroborating our findings!"
    tp.font.size = Pt(11)
    tp.font.bold = True
    tp.font.color.rgb = COLOR_GREEN
    tp.alignment = PP_ALIGN.CENTER

    set_speaker_notes(slide4, (
        "Our architecture builds on recent peer-reviewed literature. In 2026, Vukšić and colleagues published in Applied "
        "Sciences demonstrating a 68-minute median lead time using deep learning on reefer containers, which independently corroborates "
        "our empirical results. In 2025, Xie et al. benchmarked Isolation Forest on cold-chain streams, while Meng et al. and Wu et al. "
        "established digital twin foundations. Finally, we incorporate Sensoy et al.'s evidential deep learning from NeurIPS to fuse multi-modal evidence under uncertainty."
    ))

    # ==========================================================================
    # SLIDE 5: DATA STRATEGY & STRUCTURAL PROXY FRAMING
    # ==========================================================================
    slide5 = add_base_slide(
        "Data Strategy: Empirical Telemetry & Structural Proxy",
        "Kaggle IoT Sensor Stream (97,606 Readings) with High Arrival Irregularity"
    )

    card_data = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.8), Inches(3.8))
    card_data.fill.solid()
    card_data.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_data.line.color.rgb = COLOR_BORDER
    td = card_data.text_frame
    td.word_wrap = True
    p = td.paragraphs[0]
    p.text = "Empirical Telemetry Properties & Edge Jitter"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(8)

    data_bullets = [
        "Real IoT Telemetry: 97,606 raw readings across 133 continuous days (July 28 to Dec 8, 2018), 27,920 unique minute timestamps.",
        "Extreme Arrival Irregularity: Mean arrival gap = 117.8 s, Median = 0.0 s, Std = 5,446.3 s, Coefficient of Variation CoV = 46.23. Dropouts reach up to 11.57 days, accurately reflecting edge cellular network jitter.",
        "Dual Streams: Ambient conditions (Out stream, 77,260 rows) and internal enclosure conditions (In stream, 20,345 rows)."
    ]
    for b in data_bullets:
        bp = td.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(11)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(8)

    rigor_card = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.4), Inches(5.8), Inches(1.5))
    rigor_card.fill.solid()
    rigor_card.fill.fore_color.rgb = RGBColor(255, 251, 235)
    rigor_card.line.color.rgb = COLOR_AMBER
    rtf = rigor_card.text_frame
    rtf.word_wrap = True
    rp = rtf.paragraphs[0]
    rp.text = "Academic Rigor: Structural Proxy Notice (Decision D31)"
    rp.font.size = Pt(12)
    rp.font.bold = True
    rp.font.color.rgb = COLOR_AMBER
    rp.space_after = Pt(4)
    rp2 = rtf.add_paragraph()
    rp2.text = "Originates from an office IoT deployment ('Room Admin'), not live vaccine reefers. Framed strictly as an experimental structural proxy to evaluate irregular streaming pipelines, buffer dynamics, and fault detection without fabricating unverified pharmaceutical claims."
    rp2.font.size = Pt(9.5)
    rp2.font.color.rgb = COLOR_DARK

    fig1_path = os.path.join(FIG_DIR, "fig_temperature_distribution.png")
    fig2_path = os.path.join(FIG_DIR, "fig_sampling_intervals_corrected.png")
    if os.path.exists(fig1_path):
        slide5.shapes.add_picture(fig1_path, Inches(6.9), Inches(1.4), width=Inches(5.6))
    if os.path.exists(fig2_path):
        slide5.shapes.add_picture(fig2_path, Inches(6.9), Inches(4.2), width=Inches(5.6))

    set_speaker_notes(slide5, (
        "For our empirical evaluation, we utilized a real-world IoT telemetry dataset of over 97,000 readings spanning 133 days. "
        "Real cold-chain IoT networks suffer from severe cellular jitter and packet dropouts—our telemetry reflects this with an arrival "
        "variation coefficient of 46.2 and dropouts reaching several days. In adherence to academic integrity and our Architectural Decision D31, "
        "we explicitly frame this as a structural proxy for irregular streaming mechanics, rather than fabricating claims of live clinical field deployment."
    ))

    # ==========================================================================
    # SLIDE 6: DIGITAL TWIN ARCHITECTURE & SIMPY SIMULATION
    # ==========================================================================
    slide6 = add_base_slide(
        "System Architecture: SimPy Discrete-Event Digital Twin",
        "Causal Streaming Pipeline with Embedded Anomaly Monitors & Buffer Pre-Warming"
    )

    card_arch = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.5))
    card_arch.fill.solid()
    card_arch.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_arch.line.color.rgb = COLOR_BORDER
    ta = card_arch.text_frame
    ta.word_wrap = True
    p = ta.paragraphs[0]
    p.text = "Discrete-Event Simulation Architecture"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(10)

    arch_bullets = [
        "Causal Ingestion: Day-first timestamp parsing (preventing 48.8% silent parse inversions). Trailing rolling statistics computed with strict zero look-ahead leakage (D22).",
        "SimPy 3-Stage Transit: Models physical progression across Source, Transit, and Destination driven by real historical inter-arrival gaps.",
        "Embedded Streaming Monitors: Real-time scoring at destination sink via Baseline 2-sigma, Isolation Forest, Baseline LSTM-AE, Physics-Informed LSTM, and Evidential Fusion.",
        "Silent Buffer Pre-Warming (D33): Sliding window buffers are primed with historical telemetry before visible playback begins, eliminating cold-start false alarms."
    ]
    for b in arch_bullets:
        bp = ta.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(11)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(10)

    flow_steps = [
        ("1. Physical Stream Ingestion", "97,606 raw IoT sensor events read causally from disk", COLOR_NAVY, COLOR_WHITE),
        ("2. Causal Feature Engineering", "dayfirst=True, Δt_k, trailing rolling statistics, zero leakage", COLOR_LIGHT_BG, COLOR_NAVY),
        ("3. SimPy Digital Twin Engine", "Source -> Transit -> Destination stages on virtual clock", RGBColor(240, 253, 250), COLOR_TEAL),
        ("4. Embedded Streaming Monitors", "Baseline 2σ | Isolation Forest | LSTM-AE | PILSTM | Evidential Fusion", RGBColor(248, 250, 252), COLOR_DARK),
        ("5. Live Verification & UI", "100% bit-for-bit parity, Streamlit Cloud dashboard UI", RGBColor(224, 242, 254), COLOR_BLUE)
    ]
    y_step = 1.4
    for title, desc, bg_color, text_color in flow_steps:
        box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(y_step), Inches(5.7), Inches(0.95))
        box.fill.solid()
        box.fill.fore_color.rgb = bg_color
        box.line.color.rgb = COLOR_BLUE
        btf = box.text_frame
        btf.word_wrap = True
        bp = btf.paragraphs[0]
        bp.text = title
        bp.font.size = Pt(12)
        bp.font.bold = True
        bp.font.color.rgb = text_color
        bp2 = btf.add_paragraph()
        bp2.text = desc
        bp2.font.size = Pt(9.5)
        bp2.font.color.rgb = text_color
        y_step += 1.1

    set_speaker_notes(slide6, (
        "The heart of our system is an event-driven SimPy digital twin modeling the journey of goods from Source, "
        "through Transit, to Destination. Every telemetry packet advances the simulation clock based on its true historical "
        "inter-arrival interval. At the destination sink, embedded monitors evaluate the stream in real time. We introduced silent "
        "buffer pre-warming, ensuring sliding feature windows are primed before playback starts, completely eliminating cold-start false positives."
    ))

    # ==========================================================================
    # SLIDE 7: CONTROLLED ANOMALY PROTOCOL & SPLIT DISCIPLINE
    # ==========================================================================
    slide7 = add_base_slide(
        "Controlled Anomaly Protocol & Split Discipline",
        "30 Synthetic Disruption Injections with Chronological 70/30 Train/Test Split"
    )

    card_inj = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.8), Inches(4.3))
    card_inj.fill.solid()
    card_inj.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_inj.line.color.rgb = COLOR_BORDER
    ti = card_inj.text_frame
    ti.word_wrap = True
    p = ti.paragraphs[0]
    p.text = "Controlled Perturbation Protocol (Seed 42)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(8)

    inj_bullets = [
        "30 Controlled Injections (15 Out / 15 In) representing 3 real failure modes:\n  - Step Spikes (10): Abrupt +5°C to +15°C jumps (door left open).\n  - Linear Drifts (10): Gradual ramps +0.05°C to +0.25°C/min (refrigerant leak).\n  - Sensor Flatlines (10): Zero variance persistence (frozen ADC / stiction).",
        "Strict Chronological Split: 70% Train / 30% Test split (Cutoff: Oct 29, 2018 11:10:48).",
        "Out-of-Sample Discipline: 24 injections fall on train split. All formal benchmark claims are evaluated exclusively on the 6 untouched test injections."
    ]
    for b in inj_bullets:
        bp = ti.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(11)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(8)

    formula_box = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.85), Inches(5.8), Inches(1.05))
    formula_box.fill.solid()
    formula_box.fill.fore_color.rgb = RGBColor(240, 247, 255)
    formula_box.line.color.rgb = COLOR_BLUE
    ftf = formula_box.text_frame
    ftf.word_wrap = True
    fp = ftf.paragraphs[0]
    fp.text = "Lead Time Metric: Δt_lead = t_irreversibility - t_alarm"
    fp.font.size = Pt(12)
    fp.font.bold = True
    fp.font.color.rgb = COLOR_NAVY
    fp2 = ftf.add_paragraph()
    fp2.text = "(Where t_irr is a sustained 10-minute breach. Positive = Early Warning; Negative = Late Alarm)"
    fp2.font.size = Pt(10)
    fp2.font.color.rgb = COLOR_DARK

    fig_inj = os.path.join(FIG_DIR, "fig_injection_examples.png")
    if os.path.exists(fig_inj):
        slide7.shapes.add_picture(fig_inj, Inches(6.9), Inches(1.4), width=Inches(5.6))

    set_speaker_notes(slide7, (
        "To test the system rigorously, we injected 30 controlled synthetic disruptions representing real failure modes: "
        "abrupt steps, gradual drifts, and flatlines. We enforced a strict chronological 70/30 train/test split. To ensure scientific "
        "validity, all our performance benchmarks are evaluated solely on the 6 untouched test-set injections."
    ))

    # ==========================================================================
    # SLIDE 8: BASELINE MODELS & INITIAL EMPIRICAL FINDINGS
    # ==========================================================================
    slide8 = add_base_slide(
        "Initial Findings: Lead-Time Benchmark on Test Injections",
        "Isolation Forest Decisive Drift Win (+64 min) vs. Deep Learning Adaptation Lag (-14 min)"
    )

    rows, cols = 7, 5
    t_shape = slide8.shapes.add_table(rows, cols, Inches(0.8), Inches(1.4), Inches(7.5), Inches(3.2))
    tbl = t_shape.table
    tbl.columns[0].width = Inches(1.6)
    tbl.columns[1].width = Inches(1.0)
    tbl.columns[2].width = Inches(1.4)
    tbl.columns[3].width = Inches(1.8)
    tbl.columns[4].width = Inches(1.7)

    headers = ["Injection ID", "Type", "Baseline (2σ)", "Isolation Forest", "Baseline LSTM-AE"]
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

    lead_data = [
        ("out_step_001", "Step", "0.0 min", "0.0 min", "0.0 min"),
        ("out_drift_009", "Drift", "0.0 min", "+64.0 min (Early)", "-14.0 min (Late)"),
        ("out_flatline_012", "Flatline", "Missed", "Detected", "Detected"),
        ("out_flatline_013", "Flatline", "Missed", "Detected", "Missed"),
        ("in_step_018", "Step", "0.0 min", "0.0 min", "0.0 min"),
        ("in_drift_023", "Drift", "0.0 min", "+11.0 min (Early)", "0.0 min")
    ]
    for r_idx, row in enumerate(lead_data, start=1):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(255, 255, 255) if r_idx % 2 != 0 else COLOR_HEADER_BG
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(9.5)
            if "+64.0" in val or "+11.0" in val:
                p.font.bold = True
                p.font.color.rgb = COLOR_GREEN
            elif "-14.0" in val:
                p.font.bold = True
                p.font.color.rgb = COLOR_RED
            else:
                p.font.color.rgb = COLOR_DARK

    card_takeaways = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.8), Inches(7.5), Inches(2.1))
    card_takeaways.fill.solid()
    card_takeaways.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_takeaways.line.color.rgb = COLOR_BORDER
    tt = card_takeaways.text_frame
    tt.word_wrap = True
    p = tt.paragraphs[0]
    p.text = "Summary Takeaways & Trade-offs"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(4)

    t_bullets = [
        "Decisive Drift Lead Time: Isolation Forest alarms 64 min (Out) and 11 min (In) before irreversibility, detecting anomalous variance before absolute temperatures breach baseline thresholds.",
        "Step Synchrony: For sudden jumps, all models trigger simultaneously at onset (0.0 min).",
        "Flatline Blindspot: Static thresholds fail completely; Isolation Forest catches both frozen sensor events.",
        "LSTM Adaptation Lag: LSTM was late by 14 min on Out drift due to gradual sequence reconstruction adaptation."
    ]
    for b in t_bullets:
        bp = tt.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(9.5)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(3)

    fig_lead = os.path.join(FIG_DIR, "fig_m4b_three_way_lead_times.png")
    if os.path.exists(fig_lead):
        slide8.shapes.add_picture(fig_lead, Inches(8.5), Inches(1.4), width=Inches(4.1))

    set_speaker_notes(slide8, (
        "Here are our baseline findings: On gradual compressor drift, Isolation Forest delivered 64 minutes of early warning "
        "on ambient and 11 minutes on enclosure streams. However, we discovered a major limitation in standard deep learning: the baseline "
        "LSTM-AE actually suffered a 14-minute lag on the ambient drift because its recurrent hidden state slowly adapted to the rising trend. "
        "Furthermore, Isolation Forest suffered high false positive rates of 26% to 45%. This motivated our five GPU-accelerated research breakthroughs."
    ))

    # ==========================================================================
    # SLIDE 9: RESEARCH BREAKTHROUGHS 1 & 2 (PHYSICS & UNCERTAINTY)
    # ==========================================================================
    slide9 = add_base_slide(
        "Research Breakthroughs: Uncertainty & Physics-Informed DL",
        "Proposals P1 (Variational LSTM) & P2 (Physics-Informed LSTM Newton Cooling)"
    )

    card_p1 = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.35), Inches(5.7), Inches(4.55))
    card_p1.fill.solid()
    card_p1.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_p1.line.color.rgb = COLOR_BORDER
    tf_p1 = card_p1.text_frame
    tf_p1.word_wrap = True
    p = tf_p1.paragraphs[0]
    p.text = "P1: Uncertainty & P2: Physics-Informed DL"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(6)

    p1_bullets = [
        "P1 Variational LSTM-AE (Uncertainty Quantification):\n  • Monte Carlo Dropout (N=15) decomposes total variance into aleatoric (sensor noise) vs epistemic (structural fault) uncertainty.\n  • Detected flatline out_flatline_012 +4.0 min early with 9.69% epistemic uncertainty (HIGH_CONFIDENCE_ALARM).",
        "P2 Physics-Informed LSTM-AE (Newton Cooling):\n  • Loss = MSE + λ_phys · ||dT/dt + k(T - T_amb)||^2.\n  • Enforces thermodynamic rate limits, slashing ambient false positive rate from 20.28% down to 12.52% (-38.3% relative).\n  • Converts baseline LSTM's -14.0 min lag on out_drift_009 into +18.0 min early warning (+32 min net operational gain!)."
    ]
    for b in p1_bullets:
        bp = tf_p1.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(10)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(6)

    # Embed Figure: P2 Physics-Informed Cooling & Lag Elimination
    fig_p2 = os.path.join(FIG_DIR, "fig_breakthrough_p2_physics.png")
    if os.path.exists(fig_p2):
        slide9.shapes.add_picture(fig_p2, Inches(6.8), Inches(1.35), width=Inches(5.7))

    banner_p2 = slide9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.85))
    banner_p2.fill.solid()
    banner_p2.fill.fore_color.rgb = RGBColor(240, 253, 244)
    banner_p2.line.color.rgb = COLOR_GREEN
    btf = banner_p2.text_frame
    bp = btf.paragraphs[0]
    bp.text = "Key Physics Gain: Incorporating Newton cooling converted a 14-minute deep learning lag into an 18-minute early warning (+32 min gain) and slashed false alarms by 38.3%!"
    bp.font.size = Pt(11.5)
    bp.font.bold = True
    bp.font.color.rgb = COLOR_GREEN
    bp.alignment = PP_ALIGN.CENTER

    set_speaker_notes(slide9, (
        "To address baseline shortcomings, our first breakthrough was the Variational LSTM-AE, which runs 15 Monte Carlo dropout "
        "passes to quantify epistemic uncertainty, separating genuine structural faults from random sensor noise. Our second breakthrough "
        "was the Physics-Informed LSTM-AE. By penalizing violations of Newton's Law of Cooling directly in the loss function, we slashed "
        "the ambient false positive rate from 20.28% down to 12.52%. Crucially, the physics regularizer eliminated the LSTM's adaptation lag, "
        "turning a 14-minute delay into an 18-minute early warning—a net operational gain of 32 minutes."
    ))

    # ==========================================================================
    # SLIDE 10: RESEARCH BREAKTHROUGH 3 (MULTI-HORIZON FORECASTING)
    # ==========================================================================
    slide10 = add_base_slide(
        "Research Breakthrough 3: Multi-Horizon Forecasting",
        "Proposal P3: Temporal Fusion Transformer Quantile Forecaster with +189 min Warning Runway"
    )

    card_tft = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.35), Inches(5.7), Inches(5.55))
    card_tft.fill.solid()
    card_tft.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_tft.line.color.rgb = COLOR_BORDER
    tf_tft = card_tft.text_frame
    tf_tft.word_wrap = True
    p = tf_tft.paragraphs[0]
    p.text = "Proactive Excursion Prevention via Quantile Forecasting"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(8)

    tft_bullets = [
        "Temporal Fusion Transformer (TFT): Autoregressive forecaster predicting future trajectories across 30, 60, and 120-minute horizons.",
        "Quantile Loss (Pinball Loss): Simultaneously outputs 10th, 50th (median), and 90th percentiles, establishing a conservative upper-bound thermal risk frontier.",
        "Pre-emptive Breach Alarm: Alarms trigger when the 90th percentile forecast breaches thermal bounds within the forecast window—long before the physical cargo heats up.",
        "Massive Lead-Time Gains:\n  • On in_drift_023: Achieves +189.0 minutes (+3.15 hours) of pre-emptive early warning!\n  • On out_drift_009: Achieves +56.0 minutes of pre-emptive early warning!",
        "Actionability: Gives dispatchers sufficient operational runway to reroute vehicles, service auxiliary refrigeration units, or swap towing units."
    ]
    for b in tft_bullets:
        bp = tf_tft.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(10)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(7)

    # Embed Figure: P3 Multi-Horizon Quantile Forecast Fan Chart
    fig_tft = os.path.join(FIG_DIR, "fig_breakthrough_p3_tft_forecast.png")
    if os.path.exists(fig_tft):
        slide10.shapes.add_picture(fig_tft, Inches(6.8), Inches(1.35), width=Inches(5.7))

    set_speaker_notes(slide10, (
        "Our third breakthrough was a Temporal Fusion Transformer for multi-horizon quantile forecasting. Instead of "
        "merely asking whether the current temperature reading is anomalous, the model forecasts temperature trajectories 30, 60, "
        "and 120 minutes into the future across the 10th, 50th, and 90th percentiles. When the 90th percentile indicates a future boundary "
        "breach, the system triggers a pre-emptive alert. This extended our early warning lead time to an extraordinary 189 minutes—more "
        "than three hours before product spoilage becomes irreversible."
    ))

    # ==========================================================================
    # SLIDE 11: RESEARCH BREAKTHROUGHS 4 & 5 (ADAPTIVE THRESHOLDS & EVIDENTIAL FUSION)
    # ==========================================================================
    slide11 = add_base_slide(
        "Research Breakthroughs: Adaptive Filter & Evidential Fusion",
        "Proposals P4 (Kalman CUSUM) & P5 (Dempster-Shafer Multimodal Evidence Fusion)"
    )

    card_p4 = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.35), Inches(5.7), Inches(4.55))
    card_p4.fill.solid()
    card_p4.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_p4.line.color.rgb = COLOR_BORDER
    tf_p4 = card_p4.text_frame
    tf_p4.word_wrap = True
    p = tf_p4.paragraphs[0]
    p.text = "P4: Kalman Filter & P5: Evidential Fusion"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(6)

    p4_bullets = [
        "Proposal P4: Contamination-Guarded Kalman CUSUM:\n  • 1D Kalman state estimator + two-sided CUSUM change-point detector.\n  • Freezes covariance updates when P_anomaly > 0.70 (Contamination Guard).\n  • Slashed Out stream FPR from 45.68% down to 29.45% (-35.5% relative).",
        "Proposal P5: Dempster-Shafer Evidential Fusion:\n  • Fuses Physics Residuals, Reconstruction Errors, and Uncertainty into Dirichlet belief masses.\n  • Zero False Alarm Rate: Achieved 0.00% FPR across both Out and In streams (0 false positives out of 17,051 test readings!).\n  • 100% Precision, 86.96% Recall, F1 = 0.9302, In PR-AUC = 0.9137.\n  • Retained Lead Times: +178 min (in_drift), +30 min (out_drift), +46 min (out_step)."
    ]
    for b in p4_bullets:
        bp = tf_p4.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(10)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(6)

    # Embed Figure: P5 Evidential Multimodal Fusion
    fig_p5 = os.path.join(FIG_DIR, "fig_breakthrough_p5_evidential_fusion.png")
    if os.path.exists(fig_p5):
        slide11.shapes.add_picture(fig_p5, Inches(6.8), Inches(1.35), width=Inches(5.7))

    banner_p5 = slide11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.85))
    banner_p5.fill.solid()
    banner_p5.fill.fore_color.rgb = RGBColor(240, 253, 244)
    banner_p5.line.color.rgb = COLOR_GREEN
    btf = banner_p5.text_frame
    bp = btf.paragraphs[0]
    bp.text = "The Evidential Fusion Breakthrough: 0.00% False Positive Rate, 100% Precision, F1 of 0.9302, and up to 178 minutes of early warning!"
    bp.font.size = Pt(11.5)
    bp.font.bold = True
    bp.font.color.rgb = COLOR_GREEN
    bp.alignment = PP_ALIGN.CENTER

    set_speaker_notes(slide11, (
        "Our fourth breakthrough was Kalman-CUSUM adaptive thresholding with a contamination guard, which reduced false positives "
        "by 35%. However, our crowning achievement is Proposal P5: Evidential Deep Learning Fusion. Using Dempster-Shafer theory, we fused physics "
        "residuals, temporal reconstruction errors, and epistemic uncertainty into a unified belief space. This completely eliminated false alarms—achieving "
        "a 0.00% False Positive Rate across more than 17,000 test observations, 100% Precision, an F1 score of 0.93, while preserving up to 178 minutes "
        "of actionable early warning."
    ))

    # ==========================================================================
    # SLIDE 12: MASTER BENCHMARK & COMPARATIVE PERFORMANCE MATRIX
    # ==========================================================================
    slide12 = add_base_slide(
        "Master Performance Benchmark Across All Paradigms",
        "Comprehensive Single-Source-of-Truth Metrics on the Out-of-Sample Test Split (D26)"
    )

    rows, cols = 8, 8
    t_shape = slide12.shapes.add_table(rows, cols, Inches(0.8), Inches(1.3), Inches(11.733), Inches(2.7))
    tbl = t_shape.table
    tbl.columns[0].width = Inches(2.4)
    tbl.columns[1].width = Inches(1.2)
    tbl.columns[2].width = Inches(1.2)
    tbl.columns[3].width = Inches(1.2)
    tbl.columns[4].width = Inches(1.2)
    tbl.columns[5].width = Inches(1.4)
    tbl.columns[6].width = Inches(1.5)
    tbl.columns[7].width = Inches(1.633)

    headers = ["Model Paradigm", "In FPR", "Out FPR", "Recall", "F1 Score", "In PR-AUC", "In Drift Lead", "Out Drift Lead"]
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

    master_data = [
        ("Static Threshold (2σ)", "26.98%", "45.68%", "91.30%", "0.0400", "0.0400", "0.0 min", "0.0 min"),
        ("Isolation Forest", "26.98%", "45.59%", "91.30%", "0.0400", "0.0400", "+11.0 min", "+64.0 min"),
        ("Baseline LSTM-AE", "2.85%", "20.28%", "43.48%", "0.1587", "0.3852", "0.0 min", "-14.0 min (lag)"),
        ("P1: Variational LSTM-AE", "2.80%", "19.84%", "43.48%", "0.1613", "0.3912", "0.0 min", "-14.0 min"),
        ("P2: Physics-Informed LSTM", "2.10%", "12.52%", "43.48%", "0.2041", "0.4210", "0.0 min", "+18.0 min"),
        ("P3: Multi-Horizon Forecaster", "—", "—", "—", "—", "—", "+189.0 min", "+56.0 min"),
        ("P5: Evidential Fusion (EDL)", "0.00%", "0.00%", "86.96%", "0.9302", "0.9137", "+178.0 min", "+30.0 min")
    ]
    for r_idx, row in enumerate(master_data, start=1):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.fill.solid()
            if r_idx == 7:  # Highlight EDL Fusion
                cell.fill.fore_color.rgb = RGBColor(240, 253, 244)
            else:
                cell.fill.fore_color.rgb = RGBColor(255, 255, 255) if r_idx % 2 != 0 else COLOR_HEADER_BG
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(9.0)
            if r_idx == 7:
                p.font.bold = True
                p.font.color.rgb = COLOR_GREEN
            elif "+189.0" in val or "+64.0" in val or "+18.0" in val:
                p.font.bold = True
                p.font.color.rgb = COLOR_BLUE
            elif "-14.0" in val:
                p.font.bold = True
                p.font.color.rgb = COLOR_RED
            else:
                p.font.color.rgb = COLOR_DARK

    # Embed Visual Plots side by side below table
    fig_lead_all = os.path.join(FIG_DIR, "fig_breakthrough_leadtimes.png")
    fig_pareto = os.path.join(FIG_DIR, "fig_breakthrough_master_tradeoff.png")
    if os.path.exists(fig_lead_all):
        slide12.shapes.add_picture(fig_lead_all, Inches(0.8), Inches(4.15), width=Inches(5.7))
    if os.path.exists(fig_pareto):
        slide12.shapes.add_picture(fig_pareto, Inches(6.8), Inches(4.15), width=Inches(5.7))

    set_speaker_notes(slide12, (
        "Here is our comprehensive master benchmark matrix. Moving from static thresholding to Evidential Deep Learning "
        "fusion drives our F1 score from 0.04 up to 0.9302 and PR-AUC from 0.3852 to 0.9137, while completely eliminating false positives "
        "on the test set. At the same time, our multi-horizon forecasting delivers over three hours of early warning. Every metric on this slide "
        "is backed by reproducible automated tests and JSON artifacts."
    ))

    # ==========================================================================
    # SLIDE 13: INTERACTIVE DASHBOARD & DIGITAL TWIN DEMONSTRATION
    # ==========================================================================
    slide13 = add_base_slide(
        "Interactive Dashboard & Digital Twin Deployment",
        "Streamlit Cloud Live App with Guided Tour, Free Explore & 100% Simulation Parity"
    )

    card_dash = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.5))
    card_dash.fill.solid()
    card_dash.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_dash.line.color.rgb = COLOR_BORDER
    td = card_dash.text_frame
    td.word_wrap = True
    p = td.paragraphs[0]
    p.text = "Streamlit Cloud Live Deployment"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(10)

    dash_bullets = [
        "Production Deployment: Deployed on Streamlit Community Cloud at coldchain-ews-twin.streamlit.app with full GPU research showcase.",
        "Dynamic Visualizations: Interactive Plotly time-series charts rendering temperature trajectories, 2σ boundaries, anomaly score overlays, and playhead markers.",
        "Research Showcase Tab: Dedicated interactive exploration of Physics Residuals, Epistemic Uncertainty bands, Multi-Horizon Quantile forecasts, and Evidential Belief masses."
    ]
    for b in dash_bullets:
        bp = td.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(11)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(10)

    card_modes = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.4), Inches(5.7), Inches(2.8))
    card_modes.fill.solid()
    card_modes.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_modes.line.color.rgb = COLOR_BORDER
    tm = card_modes.text_frame
    tm.word_wrap = True
    p = tm.paragraphs[0]
    p.text = "Dual User Experience Modes"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(6)

    mode_bullets = [
        "Guided Tour Mode: Curated 4-step walkthrough for non-technical executives and evaluators, highlighting baseline failure, Isolation Forest early warning, LSTM precision, and Evidential zero-FPR fusion.",
        "Free Explore Mode: Full parameter control allowing operators to select any of 30 synthetic injections, adjust replay speed (1× to 10,000×), and inspect raw telemetry."
    ]
    for b in mode_bullets:
        bp = tm.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(10)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(6)

    card_parity = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(4.4), Inches(5.7), Inches(2.5))
    card_parity.fill.solid()
    card_parity.fill.fore_color.rgb = RGBColor(240, 253, 244)
    card_parity.line.color.rgb = COLOR_GREEN
    tp = card_parity.text_frame
    tp.word_wrap = True
    p = tp.paragraphs[0]
    p.text = "100% Bit-for-Bit Digital Twin Parity (Decision D33)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN
    p.space_after = Pt(6)

    parity_bullets = [
        "High-Speed Replay: SimPy twin replayed 97,603 readings in 6.03 s CPU (>1.9M× speedup) with 0.00 s virtual clock drift.",
        "Zero Mismatches: Across 30 injections × 3 monitors, all 42 applicable test evaluations matched batch results bit-for-bit (0 mismatches)."
    ]
    for b in parity_bullets:
        bp = tp.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(10)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(6)

    set_speaker_notes(slide13, (
        "We translated our research into an operational interactive dashboard deployed live on Streamlit Cloud. It features "
        "two user modes: a Guided Tour for non-technical stakeholders and a Free Explore mode for operations engineers. Our SimPy digital "
        "twin replays over 97,000 events in just six seconds—a 1.9-million-times speedup—with zero clock drift and a 100% bit-for-bit parity match against batch evaluations."
    ))

    # ==========================================================================
    # SLIDE 14: CORPORATE ENTREPRENEURSHIP & CONCLUSION
    # ==========================================================================
    slide14 = add_base_slide(
        "Conclusion & Corporate Entrepreneurship Relevance",
        "Evidence-First Governance, Technology Adoption Strategy & Defense Summary"
    )

    ce_pillars = [
        ("1. Evidence-First Risk Management", "Honest reporting of real trade-offs: We documented where deep learning lagged on drift and where classical ML excelled, avoiding the common corporate trap of fabricating artificial 99% accuracy claims without validation."),
        ("2. Architectural Decision Governance (D1–D40)", "Maintained an append-only Architectural Decision Log across 40 formal decisions. This governance framework caught 4 critical bugs (timestamp parse inversion, rolling leakage, cold starts) before they could bias evaluation."),
        ("3. Tiered Technology Adoption Strategy", "Demonstrated that a multi-tiered architecture provides optimal ROI: lightweight classical ML / Kalman filters for cheap edge gateways, backed by physics-informed and evidential models for central cloud dispatchers."),
        ("4. 100% Technical Completion", "Comprehensive deliverable portfolio: Scaffolding, Models, Digital Twin, 26 Automated Tests, 12-Chapter IEEE Report, and Live Deployed Cloud Dashboard.")
    ]
    coords = [
        (Inches(0.8), Inches(1.4)),
        (Inches(6.8), Inches(1.4)),
        (Inches(0.8), Inches(3.9)),
        (Inches(6.8), Inches(3.9))
    ]
    for (title, desc), (x, y) in zip(ce_pillars, coords):
        card = slide14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.7), Inches(2.2))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_LIGHT_BG
        card.line.color.rgb = COLOR_BORDER
        ctf = card.text_frame
        ctf.word_wrap = True
        cp = ctf.paragraphs[0]
        cp.text = title
        cp.font.size = Pt(13)
        cp.font.bold = True
        cp.font.color.rgb = COLOR_NAVY
        cp.space_after = Pt(4)
        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.size = Pt(10)
        cp2.font.color.rgb = COLOR_DARK

    banner_final = slide14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.25), Inches(11.733), Inches(0.75))
    banner_final.fill.solid()
    banner_final.fill.fore_color.rgb = COLOR_NAVY
    banner_final.line.color.rgb = COLOR_BLUE
    btf = banner_final.text_frame
    bp = btf.paragraphs[0]
    bp.text = "Thank You for Your Time! | Open for Questions & Live Demonstration\nLive Deployed Dashboard: coldchain-ews-twin.streamlit.app"
    bp.font.size = Pt(12)
    bp.font.bold = True
    bp.font.color.rgb = COLOR_WHITE
    bp.alignment = PP_ALIGN.CENTER

    set_speaker_notes(slide14, (
        "To conclude: this project embodies the core principles of Corporate Entrepreneurship. We tackled an unsolved "
        "industrial challenge, governed development through 40 audited architectural decisions, reported genuine empirical trade-offs with "
        "complete scientific integrity, and demonstrated a multi-tiered AI architecture delivering zero false alarms and hours of operational runway. "
        "Thank you, Professor and peers. I am now open to your questions and ready for the live demonstration."
    ))

    # ==========================================================================
    # SLIDE 15: REFERENCES & SCIENTIFIC BIBLIOGRAPHY
    # ==========================================================================
    slide15 = add_base_slide(
        "References: Benchmark Literature & Project Assets",
        "Full Peer-Reviewed Academic Bibliography & Public Repository Assets"
    )

    card_r1 = slide15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.5))
    card_r1.fill.solid()
    card_r1.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_r1.line.color.rgb = COLOR_BORDER
    tf_r1 = card_r1.text_frame
    tf_r1.word_wrap = True
    p = tf_r1.paragraphs[0]
    p.text = "Cold-Chain & Digital Twin Benchmarks"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(8)

    refs1 = [
        "1. Vukšić, M., et al. (2026). Early Anomaly Detection in Maritime Refrigerated Containers Using a Hybrid Digital Twin and Deep Learning Framework. Applied Sciences, 16(4), 1887.",
        "2. Xie, Z., et al. (2025). An Anomaly Detection Scheme for Data Stream in Cold Chain Logistics. PLOS ONE, 20(3), e0315322.",
        "3. Meng, X., et al. (2024). A Cost-Effective Over-Temperature Alarm System for Cold Chain Delivery. Journal of Food Engineering, 368, 111914.",
        "4. Wu, W., et al. (2023). Internet of Everything and Digital Twin Enabled Service Platform for Cold Chain Logistics. J. Industrial Information Integration, 33, 100443.",
        "5. Defraeye, T., et al. (2023). Digital Twins of Food Cold Chains: Advances, Challenges, and Opportunities. Computers and Electronics in Agriculture, 214, 108252."
    ]
    for r in refs1:
        bp = tf_r1.add_paragraph()
        bp.text = r
        bp.font.size = Pt(9.5)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(6)

    card_r2 = slide15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.5))
    card_r2.fill.solid()
    card_r2.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_r2.line.color.rgb = COLOR_BORDER
    tf_r2 = card_r2.text_frame
    tf_r2.word_wrap = True
    p = tf_r2.paragraphs[0]
    p.text = "AI Foundations & Project Assets"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(8)

    refs2 = [
        "6. Sensoy, M., Kaplan, L., & Kandemir, M. (2018). Evidential Deep Learning to Quantify Classification Uncertainty. NeurIPS 2018, 31, 3179–3189.",
        "7. Raissi, M., Perdikaris, P., & Karniadakis, G. E. (2019). Physics-Informed Neural Networks. Journal of Computational Physics, 378, 686–707.",
        "8. Lim, B., et al. (2021). Temporal Fusion Transformers for Interpretable Multi-Horizon Time Series Forecasting. Int. J. Forecasting, 37(4), 1748–1764.",
        "9. Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation Forest. IEEE ICDM, 413–422.",
        "10. Anand Jha, A. (2018). Temperature Readings: IoT Devices Telemetry Dataset. Kaggle Datasets.\n",
        "• Live Web Application: https://coldchain-ews-twin.streamlit.app/",
        "• Open-Source Code: https://github.com/Krishna200608/coldchain-ews-twin",
        "• Institution: Department of Information Technology, IIIT Allahabad"
    ]
    for r in refs2:
        bp = tf_r2.add_paragraph()
        bp.text = r
        bp.font.size = Pt(9.5)
        bp.font.color.rgb = COLOR_DARK
        bp.space_after = Pt(6)

    set_speaker_notes(slide15, (
        "Finally, here is the complete bibliography of peer-reviewed literature across food cold chains, digital twins, "
        "physics-informed neural networks, and evidential deep learning that grounds our methodology and empirical conclusions. Thank you."
    ))

    # Save Presentation to docs/Report/Presentation.pptx and docs/Progress_Report/Presentation.pptx
    out1 = os.path.abspath("docs/Report/Presentation.pptx")
    prs.save(out1)
    print(f"Presentation saved to: {out1} (Size: {os.path.getsize(out1):,} bytes)")

    out2 = os.path.abspath("docs/Progress_Report/Presentation.pptx")
    prs.save(out2)
    print(f"Presentation saved to: {out2} (Size: {os.path.getsize(out2):,} bytes)")

if __name__ == "__main__":
    create_deck()

