"""
Visual Competitor Analyzer Agent

This agent performs a competitive analysis by:
1. Searching for competitor product images using Brave Search (1 API call).
2. Comparing the user's product image against competitors using GPT-4o Vision.
3. Identifying visual differentiation opportunities.
"""

import os
import requests
import base64
import json
from typing import Dict, Any, List, Optional
from brave import Brave
from openai import AzureOpenAI
from app.agents.state import AgentState

class VisualCompetitorAnalyzerAgent:
    def __init__(self, model_name: str = None):
        # Azure Config
        self.deployment_name = model_name or os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.getenv("AZURE_API_VERSION", "2024-02-15-preview"),
        )
        
        # Brave Config
        brave_key = os.getenv("BRAVE_API_KEY")
        if not brave_key:
            raise ValueError("BRAVE_API_KEY not found")
        self.brave = Brave(brave_key)

    def _encode_local_image(self, image_path: str) -> str:
        """Read local file and encode to base64."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image {image_path}: {e}")
            return None

    def _get_competitor_images(self, query: str, limit: int = 3) -> List[Dict[str, str]]:
        """
        Fetch competitor images using Brave Image Search API directly.
        Returns list of {title, url, source_url}
        """
        print(f" Searching competitors with query: '{query}'")
        
        api_key = os.getenv("BRAVE_API_KEY")
        if not api_key:
             print(" BRAVE_API_KEY missing")
             return []
             
        url = "https://api.search.brave.com/res/v1/images/search"
        headers = {
            "X-Subscription-Token": api_key,
            "Accept": "application/json"
        }
        params = {"q": query, "count": limit * 3} # Get extras
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code != 200:
                print(f" Brave API Error ({response.status_code}): {response.text[:200]}")
                return []
                
            data = response.json()
            competitors = []
            
            # Brave Image API structure: 'results' list
            if 'results' in data:
                for item in data['results']:
                    # Extract high-res image if possible, or thumbnail
                    # item usually has 'thumbnail' and 'url' (source page) and 'properties' -> 'url' (image)
                    image_url = None
                    if 'properties' in item and 'url' in item['properties']:
                        image_url = item['properties']['url']
                    elif 'thumbnail' in item:
                        image_url = item['thumbnail'].get('src')
                        
                    if image_url:
                        competitors.append({
                            "title": item.get('title', 'Competitor Product'),
                            "image_url": image_url,
                            "source": item.get('url', '')
                        })
                        if len(competitors) >= limit:
                            break
                            
            print(f"    Found {len(competitors)} images via Brave API")
            return competitors
            
        except Exception as e:
            print(f" Error searching competitors: {e}")
            return []

    def analyze_competition(self, user_image_b64: str, competitors: List[Dict]) -> Dict:
        """
        Compare user image vs competitors using GPT-4o Vision.
        """
        if not competitors:
            return {"error": "No competitors found to analyze"}

        # Construct Message
        content = [
            {
                "type": "text", 
                "text": (
                    "You are a Visual Brand Strategist. Perform a competitive visual analysis.\n"
                    "Image 1 is OUR PRODUCT. The subsequent images are COMPETITORS.\n\n"
                    "Analyze the following:\n"
                    "1. Common Visual Trends: What are competitors doing? (Lighting, angles, colors)\n"
                    "2. Differentiation Score (1-10): How distinct does our product look?\n"
                    "3. SWOT Analysis: Visual Strengths/Weaknesses vs competitors.\n"
                    "4. Actionable Advice: How to style future photos to stand out.\n\n"
                    "Return ONLY JSON format: {visual_trends: [], differentiation_score: int, swot: {strengths: [], weaknesses: [], opportunities: [], threats: []}, strategic_advice: []}"
                )
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{user_image_b64}"}
            }
        ]

        # Add competitors (Passing URLs directly)
        # Note: Azure might fail if URLs are guarded. 
        # In a robust prod env, we'd download and b64 encode them first.
        # For this implementation, we try URLs.
        for i, comp in enumerate(competitors):
            content.append({
                "type": "text",
                "text": f"Competitor {i+1}: {comp['title']}"
            })
            content.append({
                "type": "image_url",
                "image_url": {"url": comp['image_url']}
            })

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": content}],
                max_tokens=1000,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f" Visual Analysis Error: {e}")
            return {"error": str(e)}

    def __call__(self, state: AgentState) -> AgentState:
        """
        Main execution method for the agent.
        """
        print(" Starting Visual Competitor Analysis...")
        
        product_name = state.get("product_data", {}).get("product_name", state.get("product_description", "")[:20])
        category = state.get("category_data", {}).get("category", "products")
        subcategory = state.get("category_data", {}).get("subcategory", "")
        
        # 1. Search (Single efficient call)
        # Use subcategory/category brands to find general competitors rather than specific product name (which might be hallucinated)
        search_term = subcategory if subcategory else category
        search_query = f"best {search_term} brands product photography marketing"
        competitors = self._get_competitor_images(search_query, limit=3)
        
        if not competitors:
            print(" No competitors found. Skipping analysis.")
            state["competitor_data"] = {"error": "No competitors found"}
            return state

        # 2. Analyze
        # Encode local user image
        user_image_b64 = self._encode_local_image(state["product_image_path"])
        if not user_image_b64:
             state["competitor_data"] = {"error": "Could not read local image"}
             return state
             
        analysis = self.analyze_competition(user_image_b64, competitors)
        
        # 3. Store Results
        state["competitor_data"] = {
            "competitors_found": competitors,
            "analysis": analysis
        }
        
        print(" Competitor Analysis Complete.")
        return state
