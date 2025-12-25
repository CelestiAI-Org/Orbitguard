"""
Feature Engineering Module

Engineers features from raw CDM data for collision risk prediction.
Includes orbital regime classification, maneuver history, and conjunction frequency.
"""

from typing import List, Optional
import logging
import pandas as pd
import numpy as np

from app.config import FEATURE_CONFIG
from app.utils import logger


class FeatureEngineer:
    """
    Engineers features from CDM data for collision risk analysis.
    
    Features include:
    - Core CDM features (miss_distance, relative_velocity, etc.)
    - Geometric features (radial, along-track, cross-track components)
    - Physics-based features (kinetic_energy, collision_severity)
    - Orbital classification (LEO, MEO, GEO)
    - Historical features (maneuver_flag, conjunction_frequency)
    
    Example:
        >>> engineer = FeatureEngineer()
        >>> df_with_features = engineer.engineer_features(raw_cdm_data)
        >>> feature_names = engineer.get_feature_list()
    """
    
    def __init__(self, log_level: str = "INFO"):
        """
        Initialize the feature engineer.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.logger = logger
        self.logger.setLevel(getattr(logging, log_level.upper()))
        self.orbital_regimes = FEATURE_CONFIG["orbital_regimes"]
    
    def engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer all features from raw CDM data.
        
        Args:
            data: Raw CDM DataFrame with columns:
                - miss_distance, relative_velocity, time_to_tca
                - object1_mass, object2_mass
                - Optional: altitude, maneuver_history, conjunction_count
        
        Returns:
            DataFrame with engineered features
        
        Example:
            >>> df_features = engineer.engineer_features(df_raw)
            >>> print(df_features.columns)
        """
        self.logger.info(f"Engineering features for {len(data)} CDM records")
        df = data.copy()
        
        # Core features validation
        self._validate_core_features(df)
        
        # 1. Collision probability (if not already present)
        if 'collision_probability' not in df.columns:
            self.logger.debug("Calculating collision probability")
            df['collision_probability'] = self._calculate_collision_probability(df)
        
        # 2. Object size features (RCS - radar cross section)
        df = self._engineer_object_size_features(df)
        
        # 3. Combined mass
        if 'combined_mass' not in df.columns:
            df['combined_mass'] = df['object1_mass'] + df['object2_mass']
        
        # 4. Geometric miss distance components
        df = self._engineer_geometric_features(df)
        
        # 5. Physics-based features
        df = self._engineer_physics_features(df)
        
        # 6. Temporal features
        df = self._engineer_temporal_features(df)
        
        # 7. Orbital regime classification
        df = self._engineer_orbital_regime(df)
        
        # 8. Historical features
        df = self._engineer_historical_features(df)
        
        # 9. Interaction features
        df = self._engineer_interaction_features(df)
        
        self.logger.info(f"Feature engineering complete. Generated {len(self.get_feature_list())} features")
        
        return df
    
    def _validate_core_features(self, df: pd.DataFrame) -> None:
        """Validate that core features exist in the dataframe."""
        required = ['miss_distance', 'relative_velocity', 'time_to_tca', 
                   'object1_mass', 'object2_mass']
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    
    def _engineer_object_size_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer object size features (RCS - radar cross section).
        
        If RCS not available, estimate from mass using empirical relationship.
        """
        # Object 1 size
        if 'object1_size' not in df.columns:
            if 'object1_rcs' in df.columns:
                df['object1_size'] = df['object1_rcs']
            else:
                # Estimate RCS from mass (rough approximation)
                # RCS ≈ (mass/1000)^(2/3) square meters
                df['object1_size'] = np.power(df['object1_mass'] / 1000, 2/3)
                self.logger.debug("Estimated object1_size from mass")
        
        # Object 2 size
        if 'object2_size' not in df.columns:
            if 'object2_rcs' in df.columns:
                df['object2_size'] = df['object2_rcs']
            else:
                df['object2_size'] = np.power(df['object2_mass'] / 1000, 2/3)
                self.logger.debug("Estimated object2_size from mass")
        
        # Combined size
        df['combined_size'] = df['object1_size'] + df['object2_size']
        
        return df
    
    def _engineer_geometric_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer geometric miss distance components."""
        # Radial component
        if 'radial_miss_distance' not in df.columns:
            if 'radial_component' in df.columns:
                df['radial_miss_distance'] = df['radial_component']
            else:
                # Simplified: assume 30% of miss distance is radial
                df['radial_miss_distance'] = df['miss_distance'] * 0.3
        
        # Along-track component
        if 'along_track_miss_distance' not in df.columns:
            if 'along_track_component' in df.columns:
                df['along_track_miss_distance'] = df['along_track_component']
            else:
                # Simplified: assume 50% of miss distance is along-track
                df['along_track_miss_distance'] = df['miss_distance'] * 0.5
        
        # Cross-track component
        if 'cross_track_miss_distance' not in df.columns:
            if 'cross_track_component' in df.columns:
                df['cross_track_miss_distance'] = df['cross_track_component']
            else:
                # Simplified: assume 20% of miss distance is cross-track
                df['cross_track_miss_distance'] = df['miss_distance'] * 0.2
        
        return df
    
    def _engineer_physics_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer physics-based features."""
        # Kinetic energy at TCA
        df['kinetic_energy'] = 0.5 * df['combined_mass'] * (df['relative_velocity'] ** 2)
        
        # Miss distance to velocity ratio (seconds to impact if on collision course)
        df['miss_distance_velocity_ratio'] = df['miss_distance'] / (df['relative_velocity'] + 1e-6)
        
        # Collision severity index (combines probability, energy, and proximity)
        df['collision_severity'] = (
            df['collision_probability'] * 
            df['kinetic_energy'] / 
            (df['miss_distance'] + 1e-6)
        )
        
        # Momentum factor
        df['momentum'] = df['combined_mass'] * df['relative_velocity']
        
        return df
    
    def _engineer_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer temporal features."""
        # Time urgency factor (inverse of time to TCA)
        df['urgency_factor'] = 1.0 / (df['time_to_tca'] + 1e-6)
        
        # Time to TCA in hours (more interpretable)
        df['time_to_tca_hours'] = df['time_to_tca'] / 3600
        
        return df
    
    def _engineer_orbital_regime(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classify objects into orbital regimes (LEO, MEO, GEO).
        
        Uses altitude if available, otherwise estimates from orbital period or defaults.
        """
        if 'orbital_regime' not in df.columns:
            if 'altitude' in df.columns:
                # Classify based on altitude
                df['orbital_regime'] = df['altitude'].apply(self._classify_orbit_by_altitude)
                self.logger.debug("Classified orbital regime from altitude")
            elif 'orbital_period' in df.columns:
                # Estimate from orbital period
                df['orbital_regime'] = df['orbital_period'].apply(self._classify_orbit_by_period)
                self.logger.debug("Classified orbital regime from orbital period")
            else:
                # Default to LEO (most conjunctions occur in LEO)
                df['orbital_regime'] = 'LEO'
                self.logger.warning("No altitude/period data; defaulting all to LEO")
        
        # One-hot encode orbital regime
        regime_dummies = pd.get_dummies(df['orbital_regime'], prefix='regime')
        for col in ['regime_LEO', 'regime_MEO', 'regime_GEO']:
            if col not in regime_dummies.columns:
                regime_dummies[col] = 0
        df = pd.concat([df, regime_dummies], axis=1)
        
        return df
    
    def _classify_orbit_by_altitude(self, altitude: float) -> str:
        """Classify orbit by altitude (km)."""
        for regime, (min_alt, max_alt) in self.orbital_regimes.items():
            if min_alt <= altitude < max_alt:
                return regime
        return 'LEO'  # Default
    
    def _classify_orbit_by_period(self, period: float) -> str:
        """
        Classify orbit by orbital period (minutes).
        
        LEO: ~90 min, MEO: 2-12 hours, GEO: ~24 hours
        """
        if period < 120:  # < 2 hours
            return 'LEO'
        elif period < 720:  # < 12 hours
            return 'MEO'
        else:
            return 'GEO'
    
    def _engineer_historical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer historical features (maneuver history, conjunction frequency).
        """
        # Historical maneuver flag
        if 'historical_maneuver_flag' not in df.columns:
            if 'maneuver_history' in df.columns:
                # If maneuver_history exists, convert to binary flag
                df['historical_maneuver_flag'] = (df['maneuver_history'] > 0).astype(int)
            else:
                # Default to 0 (no maneuver history)
                df['historical_maneuver_flag'] = 0
                self.logger.debug("No maneuver history data; defaulting to 0")
        
        # Conjunction frequency (how often this pair has close approaches)
        if 'conjunction_frequency' not in df.columns:
            if 'conjunction_count' in df.columns:
                # Use existing count
                df['conjunction_frequency'] = df['conjunction_count']
            elif 'object1_id' in df.columns and 'object2_id' in df.columns:
                # Calculate from object pair occurrences
                pair_key = df['object1_id'].astype(str) + '_' + df['object2_id'].astype(str)
                pair_counts = pair_key.value_counts()
                df['conjunction_frequency'] = pair_key.map(pair_counts)
                self.logger.debug("Calculated conjunction frequency from object pairs")
            else:
                # Default to 1 (first conjunction)
                df['conjunction_frequency'] = 1
                self.logger.debug("No conjunction data; defaulting to 1")
        
        return df
    
    def _engineer_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer interaction features between variables."""
        # Size-distance interaction
        df['size_distance_ratio'] = df['combined_size'] / (df['miss_distance'] + 1e-6)
        
        # Probability-velocity interaction
        df['prob_velocity_product'] = df['collision_probability'] * df['relative_velocity']
        
        # Mass-velocity interaction (momentum-based)
        df['mass_velocity_ratio'] = df['combined_mass'] / (df['relative_velocity'] + 1e-6)
        
        return df
    
    def _calculate_collision_probability(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate collision probability based on miss distance.
        
        Uses exponential decay model: P = exp(-d²/(2σ²))
        where d is miss distance and σ is uncertainty.
        
        Args:
            df: DataFrame with miss_distance column
        
        Returns:
            Series of collision probabilities
        """
        sigma = 1000.0  # 1 km uncertainty
        prob = np.exp(-(df['miss_distance'] ** 2) / (2 * sigma ** 2))
        return prob
    
    def get_feature_list(self) -> List[str]:
        """
        Get list of all engineered features for model training.
        
        Returns:
            List of feature names
        
        Example:
            >>> features = engineer.get_feature_list()
            >>> X = df[features]
        """
        return [
            # Core features
            'miss_distance',
            'relative_velocity',
            'collision_probability',
            'time_to_tca',
            
            # Object features
            'object1_mass',
            'object2_mass',
            'object1_size',
            'object2_size',
            'combined_mass',
            'combined_size',
            
            # Geometric features
            'radial_miss_distance',
            'along_track_miss_distance',
            'cross_track_miss_distance',
            
            # Physics features
            'kinetic_energy',
            'miss_distance_velocity_ratio',
            'collision_severity',
            'momentum',
            
            # Temporal features
            'urgency_factor',
            'time_to_tca_hours',
            
            # Orbital regime (one-hot encoded)
            'regime_LEO',
            'regime_MEO',
            'regime_GEO',
            
            # Historical features
            'historical_maneuver_flag',
            'conjunction_frequency',
            
            # Interaction features
            'size_distance_ratio',
            'prob_velocity_product',
            'mass_velocity_ratio',
        ]


# Unit tests for feature engineering
def test_feature_engineering():
    """
    Unit test for feature engineering functions.
    
    Example:
        >>> test_feature_engineering()
        All tests passed!
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data
    sample_data = pd.DataFrame({
        'miss_distance': [500, 1000, 5000],
        'relative_velocity': [15000, 12000, 10000],
        'time_to_tca': [3600, 7200, 18000],
        'object1_mass': [1000, 500, 2000],
        'object2_mass': [800, 300, 1500],
        'altitude': [400, 20000, 36000],
    })
    
    engineer = FeatureEngineer()
    result = engineer.engineer_features(sample_data)
    
    # Check that all expected features are present
    expected_features = engineer.get_feature_list()
    for feature in expected_features:
        assert feature in result.columns, f"Missing feature: {feature}"
    
    # Check calculations
    assert result['combined_mass'].iloc[0] == 1800
    assert result['kinetic_energy'].iloc[0] > 0
    assert result['orbital_regime'].iloc[0] == 'LEO'
    assert result['orbital_regime'].iloc[1] == 'MEO'
    assert result['orbital_regime'].iloc[2] == 'GEO'
    
    print("✓ All feature engineering tests passed!")
    return True


if __name__ == "__main__":
    test_feature_engineering()

