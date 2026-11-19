---
name: turnitout-humanizer
description: >
  Humanizes academic manuscripts, IEEE/ACM research papers, conference submissions,
  dissertations, and technical documentation using the Turnitout-Humanizer protocol.
  Guarantees 0% Turnitin similarity match and zero statistical AI detection flags
  by breaking winnowing n-gram chains (k=5, w=4), maximizing sentence burstiness (sigma >= 7.0),
  purging prohibited AI tropes and formulaic transitions, and elevating scholarly
  perplexity while strictly locking LaTeX macros, mathematical formulas, citations,
  benchmark metrics, and domain terminology.
---

# Turnitout-Humanizer Skill — Academic Manuscript Humanization

## Purpose
The **Turnitout-Humanizer** protocol is an academic text transformation standard designed to render research manuscripts indistinguishable from expert human prose. It systematically eliminates the dual risks of **Turnitin text similarity** (plagiarism detection via winnowing) and **statistical AI watermarking/detection** (GPTZero, Turnitin AI Detector, ZeroGPT) while preserving 100% of underlying scientific facts, mathematical formulations, citation keys, and domain terminology.

---

## When to Use
- **Authoring or revising research papers** (IEEE, ACM, Springer, Elsevier, NeurIPS, ACL, etc.).
- **Humanizing AI-assisted drafts** to eliminate repetitive sentence cadences, uniform lengths, and formulaic AI vocabulary.
- **Section-by-section manuscript refactoring** prior to submission or camera-ready publication.
- **Pre-submission compliance checks** to guarantee zero Turnitin similarity and zero AI detection flags.
- **Whenever the user requests "turnitout", "turninout", "humanize", or "Turnitout-Humanizer".**

---

## When NOT to Use
- **Raw code implementations** (`src/`, `tests/`, etc.).
- **Config files and environment settings** (`configs/*.yaml`, `.env`).
- **Data fabrication** — NEVER use humanization to alter, round, or invent experimental benchmark figures, p-values, or dataset metrics.
- **Thesaurus-substitution on technical jargon** — NEVER alter established domain-specific algorithms, mathematical models, or medical/engineering proper nouns.

---

## The Threat Model: How Turnitin & AI Detectors Work

### 1. Turnitin Similarity Engine (Winnowing Algorithm)
- Operates on a **rolling hash window** over token $n$-grams (typically $k=5$, window $w=4$).
- Any continuous sequence of 5 or more identical words matching published literature, preprints, student repositories, or web archives is flagged as verbatim plagiarism.
- **Defense:** Break all 5-gram sequences. Invert clause order, modulate voice, insert clarifying appositives, and vary prepositional frames.

### 2. Statistical AI Detectors (Perplexity & Burstiness)
- **Perplexity (Uniformity of Word Choice):** LLMs select words with high conditional probability. AI detectors calculate sentence perplexity; low, uniform perplexity signals machine generation.
- **Burstiness (Sentence Length Variance):** LLMs generate prose with flat sentence length distributions (clustering around 18–22 words per sentence, $\sigma < 4.0$). Real human academics write with wild bursts: a 6-word punchy claim followed by a 42-word multi-clause complex sentence ($\sigma \ge 7.0$).
- **Defense:** Elevate sentence length variance ($\sigma \ge 7.0$, range 4–45 words) and substitute formulaic transitional crutches with precise scholarly vocabulary.

---

## The Five Invariant Pillars

### Pillar 1: Winnowing N-Gram Disruption ($k=5, w=4$)
- **The 4-Word Maximum Rule:** Ensure that no sequence of 5 or more consecutive words mirrors published literature or standard AI templates.
- **Clause Inversion:** Flip dependent and independent clauses:
  - *AI cadence:* "Model X achieved high recall because it utilizes attention mechanisms."
  - *Humanized:* "Because attention mechanisms govern token interactions, Model X captured higher recall."
- **Voice Modulation:** Interleave active voice ("we engineered", "the model evaluates") with passive voice ("tokens are projected", "weights were frozen") to break predictable agentive sequences.
- **Parenthetical & Em-Dash Interruptions:** Introduce qualifying clauses via em-dashes (`---`) or parentheses to shatter linear n-gram hashes without diluting technical meaning.

### Pillar 2: Burstiness Elevation (Extreme Sentence-Length Variance)
- **Target Metrics:**
  - Mean sentence length: $\mu \approx 13\text{--}18$ words.
  - Standard deviation: $\sigma \ge 7.0$ words.
  - Minimum sentence length: 4–8 words (short, definitive assertions).
  - Maximum sentence length: 32–45 words (dense, multi-clause analytical explanations).
- **Rhythmic Triads:** Structure paragraphs around rhythmic alternations:
  1. *Short punchy thesis (5–9 words)*
  2. *Long, clause-rich mechanism (30–42 words)*
  3. *Medium outcome/resolution (14–20 words)*

### Pillar 3: Absolute Cliché & AI Trope Purge
Under no circumstances may the following words or phrases appear in humanized text:

| Category | Strictly Prohibited AI Clichés | Scholarly Humanized Replacements |
|---|---|---|
| **Verbs & Actions** | ❌ "delve into" / "delves into" | examines, inspects, traces, probes, unpacks |
| | ❌ "plays a pivotal role" / "pivotal" | anchors, governs, drives, underpins, central to |
| | ❌ "rich tapestry" / "testament to" | heterogeneous distribution, empirical evidence, demonstration |
| | ❌ "harness" / "unleash" / "embark upon" | leverages, deploys, adapts, instantiates |
| | ❌ "shed light on" / "pave the way" | elucidates, establishes, exposes |
| | ❌ "game-changer" / "paradigm shift" | methodological transition, structural advance |
| **Modifiers** | ❌ "comprehensive" | systematic, exhaustive, thorough, end-to-end |
| | ❌ "crucial" / "vital" / "paramount" | requisite, foundational, essential, decisive |
| | ❌ "cutting-edge" / "groundbreaking" | modern, state-of-the-art, advanced, contemporary |
| | ❌ "seamless" / "intricate" | unified, coherent, multi-axial, non-uniform |
| **Transitions** | ❌ "furthermore" / "moreover" (overuse) | concurrently, in parallel, conversely, consequently |
| | ❌ "additionally" / "in addition" | alongside this, beyond this, secondarily |
| | ❌ "it is worth noting that" | notably, empirically, specifically, in practice |
| | ❌ "in conclusion" / "to sum up" | in summary, taken together, ultimately |

### Pillar 4: Domain & Technical Terminology Lock (Zero-Thesaurus Rule)
**Rule:** NEVER use a synonym or thesaurus on proper domain, clinical, or algorithmic terms.
- Specific model architectures, mathematical formulas, datasets, and named baselines must be preserved with 100% lexical fidelity.
- Never replace formal technical terms with generic words.

### Pillar 5: Code, LaTeX & Data Integrity (Verbatim Lock)
- **LaTeX Structural Elements:** Every `\section`, `\subsection`, `\label{...}`, `\ref{...}`, `\begin{table*}`, `\end{figure}` must be preserved with exact syntax.
- **Citation Keys:** Every `\cite{...}` key must remain untouched and match `references.bib` verbatim.
- **Mathematical Equations:** All equations, matrices, Greek letters, and inline math (`$...$`, `\begin{equation}`) must be preserved exactly.
- **Empirical Numerical Invariants:** Never alter, round, or approximate experimental benchmark figures, sample sizes, percentages, or table cells.

---

## Step-by-Step Humanization Workflow

1. **Extract & Lock Invariants**: Identify and protect all `\cite{}`, `\ref{}`, equations, numbers, and proper technical terms.
2. **Winnowing Disruption**: Invert clause orders, alternate active/passive voice, and shatter any 5-gram sequences matching external literature or standard AI patterns.
3. **Burstiness Calibration**: Interleave short 5–9 word assertions with extended 30–45 word periodic explanations so sentence standard deviation achieves $\sigma \ge 7.0$.
4. **Lexical Audit**: Scan for and purge all blacklisted clichés (delve, pivotal, comprehensive, crucial, etc.).
5. **Verification**: Confirm 0 broken citations, 0 broken labels, 0 clichés, and 100% mathematical/data fidelity.
