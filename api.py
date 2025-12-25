"""
Flask API for Collision Risk Prediction

Provides REST API endpoints for collision risk predictions.
"""

from flask import Flask, request, jsonify
import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, Any

from src.data_loader import CDMDataLoader
from src.preprocessor import DataPreprocessor
from src.feature_engineer import FeatureEngineer
from src.trainer import CollisionRiskTrainer
from src.predictor import CollisionRiskPredictor
from src.explainer import SHAPExplainer


app = Flask(__name__)

# Global variables for loaded models
pipeline_components = {
    'model': None,
    'preprocessor': None,
    'feature_engineer': None,
    'predictor': None,
    'explainer': None,
    'config': None
}


def load_pipeline(config_path: str = "config.yaml") -> None:
    """Load the trained model and pipeline components."""
    global pipeline_components
    
    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    pipeline_components['config'] = config
    
    # Load model
    trainer = CollisionRiskTrainer(config['model']['params'])
    model = trainer.load_model(config['output']['model_path'])
    pipeline_components['model'] = model
    
    # Initialize components
    pipeline_components['preprocessor'] = DataPreprocessor(
        random_state=config['data']['random_state']
    )
    pipeline_components['feature_engineer'] = FeatureEngineer()
    pipeline_components['predictor'] = CollisionRiskPredictor(
        model,
        confidence_threshold=config['prediction']['confidence_threshold']
    )
    
    print("Pipeline loaded successfully")


@app.route('/health', methods=['GET'])
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': pipeline_components['model'] is not None
    })


@app.route('/predict', methods=['POST'])
def predict() -> Dict[str, Any]:
    """
    Predict collision risk for a single event.
    
    Expected JSON payload:
    {
        "miss_distance": float,
        "relative_velocity": float,
        "time_to_tca": float,
        "object1_mass": float,
        "object2_mass": float
    }
    """
    try:
        # Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Convert to DataFrame
        df = pd.DataFrame([data])
        
        # Engineer features
        feature_engineer = pipeline_components['feature_engineer']
        df_with_features = feature_engineer.engineer_features(df)
        
        # Get feature list
        feature_list = feature_engineer.get_feature_list()
        
        # Make prediction
        predictor = pipeline_components['predictor']
        result = predictor.predict_single(df_with_features[feature_list].iloc[0].to_dict())
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict_batch', methods=['POST'])
def predict_batch() -> Dict[str, Any]:
    """
    Predict collision risk for multiple events.
    
    Expected JSON payload:
    {
        "events": [
            {
                "miss_distance": float,
                "relative_velocity": float,
                ...
            },
            ...
        ]
    }
    """
    try:
        # Get data from request
        data = request.get_json()
        
        if not data or 'events' not in data:
            return jsonify({'error': 'No events provided'}), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(data['events'])
        
        # Engineer features
        feature_engineer = pipeline_components['feature_engineer']
        df_with_features = feature_engineer.engineer_features(df)
        
        # Get feature list
        feature_list = feature_engineer.get_feature_list()
        
        # Make predictions
        predictor = pipeline_components['predictor']
        predictions = predictor.batch_predict(df_with_features[feature_list])
        
        # Get summary
        summary = predictor.get_prediction_summary(df_with_features[feature_list])
        
        return jsonify({
            'predictions': predictions.to_dict('records'),
            'summary': summary
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/explain', methods=['POST'])
def explain_prediction() -> Dict[str, Any]:
    """
    Explain a prediction using SHAP values.
    
    Expected JSON payload: same as /predict
    """
    try:
        # Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Convert to DataFrame
        df = pd.DataFrame([data])
        
        # Engineer features
        feature_engineer = pipeline_components['feature_engineer']
        df_with_features = feature_engineer.engineer_features(df)
        
        # Get feature list
        feature_list = feature_engineer.get_feature_list()
        X = df_with_features[feature_list]
        
        # Create explainer if not exists
        if pipeline_components['explainer'] is None:
            model = pipeline_components['model']
            pipeline_components['explainer'] = SHAPExplainer(model, X)
        
        # Get explanation
        explainer = pipeline_components['explainer']
        explanation = explainer.explain_prediction(X, sample_index=0)
        
        return jsonify(explanation)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/high_risk', methods=['POST'])
def get_high_risk_events() -> Dict[str, Any]:
    """
    Get high-risk events from a batch.
    
    Expected JSON payload: same as /predict_batch
    Query parameter: min_probability (default: 0.5)
    """
    try:
        # Get data from request
        data = request.get_json()
        min_probability = float(request.args.get('min_probability', 0.5))
        
        if not data or 'events' not in data:
            return jsonify({'error': 'No events provided'}), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(data['events'])
        
        # Engineer features
        feature_engineer = pipeline_components['feature_engineer']
        df_with_features = feature_engineer.engineer_features(df)
        
        # Get feature list
        feature_list = feature_engineer.get_feature_list()
        
        # Get high-risk events
        predictor = pipeline_components['predictor']
        high_risk_events = predictor.get_high_risk_events(
            df_with_features[feature_list],
            min_probability=min_probability
        )
        
        return jsonify({
            'high_risk_events': high_risk_events.to_dict('records'),
            'count': len(high_risk_events)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/model_info', methods=['GET'])
def get_model_info() -> Dict[str, Any]:
    """Get model information and metrics."""
    try:
        config = pipeline_components['config']
        
        # Get model path and check if file exists
        model_path = config['output']['model_path']
        
        return jsonify({
            'model_type': config['model']['type'],
            'model_params': config['model']['params'],
            'confidence_threshold': config['prediction']['confidence_threshold'],
            'target_fp_reduction': config['model']['target_fp_reduction'],
            'model_path': model_path
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def main():
    """Main entry point for Flask API."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Collision Risk API")
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='API host'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='API port'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode'
    )
    
    args = parser.parse_args()
    
    # Load pipeline
    load_pipeline(args.config)
    
    # Run app
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
