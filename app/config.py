"""
Configuration Module

Centralized configuration for the collision risk prediction system.
All paths, hyperparameters, and thresholds are defined here.
"""

import os
from pathlib import Path
from typing import Dict, Any, List


# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
PLOTS_DIR = BASE_DIR / "plots"
RESULTS_DIR = BASE_DIR / "results"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for directory in [DATA_DIR, MODELS_DIR, PLOTS_DIR, RESULTS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Data configuration
DATA_CONFIG = {
    "cdm_data_path": DATA_DIR / "cdm_data.csv",
    "train_test_split": 0.8,
    "random_state": 42,
    "time_based_split": True,  # Use temporal split for hackathon realism
}

# Feature engineering configuration
FEATURE_CONFIG = {
    # Core features from CDM
    "core_features": [
        "miss_distance",           # meters
        "relative_velocity",       # m/s
        "collision_probability",   # from CDM
        "time_to_tca",            # seconds (time to closest approach)
    ],
    
    # Object features
    "object_features": [
        "object1_mass",           # kg
        "object2_mass",           # kg
        "object1_size",           # RCS (radar cross section) if available
        "object2_size",           # RCS
    ],
    
    # Engineered features
    "engineered_features": [
        "combined_mass",
        "radial_miss_distance",
        "along_track_miss_distance",
        "cross_track_miss_distance",
        "kinetic_energy",
        "urgency_factor",
        "miss_distance_velocity_ratio",
        "collision_severity",
        "orbital_regime",          # LEO, MEO, GEO classification
        "historical_maneuver_flag",
        "conjunction_frequency",
    ],
    
    # Orbital regime thresholds (altitude in km)
    "orbital_regimes": {
        "LEO": (0, 2000),
        "MEO": (2000, 35786),
        "GEO": (35786, 100000),
    },
}

# Model configuration
MODEL_CONFIG = {
    "model_type": "RandomForest",  # Can also use XGBoost
    
    # Random Forest hyperparameters
    "rf_params": {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "random_state": 42,
        "class_weight": "balanced",  # Handle class imbalance
        "n_jobs": -1,
    },
    
    # XGBoost hyperparameters (alternative)
    "xgb_params": {
        "n_estimators": 100,
        "max_depth": 6,
        "learning_rate": 0.1,
        "random_state": 42,
        "scale_pos_weight": 1,  # Adjust for class imbalance
        "n_jobs": -1,
    },
    
    # Training configuration
    "use_smote": False,  # Use SMOTE for class imbalance (alternative to class_weight)
    "cv_folds": 5,
    
    # Model versioning
    "model_path": MODELS_DIR / "collision_risk_model.pkl",
    "model_version": "v1.0",
}

# Label strategy thresholds
LABEL_CONFIG = {
    "high_risk_thresholds": {
        "collision_probability": 1e-4,  # Pc > 10^-4
        "miss_distance": 1000,           # < 1 km
        "maneuver_performed": True,      # If maneuver was performed
        "actual_collision": True,        # If collision occurred
    },
    
    "false_alarm_thresholds": {
        "collision_probability": 1e-5,  # Pc < 10^-5
        "miss_distance": 5000,           # > 5 km
        "no_maneuver": True,
        "no_collision": True,
    },
}

# Prediction configuration
PREDICTION_CONFIG = {
    "confidence_threshold": 0.7,
    "risk_levels": {
        "LOW": (0.0, 0.3),
        "MEDIUM": (0.3, 0.7),
        "HIGH": (0.7, 1.0),
    },
}

# Target metrics (hackathon goals)
TARGET_METRICS = {
    "false_positive_reduction": 0.4,  # 40%+ reduction
    "recall_on_true_collisions": 1.0,  # 100% recall
    "precision_on_high_risk": 0.75,    # 75%+ precision
}

# Visualization configuration
VISUALIZATION_CONFIG = {
    "plots_dir": PLOTS_DIR,
    "plot_formats": ["png", "pdf"],
    "dpi": 300,
    "figsize": (10, 6),
    
    # Plots to generate for pitch deck
    "required_plots": [
        "model_accuracy_comparison",
        "roc_curve",
        "precision_recall_curve",
        "feature_importance",
        "confusion_matrix",
    ],
}

# API configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": False,
    "endpoint": "/predict",
}

# Logging configuration
LOGGING_CONFIG = {
    "log_file": LOGS_DIR / "app.log",
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
}

# Validation rules
VALIDATION_CONFIG = {
    "required_columns": [
        "miss_distance",
        "relative_velocity",
        "time_to_tca",
        "object1_mass",
        "object2_mass",
    ],
    
    "value_ranges": {
        "miss_distance": (0, 1e6),      # 0 to 1000 km
        "relative_velocity": (0, 3e4),  # 0 to 30 km/s
        "time_to_tca": (0, 86400 * 7),  # 0 to 7 days
        "collision_probability": (0, 1),
    },
}


def get_all_config() -> Dict[str, Any]:
    """
    Get all configuration as a dictionary.
    
    Returns:
        Dictionary containing all configuration settings
    """
    return {
        "data": DATA_CONFIG,
        "features": FEATURE_CONFIG,
        "model": MODEL_CONFIG,
        "labels": LABEL_CONFIG,
        "prediction": PREDICTION_CONFIG,
        "targets": TARGET_METRICS,
        "visualization": VISUALIZATION_CONFIG,
        "api": API_CONFIG,
        "logging": LOGGING_CONFIG,
        "validation": VALIDATION_CONFIG,
    }


def get_feature_list() -> List[str]:
    """
    Get complete list of features to use in model.
    
    Returns:
        List of feature names
    """
    return (
        FEATURE_CONFIG["core_features"] +
        FEATURE_CONFIG["object_features"] +
        FEATURE_CONFIG["engineered_features"]
    )


if __name__ == "__main__":
    # Print configuration for debugging
    import json
    config = get_all_config()
    print(json.dumps({k: str(v) for k, v in config.items()}, indent=2))
