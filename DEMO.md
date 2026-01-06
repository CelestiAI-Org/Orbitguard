# Hackathon Demo Guide (Time-Series LSTM)

## Quick Start (Demo Flow)

### 1. Explain the Concept (30s)
"Standard systems look at a single warning and panic. Our system looks at the **history** of warnings for a specific event. By seeing how the risk *evolves* over time (e.g., probability is increasing as we get consistent data), we can distinguish real threats from noise."

### 2. Show the Data
Open `data/download.json` or print the first few sequences using the pipeline test:
```bash
python test_pipeline.py
```
*Show that we aren't just looking at one number, but a matrix of `[Probability, Miss Distance, Time]` updates.*

### 3. Train the Model (Live)
Run the training command. It's fast enough for a live demo (50 epochs takes <10 seconds on small data).
```bash
python main.py --mode train
```
**Point out:**
- The Loss decreases rapidly (e.g., 0.003 -> 0.00003).
- The model is learning the "trajectory" of collision risk.

### 4. Run Inference & Show Results
Generate the predictions:
```bash
python main.py --mode inference
```
Open `results/predictions_lstm.csv` and show:
- **Predicted_PC**: The forecasted collision probability.
- **Certainty**: A score (0-1) indicating how stable/confident the model is in this prediction.

### 5. "What this means?"
"We can now tell an operator: 'This event has a high collision probability, AND our model is 95% certain based on the trend.' This massively reduces false positives caused by a single bad sensor reading."

## Future Roadmap
1. **Live API**: Connect `SpaceTrackApiDataSource` to simplified real-time data.
2. **More Features**: Incorporate Covariance matrices into the LSTM state.
3. **Transformer Model**: Upgrade from LSTM to Transformer for better long-range dependency handling.
