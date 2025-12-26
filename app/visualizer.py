"""
Visualization Module

Creates visualizations for model results and analysis.
"""

from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc, precision_recall_curve
from pathlib import Path
import shap


class CollisionRiskVisualizer:
    """Creates visualizations for collision risk analysis."""
    
    def __init__(self, output_dir: str = "plots"):
        """
        Initialize the visualizer.
        
        Args:
            output_dir: Directory to save plots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
    
    def plot_confusion_matrix(self, y_true: pd.Series, y_pred: np.ndarray,
                             title: str = "Confusion Matrix",
                             save_name: str = "confusion_matrix.png") -> None:
        """
        Plot confusion matrix.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            title: Plot title
            save_name: Filename to save plot
        """
        cm = confusion_matrix(y_true, y_pred, labels=['FALSE_ALARM', 'HIGH_RISK'])
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['FALSE_ALARM', 'HIGH_RISK'],
                   yticklabels=['FALSE_ALARM', 'HIGH_RISK'])
        plt.title(title)
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Confusion matrix saved to {save_path}")
    
    def plot_feature_importance(self, feature_importance: Dict[str, float],
                               title: str = "Feature Importance",
                               top_k: int = 10,
                               save_name: str = "feature_importance.png") -> None:
        """
        Plot feature importance.
        
        Args:
            feature_importance: Dictionary of feature names and importance scores
            title: Plot title
            top_k: Number of top features to show
            save_name: Filename to save plot
        """
        # Sort and get top k features
        sorted_features = sorted(feature_importance.items(), 
                                key=lambda x: x[1], reverse=True)[:top_k]
        features, importance = zip(*sorted_features)
        
        plt.figure(figsize=(10, 6))
        plt.barh(range(len(features)), importance, color='steelblue')
        plt.yticks(range(len(features)), features)
        plt.xlabel('Importance Score')
        plt.title(title)
        plt.gca().invert_yaxis()
        
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Feature importance plot saved to {save_path}")
    
    def plot_roc_curve(self, y_true: pd.Series, y_pred_proba: np.ndarray,
                      title: str = "ROC Curve",
                      save_name: str = "roc_curve.png") -> None:
        """
        Plot ROC curve.
        
        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities for positive class
            title: Plot title
            save_name: Filename to save plot
        """
        # Convert labels to binary
        y_true_binary = (y_true == 'HIGH_RISK').astype(int)
        
        fpr, tpr, _ = roc_curve(y_true_binary, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2,
                label=f'ROC curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--',
                label='Random Classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(title)
        plt.legend(loc="lower right")
        
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"ROC curve saved to {save_path}")
    
    def plot_precision_recall_curve(self, y_true: pd.Series, y_pred_proba: np.ndarray,
                                   title: str = "Precision-Recall Curve",
                                   save_name: str = "precision_recall_curve.png") -> None:
        """
        Plot precision-recall curve.
        
        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities for positive class
            title: Plot title
            save_name: Filename to save plot
        """
        # Convert labels to binary
        y_true_binary = (y_true == 'HIGH_RISK').astype(int)
        
        precision, recall, _ = precision_recall_curve(y_true_binary, y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, color='blue', lw=2)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(title)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Precision-recall curve saved to {save_path}")
    
    def plot_prediction_distribution(self, predictions: pd.DataFrame,
                                    title: str = "Prediction Distribution",
                                    save_name: str = "prediction_distribution.png") -> None:
        """
        Plot distribution of predictions and confidence scores.
        
        Args:
            predictions: DataFrame with prediction results
            title: Plot title
            save_name: Filename to save plot
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot 1: Prediction counts
        pred_counts = predictions['prediction'].value_counts()
        axes[0].bar(pred_counts.index, pred_counts.values, color=['green', 'red'])
        axes[0].set_xlabel('Prediction')
        axes[0].set_ylabel('Count')
        axes[0].set_title('Prediction Counts')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Plot 2: Confidence distribution
        axes[1].hist(predictions['confidence'], bins=30, color='steelblue', edgecolor='black')
        axes[1].set_xlabel('Confidence Score')
        axes[1].set_ylabel('Frequency')
        axes[1].set_title('Confidence Distribution')
        
        plt.suptitle(title)
        
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Prediction distribution plot saved to {save_path}")
    
    def plot_shap_summary(self, shap_values: np.ndarray, X: pd.DataFrame,
                         title: str = "SHAP Summary",
                         save_name: str = "shap_summary.png") -> None:
        """
        Plot SHAP summary plot.
        
        Args:
            shap_values: SHAP values array
            X: Features DataFrame
            title: Plot title
            save_name: Filename to save plot
        """
        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values, X, show=False)
        plt.title(title)
        
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"SHAP summary plot saved to {save_path}")
    
    def plot_shap_waterfall(self, shap_values: np.ndarray, X: pd.DataFrame,
                           sample_index: int = 0,
                           expected_value: float = 0.0,
                           title: str = "SHAP Waterfall",
                           save_name: str = "shap_waterfall.png") -> None:
        """
        Plot SHAP waterfall plot for a single prediction.
        
        Args:
            shap_values: SHAP values array
            X: Features DataFrame
            sample_index: Index of sample to explain
            expected_value: Model's expected value
            title: Plot title
            save_name: Filename to save plot
        """
        plt.figure(figsize=(10, 8))
        
        # Create explanation object for waterfall plot
        explanation = shap.Explanation(
            values=shap_values[sample_index],
            base_values=expected_value,
            data=X.iloc[sample_index].values,
            feature_names=X.columns.tolist()
        )
        
        shap.plots.waterfall(explanation, show=False)
        plt.title(title)
        
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"SHAP waterfall plot saved to {save_path}")
    
    def create_dashboard(self, metrics: Dict[str, Any], 
                        y_true: pd.Series, y_pred: np.ndarray,
                        y_pred_proba: np.ndarray,
                        feature_importance: Dict[str, float]) -> None:
        """
        Create a comprehensive dashboard with multiple plots.
        
        Args:
            metrics: Dictionary with model metrics
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities
            feature_importance: Feature importance scores
        """
        print("Creating visualization dashboard...")
        
        self.plot_confusion_matrix(y_true, y_pred)
        self.plot_feature_importance(feature_importance)
        self.plot_roc_curve(y_true, y_pred_proba)
        self.plot_precision_recall_curve(y_true, y_pred_proba)
        
        print(f"Dashboard created in {self.output_dir}")
