"""
Main Pipeline Script

Orchestrates the complete collision risk ML pipeline.
"""

import yaml
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, Any

from app.data_loader import CDMDataLoader
from app.preprocessor import DataPreprocessor
from app.feature_engineering import FeatureEngineer
from app.model import CollisionRiskTrainer
from app.predictor import CollisionRiskPredictor
from app.explainer import SHAPExplainer
from app.visualizer import CollisionRiskVisualizer


class CollisionRiskPipeline:
    """Main pipeline for collision risk prediction."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the pipeline.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.data_loader: CDMDataLoader = None
        self.preprocessor: DataPreprocessor = None
        self.feature_engineer: FeatureEngineer = None
        self.trainer: CollisionRiskTrainer = None
        self.predictor: CollisionRiskPredictor = None
        self.explainer: SHAPExplainer = None
        self.visualizer: CollisionRiskVisualizer = None
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def run_training_pipeline(self) -> None:
        """Run the complete training pipeline."""
        print("="*60)
        print("SATELLITE COLLISION RISK ML PIPELINE")
        print("="*60)
        
        # 1. Load data
        print("\n[1/7] Loading CDM data...")
        self.data_loader = CDMDataLoader(self.config['data']['cdm_data_path'])
        data = self.data_loader.load_data()
        print(f"Loaded {len(data)} records")
        summary = self.data_loader.get_summary()
        print(f"  - HIGH_RISK: {summary['high_risk_count']}")
        print(f"  - FALSE_ALARM: {summary['false_alarm_count']}")
        
        # 2. Engineer features
        print("\n[2/7] Engineering features...")
        self.feature_engineer = FeatureEngineer()
        data_with_features = self.feature_engineer.engineer_features(data)
        feature_list = self.feature_engineer.get_feature_list()
        print(f"Engineered {len(feature_list)} features")
        
        # 3. Preprocess data
        print("\n[3/7] Preprocessing data...")
        self.preprocessor = DataPreprocessor(
            random_state=self.config['data']['random_state']
        )
        X_train, X_test, y_train, y_test = self.preprocessor.prepare_data(
            data_with_features,
            feature_columns=feature_list,
            test_size=1 - self.config['data']['train_test_split'],
            fit=True
        )
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # 4. Train model
        print("\n[4/7] Training Random Forest model...")
        self.trainer = CollisionRiskTrainer(self.config['model']['params'])
        model = self.trainer.train(X_train, y_train, X_test, y_test)
        
        # 5. Save model
        print("\n[5/7] Saving model...")
        self.trainer.save_with_preprocessor(
            self.config['output']['model_path'],
            self.preprocessor
        )
        
        # 6. Create predictor and explainer
        print("\n[6/7] Creating predictor and explainer...")
        self.predictor = CollisionRiskPredictor(
            model, 
            confidence_threshold=self.config['prediction']['confidence_threshold']
        )
        self.explainer = SHAPExplainer(model, X_train)
        
        # 7. Create visualizations
        print("\n[7/7] Creating visualizations...")
        self.visualizer = CollisionRiskVisualizer(
            output_dir=self.config['output']['plots_dir']
        )
        
        # Make predictions on test set
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Create dashboard
        self.visualizer.create_dashboard(
            metrics=self.trainer.training_metrics['test'],
            y_true=y_test,
            y_pred=y_pred,
            y_pred_proba=y_pred_proba,
            feature_importance=self.trainer.training_metrics['feature_importance']
        )
        
        # Create SHAP visualizations
        print("\nGenerating SHAP visualizations...")
        shap_values = self.explainer.calculate_shap_values(X_test.head(100))
        self.visualizer.plot_shap_summary(
            shap_values, X_test.head(100), 
            save_name="shap_summary.png"
        )
        
        # Create prediction distribution
        predictions = self.predictor.predict(X_test)
        self.visualizer.plot_prediction_distribution(predictions)
        
        print("\n" + "="*60)
        print("PIPELINE COMPLETE")
        print("="*60)
        print(f"\nModel saved to: {self.config['output']['model_path']}")
        print(f"Plots saved to: {self.config['output']['plots_dir']}")
        print(f"\nFalse Positive Reduction: {self.trainer.training_metrics['false_positive_reduction']:.2%}")
        
        target_met = self.trainer.training_metrics['false_positive_reduction'] >= 0.6
        print(f"Target (60%+ reduction): {'✓ ACHIEVED' if target_met else '✗ NOT MET'}")
        print("="*60 + "\n")
    
    def run_inference(self, data_path: str) -> pd.DataFrame:
        """
        Run inference on new data.
        
        Args:
            data_path: Path to new CDM data
        
        Returns:
            DataFrame with predictions
        """
        print(f"Running inference on {data_path}...")
        
        # Load model if not already loaded
        if self.trainer is None:
            self.trainer = CollisionRiskTrainer(self.config['model']['params'])
            model = self.trainer.load_model(self.config['output']['model_path'])
            
            # Load preprocessor if saved with model
            import joblib
            save_data = joblib.load(self.config['output']['model_path'])
            if 'preprocessor' in save_data:
                self.preprocessor = save_data['preprocessor']
        else:
            model = self.trainer.model
        
        # Load and prepare data
        data_loader = CDMDataLoader(data_path)
        data = data_loader.load_data()
        
        # Engineer features
        if self.feature_engineer is None:
            self.feature_engineer = FeatureEngineer()
        data_with_features = self.feature_engineer.engineer_features(data)
        
        # Get feature list
        feature_list = self.feature_engineer.get_feature_list()
        
        # Preprocess if preprocessor is available
        if self.preprocessor is not None:
            X, _, _, _ = self.preprocessor.prepare_data(
                data_with_features,
                feature_columns=feature_list,
                fit=False
            )
        else:
            # Use raw features (not recommended for production)
            X = data_with_features[feature_list]
            print("Warning: Using raw features without normalization")
        
        # Make predictions
        if self.predictor is None:
            self.predictor = CollisionRiskPredictor(
                model,
                confidence_threshold=self.config['prediction']['confidence_threshold']
            )
        
        predictions = self.predictor.predict(X)
        
        # Add original data
        results = pd.concat([data, predictions], axis=1)
        
        print(f"Predictions complete for {len(results)} events")
        print(self.predictor.get_prediction_summary(X))
        
        return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Satellite Collision Risk ML Pipeline"
    )
    parser.add_argument(
        '--mode', 
        choices=['train', 'inference'],
        default='train',
        help='Pipeline mode: train or inference'
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--data',
        help='Path to data file (for inference mode)'
    )
    parser.add_argument(
        '--output',
        help='Path to save inference results'
    )
    
    args = parser.parse_args()
    
    pipeline = CollisionRiskPipeline(args.config)
    
    if args.mode == 'train':
        pipeline.run_training_pipeline()
    elif args.mode == 'inference':
        if not args.data:
            print("Error: --data argument required for inference mode")
            return
        
        results = pipeline.run_inference(args.data)
        
        if args.output:
            results.to_csv(args.output, index=False)
            print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
