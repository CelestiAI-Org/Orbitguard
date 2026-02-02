from ml.runner import MLRunner
import json

def test_ml_integration():
    print("Initializing MLRunner...")
    runner = MLRunner()
    
    if not runner.ready:
        print("ML Model NOT ready.")
        return
        
    print("ML Model Initialized.")
    
    # Mock Data (based on backend/inspect_cdm.py output)
    mock_data = [
        {
            "CDM_ID": "1319792095",
            "CREATED": "2026-01-25 23:30:17.000000",
            "TCA": "2026-01-26T16:18:38.552000",
            "MIN_RNG": "35",
            "PC": "0.00078",
            "SAT_1_ID": "65004",
            "SAT_2_ID": "29891"
        },
        # Add a stored update
        {
            "CDM_ID": "1319792096",
            "CREATED": "2026-01-25 23:40:17.000000",
            "TCA": "2026-01-26T16:18:38.552000", # Same TCA
            "MIN_RNG": "30",
            "PC": "0.00079",
            "SAT_1_ID": "65004",
            "SAT_2_ID": "29891"
        }
    ]
    
    print("Running Prediction on Mock Data...")
    results = runner.predict(mock_data)
    
    print("Results:")
    print(json.dumps(results, indent=2))
    
    # Check Key
    expected_key = "65004_29891_2026-01-26T16:18:00"
    if expected_key in results:
        print(f"SUCCESS: Key {expected_key} found.")
    else:
        print(f"FAILURE: Key {expected_key} NOT found. Found keys: {list(results.keys())}")

if __name__ == "__main__":
    test_ml_integration()
