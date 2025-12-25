"""
SHAP Explainer Module

Provides model interpretability using SHAP values.
"""

from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
import shap
from sklearn.ensemble import RandomForestClassifier


class SHAPExplainer:
    """Explains model predictions using SHAP values."""
    
    def __init__(self, model: RandomForestClassifier, X_train: pd.DataFrame):
        """
        Initialize the SHAP explainer.
        
        Args:
            model: Trained RandomForestClassifier
            X_train: Training data for background distribution
        """
        self.model = model
        self.X_train = X_train
        self.explainer: Optional[shap.TreeExplainer] = None
        self.shap_values: Optional[np.ndarray] = None
    
    def create_explainer(self) -> shap.TreeExplainer:
        """
        Create SHAP TreeExplainer.
        
        Returns:
            SHAP TreeExplainer object
        """
        print("Creating SHAP explainer...")
        self.explainer = shap.TreeExplainer(self.model)
        return self.explainer
    
    def calculate_shap_values(self, X: pd.DataFrame) -> np.ndarray:
        """
        Calculate SHAP values for given data.
        
        Args:
            X: Features DataFrame
        
        Returns:
            SHAP values array
        """
        if self.explainer is None:
            self.create_explainer()
        
        print("Calculating SHAP values...")
        self.shap_values = self.explainer.shap_values(X)
        
        # For binary classification, return HIGH_RISK class SHAP values
        if isinstance(self.shap_values, list) and len(self.shap_values) == 2:
            return self.shap_values[1]
        
        return self.shap_values
    
    def get_feature_importance(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Get feature importance based on SHAP values.
        
        Args:
            X: Features DataFrame
        
        Returns:
            DataFrame with feature importance rankings
        """
        shap_values = self.calculate_shap_values(X)
        
        # Calculate mean absolute SHAP value for each feature
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': np.abs(shap_values).mean(axis=0)
        })
        
        feature_importance = feature_importance.sort_values(
            'importance', ascending=False
        ).reset_index(drop=True)
        
        return feature_importance
    
    def explain_prediction(self, X_sample: pd.DataFrame, 
                          sample_index: int = 0) -> Dict[str, Any]:
        """
        Explain a single prediction using SHAP values.
        
        Args:
            X_sample: Features DataFrame
            sample_index: Index of the sample to explain
        
        Returns:
            Dictionary with explanation details
        """
        shap_values = self.calculate_shap_values(X_sample)
        
        # Get prediction
        prediction = self.model.predict(X_sample)[sample_index]
        prediction_proba = self.model.predict_proba(X_sample)[sample_index]
        
        # Get SHAP values for this sample
        sample_shap_values = shap_values[sample_index]
        
        # Create feature contribution DataFrame
        feature_contributions = pd.DataFrame({
            'feature': X_sample.columns,
            'value': X_sample.iloc[sample_index].values,
            'shap_value': sample_shap_values,
            'abs_shap_value': np.abs(sample_shap_values)
        })
        
        feature_contributions = feature_contributions.sort_values(
            'abs_shap_value', ascending=False
        ).reset_index(drop=True)
        
        explanation = {
            'prediction': prediction,
            'prediction_probability': {
                'FALSE_ALARM': float(prediction_proba[0]),
                'HIGH_RISK': float(prediction_proba[1])
            },
            'base_value': float(self.explainer.expected_value[1] if isinstance(
                self.explainer.expected_value, (list, np.ndarray)
            ) else self.explainer.expected_value),
            'feature_contributions': feature_contributions.to_dict('records'),
            'top_contributing_features': feature_contributions.head(5).to_dict('records')
        }
        
        return explanation
    
    def get_global_explanation(self, X: pd.DataFrame, 
                               top_k: int = 10) -> Dict[str, Any]:
        """
        Get global model explanation.
        
        Args:
            X: Features DataFrame
            top_k: Number of top features to include
        
        Returns:
            Dictionary with global explanation
        """
        feature_importance = self.get_feature_importance(X)
        
        explanation = {
            'feature_importance': feature_importance.head(top_k).to_dict('records'),
            'num_features': len(X.columns),
            'num_samples': len(X)
        }
        
        return explanation
    
    def get_interaction_effects(self, X: pd.DataFrame, 
                                feature1: str, feature2: str) -> np.ndarray:
        """
        Calculate SHAP interaction values between two features.
        
        Args:
            X: Features DataFrame
            feature1: First feature name
            feature2: Second feature name
        
        Returns:
            Interaction values array
        """
        if self.explainer is None:
            self.create_explainer()
        
        print(f"Calculating interaction effects between {feature1} and {feature2}...")
        
        # Get feature indices
        feature1_idx = list(X.columns).index(feature1)
        feature2_idx = list(X.columns).index(feature2)
        
        # Calculate interaction values (simplified - using correlation of SHAP values)
        shap_values = self.calculate_shap_values(X)
        
        interaction = np.corrcoef(
            shap_values[:, feature1_idx], 
            shap_values[:, feature2_idx]
        )[0, 1]
        
        return interaction
