"""
Feature Engineering Module

Engineers features from raw CDM data for collision risk prediction.
"""

from typing import List
import pandas as pd
import numpy as np


class FeatureEngineer:
    """Engineers features from CDM data for collision risk analysis."""
    
    def __init__(self):
        """Initialize the feature engineer."""
        pass
    
    def engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features from raw CDM data.
        
        Args:
            data: Raw CDM DataFrame
        
        Returns:
            DataFrame with engineered features
        """
        df = data.copy()
        
        # Basic features (already present)
        # - miss_distance
        # - relative_velocity
        # - time_to_tca
        
        # Collision probability (if not already present)
        if 'collision_probability' not in df.columns:
            df['collision_probability'] = self._calculate_collision_probability(df)
        
        # Combined mass
        if 'combined_mass' not in df.columns:
            df['combined_mass'] = df['object1_mass'] + df['object2_mass']
        
        # Velocity components and derived features
        if 'radial_miss_distance' not in df.columns:
            df['radial_miss_distance'] = self._calculate_radial_miss_distance(df)
        
        if 'along_track_miss_distance' not in df.columns:
            df['along_track_miss_distance'] = self._calculate_along_track_miss_distance(df)
        
        if 'cross_track_miss_distance' not in df.columns:
            df['cross_track_miss_distance'] = self._calculate_cross_track_miss_distance(df)
        
        # Kinetic energy at TCA
        df['kinetic_energy'] = 0.5 * df['combined_mass'] * (df['relative_velocity'] ** 2)
        
        # Time urgency factor (inverse of time to TCA)
        df['urgency_factor'] = 1.0 / (df['time_to_tca'] + 1e-6)
        
        # Miss distance to velocity ratio
        df['miss_distance_velocity_ratio'] = df['miss_distance'] / (df['relative_velocity'] + 1e-6)
        
        # Collision severity index
        df['collision_severity'] = (
            df['collision_probability'] * 
            df['kinetic_energy'] / 
            (df['miss_distance'] + 1e-6)
        )
        
        return df
    
    def _calculate_collision_probability(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate collision probability based on miss distance and covariance.
        
        Simplified model using miss distance and relative velocity.
        """
        # Simplified probability model
        # P_collision = exp(-miss_distance^2 / (2 * sigma^2))
        sigma = 1000.0  # 1 km uncertainty
        prob = np.exp(-(df['miss_distance'] ** 2) / (2 * sigma ** 2))
        return prob
    
    def _calculate_radial_miss_distance(self, df: pd.DataFrame) -> pd.Series:
        """Calculate radial component of miss distance."""
        # Simplified: assume 30% of miss distance is radial
        if 'radial_component' in df.columns:
            return df['radial_component']
        return df['miss_distance'] * 0.3
    
    def _calculate_along_track_miss_distance(self, df: pd.DataFrame) -> pd.Series:
        """Calculate along-track component of miss distance."""
        # Simplified: assume 50% of miss distance is along-track
        if 'along_track_component' in df.columns:
            return df['along_track_component']
        return df['miss_distance'] * 0.5
    
    def _calculate_cross_track_miss_distance(self, df: pd.DataFrame) -> pd.Series:
        """Calculate cross-track component of miss distance."""
        # Simplified: assume 20% of miss distance is cross-track
        if 'cross_track_component' in df.columns:
            return df['cross_track_component']
        return df['miss_distance'] * 0.2
    
    def get_feature_list(self) -> List[str]:
        """
        Get list of all engineered features.
        
        Returns:
            List of feature names
        """
        return [
            'miss_distance',
            'relative_velocity',
            'collision_probability',
            'time_to_tca',
            'combined_mass',
            'radial_miss_distance',
            'along_track_miss_distance',
            'cross_track_miss_distance',
            'kinetic_energy',
            'urgency_factor',
            'miss_distance_velocity_ratio',
            'collision_severity'
        ]
