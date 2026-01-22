# 🛰️ AI Collision Risk Classifier

> **Turning Raw Space Data into Actionable Intelligence.**

In the crowded orbital environment, satellite operators are overwhelmed by thousands of Conjunction Data Messages (CDMs) daily. Most are noise; a few are critical. This system cuts through that noise using **Deep Learning** to analyse not just the probability of collision, but the *evolution of risk over time*, giving operators clear, actionable deadlines.

---

## 🏗️ System Architecture

The solution builds a complete end-to-end pipeline: **Ingest (ETL) -> Deep Learning -> Actionable Dashboard**.

### 1. The Data Pipeline (ETL & Feature Engineering)
Raw CDMs are typically snapshot updates. A single conjunction event might receive 20-30 updates over the course of a week.
*   **Ingest**: We load raw JSON CDMs (compliant with CCSDS standards).
*   **Grouping & Sorting**: The pipeline groups messages by unique event signatures: `(SAT_1_ID, SAT_2_ID, TCA)`. It then sorts them by `CREATION_DATE` to reconstruct the *narrative* of the event.
*   **Feature Engineering**:
    *   **Log-Scaling**: Miss Distance (`MIN_RNG`) often varies from 10km to 10m. We use log-scaling to normalize this dynamic range for the neural network.
    *   **Time Deltas**: We calculate `Time_to_TCA` to help the model understand urgency.
    *   **Sequence Padding**: Events have varying update counts. The `TimeSeriesPreprocessor` dynamically pads or truncates sequences (default `seq_len=5`) to create uniform tensors for batch processing.

### 2. Machine Learning Architecture (The Brain)
We treat conjunction risk classification as a **Time-Series Forecasting** problem.

#### The Evolution: Version 1 vs Version 2
*   **Version 1 (Standard LSTM)**: A canonical Long Short-Term Memory network. It successfully learned temporal patterns but struggled to react quickly to sudden changes in the probability reported by space surveillance networks (Validation Loss: `1.5e-5`).
*   **Version 2 (Skip-Connection LSTM - *Champion Model*)**: We introduced a **Residual Skip Connection**.
    *   *Concept*: The model receives the full sequence but also gets a direct "shortcut" to the latest reported Probability.
    *   *Result*: **Validation Loss: `3.0e-6`**. A **5x improvement** in accuracy and faster convergence.

### 3. Actionable Outputs (The Dashboard)
We don't just output a probability number. We generate **Actionable Intelligence**:

1.  🚦 **Traffic Light Status**:
    *   **RED**: High Probability (>1e-4) OR Critical Miss Distance (<1km). Immediate review.
    *   **YELLOW**: Elevated risk (>1e-5). Monitor closely.
    *   **GREEN**: Routine.

2.  ⏳ **Time of Last Opportunity (TLO)**:
    *   Calculates `Hours_To_Decision`.
    *   *Formula*: `TCA - Reaction_Time (e.g., 6h) - Message_Received_Time`.
    *   Tells the operator: *"You have 11.8 hours left to upload a maneuver."*

3.  📈 **Risk Trend**:
    *   Identifies if the risk is `INCREASING`, `DECREASING`, or `STABLE` compared to the previous update.

4.  🔮 **"History of the Future" Visualization**:
    *   For every high-risk event, the system automatically plots the specific history of that conjunction, identifying the exact moment the PC deviates from the trend.
    *   includes **Certainty Estimation** (using Monte Carlo Dropout) to quantify confidence.

---

## 🚀 Quick Start

### 1. Open project in [devcontainer](https://containers.dev/)
Python & npm dependencies will be installed automatically for development

### 2. Environment file

1. Create a `.env` file 
2. Add the following to it:
    ```
    # Collision Risk AI Configuration

    # Backend Configuration
    BACKEND_PORT=PORT

    # Frontend Configuration
    FRONTEND_PORT=PORT

    # Gemini API (optional)
    GEMINI_API_KEY=API_KEY_HERE
    ```
3. Replace `PORT` & `API_KEY_HERE`

### 3. Start up script

1. Make the `start.sh` script executable
    ```bash
    chmod +x ./start.sh
    ```

2. Run script to start application
    ```bash
    ./start.sh
    ```

---
### 🖥️ Machine learning
---

### 1. Configuration (`app/backend/config.yaml`)
Customize your risk thresholds and model parameters:
```yaml
model:
  type: "LSTM_SKIP"  # The high-performance architecture
  sequence_length: 5

thresholds:
  high_risk: 0.0001        # Risk > 1e-4 triggers RED
  reaction_time_hours: 6   # How long your ops team needs
```

### 2. Run Inference (The Dashboard)
Run the full pipeline to process data and generate the dashboard:
```bash
python app/backend/src/main.py --mode inference
```
*   **Output CSV**: `results/predictions_dashboard.csv` (Contains TLO, Status, Trend)
*   **Plots**: Check the `plots/` directory for trend visualizations.

### 3. Training (Optional)
To retrain the model on new datasets:
```bash
python app/backend/src/main.py --mode train
```

---

## 📊 Final Output Example

| Event | TCA | Risk Status | Hours to Decision | Trend | AI Certainty |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Sat A vs Sat B** | Dec 25, 12:00 | **ESCALATING** 🛑 | **4.5 hrs** left | **INCREASING** 📈 | **98%** |
| **Sat X vs Sat Y** | Dec 26, 09:00 | **RESOLVING** ✅ | 28.0 hrs left | **DECREASING** 📉 | **99%** |
| **Sat Z vs Sat T** | Dec 25, 12:00 | **STABLE** 🛑 | **4.5 hrs** left | **STABLE** 📈 | **98%** |

---

## 👥 Authors
**Mostafa & NEO-FLUX Team** - *Hackathons/ActInSpace*
