"""
Utils Module

Logging, validation, and error handling utilities.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

from app.config import LOGGING_CONFIG, VALIDATION_CONFIG


def setup_logging(log_file: Optional[Path] = None, log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        log_file: Path to log file (optional)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger
    
    Example:
        >>> logger = setup_logging()
        >>> logger.info("Starting application")
    """
    if log_file is None:
        log_file = LOGGING_CONFIG["log_file"]
    
    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("collision_risk")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_formatter = logging.Formatter(
        LOGGING_CONFIG["log_format"],
        datefmt=LOGGING_CONFIG["date_format"]
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(
        "%(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


def validate_cdm_data(data: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate CDM data format and values.
    
    Args:
        data: CDM DataFrame to validate
    
    Returns:
        Tuple of (is_valid, error_messages)
    
    Example:
        >>> is_valid, errors = validate_cdm_data(df)
        >>> if not is_valid:
        >>>     for error in errors:
        >>>         print(error)
    """
    errors = []
    
    # Check required columns
    required_columns = VALIDATION_CONFIG["required_columns"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Check for empty dataframe
    if len(data) == 0:
        errors.append("DataFrame is empty")
        return False, errors
    
    # Check value ranges
    value_ranges = VALIDATION_CONFIG["value_ranges"]
    for column, (min_val, max_val) in value_ranges.items():
        if column in data.columns:
            out_of_range = (data[column] < min_val) | (data[column] > max_val)
            if out_of_range.any():
                count = out_of_range.sum()
                errors.append(
                    f"Column '{column}' has {count} values outside valid range "
                    f"[{min_val}, {max_val}]"
                )
    
    # Check for missing values
    null_counts = data[required_columns].isnull().sum()
    columns_with_nulls = null_counts[null_counts > 0]
    if not columns_with_nulls.empty:
        for col, count in columns_with_nulls.items():
            errors.append(f"Column '{col}' has {count} missing values")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def handle_missing_values(
    data: pd.DataFrame,
    strategy: str = "median",
    logger: Optional[logging.Logger] = None
) -> pd.DataFrame:
    """
    Handle missing values in CDM data.
    
    Args:
        data: DataFrame with potential missing values
        strategy: Imputation strategy ('median', 'mean', 'drop')
        logger: Logger instance (optional)
    
    Returns:
        DataFrame with missing values handled
    
    Example:
        >>> df_clean = handle_missing_values(df, strategy='median')
    """
    df = data.copy()
    
    if logger:
        logger.info(f"Handling missing values with strategy: {strategy}")
    
    # Count missing values
    missing_before = df.isnull().sum().sum()
    
    if strategy == "drop":
        df = df.dropna()
    elif strategy == "median":
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if df[col].isnull().any():
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
                if logger:
                    logger.debug(f"Filled {col} missing values with median: {median_val}")
    elif strategy == "mean":
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if df[col].isnull().any():
                mean_val = df[col].mean()
                df[col].fillna(mean_val, inplace=True)
                if logger:
                    logger.debug(f"Filled {col} missing values with mean: {mean_val}")
    
    missing_after = df.isnull().sum().sum()
    
    if logger:
        logger.info(
            f"Missing values: {missing_before} before, {missing_after} after "
            f"({missing_before - missing_after} handled)"
        )
    
    return df


def validate_model_input(features: pd.DataFrame, feature_names: List[str]) -> Tuple[bool, str]:
    """
    Validate features before model prediction.
    
    Args:
        features: Feature DataFrame
        feature_names: Expected feature names
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Example:
        >>> is_valid, error = validate_model_input(X, model_features)
        >>> if not is_valid:
        >>>     raise ValueError(error)
    """
    # Check if all required features are present
    missing_features = set(feature_names) - set(features.columns)
    if missing_features:
        return False, f"Missing features: {', '.join(missing_features)}"
    
    # Check for NaN values
    if features[feature_names].isnull().any().any():
        null_cols = features[feature_names].columns[features[feature_names].isnull().any()].tolist()
        return False, f"Features contain NaN values in columns: {', '.join(null_cols)}"
    
    # Check for infinite values
    if np.isinf(features[feature_names].select_dtypes(include=[np.number]).values).any():
        return False, "Features contain infinite values"
    
    return True, ""


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_pred_proba: np.ndarray) -> Dict[str, float]:
    """
    Calculate comprehensive model metrics.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_pred_proba: Prediction probabilities
    
    Returns:
        Dictionary of metric names and values
    
    Example:
        >>> metrics = calculate_metrics(y_test, predictions, probabilities)
        >>> print(f"Accuracy: {metrics['accuracy']:.2%}")
    """
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score,
        roc_auc_score, confusion_matrix
    )
    
    # Convert string labels to binary if needed
    if y_true.dtype == object:
        y_true_binary = (y_true == 'HIGH_RISK').astype(int)
        y_pred_binary = (y_pred == 'HIGH_RISK').astype(int)
    else:
        y_true_binary = y_true
        y_pred_binary = y_pred
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_true_binary, y_pred_binary),
        'precision': precision_score(y_true_binary, y_pred_binary, zero_division=0),
        'recall': recall_score(y_true_binary, y_pred_binary, zero_division=0),
        'f1_score': f1_score(y_true_binary, y_pred_binary, zero_division=0),
    }
    
    # ROC AUC (requires probabilities)
    try:
        if len(np.unique(y_true_binary)) > 1:  # Need both classes for ROC AUC
            metrics['roc_auc'] = roc_auc_score(y_true_binary, y_pred_proba)
    except Exception:
        metrics['roc_auc'] = 0.0
    
    # Confusion matrix
    cm = confusion_matrix(y_true_binary, y_pred_binary)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        metrics['true_negatives'] = int(tn)
        metrics['false_positives'] = int(fp)
        metrics['false_negatives'] = int(fn)
        metrics['true_positives'] = int(tp)
        
        # False positive rate
        metrics['false_positive_rate'] = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        
        # Calculate false positive reduction
        # Baseline: all samples predicted as positive
        baseline_fp = tn + fp
        actual_fp = fp
        metrics['fp_reduction'] = (baseline_fp - actual_fp) / baseline_fp if baseline_fp > 0 else 0.0
    
    return metrics


def format_error_message(error: Exception, context: str = "") -> str:
    """
    Format error message for logging.
    
    Args:
        error: Exception object
        context: Additional context about where error occurred
    
    Returns:
        Formatted error message
    
    Example:
        >>> try:
        >>>     risky_operation()
        >>> except Exception as e:
        >>>     logger.error(format_error_message(e, "Data loading"))
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    if context:
        return f"{context} - {error_type}: {error_msg}"
    else:
        return f"{error_type}: {error_msg}"


def check_class_imbalance(y: pd.Series, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    Check and report class imbalance in labels.
    
    Args:
        y: Label series
        logger: Logger instance (optional)
    
    Returns:
        Dictionary with class distribution statistics
    
    Example:
        >>> imbalance_info = check_class_imbalance(y_train, logger)
        >>> if imbalance_info['imbalance_ratio'] > 3:
        >>>     print("Significant class imbalance detected!")
    """
    value_counts = y.value_counts()
    total = len(y)
    
    distribution = {
        'total_samples': total,
        'class_counts': value_counts.to_dict(),
        'class_percentages': (value_counts / total * 100).to_dict(),
    }
    
    # Calculate imbalance ratio
    if len(value_counts) == 2:
        majority_count = value_counts.max()
        minority_count = value_counts.min()
        distribution['imbalance_ratio'] = majority_count / minority_count
    
    if logger:
        logger.info("Class distribution:")
        for class_label, count in value_counts.items():
            percentage = count / total * 100
            logger.info(f"  {class_label}: {count} ({percentage:.1f}%)")
        
        if 'imbalance_ratio' in distribution:
            logger.info(f"  Imbalance ratio: {distribution['imbalance_ratio']:.2f}:1")
    
    return distribution


# Create default logger
logger = setup_logging()


if __name__ == "__main__":
    # Test logging
    test_logger = setup_logging()
    test_logger.info("Logging system initialized")
    test_logger.debug("This is a debug message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
