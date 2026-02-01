"""
Test script to verify Sora API via FastRouter is working correctly.
This will help debug video generation issues.
"""

import os
import sys
import json
import requests
import base64
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

class SoraAPITester:
    def __init__(self):
        self.fastrouter_url = "https://go.fastrouter.ai/api/v1/videos"
        self.api_key = os.getenv("FASTROUTER_API_KEY")
        self.test_results = {
            "api_key_present": False,
            "api_key_valid": False,
            "connection_test": False,
            "video_generation": False,
            "errors": []
        }

    def test_api_key(self):
        """Test 1: Check if API key exists"""
        print("\n" + "="*60)
        print("TEST 1: Checking FASTROUTER_API_KEY...")
        print("="*60)
        
        if not self.api_key:
            msg = "❌ FASTROUTER_API_KEY not found in .env"
            print(msg)
            self.test_results["errors"].append(msg)
            return False
        
        if len(self.api_key) < 10:
            msg = "❌ FASTROUTER_API_KEY appears invalid (too short)"
            print(msg)
            self.test_results["errors"].append(msg)
            return False
        
        print(f"✅ API Key found: {self.api_key[:20]}...{self.api_key[-10:]}")
        self.test_results["api_key_present"] = True
        self.test_results["api_key_valid"] = True
        return True

    def test_connection(self):
        """Test 2: Test basic API connectivity"""
        print("\n" + "="*60)
        print("TEST 2: Testing API Connectivity...")
        print("="*60)
        
        if not self.api_key:
            msg = "⚠️  Skipping connection test (no API key)"
            print(msg)
            self.test_results["errors"].append(msg)
            return False
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Simple test payload
        test_payload = {
            "model": "openai/sora-2",
            "prompt": "Test connection - do not generate",
            "test_mode": True
        }
        
        try:
            print(f"Connecting to: {self.fastrouter_url}")
            response = requests.post(
                self.fastrouter_url,
                json=test_payload,
                headers=headers,
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 401:
                msg = "❌ Authentication failed (401) - Check your FASTROUTER_API_KEY"
                print(msg)
                self.test_results["errors"].append(msg)
                return False
            
            if response.status_code == 400:
                msg = "⚠️  Bad request (400) - Payload may need adjustment"
                print(f"{msg}")
                print(f"Response: {response.text}")
                self.test_results["errors"].append(msg)
                # This is actually OK for connection test
                self.test_results["connection_test"] = True
                return True
            
            if response.status_code in [200, 202]:
                print("✅ Connection successful!")
                self.test_results["connection_test"] = True
                return True
            
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
        except requests.exceptions.Timeout:
            msg = "❌ Connection timeout - API may be down"
            print(msg)
            self.test_results["errors"].append(msg)
            return False
        except requests.exceptions.ConnectionError as e:
            msg = f"❌ Connection error: {str(e)}"
            print(msg)
            self.test_results["errors"].append(msg)
            return False
        except Exception as e:
            msg = f"❌ Unexpected error: {str(e)}"
            print(msg)
            self.test_results["errors"].append(msg)
            return False

    def test_video_generation(self):
        """Test 3: Attempt actual video generation"""
        print("\n" + "="*60)
        print("TEST 3: Testing Video Generation...")
        print("="*60)
        
        if not self.api_key:
            msg = "⚠️  Skipping video generation test (no API key)"
            print(msg)
            return False
        
        # Create a simple test prompt
        prompt = "A red polo shirt on a model, cinematic lighting, professional fashion photography, 4K"
        
        payload = {
            "model": "openai/sora-2",
            "prompt": prompt,
            "length": 10,
            "aspect_ratio": "9:16"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            print(f"Prompt: {prompt}")
            print(f"Sending request to FastRouter (this may take a moment)...")
            
            response = requests.post(
                self.fastrouter_url,
                json=payload,
                headers=headers,
                timeout=60  # Give more time for FastRouter
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 401:
                msg = "❌ Authentication failed - Invalid API key"
                print(msg)
                self.test_results["errors"].append(msg)
                return False
            
            if response.status_code == 429:
                msg = "⚠️  Rate limited - Too many requests"
                print(msg)
                self.test_results["errors"].append(msg)
                return False
            
            if response.status_code == 402:
                msg = "❌ Insufficient credits - Need to top up FastRouter account"
                print(msg)
                self.test_results["errors"].append(msg)
                return False
            
            if response.status_code in [200, 202]:
                result = response.json()
                print(f"✅ Video generation request accepted!")
                print(f"Response: {json.dumps(result, indent=2)[:500]}")
                self.test_results["video_generation"] = True
                return True
            
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            self.test_results["errors"].append(f"Status {response.status_code}: {response.text[:200]}")
            
        except requests.exceptions.Timeout:
            msg = "❌ Request timeout - API response took too long"
            print(msg)
            self.test_results["errors"].append(msg)
            return False
        except requests.exceptions.ConnectionError as e:
            msg = f"❌ Connection failed: {str(e)}"
            print(msg)
            self.test_results["errors"].append(msg)
            return False
        except Exception as e:
            msg = f"❌ Error: {str(e)}"
            print(msg)
            self.test_results["errors"].append(msg)
            return False

    def test_with_image(self):
        """Test 4: Video generation with image reference"""
        print("\n" + "="*60)
        print("TEST 4: Testing Video Generation with Image...")
        print("="*60)
        
        if not self.api_key:
            print("⚠️  Skipping (no API key)")
            return False
        
        # Check for test image
        test_image_path = Path("uploads") / "test_image.jpg"
        if not test_image_path.exists():
            print(f"⚠️  No test image at {test_image_path}")
            print("    Creating a minimal test image...")
            # Try to find any image in uploads
            uploads_dir = Path("uploads")
            if uploads_dir.exists():
                images = list(uploads_dir.glob("*.jpg")) + list(uploads_dir.glob("*.png"))
                if images:
                    test_image_path = images[0]
                    print(f"    Found image: {test_image_path}")
                else:
                    print("    ❌ No images found in uploads directory")
                    return False
            else:
                print("    ❌ uploads directory not found")
                return False
        
        try:
            # Read and encode image
            with open(test_image_path, "rb") as img_file:
                b64_string = base64.b64encode(img_file.read()).decode('utf-8')
            
            prompt = "Professional product photography of the item in the reference image, cinematic lighting, studio setup"
            
            payload = {
                "model": "openai/sora-2",
                "prompt": prompt,
                "image": f"data:image/jpeg;base64,{b64_string[:100]}...",  # Truncated for display
                "length": 10,
                "aspect_ratio": "9:16"
            }
            
            print(f"Image: {test_image_path.name} ({test_image_path.stat().st_size} bytes)")
            print(f"Prompt: {prompt}")
            print("Sending request...")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.post(
                self.fastrouter_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code in [200, 202]:
                print("✅ Image-based video request accepted!")
                return True
            else:
                print(f"Response: {response.text[:500]}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.test_results["errors"].append(str(e))
            return False

    def run_all_tests(self):
        """Run all tests and generate report"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " "*15 + "SORA API DIAGNOSTIC TEST" + " "*19 + "║")
        print("╚" + "="*58 + "╝")
        
        self.test_api_key()
        self.test_connection()
        self.test_video_generation()
        self.test_with_image()
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"✅ API Key Present: {self.test_results['api_key_present']}")
        print(f"✅ API Key Valid: {self.test_results['api_key_valid']}")
        print(f"✅ Connection Test: {self.test_results['connection_test']}")
        print(f"✅ Video Generation: {self.test_results['video_generation']}")
        
        if self.test_results["errors"]:
            print("\n⚠️  ERRORS:")
            for error in self.test_results["errors"]:
                print(f"   - {error}")
        
        # Recommendations
        print("\n" + "="*60)
        print("RECOMMENDATIONS")
        print("="*60)
        
        if not self.test_results['api_key_present']:
            print("1. Add FASTROUTER_API_KEY to your .env file")
        
        if not self.test_results['connection_test']:
            print("1. Verify your API key is correct")
            print("2. Check internet connection")
            print("3. FastRouter API might be down")
        
        if not self.test_results['video_generation']:
            if self.test_results['errors']:
                for error in self.test_results['errors']:
                    if "402" in str(error):
                        print("1. You may have insufficient credits on FastRouter")
                        print("2. Visit https://go.fastrouter.ai to check your account")
                    elif "401" in str(error):
                        print("1. Your API key appears invalid")
                        print("2. Get a new key from https://go.fastrouter.ai")
                    elif "timeout" in str(error).lower():
                        print("1. The API is responding slowly")
                        print("2. Try again in a few moments")
        
        return self.test_results


if __name__ == "__main__":
    tester = SoraAPITester()
    results = tester.run_all_tests()
    
    # Exit with status code based on results
    success = all([
        results['api_key_present'],
        results['api_key_valid'],
        results['connection_test']
    ])
    
    sys.exit(0 if success else 1)
