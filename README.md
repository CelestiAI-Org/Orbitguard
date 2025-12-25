# Satellite Collision Risk AI System

A machine learning system for predicting satellite collision risks from Conjunction Data Message (CDM) data. This system achieves 60%+ false positive reduction using Random Forest classification, with SHAP-based explainability and comprehensive visualizations.

## 🚀 Features

- **CDM Data Loader**: Robust loading and validation of satellite conjunction data
- **Feature Engineering**: Advanced features including miss distance, relative velocity, collision probability, and kinetic energy
- **Random Forest Classifier**: Optimized for HIGH_RISK vs FALSE_ALARM classification
- **Confidence Scoring**: Predictions with confidence levels and uncertainty handling
- **SHAP Explainability**: Model interpretability with SHAP values and visualizations
- **Matplotlib Visualizations**: Comprehensive plots including confusion matrices, ROC curves, feature importance
- **Flask REST API**: Optional API endpoints for real-time predictions
- **Config-Driven**: YAML-based configuration for easy customization
- **Type-Hinted**: Full type annotations for better code quality

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/aayushpx/collision-risk-ai.git
cd collision-risk-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Generate sample data:
```bash
python generate_data.py
```

## 🎯 Quick Start

### Training the Model

Run the complete training pipeline:
```bash
python main.py --mode train
```

This will:
1. Load CDM data from `data/cdm_data.csv`
2. Engineer 12+ features from raw data
3. Train a Random Forest classifier
4. Generate performance metrics and visualizations
5. Save the trained model to `models/collision_risk_model.pkl`

### Making Predictions

Run inference on new data:
```bash
python main.py --mode inference --data data/cdm_data_test.csv --output results/predictions.csv
```

### Using the API

Start the Flask API server:
```bash
python api.py --host 0.0.0.0 --port 5000
```

#### API Endpoints

**Health Check**
```bash
curl http://localhost:5000/health
```

**Single Prediction**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "miss_distance": 500.0,
    "relative_velocity": 15000.0,
    "time_to_tca": 12.5,
    "object1_mass": 1000.0,
    "object2_mass": 800.0
  }'
```

**Batch Predictions**
```bash
curl -X POST http://localhost:5000/predict_batch \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "miss_distance": 500.0,
        "relative_velocity": 15000.0,
        "time_to_tca": 12.5,
        "object1_mass": 1000.0,
        "object2_mass": 800.0
      }
    ]
  }'
```

**Explain Prediction**
```bash
curl -X POST http://localhost:5000/explain \
  -H "Content-Type: application/json" \
  -d '{
    "miss_distance": 500.0,
    "relative_velocity": 15000.0,
    "time_to_tca": 12.5,
    "object1_mass": 1000.0,
    "object2_mass": 800.0
  }'
```

## 📊 Features Engineered

The system engineers the following features from raw CDM data:

1. **miss_distance**: Distance at closest approach (meters)
2. **relative_velocity**: Relative velocity between objects (m/s)
3. **collision_probability**: Calculated collision probability
4. **time_to_tca**: Time to Time of Closest Approach (hours)
5. **combined_mass**: Sum of both object masses (kg)
6. **radial_miss_distance**: Radial component of miss distance
7. **along_track_miss_distance**: Along-track component
8. **cross_track_miss_distance**: Cross-track component
9. **kinetic_energy**: Kinetic energy at TCA
10. **urgency_factor**: Inverse of time to TCA
11. **miss_distance_velocity_ratio**: Miss distance to velocity ratio
12. **collision_severity**: Combined severity index

## 🎨 Visualizations

The system generates the following visualizations in the `plots/` directory:

- **Confusion Matrix**: Model classification performance
- **Feature Importance**: Top contributing features
- **ROC Curve**: Receiver Operating Characteristic with AUC
- **Precision-Recall Curve**: Precision vs Recall tradeoff
- **Prediction Distribution**: Distribution of predictions and confidence scores
- **SHAP Summary**: Global feature importance using SHAP
- **SHAP Waterfall**: Individual prediction explanations

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
data:
  cdm_data_path: "data/cdm_data.csv"
  train_test_split: 0.8
  random_state: 42

model:
  type: "RandomForest"
  params:
    n_estimators: 100
    max_depth: 10
    min_samples_split: 5
    min_samples_leaf: 2
    class_weight: "balanced"

prediction:
  confidence_threshold: 0.7

output:
  model_path: "models/collision_risk_model.pkl"
  plots_dir: "plots"
```

## 📈 Performance

Target metric: **60%+ false positive reduction**

The system achieves this by:
- Using balanced class weights to handle imbalanced data
- Engineering domain-specific features
- Applying confidence thresholds for uncertain predictions
- Optimizing for precision on the HIGH_RISK class

Example output:
```
False Positive Reduction: 65.32%
✓ Target achieved (60%+ false positive reduction)

Test Set Performance:
  Accuracy:  0.8850
  Precision: 0.8421
  Recall:    0.8667
  F1 Score:  0.8542
```

## 🏗️ Project Structure

```
collision-risk-ai/
├── src/
│   ├── __init__.py
│   ├── data_loader.py        # CDM data loading
│   ├── preprocessor.py       # Data preprocessing
│   ├── feature_engineer.py   # Feature engineering
│   ├── trainer.py            # Model training
│   ├── predictor.py          # Prediction with confidence
│   ├── explainer.py          # SHAP explainability
│   └── visualizer.py         # Matplotlib visualizations
├── data/
│   ├── cdm_data.csv          # Training data
│   └── cdm_data_test.csv     # Test data
├── models/
│   └── collision_risk_model.pkl  # Trained model
├── plots/                    # Generated visualizations
├── results/                  # Prediction results
├── main.py                   # Main pipeline script
├── api.py                    # Flask REST API
├── generate_data.py          # Sample data generator
├── config.yaml               # Configuration file
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🧪 Testing

To test the system with sample data:

1. Generate sample CDM data:
```bash
python generate_data.py
```

2. Train the model:
```bash
python main.py --mode train
```

3. Run inference:
```bash
python main.py --mode inference --data data/cdm_data_test.csv
```

## 🔬 SHAP Explainability

The system provides model interpretability through SHAP (SHapley Additive exPlanations):

- **Global Explanations**: Feature importance across all predictions
- **Local Explanations**: Why a specific prediction was made
- **Interaction Effects**: How features interact to affect predictions

Access SHAP explanations via:
- API endpoint: `/explain`
- Visualizations in `plots/shap_summary.png`

## 🎯 Hackathon Demo

This system is designed for hackathon demonstrations with:

- Quick setup (< 5 minutes)
- Sample data generation
- Pre-configured optimal parameters
- Comprehensive visualizations
- REST API for live demos
- Achieves target 60%+ false positive reduction

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👥 Authors

- Aayush Prakash

## 🙏 Acknowledgments

- Based on satellite conjunction data analysis principles
- SHAP library for model interpretability
- scikit-learn for machine learning infrastructure