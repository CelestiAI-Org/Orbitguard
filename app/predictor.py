"""
Prediction Module

Makes collision risk predictions with confidence scores.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier


class CollisionRiskPredictor:
    """Predicts collision risk with confidence scores."""
    
    def __init__(self, model: RandomForestClassifier, 
                 confidence_threshold: float = 0.7):
        """
        Initialize the predictor.
        
        Args:
            model: Trained RandomForestClassifier
            confidence_threshold: Minimum confidence for HIGH_RISK prediction
        """
        self.model = model
        self.confidence_threshold = confidence_threshold
    
    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Make predictions with confidence scores.
        
        Args:
            X: Features DataFrame
        
        Returns:
            DataFrame with predictions and confidence scores
        """
        # Get class predictions
        predictions = self.model.predict(X)
        
        # Get probability estimates
        probabilities = self.model.predict_proba(X)
        
        # Create results DataFrame
        results = pd.DataFrame({
            'prediction': predictions,
            'confidence': np.max(probabilities, axis=1),
            'high_risk_probability': probabilities[:, 1] if probabilities.shape[1] > 1 else probabilities[:, 0],
            'false_alarm_probability': probabilities[:, 0] if probabilities.shape[1] > 1 else 1 - probabilities[:, 0]
        })
        
        # Apply confidence threshold
        results['final_prediction'] = results.apply(
            lambda row: row['prediction'] if row['confidence'] >= self.confidence_threshold 
            else 'UNCERTAIN', axis=1
        )
        
        return results
    
    def predict_single(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Make prediction for a single conjunction event.
        
        Args:
            features: Dictionary of feature values
        
        Returns:
            Dictionary with prediction results
        """
        # Convert to DataFrame
        X = pd.DataFrame([features])
        
        # Get predictions
        results = self.predict(X)
        
        # Format output
        result = {
            'prediction': results['prediction'].iloc[0],
            'confidence': float(results['confidence'].iloc[0]),
            'high_risk_probability': float(results['high_risk_probability'].iloc[0]),
            'false_alarm_probability': float(results['false_alarm_probability'].iloc[0]),
            'final_prediction': results['final_prediction'].iloc[0],
            'risk_level': self._categorize_risk(results['high_risk_probability'].iloc[0])
        }
        
        return result
    
    def _categorize_risk(self, probability: float) -> str:
        """
        Categorize risk level based on probability.
        
        Args:
            probability: High risk probability
        
        Returns:
            Risk level category
        """
        if probability >= 0.8:
            return "CRITICAL"
        elif probability >= 0.6:
            return "HIGH"
        elif probability >= 0.4:
            return "MEDIUM"
        elif probability >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"
    
    def batch_predict(self, X: pd.DataFrame, 
                     return_detailed: bool = True) -> pd.DataFrame:
        """
        Make predictions for a batch of conjunction events.
        
        Args:
            X: Features DataFrame
            return_detailed: Whether to return detailed predictions
        
        Returns:
            DataFrame with predictions
        """
        results = self.predict(X)
        
        if return_detailed:
            results['risk_level'] = results['high_risk_probability'].apply(
                self._categorize_risk
            )
        
        return results
    
    def get_high_risk_events(self, X: pd.DataFrame, 
                            min_probability: float = 0.5) -> pd.DataFrame:
        """
        Filter and return high-risk conjunction events.
        
        Args:
            X: Features DataFrame
            min_probability: Minimum probability threshold for high risk
        
        Returns:
            DataFrame with high-risk events only
        """
        results = self.predict(X)
        high_risk_mask = (
            (results['prediction'] == 'HIGH_RISK') & 
            (results['high_risk_probability'] >= min_probability)
        )
        
        high_risk_results = results[high_risk_mask].copy()
        high_risk_results['features'] = X[high_risk_mask].to_dict('records')
        
        return high_risk_results
    
    def get_prediction_summary(self, X: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics of predictions.
        
        Args:
            X: Features DataFrame
        
        Returns:
            Dictionary with prediction summary
        """
        results = self.predict(X)
        
        summary = {
            'total_events': len(results),
            'high_risk_count': len(results[results['prediction'] == 'HIGH_RISK']),
            'false_alarm_count': len(results[results['prediction'] == 'FALSE_ALARM']),
            'uncertain_count': len(results[results['final_prediction'] == 'UNCERTAIN']),
            'average_confidence': float(results['confidence'].mean()),
            'average_high_risk_prob': float(results['high_risk_probability'].mean()),
            'high_confidence_predictions': len(results[results['confidence'] >= self.confidence_threshold]),
            'risk_level_distribution': results.apply(
                lambda row: self._categorize_risk(row['high_risk_probability']), axis=1
            ).value_counts().to_dict()
        }
        
        return summary
