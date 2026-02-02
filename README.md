# 🛰️ OrbitGuard
**AI-Powered Collision Risk Intelligence for Satellite Operators** | ActInSpace 2026

Built in 24 hours at ActInSpace 2026. As a first-year CS student, I led a team of 4 to develop an AI system that filters critical satellite collision warnings from thousands of daily false positives. Our LSTM learns how risk evolves over time and tells operators exactly when they need to act.

ActInSpace isn't just about tech demos. We pitched this as a SaaS platform with a full business model targeting commercial satellite operators.

## 👥 Team

| Name | Role | What They Did |
|------|------|---------------|
| **Aayush Prakash** | Team Lead | Coordinated team, made key architecture decisions, delivered final pitch |
| **Mostafa Sherif** | ML Engineer | Built skip-connection LSTM, designed preprocessing pipeline, implemented uncertainty quantification |
| **Jonty McBreen-Graham** | Software Engineer | TypeScript backend, API integration, deployment |
| **Nathan Rawiri** | Aerospace Engineer | Research on orbital mechanics, created pitch deck, provided domain expertise |

## 🎯 The Problem

Satellite operators get 20-30 collision warning updates per event over a week. Most are noise. The current approach treats each message independently, so you can't tell if risk is increasing or decreasing. We needed a system that learns temporal patterns and tells operators **when** to act, not just how risky things are.

## 🧠 The Solution

### Data Pipeline
Raw CDMs come in as JSON snapshots. We built an ETL pipeline that groups messages by event, reconstructs the timeline, log-scales miss distance (10km to 10m range), and pads sequences for batch processing.

### The Neural Network

**Version 1: Standard LSTM**  
Learned temporal patterns but was slow to react to sudden probability jumps. Validation loss: 1.5e-5.

**Version 2: Skip-Connection LSTM (Final)**  
Added a residual skip connection giving the model direct access to the latest probability alongside the full sequence. This was the breakthrough.

**Results:**
- Validation loss: 3.0e-6 (5x better)
- Faster convergence
- Much better at catching sudden risk changes

The insight: sometimes the latest data point is most important, but you need full history for context. The skip connection uses both.

### The Dashboard

🚦 **Status:** ESCALATING (immediate review) | STABLE (monitor) | RESOLVING (routine)

⏳ **Time of Last Opportunity:** Calculates exact hours left to upload a maneuver  
Example: "You have 11.8 hours left to decide"

📈 **Risk Trends:** INCREASING | DECREASING | STABLE

🔮 **Uncertainty:** Monte Carlo Dropout gives confidence scores (98% vs 60%) so operators know when to trust predictions

## 🚀 Quick Start

```bash
git clone https://github.com/CelestiAI-Org/Orbitguard.git
cd Orbitguard

# Create .env file
echo "ST_IDENTITY=your_email@example.com" >> .env
echo "ST_PASSWORD=your_password" >> .env

# Run
chmod +x ./start.sh
./start.sh
```

Or open in [DevContainer](https://containers.dev/).

### Run Inference
```bash
python app/backend/src/main.py --mode inference
```

Outputs go to `results/predictions_dashboard.csv` and `plots/` directory.

## 📊 Example Output

| Event | TCA | Status | Hours Left | Trend | Certainty |
|-------|-----|--------|-----------|-------|-----------|
| Sat A vs Sat B | Dec 25, 12:00 | 🛑 ESCALATING | 4.5 hrs | 📈 INCREASING | 98% |
| Sat X vs Sat Y | Dec 26, 09:00 | ✅ RESOLVING | 28.0 hrs | 📉 DECREASING | 99% |

## 💼 Business Model

We pitched OrbitGuard as SaaS targeting commercial operators (Starlink, OneWeb), emerging space nations, and insurance companies. Tiered subscription based on number of satellites. The pitch: avoid one collision and you've paid for decades of service.

## 🛠️ Tech Stack

Python • PyTorch/TensorFlow • TypeScript • Docker • DevContainers

## 🌠 Reflection

Leading a technical team at a hackathon is chaotic, especially when you're a first-year CS student coordinating an aerospace engineer, ML engineer, and software engineer. This was my second time doing it, and I still had impostor syndrome at times. But you have 24 hours to build something that works AND pitch it as a viable business.

**On leadership:**  
Making fast decisions about what's realistic vs nice-to-have is hard. We cut features like real-time orbital propagation because they weren't achievable. Learning to trust your team while coordinating was key. Nathan's aerospace expertise gave us credibility when judges asked about orbital mechanics.

**On the business side:**  
Nathan built the pitch deck and worked on the business model canvas alongside me, then I practiced the pitch. Having an actual aerospace engineer made a huge difference when judges asked technical questions. Meanwhile, Mostafa and Jonty were finishing the ML pipeline.

**On ML:**  
The skip connection was Mostafa's idea we almost didn't try. He spent 4 hours at 2am debugging it. Turns out it gave us 5x improvement. Sometimes weird ideas are worth pursuing, and trusting your team's instincts is part of leading.

**On collaboration:**  
Everyone brought something different. Mostafa knew ML inside out, Jonty kept infrastructure from falling apart, Nathan understood the actual aerospace problem, and I made sure we had a cohesive story. The best part was seeing it come together in the final pitch.

The judges liked that we built something that could actually become a company. That's what ActInSpace is about.

---

**Built by NEO-FLUX Team for ActInSpace 2025**  
*Making space safer, one prediction at a time.*
