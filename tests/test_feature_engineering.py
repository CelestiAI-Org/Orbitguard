"""
Unit Tests for Feature Engineering

Tests the feature engineering functions to ensure they work correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from app.feature_engineering import FeatureEngineer


def test_feature_engineering_basic():
    """Test basic feature engineering functionality."""
    print("=" * 60)
    print("TEST: Basic Feature Engineering")
    print("=" * 60)
    
    # Create sample data with all required columns
    sample_data = pd.DataFrame({
        'miss_distance': [500, 1000, 5000],
        'relative_velocity': [15000, 12000, 10000],
        'time_to_tca': [3600, 7200, 18000],  # seconds
        'object1_mass': [1000, 500, 2000],
        'object2_mass': [800, 300, 1500],
    })
    
    engineer = FeatureEngineer()
    result = engineer.engineer_features(sample_data)
    
    # Check that basic features are present
    assert 'combined_mass' in result.columns, "Missing combined_mass"
    assert result['combined_mass'].iloc[0] == 1800, "combined_mass calculation incorrect"
    
    assert 'kinetic_energy' in result.columns, "Missing kinetic_energy"
    assert result['kinetic_energy'].iloc[0] > 0, "kinetic_energy should be positive"
    
    print("✓ Basic feature engineering passed")
    return True


def test_orbital_regime_classification():
    """Test orbital regime classification."""
    print("\n" + "=" * 60)
    print("TEST: Orbital Regime Classification")
    print("=" * 60)
    
    sample_data = pd.DataFrame({
        'miss_distance': [500, 1000, 5000],
        'relative_velocity': [15000, 12000, 10000],
        'time_to_tca': [3600, 7200, 18000],
        'object1_mass': [1000, 500, 2000],
        'object2_mass': [800, 300, 1500],
        'altitude': [400, 20000, 36000],  # LEO, MEO, GEO
    })
    
    engineer = FeatureEngineer()
    result = engineer.engineer_features(sample_data)
    
    # Check orbital regime classification
    assert 'orbital_regime' in result.columns, "Missing orbital_regime"
    assert result['orbital_regime'].iloc[0] == 'LEO', "Altitude 400 should be LEO"
    assert result['orbital_regime'].iloc[1] == 'MEO', "Altitude 20000 should be MEO"
    assert result['orbital_regime'].iloc[2] == 'GEO', "Altitude 36000 should be GEO"
    
    # Check one-hot encoding
    assert 'regime_LEO' in result.columns, "Missing regime_LEO"
    assert 'regime_MEO' in result.columns, "Missing regime_MEO"
    assert 'regime_GEO' in result.columns, "Missing regime_GEO"
    
    assert result['regime_LEO'].iloc[0] == 1, "LEO flag incorrect"
    assert result['regime_MEO'].iloc[1] == 1, "MEO flag incorrect"
    assert result['regime_GEO'].iloc[2] == 1, "GEO flag incorrect"
    
    print("✓ Orbital regime classification passed")
    return True


def test_historical_features():
    """Test historical feature engineering."""
    print("\n" + "=" * 60)
    print("TEST: Historical Features")
    print("=" * 60)
    
    sample_data = pd.DataFrame({
        'miss_distance': [500, 1000, 5000],
        'relative_velocity': [15000, 12000, 10000],
        'time_to_tca': [3600, 7200, 18000],
        'object1_mass': [1000, 500, 2000],
        'object2_mass': [800, 300, 1500],
        'maneuver_history': [3, 0, 1],
        'object1_id': ['OBJ001', 'OBJ002', 'OBJ001'],
        'object2_id': ['OBJ003', 'OBJ004', 'OBJ003'],
    })
    
    engineer = FeatureEngineer()
    result = engineer.engineer_features(sample_data)
    
    # Check historical features
    assert 'historical_maneuver_flag' in result.columns, "Missing historical_maneuver_flag"
    assert result['historical_maneuver_flag'].iloc[0] == 1, "Should have maneuver flag for history > 0"
    assert result['historical_maneuver_flag'].iloc[1] == 0, "Should not have maneuver flag for history = 0"
    
    assert 'conjunction_frequency' in result.columns, "Missing conjunction_frequency"
    assert result['conjunction_frequency'].iloc[0] > 0, "Conjunction frequency should be positive"
    
    print("✓ Historical features passed")
    return True


def test_physics_features():
    """Test physics-based features."""
    print("\n" + "=" * 60)
    print("TEST: Physics Features")
    print("=" * 60)
    
    sample_data = pd.DataFrame({
        'miss_distance': [500, 1000, 5000],
        'relative_velocity': [15000, 12000, 10000],
        'time_to_tca': [3600, 7200, 18000],
        'object1_mass': [1000, 500, 2000],
        'object2_mass': [800, 300, 1500],
    })
    
    engineer = FeatureEngineer()
    result = engineer.engineer_features(sample_data)
    
    # Check physics features
    assert 'kinetic_energy' in result.columns, "Missing kinetic_energy"
    assert 'collision_severity' in result.columns, "Missing collision_severity"
    assert 'momentum' in result.columns, "Missing momentum"
    
    # Verify calculations
    expected_ke = 0.5 * 1800 * (15000 ** 2)
    assert abs(result['kinetic_energy'].iloc[0] - expected_ke) < 1e6, "Kinetic energy calculation incorrect"
    
    print("✓ Physics features passed")
    return True


def test_interaction_features():
    """Test interaction features."""
    print("\n" + "=" * 60)
    print("TEST: Interaction Features")
    print("=" * 60)
    
    sample_data = pd.DataFrame({
        'miss_distance': [500, 1000, 5000],
        'relative_velocity': [15000, 12000, 10000],
        'time_to_tca': [3600, 7200, 18000],
        'object1_mass': [1000, 500, 2000],
        'object2_mass': [800, 300, 1500],
    })
    
    engineer = FeatureEngineer()
    result = engineer.engineer_features(sample_data)
    
    # Check interaction features
    assert 'size_distance_ratio' in result.columns, "Missing size_distance_ratio"
    assert 'prob_velocity_product' in result.columns, "Missing prob_velocity_product"
    assert 'mass_velocity_ratio' in result.columns, "Missing mass_velocity_ratio"
    
    print("✓ Interaction features passed")
    return True


def test_feature_list_completeness():
    """Test that all features are returned in the feature list."""
    print("\n" + "=" * 60)
    print("TEST: Feature List Completeness")
    print("=" * 60)
    
    engineer = FeatureEngineer()
    feature_list = engineer.get_feature_list()
    
    # Expected number of features
    assert len(feature_list) == 29, f"Expected 29 features, got {len(feature_list)}"
    
    # Check key feature categories
    required_features = [
        'miss_distance', 'relative_velocity', 'collision_probability',
        'kinetic_energy', 'collision_severity',
        'regime_LEO', 'regime_MEO', 'regime_GEO',
        'historical_maneuver_flag', 'conjunction_frequency'
    ]
    
    for feature in required_features:
        assert feature in feature_list, f"Missing required feature: {feature}"
    
    print(f"✓ Feature list completeness passed ({len(feature_list)} features)")
    return True


def test_missing_data_handling():
    """Test handling of missing optional data."""
    print("\n" + "=" * 60)
    print("TEST: Missing Data Handling")
    print("=" * 60)
    
    # Data without optional columns
    sample_data = pd.DataFrame({
        'miss_distance': [500, 1000],
        'relative_velocity': [15000, 12000],
        'time_to_tca': [3600, 7200],
        'object1_mass': [1000, 500],
        'object2_mass': [800, 300],
        # No altitude, maneuver_history, or object IDs
    })
    
    engineer = FeatureEngineer()
    result = engineer.engineer_features(sample_data)
    
    # Should still work with defaults
    assert 'orbital_regime' in result.columns, "Should handle missing altitude"
    assert 'historical_maneuver_flag' in result.columns, "Should handle missing maneuver history"
    assert 'conjunction_frequency' in result.columns, "Should handle missing conjunction data"
    
    print("✓ Missing data handling passed")
    return True


def run_all_tests():
    """Run all feature engineering tests."""
    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING UNIT TESTS")
    print("=" * 60 + "\n")
    
    tests = [
        test_feature_engineering_basic,
        test_orbital_regime_classification,
        test_historical_features,
        test_physics_features,
        test_interaction_features,
        test_feature_list_completeness,
        test_missing_data_handling,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed: {test.__name__}")
            print(f"  Error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
