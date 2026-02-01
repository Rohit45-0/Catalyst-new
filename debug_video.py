"""
Debug script for video generation in end_to_end_workflow.py
Tests the actual video generation with proper error handling and detailed logging.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv(override=True)

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_environment():
    """Check if all required environment variables are set."""
    print("\n" + "="*70)
    print("ENVIRONMENT CHECK")
    print("="*70)
    
    required_vars = {
        "FASTROUTER_API_KEY": "Video generation API key",
        "AZURE_OPENAI_KEY": "LLM for script generation",
        "DATABASE_URL": "Database connection",
    }
    
    optional_vars = {
        "REPLICATE_API_TOKEN": "VTON (optional, skipped by default)",
    }
    
    missing = []
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:20] + "..." + value[-10:] if len(value) > 30 else value
            print(f"✅ {var}: {masked}")
        else:
            print(f"❌ {var}: MISSING")
            missing.append(var)
    
    print("\nOptional:")
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:20] + "..." + value[-10:] if len(value) > 30 else value
            print(f"✅ {var}: {masked}")
        else:
            print(f"⚠️  {var}: Not set (will skip VTON)")
    
    return len(missing) == 0, missing


def check_test_image():
    """Check if a test image exists."""
    print("\n" + "="*70)
    print("TEST IMAGE CHECK")
    print("="*70)
    
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        print(f"❌ uploads directory not found at {uploads_dir.absolute()}")
        return None
    
    images = list(uploads_dir.glob("*.jpg")) + list(uploads_dir.glob("*.png")) + list(uploads_dir.glob("*.jpeg"))
    
    if not images:
        print(f"❌ No images found in {uploads_dir}")
        return None
    
    # Return the first image
    image_path = images[0]
    size_mb = image_path.stat().st_size / (1024 * 1024)
    print(f"✅ Found test image: {image_path.name} ({size_mb:.2f} MB)")
    return str(image_path.absolute())


def test_llm_for_script():
    """Test if LLM can generate a video script."""
    print("\n" + "="*70)
    print("LLM SCRIPT GENERATION TEST")
    print("="*70)
    
    try:
        from app.agents.video_creator import VideoCreatorAgent
        
        agent = VideoCreatorAgent()
        
        # Test data
        product_data = {
            "product_name": "Crimson Casual Button-Detail Polo",
            "category": "Fashion",
            "key_features": ["Mandarin collar", "Navy blue cuffs", "Red color"]
        }
        
        market_data = {
            "market_trends": ["minimalist design", "sustainable fashion", "bold colors"]
        }
        
        emotional_data = {
            "primary_emotion": "ASPIRATION"
        }
        
        hook_data = {
            "best_hook": "Transform your wardrobe with one game-changing piece"
        }
        
        print("Calling LLM to generate video script...")
        print("Product:", product_data["product_name"])
        
        result = agent._generate_script(product_data, market_data, emotional_data, hook_data)
        
        if result:
            print("✅ Script generation successful!")
            print(f"   Title: {result.get('title', 'N/A')}")
            print(f"   Video Prompt: {result.get('video_prompt', 'N/A')[:100]}...")
            print(f"   Scenes: {len(result.get('script_scenes', []))} scenes")
            return True
        else:
            print("❌ Script generation returned None")
            return False
            
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_request():
    """Test the actual FastRouter API call."""
    print("\n" + "="*70)
    print("FASTROUTER API TEST")
    print("="*70)
    
    import requests
    
    api_key = os.getenv("FASTROUTER_API_KEY")
    if not api_key:
        print("❌ No FASTROUTER_API_KEY found")
        return False
    
    # Test payload
    payload = {
        "model": "openai/sora-2",
        "prompt": "A red polo shirt on a fashion model, professional studio lighting, cinematic 4K",
        "length": 10,
        "aspect_ratio": "9:16"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    print(f"Making request to FastRouter API...")
    print(f"Model: {payload['model']}")
    print(f"Prompt: {payload['prompt']}")
    print(f"Length: {payload['length']}s")
    
    try:
        response = requests.post(
            "https://go.fastrouter.ai/api/v1/videos",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ API request successful!")
                print(f"   Response: {json.dumps(data, indent=2)[:500]}")
                return True
            except:
                print(f"Response text: {response.text[:500]}")
                return False
        elif response.status_code == 402:
            print("❌ Insufficient credits - You need to top up your FastRouter account")
            print("   Visit: https://go.fastrouter.ai/dashboard")
            return False
        elif response.status_code == 401:
            print("❌ Authentication failed - Check your FASTROUTER_API_KEY")
            return False
        elif response.status_code == 429:
            print("❌ Rate limited - Too many requests")
            return False
        else:
            print(f"❌ API Error {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - API took too long to respond")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Run all debug tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "VIDEO GENERATION DEBUG SUITE" + " "*25 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {}
    
    # Test 1: Environment
    env_ok, missing = check_environment()
    results["environment"] = env_ok
    
    if not env_ok:
        print(f"\n❌ Missing required variables: {', '.join(missing)}")
        print("Please update your .env file")
        return
    
    # Test 2: Test Image
    image_path = check_test_image()
    results["test_image"] = image_path is not None
    
    # Test 3: LLM
    llm_ok = test_llm_for_script()
    results["llm"] = llm_ok
    
    # Test 4: API
    api_ok = test_api_request()
    results["api"] = api_ok
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test}")
    
    # Recommendations
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    
    if all(results.values()):
        print("✅ All tests passed! Ready to generate videos.")
        print("\nRun the workflow with video generation:")
        print("  python end_to_end_workflow.py --generate-video")
    else:
        if not results["environment"]:
            print("1. Fix environment variables in .env")
        if not results["test_image"]:
            print("1. Add a test image to the uploads/ directory")
        if not results["llm"]:
            print("1. Check your Azure OpenAI configuration")
        if not results["api"]:
            print("1. Check your FastRouter API key and credits")
            print("2. Visit https://go.fastrouter.ai/dashboard to manage credits")


if __name__ == "__main__":
    main()
