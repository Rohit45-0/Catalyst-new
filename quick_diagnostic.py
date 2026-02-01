"""
Quick video generation diagnostic - minimal testing
"""
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

print("\n" + "="*60)
print("QUICK VIDEO GENERATION DIAGNOSTIC")
print("="*60 + "\n")

# 1. API Key Check
api_key = os.getenv("FASTROUTER_API_KEY")
if api_key:
    print(f"✅ FASTROUTER_API_KEY found")
    print(f"   Value: {api_key[:30]}...{api_key[-10:]}")
else:
    print(f"❌ FASTROUTER_API_KEY not found in .env")
    sys.exit(1)

# 2. Quick API connectivity test
print("\n" + "="*60)
print("Testing API connectivity...")
print("="*60)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "openai/sora-2",
    "prompt": "Test: Do not generate. Simple connectivity check.",
}

try:
    print("Sending test request...")
    response = requests.post(
        "https://go.fastrouter.ai/api/v1/videos",
        json=payload,
        headers=headers,
        timeout=15
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("❌ ERROR 401: Authentication failed")
        print("   Your FASTROUTER_API_KEY may be invalid")
        print("   Get a new key from https://go.fastrouter.ai")
        
    elif response.status_code == 402:
        print("❌ ERROR 402: Payment Required")
        print("   You have insufficient credits on FastRouter")
        print("   Visit https://go.fastrouter.ai/dashboard to add credits")
        
    elif response.status_code == 400:
        print("⚠️  Status 400: Bad Request (Expected for test)")
        print("   This is OK - means API is reachable")
        print("✅ API is accessible!")
        
    elif response.status_code in [200, 202]:
        print("✅ API request accepted!")
        data = response.json()
        print(f"   Response ID: {data.get('id', 'N/A')}")
        
    else:
        print(f"⚠️  Unexpected status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except requests.exceptions.Timeout:
    print("❌ Timeout: API took too long to respond")
except requests.exceptions.ConnectionError:
    print("❌ Connection failed: Cannot reach FastRouter API")
except Exception as e:
    print(f"❌ Error: {e}")

# 3. Database check
print("\n" + "="*60)
print("Database status...")
print("="*60)

db_url = os.getenv("DATABASE_URL")
if db_url:
    print("✅ DATABASE_URL configured")
else:
    print("❌ DATABASE_URL not found")

# 4. Azure OpenAI check
print("\n" + "="*60)
print("Azure OpenAI status...")
print("="*60)

azure_key = os.getenv("AZURE_OPENAI_KEY")
if azure_key:
    print("✅ AZURE_OPENAI_KEY configured")
else:
    print("❌ AZURE_OPENAI_KEY not found")

# 5. Test image check
print("\n" + "="*60)
print("Test image check...")
print("="*60)

uploads = Path("uploads")
if uploads.exists():
    images = list(uploads.glob("*.jpg")) + list(uploads.glob("*.png"))
    if images:
        print(f"✅ Found {len(images)} image(s) in uploads/")
        print(f"   Using: {images[0].name}")
    else:
        print("⚠️  No images in uploads/ directory")
else:
    print("❌ uploads/ directory not found")

# Summary
print("\n" + "="*60)
print("NEXT STEPS")
print("="*60)
print("\nTo test the full workflow with video generation, run:")
print("  python end_to_end_workflow.py --generate-video")
print("\nTo test without video (faster, no credits used):")
print("  python end_to_end_workflow.py")

print("\n")
