#!/usr/bin/env python3
"""
Frontend Integration Test Script
Tests the Catalyst AI Backend API endpoints
"""

import requests
import json
import sys
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "uploads/wallet.webp"  # Use existing test image

class APITester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.token = None
        self.user_email = "test@catalyst.ai"
        self.user_password = "TestPassword123!"
    
    def print_header(self, title):
        """Print test section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_response(self, response, title="Response"):
        """Pretty print API response"""
        print(f"\n{title}:")
        print(f"Status Code: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        self.print_header("TEST 1: Health Check")
        
        try:
            response = requests.get(f"{self.base_url}/")
            self.print_response(response)
            return response.status_code == 200
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    def test_register(self):
        """Test user registration"""
        self.print_header("TEST 2: User Registration")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json={
                    "email": self.user_email,
                    "password": self.user_password
                }
            )
            self.print_response(response)
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    def test_login(self):
        """Test user login"""
        self.print_header("TEST 3: User Login")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "email": self.user_email,
                    "password": self.user_password
                }
            )
            self.print_response(response)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                print(f"\n✓ Token obtained: {self.token[:20]}...")
                return True
            return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    def test_campaign_generation(self, generate_video=False):
        """Test campaign generation endpoint"""
        title = "TEST 4: Campaign Generation"
        if generate_video:
            title += " (WITH VIDEO)"
        self.print_header(title)
        
        if not self.token:
            print("ERROR: Not authenticated. Run login test first.")
            return False
        
        if not os.path.exists(TEST_IMAGE_PATH):
            print(f"ERROR: Test image not found at {TEST_IMAGE_PATH}")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            with open(TEST_IMAGE_PATH, "rb") as f:
                files = {"image": f}
                data = {
                    "product_name": "Test Product",
                    "brand_name": "Test Brand",
                    "price": "$99.99",
                    "description": "A high-quality test product",
                    "campaign_goal": "brand awareness",
                    "target_audience": "Everyone",
                    "brand_persona": "Professional",
                    "generate_video": "true" if generate_video else "false"
                }
                
                print(f"\nSending campaign generation request...")
                print(f"  Product: {data['product_name']}")
                print(f"  Image: {TEST_IMAGE_PATH}")
                print(f"  Generate Video: {generate_video}")
                
                response = requests.post(
                    f"{self.base_url}/api/v1/campaigns/generate",
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=300  # 5 minutes timeout
                )
            
            self.print_response(response)
            
            if response.status_code == 200:
                campaign = response.json()
                if campaign.get("success"):
                    print(f"\n✓ Campaign generated successfully!")
                    print(f"  Campaign ID: {campaign['campaign_id']}")
                    print(f"  Category: {campaign['category']}")
                    print(f"  Poster: {campaign['poster_url']}")
                    if campaign.get('video_url'):
                        print(f"  Video: {campaign['video_url']}")
                    return True
            return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    def test_list_campaigns(self):
        """Test campaign listing"""
        self.print_header("TEST 5: List Campaigns")
        
        if not self.token:
            print("ERROR: Not authenticated. Run login test first.")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/v1/campaigns/list?skip=0&limit=10",
                headers=headers
            )
            self.print_response(response)
            return response.status_code == 200
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    def run_all_tests(self, skip_video=True):
        """Run all tests"""
        print("\n" + "="*60)
        print("  CATALYST AI BACKEND - API TEST SUITE")
        print("="*60)
        print(f"Base URL: {self.base_url}")
        
        results = {}
        
        # Basic tests
        results["Health Check"] = self.test_health_check()
        results["Register"] = self.test_register()
        results["Login"] = self.test_login()
        
        if results["Login"]:
            results["Campaign Generation"] = self.test_campaign_generation(generate_video=False)
            results["List Campaigns"] = self.test_list_campaigns()
            
            # Optional: Test with video (longer)
            if not skip_video:
                results["Campaign with Video"] = self.test_campaign_generation(generate_video=True)
        
        # Print summary
        self.print_header("TEST SUMMARY")
        for test_name, passed in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        total = len(results)
        passed = sum(1 for v in results.values() if v)
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return all(results.values())

def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Catalyst AI Backend API")
    parser.add_argument("--url", default=BASE_URL, help="Base URL of the API")
    parser.add_argument("--video", action="store_true", help="Include video generation test")
    args = parser.parse_args()
    
    tester = APITester(args.url)
    success = tester.run_all_tests(skip_video=not args.video)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
