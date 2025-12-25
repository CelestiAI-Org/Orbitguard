"""
Generate Sample CDM Data

Creates synthetic CDM data for demonstration and testing.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def generate_sample_cdm_data(n_samples: int = 1000, 
                             high_risk_ratio: float = 0.3,
                             random_state: int = 42) -> pd.DataFrame:
    """
    Generate synthetic CDM (Conjunction Data Message) data.
    
    Args:
        n_samples: Number of samples to generate
        high_risk_ratio: Ratio of HIGH_RISK events
        random_state: Random seed
    
    Returns:
        DataFrame with synthetic CDM data
    """
    np.random.seed(random_state)
    
    # Calculate number of high risk and false alarm samples
    n_high_risk = int(n_samples * high_risk_ratio)
    n_false_alarm = n_samples - n_high_risk
    
    # Generate HIGH_RISK events (close encounters)
    high_risk_data = {
        'miss_distance': np.random.exponential(500, n_high_risk) + 10,  # 10-2000m
        'relative_velocity': np.random.normal(15000, 3000, n_high_risk).clip(5000, 25000),  # m/s
        'time_to_tca': np.random.exponential(24, n_high_risk) + 0.1,  # hours
        'object1_mass': np.random.lognormal(6, 1.5, n_high_risk).clip(10, 5000),  # kg
        'object2_mass': np.random.lognormal(6, 1.5, n_high_risk).clip(10, 5000),  # kg
        'risk_label': ['HIGH_RISK'] * n_high_risk
    }
    
    # Generate FALSE_ALARM events (distant encounters)
    false_alarm_data = {
        'miss_distance': np.random.exponential(5000, n_false_alarm) + 1000,  # 1000-50000m
        'relative_velocity': np.random.normal(12000, 4000, n_false_alarm).clip(3000, 20000),  # m/s
        'time_to_tca': np.random.exponential(48, n_false_alarm) + 1,  # hours
        'object1_mass': np.random.lognormal(5.5, 1.5, n_false_alarm).clip(5, 3000),  # kg
        'object2_mass': np.random.lognormal(5.5, 1.5, n_false_alarm).clip(5, 3000),  # kg
        'risk_label': ['FALSE_ALARM'] * n_false_alarm
    }
    
    # Combine datasets
    high_risk_df = pd.DataFrame(high_risk_data)
    false_alarm_df = pd.DataFrame(false_alarm_data)
    
    df = pd.concat([high_risk_df, false_alarm_df], ignore_index=True)
    
    # Shuffle the data
    df = df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    
    # Add some noise to make it more realistic
    df['miss_distance'] = df['miss_distance'].clip(10, 50000)
    df['relative_velocity'] = df['relative_velocity'].clip(1000, 30000)
    df['time_to_tca'] = df['time_to_tca'].clip(0.1, 200)
    df['object1_mass'] = df['object1_mass'].clip(1, 10000)
    df['object2_mass'] = df['object2_mass'].clip(1, 10000)
    
    return df


def main():
    """Generate and save sample CDM data."""
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Generate training data
    print("Generating sample CDM data...")
    df = generate_sample_cdm_data(n_samples=1000, high_risk_ratio=0.3)
    
    # Save to CSV
    output_path = data_dir / "cdm_data.csv"
    df.to_csv(output_path, index=False)
    
    print(f"Generated {len(df)} CDM events")
    print(f"  - HIGH_RISK: {len(df[df['risk_label'] == 'HIGH_RISK'])}")
    print(f"  - FALSE_ALARM: {len(df[df['risk_label'] == 'FALSE_ALARM'])}")
    print(f"Data saved to {output_path}")
    
    # Print sample statistics
    print("\nSample Statistics:")
    print(df.describe())
    
    # Generate smaller test dataset
    test_df = generate_sample_cdm_data(n_samples=100, high_risk_ratio=0.3, random_state=123)
    test_output_path = data_dir / "cdm_data_test.csv"
    test_df.to_csv(test_output_path, index=False)
    print(f"\nTest data saved to {test_output_path}")


if __name__ == "__main__":
    main()
