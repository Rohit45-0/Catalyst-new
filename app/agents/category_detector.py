"""
Category Detector Agent

This agent analyzes product images and descriptions to classify them into 
predefined marketing categories. This enables downstream agents to use 
category-specific strategies and prompts.
"""

import os
import base64
import json
from typing import Dict, Any, List
from openai import AzureOpenAI
from app.agents.state import AgentState

class CategoryDetectorAgent:
    """
    Classifies products into 7 primary marketing categories:
    1. Tech/Gadgets
    2. Fashion/Apparel
    3. Beauty/Wellness
    4. Food/Beverage
    5. Home/Decor
    6. Fitness/Sports
    7. B2B/SaaS
    """
    
    CATEGORIES = [
        "tech_gadgets",
        "fashion_apparel",
        "beauty_wellness",
        "food_beverage",
        "home_decor",
        "fitness_sports",
        "b2b_saas"
    ]
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_key = os.getenv("AZURE_OPENAI_KEY")
        self.deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")
        api_version = os.getenv("AZURE_API_VERSION", "2024-02-15-preview")
        
        if not azure_endpoint or not azure_key:
            raise ValueError("Azure OpenAI credentials missing")
            
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=azure_key,
            api_version=api_version,
        )

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        if not image_path or not os.path.exists(image_path):
            return ""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def detect_category(self, state: AgentState) -> AgentState:
        """
        Detect product category from image and description.
        Updates state['category_data'].
        """
        print(f"   Detecting product category...")
        
        product_description = state.get("product_description", "")
        product_image_path = state.get("product_image_path", "")
        
        # Prepare content parts
        content = [
            {
                "type": "text", 
                "text": f"Analyze this product and classify it. Description: {product_description}"
            }
        ]
        
        # Add image if available
        if product_image_path:
            base64_image = self.encode_image(product_image_path)
            if base64_image:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })

        # System prompt for classification
        system_prompt = """
        You are an expert Marketing Category Analyst.
        Classify the product into EXACTLY ONE of these categories:
        
        1. tech_gadgets (Electronics, software, hardware, digital tools)
        2. fashion_apparel (Clothing, shoes, accessories, jewelry)
        3. beauty_wellness (Skincare, makeup, supplements, personal care)
        4. food_beverage (Snacks, drinks, meals, ingredients)
        5. home_decor (Furniture, lighting, kitchenware, art)
        6. fitness_sports (Gym gear, sports equipment, athletic wear)
        7. b2b_saas (Business software, enterprise solutions, services)
        
        If unsure, choose the closest match.
        
        Return JSON ONLY:
        {
            "category": "one_of_the_above_ids",
            "subcategory": "specific_niche",
            "confidence": 0.0_to_1.0,
            "reasoning": "brief explanation"
        }
        """

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ],
                temperature=0.1,  # Low temperature for consistent classification
                response_format={"type": "json_object"},
                max_tokens=300
            )

            result_json = response.choices[0].message.content
            category_data = json.loads(result_json)
            
            # Validate category
            if category_data.get("category") not in self.CATEGORIES:
                print(f"   Invalid category returned: {category_data.get('category')}. Defaulting to tech_gadgets.")
                category_data["category"] = "tech_gadgets"
            
            print(f"   Category detected: {category_data['category']} ({category_data['subcategory']}) - {category_data['confidence']:.2f}")
            
            # Update state
            state["category_data"] = category_data
            
            return state
            
        except Exception as e:
            print(f"   Category detection failed: {e}")
            # Fallback
            state["category_data"] = {
                "category": "tech_gadgets",
                "subcategory": "general",
                "confidence": 0.0,
                "reasoning": f"Analysis failed: {str(e)}"
            }
            return state
