"""
Data Preprocessor Module

Handles data cleaning, normalization, and preparation for model training.
"""

from typing import Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


class DataPreprocessor:
    """Preprocesses CDM data for machine learning."""
    
    def __init__(self, random_state: int = 42):
        """
        Initialize the preprocessor.
        
        Args:
            random_state: Random seed for reproducibility
        """
        self.random_state = random_state
        self.scaler: Optional[StandardScaler] = None
        self.feature_columns: Optional[list] = None
    
    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the data by handling missing values and outliers.
        
        Args:
            data: Raw CDM data
        
        Returns:
            Cleaned DataFrame
        """
        df = data.copy()
        
        # Remove rows with missing values
        df = df.dropna()
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle outliers using IQR method for key features
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in ['risk_label']:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 3 * IQR
                upper_bound = Q3 + 3 * IQR
                df[col] = df[col].clip(lower_bound, upper_bound)
        
        return df
    
    def normalize_features(self, data: pd.DataFrame, 
                          feature_columns: list,
                          fit: bool = True) -> pd.DataFrame:
        """
        Normalize features using StandardScaler.
        
        Args:
            data: DataFrame with features
            feature_columns: List of columns to normalize
            fit: Whether to fit the scaler (True for training, False for inference)
        
        Returns:
            DataFrame with normalized features
        """
        df = data.copy()
        
        if fit:
            self.scaler = StandardScaler()
            self.feature_columns = feature_columns
            df[feature_columns] = self.scaler.fit_transform(df[feature_columns])
        else:
            if self.scaler is None:
                raise ValueError("Scaler not fitted. Call with fit=True first.")
            df[feature_columns] = self.scaler.transform(df[feature_columns])
        
        return df
    
    def split_data(self, data: pd.DataFrame, 
                   feature_columns: list,
                   target_column: str = 'risk_label',
                   test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame, 
                                                      pd.Series, pd.Series]:
        """
        Split data into training and testing sets.
        
        Args:
            data: Preprocessed DataFrame
            feature_columns: List of feature column names
            target_column: Name of the target column
            test_size: Fraction of data to use for testing
        
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        X = data[feature_columns]
        y = data[target_column]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state, stratify=y
        )
        
        return X_train, X_test, y_train, y_test
    
    def prepare_data(self, data: pd.DataFrame,
                    feature_columns: list,
                    target_column: str = 'risk_label',
                    test_size: float = 0.2,
                    fit: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, 
                                                pd.Series, pd.Series]:
        """
        Complete data preparation pipeline.
        
        Args:
            data: Raw CDM data
            feature_columns: List of feature column names
            target_column: Name of the target column
            test_size: Fraction of data to use for testing
            fit: Whether to fit the scaler
        
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Clean data
        cleaned_data = self.clean_data(data)
        
        # Normalize features
        normalized_data = self.normalize_features(
            cleaned_data, feature_columns, fit=fit
        )
        
        # Split data
        if fit:
            return self.split_data(
                normalized_data, feature_columns, target_column, test_size
            )
        else:
            # For inference, return features and labels separately
            X = normalized_data[feature_columns]
            y = normalized_data[target_column] if target_column in normalized_data else None
            return X, None, y, None
