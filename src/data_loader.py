"""
CDM Data Loader Module

Loads Conjunction Data Message (CDM) data for satellite collision risk analysis.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from pathlib import Path


class CDMDataLoader:
    """Loads and validates CDM data for collision risk analysis."""
    
    def __init__(self, data_path: str):
        """
        Initialize the CDM data loader.
        
        Args:
            data_path: Path to the CDM data file (CSV format)
        """
        self.data_path = Path(data_path)
        self.data: Optional[pd.DataFrame] = None
    
    def load_data(self) -> pd.DataFrame:
        """
        Load CDM data from CSV file.
        
        Returns:
            DataFrame containing CDM data
        
        Raises:
            FileNotFoundError: If data file doesn't exist
            ValueError: If data format is invalid
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        try:
            self.data = pd.read_csv(self.data_path)
            self._validate_data()
            return self.data
        except Exception as e:
            raise ValueError(f"Error loading CDM data: {str(e)}")
    
    def _validate_data(self) -> None:
        """Validate that required columns exist in the data."""
        required_columns = [
            'miss_distance', 'relative_velocity', 'time_to_tca',
            'object1_mass', 'object2_mass', 'risk_label'
        ]
        
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of the loaded data.
        
        Returns:
            Dictionary containing data summary
        """
        if self.data is None:
            return {}
        
        return {
            'total_records': len(self.data),
            'high_risk_count': len(self.data[self.data['risk_label'] == 'HIGH_RISK']),
            'false_alarm_count': len(self.data[self.data['risk_label'] == 'FALSE_ALARM']),
            'columns': list(self.data.columns),
            'date_range': {
                'min': self.data['time_to_tca'].min() if 'time_to_tca' in self.data else None,
                'max': self.data['time_to_tca'].max() if 'time_to_tca' in self.data else None
            }
        }
