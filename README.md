🛰️ OrbitGuard

AI-Powered Collision Risk Intelligence for Satellite Operators | ActInSpace 2026

Built in 24 hours at ActInSpace 2026. As a first-year CS student, I led a team of 4 to develop an AI system that filters critical satellite collision warnings from thousands of daily false positives. Our LSTM learns how risk evolves over time and tells operators exactly when they need to act.

ActInSpace isn’t just about tech demos — we pitched OrbitGuard as a SaaS platform with a full business model targeting commercial satellite operators.

🎬 Demo

This GIF demonstrates the OrbitGuard dashboard, including real-time risk assessment, trends, and uncertainty indicators. Loops automatically.

👥 Team
Name	Role	Contributions
Aayush Prakash	Team Lead	Coordinated team, architecture decisions, delivered final pitch
Mostafa Sherif	ML Engineer	Skip-connection LSTM, preprocessing pipeline, uncertainty quantification
Jonty McBreen-Graham	Software Engineer	TypeScript backend, API integration, deployment
Nathan Rawiri	Aerospace Engineer	Orbital mechanics research, pitch deck, domain expertise
🎯 The Problem

Satellite operators receive 20–30 collision warning updates per event over a week. Most are noise. Current systems treat each message independently, so it’s impossible to track whether risk is increasing or decreasing. OrbitGuard learns temporal patterns and tells operators when to act, not just the risk level.

🧠 The Solution
Data Pipeline

Raw CDMs come as JSON snapshots sourced from Space-Track.org
. We built an ETL pipeline that:

Groups messages by event

Reconstructs the timeline

Log-scales miss distance (10 km → 10 m)

Pads sequences for batch processing

Neural Network

Version 1: Standard LSTM

Learned temporal patterns but slow on sudden probability jumps

Validation loss: 1.5e-5

Version 2: Skip-Connection LSTM (Final)

Residual skip connection gives direct access to latest probability alongside full history

Validation loss: 3.0e-6 (5x better)

Faster convergence and better at catching sudden risk changes

Dashboard

🚦 Status: ESCALATING | STABLE | RESOLVING
⏳ Time of Last Opportunity: Hours left to upload maneuver
📈 Risk Trends: INCREASING | DECREASING | STABLE
🔮 Uncertainty: Monte Carlo Dropout gives confidence scores (e.g., 98% vs 60%)

🚀 Quick Start
git clone https://github.com/CelestiAI-Org/Orbitguard.git
cd Orbitguard

# Create .env file
echo "ST_IDENTITY=your_email@example.com" >> .env
echo "ST_PASSWORD=your_password" >> .env

# Run
chmod +x ./start.sh
./start.sh


Or open in DevContainer
.

Run Inference
python app/backend/src/main.py --mode inference


Outputs go to results/predictions_dashboard.csv and plots/ directory.

📊 Example Output
Event	TCA	Status	Hours Left	Trend	Certainty
Sat A vs Sat B	Dec 25, 12:00	🛑 ESCALATING	4.5 hrs	📈 INCREASING	98%
Sat X vs Sat Y	Dec 26, 09:00	✅ RESOLVING	28.0 hrs	📉 DECREASING	99%
💼 Business Model

OrbitGuard was pitched as SaaS for:

Commercial operators (Starlink, OneWeb)

Emerging space nations

Insurance companies

Tiered subscriptions are based on satellite fleet size. Avoiding just one collision pays for decades of service.

🛠️ Tech Stack

Python • PyTorch/TensorFlow • TypeScript • Docker • DevContainers

🌠 Reflection

Leading a team at a 24-hour hackathon is chaotic, especially as a first-year CS student. Key takeaways:

Leadership: Make fast, realistic decisions; trust your team’s instincts.
Business: Nathan’s aerospace expertise lent credibility; the pitch deck and BMC helped judges see OrbitGuard as a real SaaS.
ML: Skip connections were a 2am breakthrough, improving validation loss 5x.
Collaboration: Each team member’s expertise was essential.

The judges valued that OrbitGuard was both technically sound and business-ready.

Built by NEO-FLUX Team for ActInSpace 2026
Making space safer, one prediction at a time.
