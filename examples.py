"""
Example Usage of Collision Risk AI System

Demonstrates how to use the system for training, inference, and API calls.
"""

import requests
import json

# API base URL (assuming API is running)
API_URL = "http://localhost:5000"


def example_single_prediction():
    """Example: Make a single prediction."""
    print("=" * 60)
    print("EXAMPLE 1: Single Prediction")
    print("=" * 60)
    
    # High-risk event
    high_risk_event = {
        "miss_distance": 100.0,
        "relative_velocity": 18000.0,
        "time_to_tca": 2.0,
        "object1_mass": 2000.0,
        "object2_mass": 1500.0
    }
    
    response = requests.post(
        f"{API_URL}/predict",
        json=high_risk_event,
        headers={"Content-Type": "application/json"}
    )
    
    print("\nInput:")
    print(json.dumps(high_risk_event, indent=2))
    
    print("\nPrediction:")
    print(json.dumps(response.json(), indent=2))
    print()


def example_batch_prediction():
    """Example: Make batch predictions."""
    print("=" * 60)
    print("EXAMPLE 2: Batch Prediction")
    print("=" * 60)
    
    events = {
        "events": [
            {
                "miss_distance": 100.0,
                "relative_velocity": 18000.0,
                "time_to_tca": 2.0,
                "object1_mass": 2000.0,
                "object2_mass": 1500.0
            },
            {
                "miss_distance": 5000.0,
                "relative_velocity": 10000.0,
                "time_to_tca": 50.0,
                "object1_mass": 500.0,
                "object2_mass": 300.0
            },
            {
                "miss_distance": 200.0,
                "relative_velocity": 20000.0,
                "time_to_tca": 1.0,
                "object1_mass": 3000.0,
                "object2_mass": 2500.0
            }
        ]
    }
    
    response = requests.post(
        f"{API_URL}/predict_batch",
        json=events,
        headers={"Content-Type": "application/json"}
    )
    
    result = response.json()
    
    print("\nSummary:")
    print(json.dumps(result['summary'], indent=2))
    
    print("\nPredictions:")
    for i, pred in enumerate(result['predictions'], 1):
        print(f"\nEvent {i}:")
        print(f"  Prediction: {pred['prediction']}")
        print(f"  Confidence: {pred['confidence']:.2%}")
        print(f"  Risk Level: {pred['risk_level']}")
    print()


def example_high_risk_filter():
    """Example: Get only high-risk events."""
    print("=" * 60)
    print("EXAMPLE 3: Filter High-Risk Events")
    print("=" * 60)
    
    events = {
        "events": [
            {
                "miss_distance": 100.0,
                "relative_velocity": 18000.0,
                "time_to_tca": 2.0,
                "object1_mass": 2000.0,
                "object2_mass": 1500.0
            },
            {
                "miss_distance": 5000.0,
                "relative_velocity": 10000.0,
                "time_to_tca": 50.0,
                "object1_mass": 500.0,
                "object2_mass": 300.0
            },
            {
                "miss_distance": 150.0,
                "relative_velocity": 16000.0,
                "time_to_tca": 3.0,
                "object1_mass": 1800.0,
                "object2_mass": 1200.0
            }
        ]
    }
    
    response = requests.post(
        f"{API_URL}/high_risk?min_probability=0.5",
        json=events,
        headers={"Content-Type": "application/json"}
    )
    
    result = response.json()
    
    print(f"\nFound {result['count']} high-risk events:")
    for event in result['high_risk_events']:
        print(f"\n  High Risk Probability: {event['high_risk_probability']:.2%}")
        print(f"  Confidence: {event['confidence']:.2%}")
        print(f"  Risk Level: {event['risk_level']}")
    print()


def example_model_info():
    """Example: Get model information."""
    print("=" * 60)
    print("EXAMPLE 4: Model Information")
    print("=" * 60)
    
    response = requests.get(f"{API_URL}/model_info")
    
    print("\nModel Configuration:")
    print(json.dumps(response.json(), indent=2))
    print()


def example_health_check():
    """Example: Check API health."""
    print("=" * 60)
    print("EXAMPLE 5: Health Check")
    print("=" * 60)
    
    response = requests.get(f"{API_URL}/health")
    
    print("\nAPI Status:")
    print(json.dumps(response.json(), indent=2))
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("COLLISION RISK AI - USAGE EXAMPLES")
    print("=" * 60 + "\n")
    
    print("Make sure the API server is running:")
    print("  python api.py --host 0.0.0.0 --port 5000")
    print()
    
    try:
        # Check if API is running
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code != 200:
            print("Error: API is not responding correctly")
            return
    except requests.exceptions.RequestException:
        print("Error: API is not running. Please start it first.")
        return
    
    # Run examples
    example_health_check()
    example_single_prediction()
    example_batch_prediction()
    example_high_risk_filter()
    example_model_info()
    
    print("=" * 60)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
