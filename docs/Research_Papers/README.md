# Reviewed Research Papers Repository

**Project Title:** Digital Twin-Based Early Warning System for Cold Chain Disruption Detection (Topic 21)  
**Student Name:** Krishna Sikheriya  
**Roll Number:** IIT2023139  
**Degree:** B.Tech (Information Technology), 7th Semester  
**Course:** Managing Corporate Entrepreneurship  
**Instructor:** Dr. Netranand Pathak  
**Institution:** Indian Institute of Information Technology, Allahabad (IIITA)  

---

## Overview of Reviewed Literature

This directory contains full-text PDFs of the primary peer-reviewed literature reviewed, analyzed, and implemented in the development of our Digital Twin-Based Cold Chain Early Warning System. The literature spans four foundational scientific domains:
1. **Cold Chain Digital Twins & Thermal Engineering:** Physical principles of temperature monitoring, reefer containers, and thermal inertia.
2. **Deep Learning for Temporal Anomaly Detection:** Recurrent architectures (LSTM Autoencoders) for multi-variate and single-variate temporal reconstruction.
3. **Epistemic & Aleatoric Uncertainty Quantification:** Bayesian approximations (MC Dropout) and Evidential Deep Learning (Dirichlet prior networks).
4. **Physics-Informed Deep Learning & Multi-Horizon Forecasting:** Physics-Informed Neural Networks (PINNs) and Temporal Fusion Transformers (TFT).

---

## Catalog of Downloaded Papers

### 1. Cold Chain Digital Twins & Maritime Reefer Telemetry
* **File:** `Vuksic_2026_Maritime_Reefer_Digital_Twin.pdf`
* **Full Citation:** Vukšić, M., Ćelić, J., Ogrizović, D., & Perić Hadžić, A. (2026). Early Anomaly Detection in Maritime Refrigerated Containers Using a Hybrid Digital Twin and Deep Learning Framework. *Applied Sciences*, 16(4), 1887.
* **DOI:** [10.3390/app16041887](https://doi.org/10.3390/app16041887)
* **Relevance to Project:** Directly serves as our primary benchmark comparison. Examines hybrid digital twins integrating physical thermal models with deep learning for maritime reefer containers, validating our lead-time early warning paradigm.

---

### 2. Cold Chain Logistics Stream Anomaly Detection
* **File:** `Xie_2025_Cold_Chain_Anomaly_Detection.pdf`
* **Full Citation:** Xie, Z., Long, H., Ling, C., Zhou, Y., & Luo, Y. (2025). An Anomaly Detection Scheme for Data Stream in Cold Chain Logistics. *PLOS ONE*, 20(3), e0315322.
* **DOI:** [10.1371/journal.pone.0315322](https://doi.org/10.1371/journal.pone.0315322)
* **Relevance to Project:** Explores high-throughput IoT streaming anomaly detection in perishable food transit, highlighting the severe vulnerability of static threshold detectors to sensor drift and diurnal fluctuation.

---

### 3. Evidential Deep Learning & Multi-Head Uncertainty Fusion
* **File:** `Sensoy_2018_Evidential_Deep_Learning.pdf`
* **Full Citation:** Sensoy, M., Kaplan, L., & Kandemir, M. (2018). Evidential Deep Learning to Quantify Classification Uncertainty. *Advances in Neural Information Processing Systems (NeurIPS 2018)*, 31, 3183–3193.
* **Relevance to Project:** Provides theoretical and algorithmic basis for our Breakthrough Pipeline 5 (Evidential Multi-Head Decision Fusion). Places Dirichlet priors over class probabilities to compute operational belief mass and total epistemic vacuity in a single deterministic pass.

---

### 4. Recurrent Architectures for Temporal Reconstruction
* **File:** `Malhotra_2016_LSTM_Anomaly_Detection.pdf`
* **Full Citation:** Malhotra, P., Ramakrishnan, A., Anand, G., Vig, L., Agarwal, P., & Shroff, G. (2016). LSTM-Based Encoder-Decoder for Multi-Sensor Anomaly Detection. *arXiv:1607.00148*, ICML Anomaly Detection Workshop.
* **Relevance to Project:** Foundations of our Model 3 (LSTM Autoencoder). Encodes nominal sequence patterns into a latent space and computes anomaly scores from reconstruction error residuals ($e_t = |x_t - \hat{x}_t|$).

---

### 5. Physics-Informed Neural Networks (PINNs)
* **File:** `Raissi_2019_Physics_Informed_Neural_Networks.pdf`
* **Full Citation:** Raissi, M., Perdikaris, P., & Karniadakis, G. E. (2019). Physics-Informed Neural Networks: A Deep Learning Framework for Solving Forward and Inverse Problems Involving Nonlinear Partial Differential Equations. *Journal of Computational Physics*, 378, 686–707.
* **DOI:** [10.1016/j.jcp.2018.10.045](https://doi.org/10.1016/j.jcp.2018.10.045)
* **Relevance to Project:** Foundations of our Breakthrough Pipeline 2 (Physics-Informed LSTM Autoencoder). Embeds Newton's law of cooling ($\frac{dT}{dt} = -k(T - T_{amb})$) into the training loss function to penalize non-physical temperature predictions.

---

### 6. Temporal Fusion Transformers (TFT)
* **File:** `Lim_2021_Temporal_Fusion_Transformers.pdf`
* **Full Citation:** Lim, B., Arık, S. Ö., Loeff, N., & Pfister, T. (2021). Temporal Fusion Transformers for Interpretable Multi-Horizon Time Series Forecasting. *International Journal of Forecasting*, 37(4), 1748–1764.
* **DOI:** [10.1016/j.ijforecast.2021.03.012](https://doi.org/10.1016/j.ijforecast.2021.03.012)
* **Relevance to Project:** Foundations of our Breakthrough Pipeline 3 (TFT Multi-Horizon Forecasting). Enables quantile forecasting (P10, P50, P90) over 12-hour horizons to predict temperature excursions before they physically occur.

---

### 7. Bayesian Deep Learning via Monte Carlo Dropout
* **File:** `Gal_2016_Dropout_Bayesian_Approximation.pdf`
* **Full Citation:** Gal, Y., & Ghahramani, Z. (2016). Dropout as a Bayesian Approximation: Representing Model Uncertainty in Deep Learning. *Proceedings of the 33rd International Conference on Machine Learning (ICML 2016)*, PMLR 48:1050–1059.
* **Relevance to Project:** Foundations of our Breakthrough Pipeline 1 (Variational Monte Carlo Dropout LSTM). Quantifies epistemic uncertainty through stochastic forward passes at inference time to prevent false alarms during high-uncertainty regimes.

---

### 8. Unsupervised Anomaly Isolation
* **File:** `Liu_2008_Isolation_Forest.pdf`
* **Full Citation:** Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation Forest. *2008 Eighth IEEE International Conference on Data Mining (ICDM)*, 413–422.
* **DOI:** [10.1109/ICDM.2008.17](https://doi.org/10.1109/ICDM.2008.17)
* **Relevance to Project:** Foundations of our Model 2 (Isolation Forest baseline). Isolates anomalous observations by randomly partitioning feature dimensions, providing a tree-based comparison against deep sequence models.

---

## Additional Seminal References Reviewed

In addition to the PDFs above, the project incorporates methodology and theoretical insights from:
- **Defraeye, T. et al. (2023 / 2021 / 2019):** *Digital twins of food cold chains: Advances, challenges, and opportunities.* Formulates the end-to-end framework for sensor-to-twin hygrothermal data upcycling in horticultural and cold chain supply chains.
- **Meng, X. et al. (2024):** *A cost-effective over-temperature alarm system for cold chain delivery.* *Journal of Food Engineering*, 368, 111914. Formulates hardware-constrained threshold alarms for delivery vans.
- **Wu, W. et al. (2023):** *Internet of Everything and Digital Twin enabled service platform for cold chain logistics.* *Journal of Industrial Information Integration*, 33, 100443. Details cloud-edge telemetry pipelines.
- **Page, E. S. (1954):** *Continuous Inspection Schemes.* *Biometrika*, 41(1–2), 100–115. Introduces CUSUM sequential drift detection utilized in our Breakthrough Pipeline 4.
