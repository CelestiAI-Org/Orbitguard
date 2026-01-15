from app.pipeline.datasource import JsonFileDataSource
from app.pipeline.preprocessor import TimeSeriesPreprocessor
import numpy as np

def test_pipeline():
    print("Testing Data Pipeline...")
    
    # 1. Load Data
    source = JsonFileDataSource("data/download.json")
    try:
        data = source.fetch_data()
        print(f"Loaded {len(data)} records from JSON.")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # 2. Preprocess
    preprocessor = TimeSeriesPreprocessor(sequence_length=5, log_level="DEBUG")
    sequences, targets = preprocessor.process(data)
    
    print(f"Generated {len(sequences)} sequences.")
    
    if len(sequences) > 0:
        print(f"Shape of first sequence: {sequences[0].shape}")
        print(f"First sequence sample:\n{sequences[0]}")
        print(f"First target: {targets[0]}")
        
        # Verify shape
        # expecting (5, 3) -> 5 timestamps, 3 features (PC, MinRng, TimeToTCA)
        assert sequences[0].shape == (5, 3)
        print("Sequence shape verification PASSED.")
    else:
        print("WARNING: No sequences generated. Check grouping logic.")

import logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    test_pipeline()
