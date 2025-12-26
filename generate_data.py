"""
Generate Sample CDM Data

Creates synthetic CDM data for demonstration and testing.
Includes features for orbital regime, maneuver history, and conjunction frequency.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple


def generate_sample_cdm_data(n_samples: int = 1000, 
                             high_risk_ratio: float = 0.3,
                             random_state: int = 42) -> pd.DataFrame:
    """
    Generate synthetic CDM (Conjunction Data Message) data.
    
    Includes all features needed for the enhanced feature engineering:
    - Basic CDM features (miss_distance, velocity, time, masses)
    - Altitude for orbital regime classification
    - Maneuver history for historical features
    - Object IDs for conjunction frequency calculation
    
    Args:
        n_samples: Number of samples to generate
        high_risk_ratio: Ratio of HIGH_RISK events
        random_state: Random seed
    
    Returns:
        DataFrame with synthetic CDM data including new features
    
    Example:
        >>> df = generate_sample_cdm_data(n_samples=100)
        >>> print(df.columns)
    """
    np.random.seed(random_state)
    
    # Calculate number of high risk and false alarm samples
    n_high_risk = int(n_samples * high_risk_ratio)
    n_false_alarm = n_samples - n_high_risk
    
    # Generate HIGH_RISK events (close encounters)
    high_risk_data = {
        'miss_distance': np.random.exponential(500, n_high_risk) + 10,  # 10-2000m
        'relative_velocity': np.random.normal(15000, 3000, n_high_risk).clip(5000, 25000),  # m/s
        'time_to_tca': np.random.exponential(24, n_high_risk) + 0.1,  # hours, convert to seconds
        'object1_mass': np.random.lognormal(6, 1.5, n_high_risk).clip(10, 5000),  # kg
        'object2_mass': np.random.lognormal(6, 1.5, n_high_risk).clip(10, 5000),  # kg
        'risk_label': ['HIGH_RISK'] * n_high_risk
    }
    
    # Generate FALSE_ALARM events (distant encounters)
    false_alarm_data = {
        'miss_distance': np.random.exponential(5000, n_false_alarm) + 1000,  # 1000-50000m
        'relative_velocity': np.random.normal(12000, 4000, n_false_alarm).clip(3000, 20000),  # m/s
        'time_to_tca': np.random.exponential(48, n_false_alarm) + 1,  # hours, convert to seconds
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
    df['time_to_tca'] = df['time_to_tca'] * 3600  # Convert hours to seconds
    df['time_to_tca'] = df['time_to_tca'].clip(360, 720000)  # 1 hour to 200 hours
    df['object1_mass'] = df['object1_mass'].clip(1, 10000)
    df['object2_mass'] = df['object2_mass'].clip(1, 10000)
    
    # Add NEW FEATURES for enhanced feature engineering
    
    # 1. Altitude for orbital regime classification (LEO, MEO, GEO)
    # HIGH_RISK events tend to be in LEO, FALSE_ALARM more distributed
    df['altitude'] = _generate_altitude(df, random_state)
    
    # 2. Maneuver history (has object maneuvered before?)
    # HIGH_RISK events more likely to have maneuver history
    df['maneuver_history'] = _generate_maneuver_history(df, random_state)
    
    # 3. Object IDs for conjunction frequency calculation
    # Some object pairs have multiple conjunctions
    df['object1_id'], df['object2_id'] = _generate_object_ids(df, random_state)
    
    # 4. Conjunction count (for specific object pairs)
    df['conjunction_count'] = _generate_conjunction_counts(df, random_state)
    
    return df


def _generate_altitude(df: pd.DataFrame, random_state: int) -> np.ndarray:
    """
    Generate altitude values based on risk label.
    
    HIGH_RISK events are more common in LEO (200-2000 km).
    FALSE_ALARM events are more distributed across LEO, MEO, GEO.
    """
    np.random.seed(random_state + 1)
    altitudes = np.zeros(len(df))
    
    for idx, row in df.iterrows():
        if row['risk_label'] == 'HIGH_RISK':
            # Mostly LEO for high risk
            if np.random.random() < 0.8:
                altitudes[idx] = np.random.uniform(300, 1500)  # LEO
            elif np.random.random() < 0.5:
                altitudes[idx] = np.random.uniform(2000, 10000)  # MEO
            else:
                altitudes[idx] = np.random.uniform(35786, 36786)  # GEO
        else:
            # More distributed for false alarms
            regime = np.random.choice(['LEO', 'MEO', 'GEO'], p=[0.5, 0.3, 0.2])
            if regime == 'LEO':
                altitudes[idx] = np.random.uniform(300, 1800)
            elif regime == 'MEO':
                altitudes[idx] = np.random.uniform(2000, 35000)
            else:
                altitudes[idx] = np.random.uniform(35786, 36786)
    
    return altitudes


def _generate_maneuver_history(df: pd.DataFrame, random_state: int) -> np.ndarray:
    """
    Generate maneuver history (number of past maneuvers).
    
    HIGH_RISK events more likely to have maneuver history (operators respond).
    """
    np.random.seed(random_state + 2)
    maneuvers = np.zeros(len(df), dtype=int)
    
    for idx, row in df.iterrows():
        if row['risk_label'] == 'HIGH_RISK':
            # 60% chance of having maneuvered before
            if np.random.random() < 0.6:
                maneuvers[idx] = np.random.randint(1, 5)
        else:
            # 20% chance of having maneuvered before
            if np.random.random() < 0.2:
                maneuvers[idx] = np.random.randint(1, 3)
    
    return maneuvers


def _generate_object_ids(df: pd.DataFrame, random_state: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate object IDs with some repeating pairs.
    
    Some object pairs have multiple conjunctions (conjunction frequency).
    """
    np.random.seed(random_state + 3)
    n = len(df)
    
    # Create a pool of object IDs
    n_objects = min(n // 3, 200)  # About 1/3 unique objects
    object_pool = [f"OBJ{i:05d}" for i in range(n_objects)]
    
    object1_ids = []
    object2_ids = []
    
    # Create some repeated pairs for HIGH_RISK (they track same objects)
    high_risk_pairs = []
    for idx, row in df.iterrows():
        if row['risk_label'] == 'HIGH_RISK' and len(high_risk_pairs) < 10:
            # Start tracking some pairs
            if np.random.random() < 0.3:
                obj1 = np.random.choice(object_pool)
                obj2 = np.random.choice(object_pool)
                if obj1 != obj2:
                    high_risk_pairs.append((obj1, obj2))
    
    # Assign IDs
    for idx, row in df.iterrows():
        if row['risk_label'] == 'HIGH_RISK' and high_risk_pairs and np.random.random() < 0.4:
            # Reuse a high-risk pair
            obj1, obj2 = high_risk_pairs[np.random.randint(0, len(high_risk_pairs))]
        else:
            # Random objects
            obj1 = np.random.choice(object_pool)
            obj2 = np.random.choice(object_pool)
            while obj1 == obj2:  # Ensure different objects
                obj2 = np.random.choice(object_pool)
        
        object1_ids.append(obj1)
        object2_ids.append(obj2)
    
    return np.array(object1_ids), np.array(object2_ids)


def _generate_conjunction_counts(df: pd.DataFrame, random_state: int) -> np.ndarray:
    """
    Generate conjunction counts based on how frequently object pairs appear.
    """
    np.random.seed(random_state + 4)
    
    # Count pair occurrences
    pair_keys = [f"{df.loc[i, 'object1_id']}_{df.loc[i, 'object2_id']}" for i in range(len(df))]
    pair_counts = pd.Series(pair_keys).value_counts().to_dict()
    
    # Assign counts
    conjunction_counts = np.array([pair_counts[key] for key in pair_keys])
    
    # Add some noise
    noise = np.random.randint(0, 3, len(df))
    conjunction_counts = conjunction_counts + noise
    
    return conjunction_counts.clip(1, 20)


def main():
    """Generate and save sample CDM data with enhanced features."""
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Generate training data
    print("Generating sample CDM data with enhanced features...")
    df = generate_sample_cdm_data(n_samples=1000, high_risk_ratio=0.3)
    
    # Save to CSV
    output_path = data_dir / "cdm_data.csv"
    df.to_csv(output_path, index=False)
    
    print(f"\nGenerated {len(df)} CDM events")
    print(f"  - HIGH_RISK: {len(df[df['risk_label'] == 'HIGH_RISK'])}")
    print(f"  - FALSE_ALARM: {len(df[df['risk_label'] == 'FALSE_ALARM'])}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"Data saved to {output_path}")
    
    # Print sample statistics
    print("\nSample Statistics:")
    print(df.describe())
    
    print("\nOrbital Regime Distribution:")
    print(df.groupby('risk_label').apply(
        lambda x: pd.cut(x['altitude'], 
                        bins=[0, 2000, 35786, 100000], 
                        labels=['LEO', 'MEO', 'GEO']).value_counts()
    ))
    
    print("\nManeuver History Distribution:")
    print(df.groupby('risk_label')['maneuver_history'].apply(
        lambda x: f"Mean: {x.mean():.2f}, Max: {x.max()}"
    ))
    
    # Generate smaller test dataset
    test_df = generate_sample_cdm_data(n_samples=100, high_risk_ratio=0.3, random_state=123)
    test_output_path = data_dir / "cdm_data_test.csv"
    test_df.to_csv(test_output_path, index=False)
    print(f"\nTest data saved to {test_output_path}")


if __name__ == "__main__":
    main()

