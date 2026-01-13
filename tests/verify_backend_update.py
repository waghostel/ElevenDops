
import requests
import json

BASE_URL = "http://localhost:8000"
AUDIO_ID = "9118c3bf-6a5d-4414-af27-6ac1b610a15e"

def update_audio():
    print(f"Updating audio {AUDIO_ID}...")
    payload = {
        "name": "Backend API Test Update",
        "description": "Updated via Python script verifying backend works"
    }
    
    try:
        resp = requests.put(f"{BASE_URL}/api/audio/{AUDIO_ID}", json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        resp.raise_for_status()
        print("Update successful!")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    update_audio()
