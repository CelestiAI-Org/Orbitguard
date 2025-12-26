# Hackathon Demo Guide

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Sample Data
```bash
python generate_data.py
```

### 3. Train the Model
```bash
python main.py --mode train
```

Expected output:
- False Positive Reduction: **97.86%** ✅ (Target: 60%+)
- Test Accuracy: **96.50%**
- Model saved to `models/collision_risk_model.pkl`
- 6 visualizations in `plots/`

### 4. Run Inference
```bash
python main.py --mode inference --data data/cdm_data_test.csv --output results/predictions.csv
```

### 5. Start API Server (Optional)
```bash
python api.py --host 0.0.0.0 --port 5000
```

### 6. Test API
```bash
python examples.py
```

## Demo Scenarios

### Scenario 1: High-Risk Collision Detection

**Input:**
```json
{
  "miss_distance": 100.0,
  "relative_velocity": 18000.0,
  "time_to_tca": 2.0,
  "object1_mass": 2000.0,
  "object2_mass": 1500.0
}
```

**Expected Output:**
```json
{
  "prediction": "HIGH_RISK",
  "confidence": 1.0,
  "high_risk_probability": 1.0,
  "risk_level": "CRITICAL"
}
```

### Scenario 2: False Alarm Filtering

**Input:**
```json
{
  "miss_distance": 5000.0,
  "relative_velocity": 10000.0,
  "time_to_tca": 50.0,
  "object1_mass": 500.0,
  "object2_mass": 300.0
}
```

**Expected Output:**
```json
{
  "prediction": "FALSE_ALARM",
  "confidence": 1.0,
  "high_risk_probability": 0.0,
  "risk_level": "MINIMAL"
}
```

## Key Features to Demonstrate

### 1. Superior Performance
- **97.86% False Positive Reduction** (vs 60% target)
- Only 3 false positives out of 140 negative cases
- 96.5% accuracy, 99% AUC

### 2. Feature Engineering
Show the 12 engineered features:
- Basic: miss_distance, relative_velocity, time_to_tca
- Derived: collision_probability, combined_mass
- Geometric: radial/along-track/cross-track miss distances
- Advanced: kinetic_energy, urgency_factor, collision_severity

### 3. Model Explainability (SHAP)
```python
# Top 3 most important features:
1. miss_distance_velocity_ratio: 0.2301
2. cross_track_miss_distance: 0.1442
3. radial_miss_distance: 0.1440
```

### 4. Visualizations
Show plots in `plots/` directory:
- Confusion Matrix: Clear visualization of performance
- ROC Curve: AUC = 0.99
- Feature Importance: What drives predictions
- SHAP Summary: How features affect predictions

### 5. REST API
Live demo with curl commands:

```bash
# Health check
curl http://localhost:5000/health

# Single prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"miss_distance": 100.0, "relative_velocity": 18000.0, ...}'

# Batch prediction
curl -X POST http://localhost:5000/predict_batch \
  -H "Content-Type: application/json" \
  -d '{"events": [...]}'

# Get high-risk events only
curl -X POST http://localhost:5000/high_risk?min_probability=0.5 \
  -H "Content-Type: application/json" \
  -d '{"events": [...]}'

# Model info
curl http://localhost:5000/model_info
```

## Architecture Highlights

### Clean Code Structure
```
collision-risk-ai/
├── src/
│   ├── data_loader.py      # CDM data ingestion
│   ├── preprocessor.py     # Data cleaning & normalization
│   ├── feature_engineer.py # Feature engineering
│   ├── trainer.py          # Model training
│   ├── predictor.py        # Predictions with confidence
│   ├── explainer.py        # SHAP interpretability
│   └── visualizer.py       # Matplotlib plots
├── main.py                 # Pipeline orchestration
├── api.py                  # Flask REST API
├── config.yaml             # Configuration
└── requirements.txt        # Dependencies
```

### Type Safety
All code is fully type-hinted:
```python
def predict(self, X: pd.DataFrame) -> pd.DataFrame:
    """Make predictions with confidence scores."""
    ...
```

### Configuration-Driven
Easy to customize via `config.yaml`:
```yaml
model:
  type: "RandomForest"
  params:
    n_estimators: 100
    max_depth: 10
    class_weight: "balanced"

prediction:
  confidence_threshold: 0.7
```

## Demo Script

### Opening (30 seconds)
"We built a machine learning system that reduces false positive satellite collision alerts by 97.86%, far exceeding the 60% target. This means operators can focus on real threats while ignoring 98% of false alarms."

### Technical Overview (1 minute)
1. "We load CDM data with 5 key parameters"
2. "Engineer 12 features including collision probability and kinetic energy"
3. "Train a Random Forest classifier with balanced class weights"
4. "Achieve 96.5% accuracy and 99% AUC"

### Live Demo (2 minutes)
1. **Show training output**: "Model trains in seconds and immediately shows 97.86% FP reduction"
2. **Show visualizations**: "Confusion matrix shows only 3 false positives"
3. **API demo**: "Real-time predictions via REST API"
4. **SHAP explanation**: "Model is fully explainable - miss_distance_velocity_ratio is most important"

### Closing (30 seconds)
"This system is production-ready with:
- Config-driven architecture
- Full type hints
- REST API
- SHAP explainability
- Comprehensive visualizations

Ready to deploy and save millions in false alarm costs."

## Troubleshooting

### Issue: Model not found
```bash
python main.py --mode train
```

### Issue: API not responding
```bash
# Check if running
curl http://localhost:5000/health

# Restart if needed
python api.py --host 0.0.0.0 --port 5000
```

### Issue: Dependencies missing
```bash
pip install -r requirements.txt
```

## Performance Metrics Summary

| Metric | Value | Target |
|--------|-------|--------|
| False Positive Reduction | 97.86% | 60%+ ✅ |
| Accuracy | 96.50% | - |
| Precision | 94.92% | - |
| Recall | 93.33% | - |
| F1 Score | 94.12% | - |
| AUC | 0.99 | - |
| True Negatives | 137 | - |
| False Positives | 3 | - |
| False Negatives | 4 | - |
| True Positives | 56 | - |

## Next Steps (Post-Hackathon)

1. **Production Deployment**
   - Containerize with Docker
   - Deploy to cloud (AWS/GCP/Azure)
   - Set up CI/CD pipeline

2. **Model Improvements**
   - Add more CDM features (covariance data)
   - Ensemble with other algorithms
   - Real-time learning

3. **Integration**
   - Connect to live CDM data feeds
   - Integrate with satellite tracking systems
   - Alert notification system

4. **Monitoring**
   - Model performance tracking
   - Data drift detection
   - A/B testing framework

## Contact

For questions or demo requests, please contact the team.

---

**Built for hackathon demo - Ready to deploy! 🚀**
