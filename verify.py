import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /health...")
    try:
        res = requests.get(f"{BASE_URL}/health")
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
        assert res.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")

def test_analyze():
    print("\nTesting /analyze...")
    path = os.getcwd()
    try:
        res = requests.post(f"{BASE_URL}/analyze", json={"path": path})
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"Root name: {data.get('name')}")
            print(f"Children count: {len(data.get('children', []))}")
        else:
            print(f"Error: {res.text}")
    except Exception as e:
        print(f"Analyze failed: {e}")

def test_analyze_file():
    print("\nTesting /analyze_file...")
    # Create a dummy file to analyze
    dummy_file = "test_analysis.txt"
    with open(dummy_file, "w", encoding="utf-8") as f:
        f.write("This is a test file for the AI model. It contains simple text to summarize.")
    
    full_path = os.path.abspath(dummy_file)
    
    try:
        # Note: This might take time if model needs to download/load
        print("Sending request (this might take a while for first run)...")
        res = requests.post(f"{BASE_URL}/analyze_file", json={"path": full_path})
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print(f"Response: {res.json()}")
        else:
            print(f"Error: {res.text}")
    except Exception as e:
        print(f"File analysis failed: {e}")
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)

if __name__ == "__main__":
    test_health()
    test_analyze()
    # Skip analyze_file in automated run if we want to be quick, 
    # but let's try it to see if model loads.
    # test_analyze_file() 
