"""
Model Training Module

Trains Random Forest classifier for collision risk prediction.
"""

from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)
import joblib
from pathlib import Path


class CollisionRiskTrainer:
    """Trains Random Forest model for collision risk classification."""
    
    def __init__(self, model_params: Dict[str, Any]):
        """
        Initialize the trainer.
        
        Args:
            model_params: Parameters for Random Forest classifier
        """
        self.model_params = model_params
        self.model: Optional[RandomForestClassifier] = None
        self.training_metrics: Dict[str, Any] = {}
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series,
              X_test: pd.DataFrame, y_test: pd.Series) -> RandomForestClassifier:
        """
        Train the Random Forest model.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            y_test: Test labels
        
        Returns:
            Trained RandomForestClassifier
        """
        print("Training Random Forest model...")
        
        # Initialize and train model
        self.model = RandomForestClassifier(**self.model_params)
        self.model.fit(X_train, y_train)
        
        # Evaluate on training and test sets
        train_metrics = self._evaluate(X_train, y_train, "Training")
        test_metrics = self._evaluate(X_test, y_test, "Test")
        
        # Calculate false positive reduction
        fp_reduction = self._calculate_fp_reduction(X_test, y_test)
        
        # Store metrics
        self.training_metrics = {
            'train': train_metrics,
            'test': test_metrics,
            'false_positive_reduction': fp_reduction,
            'feature_importance': self._get_feature_importance(X_train.columns)
        }
        
        # Print summary
        self._print_training_summary()
        
        return self.model
    
    def _evaluate(self, X: pd.DataFrame, y: pd.Series, 
                  dataset_name: str) -> Dict[str, Any]:
        """Evaluate model performance on a dataset."""
        y_pred = self.model.predict(X)
        y_pred_proba = self.model.predict_proba(X)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y, y_pred)
        precision = precision_score(y, y_pred, pos_label='HIGH_RISK', average='binary')
        recall = recall_score(y, y_pred, pos_label='HIGH_RISK', average='binary')
        f1 = f1_score(y, y_pred, pos_label='HIGH_RISK', average='binary')
        
        # Confusion matrix
        cm = confusion_matrix(y, y_pred, labels=['FALSE_ALARM', 'HIGH_RISK'])
        tn, fp, fn, tp = cm.ravel()
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm,
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp)
        }
    
    def _calculate_fp_reduction(self, X_test: pd.DataFrame, 
                                y_test: pd.Series) -> float:
        """
        Calculate false positive reduction compared to baseline.
        
        Baseline: All alerts are considered HIGH_RISK (no filtering)
        """
        # Baseline false positives (all FALSE_ALARM predictions as HIGH_RISK)
        baseline_fp = len(y_test[y_test == 'FALSE_ALARM'])
        
        # Model false positives
        y_pred = self.model.predict(X_test)
        model_fp = len(y_test[(y_test == 'FALSE_ALARM') & (y_pred == 'HIGH_RISK')])
        
        # Calculate reduction
        if baseline_fp == 0:
            return 0.0
        
        fp_reduction = (baseline_fp - model_fp) / baseline_fp
        return fp_reduction
    
    def _get_feature_importance(self, feature_names: pd.Index) -> Dict[str, float]:
        """Get feature importance scores."""
        importance_dict = dict(zip(
            feature_names, 
            self.model.feature_importances_
        ))
        # Sort by importance
        return dict(sorted(importance_dict.items(), 
                          key=lambda x: x[1], reverse=True))
    
    def _print_training_summary(self) -> None:
        """Print training summary."""
        print("\n" + "="*60)
        print("TRAINING SUMMARY")
        print("="*60)
        
        print("\nTest Set Performance:")
        test_metrics = self.training_metrics['test']
        print(f"  Accuracy:  {test_metrics['accuracy']:.4f}")
        print(f"  Precision: {test_metrics['precision']:.4f}")
        print(f"  Recall:    {test_metrics['recall']:.4f}")
        print(f"  F1 Score:  {test_metrics['f1_score']:.4f}")
        
        print("\nConfusion Matrix (Test):")
        print(f"  True Negatives:  {test_metrics['true_negatives']}")
        print(f"  False Positives: {test_metrics['false_positives']}")
        print(f"  False Negatives: {test_metrics['false_negatives']}")
        print(f"  True Positives:  {test_metrics['true_positives']}")
        
        fp_reduction = self.training_metrics['false_positive_reduction']
        print(f"\nFalse Positive Reduction: {fp_reduction:.2%}")
        
        if fp_reduction >= 0.6:
            print("✓ Target achieved (60%+ false positive reduction)")
        else:
            print("⚠ Target not met (60%+ false positive reduction)")
        
        print("\nTop 5 Important Features:")
        for i, (feature, importance) in enumerate(
            list(self.training_metrics['feature_importance'].items())[:5], 1
        ):
            print(f"  {i}. {feature}: {importance:.4f}")
        
        print("="*60 + "\n")
    
    def save_model(self, model_path: str) -> None:
        """
        Save the trained model to disk.
        
        Args:
            model_path: Path to save the model
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        model_dir = Path(model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model and metrics
        save_data = {
            'model': self.model,
            'metrics': self.training_metrics,
            'params': self.model_params
        }
        
        joblib.dump(save_data, model_path)
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path: str) -> RandomForestClassifier:
        """
        Load a trained model from disk.
        
        Args:
            model_path: Path to the saved model
        
        Returns:
            Loaded RandomForestClassifier
        """
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        save_data = joblib.load(model_path)
        self.model = save_data['model']
        self.training_metrics = save_data.get('metrics', {})
        self.model_params = save_data.get('params', {})
        
        print(f"Model loaded from {model_path}")
        return self.model
    
    def save_with_preprocessor(self, model_path: str, preprocessor) -> None:
        """
        Save the trained model with preprocessor.
        
        Args:
            model_path: Path to save the model
            preprocessor: Preprocessor instance with fitted scaler
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        model_dir = Path(model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model, metrics, and preprocessor
        save_data = {
            'model': self.model,
            'metrics': self.training_metrics,
            'params': self.model_params,
            'preprocessor': preprocessor
        }
        
        joblib.dump(save_data, model_path)
        print(f"Model and preprocessor saved to {model_path}")
