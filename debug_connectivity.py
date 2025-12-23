import asyncio
import httpx
import sys

# Define configuration
BACKEND_URL = "http://localhost:8000"

async def check_backend():
    print(f"Testing connectivity to {BACKEND_URL}...")
    try:
        async with httpx.AsyncClient() as client:
            # 1. Test Health Endpoint
            print("1. Testing Health Endpoint (/api/health)...")
            try:
                response = await client.get(f"{BACKEND_URL}/api/health", timeout=10.0)
                print(f"   Status Code: {response.status_code}")
                if response.status_code == 200:
                    print(f"   Response: {response.json()}")
                    print("   ✅ Health Check Passed")
                else:
                    print(f"   Response: {response.text}")
                    print("   ❌ Health Check Failed")
            except Exception as e:
                print(f"   ❌ Health Check Error: {e}")

            # 2. Test Dashboard Stats Endpoint (which was failing in app)
            print("\n2. Testing Dashboard Stats Endpoint (/api/dashboard/stats)...")
            try:
                response = await client.get(f"{BACKEND_URL}/api/dashboard/stats", timeout=5.0)
                print(f"   Status Code: {response.status_code}")
                if response.status_code == 200:
                    print(f"   Response: {response.json()}")
                    print("   ✅ Stats Check Passed")
                else:
                    print(f"   Response: {response.text}")
                    print("   ❌ Stats Check Failed")
            except Exception as e:
                print(f"   ❌ Stats Check Error: {e}")

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_backend())
