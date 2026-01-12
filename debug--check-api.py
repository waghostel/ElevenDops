
import asyncio
import httpx
import sys

# Backend URL (defaulting to localhost:8000 based on standard setup)
BACKEND_URL = "http://localhost:8000"

async def main():
    print(f"🔍 TESTING BACKEND API at {BACKEND_URL}...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Health Check
            print("\n1. Checking Health...")
            resp = await client.get(f"{BACKEND_URL}/api/health")
            print(f"   Status: {resp.status_code}")
            import json
            print(f"   Response: {json.dumps(resp.json(), indent=2)}")
            
            # Test 2: Audio List for dr_demo_001
            print("\n2. Fetching Audio for 'dr_demo_001'...")
            resp = await client.get(f"{BACKEND_URL}/api/audio/list", params={"doctor_id": "dr_demo_001"})
            
            if resp.status_code == 200:
                data = resp.json()
                files = data.get("audio_files", [])
                print(f"   ✅ Success! Found {len(files)} files.")
                for f in files:
                    print(f"      - {f['audio_id']} (Know: {f['knowledge_id']}, Doc: {f.get('doctor_id')})")
            else:
                print(f"   ❌ Failed: {resp.status_code}")
                print(f"   Body: {resp.text}")

        except Exception as e:
            print(f"   ❌ Connection Error: {e}")
            print("   Make sure the backend is running!")

if __name__ == "__main__":
    asyncio.run(main())
