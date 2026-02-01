"""
Image Generator Agent

This agent uses the Bytez SDK to generate:
1. Fashion model images wearing the product
2. Product showcase images
3. Social media campaign images (Instagram, Facebook, TikTok styles)
"""

import os
from typing import Dict, Any, Optional, List
from langchain_core.messages import SystemMessage
from bytez import Bytez
from app.agents.state import AgentState, ProductData


class ImageGeneratorAgent:
    """
    Generates multiple types of images:
    - Fashion model images (product worn by model)
    - Product showcase images (professional product photography)
    - Social media campaign images (optimized for different platforms)
    """
    
    def __init__(self):
        """Initialize the Image Generator Agent."""
        api_key = os.getenv("BYTEZ_API_KEY")
        if not api_key:
            raise ValueError("BYTEZ_API_KEY not found in environment variables")
            
        self.client = Bytez(api_key)
        self.model_id = "ZB-Tech/Text-to-Image"
        
    def generate_fashion_prompt(self, product_data: Dict[str, Any]) -> str:
        """Create prompt for fashion model image."""
        name = product_data.get("product_name", "product")
        category = product_data.get("category", "fashion item")
        colors = ", ".join(product_data.get("primary_colors", []))
        style = product_data.get("visual_style", "modern")
        features = ", ".join(product_data.get("key_features", [])[:3])
        
        prompt = (
            f"A professional high-fashion photography shot of a model wearing a {name}. "
            f"The product is a {category} in {colors} colors. "
            f"Style: {style}. Key details: {features}. "
            f"The model is posing confidently in a studio setting with professional lighting. "
            f"High quality, photorealistic, 8k, detailed texture."
        )
        return prompt
    
    def generate_product_showcase_prompt(self, product_data: Dict[str, Any]) -> str:
        """Create prompt for professional product showcase image."""
        name = product_data.get("product_name", "product")
        category = product_data.get("category", "item")
        colors = ", ".join(product_data.get("primary_colors", []))
        style = product_data.get("visual_style", "modern")
        features = ", ".join(product_data.get("key_features", [])[:4])
        
        prompt = (
            f"Professional product photography of {name}. "
            f"Category: {category}. Colors: {colors}. Style: {style}. "
            f"Features: {features}. "
            f"The product is displayed on a clean white background with perfect studio lighting. "
            f"Multiple angles, 360-degree view, premium quality, 8k resolution, ultra detailed. "
            f"Perfect for e-commerce and marketing materials."
        )
        return prompt
    
    def generate_instagram_campaign_prompt(self, product_data: Dict[str, Any]) -> str:
        """Create prompt for Instagram/social media campaign image."""
        name = product_data.get("product_name", "product")
        colors = ", ".join(product_data.get("primary_colors", []))
        features = ", ".join(product_data.get("key_features", [])[:3])
        
        prompt = (
            f"Eye-catching Instagram campaign image for {name}. "
            f"Modern, vibrant design with {colors} color scheme. "
            f"Highlights: {features}. "
            f"Professional social media style with trendy aesthetic, dynamic composition. "
            f"Perfect for Instagram feed, Stories, and Reels. "
            f"High energy, engaging, 4K quality. Include lifestyle elements."
        )
        return prompt
    
    def generate_facebook_campaign_prompt(self, product_data: Dict[str, Any]) -> str:
        """Create prompt for Facebook campaign image."""
        name = product_data.get("product_name", "product")
        colors = ", ".join(product_data.get("primary_colors", []))
        selling_points = ", ".join(product_data.get("selling_points", ["high quality", "premium design"])[:3])
        
        prompt = (
            f"Facebook marketing campaign image for {name}. "
            f"Professional, clean design with {colors} colors. "
            f"Emphasizes: {selling_points}. "
            f"Includes lifestyle imagery, aspirational yet relatable. "
            f"Perfect for Facebook ads and business page. "
            f"Clear call-to-action ready aesthetic. High quality, engaging composition."
        )
        return prompt
    
    def generate_tiktok_campaign_prompt(self, product_data: Dict[str, Any]) -> str:
        """Create prompt for TikTok/short video campaign image."""
        name = product_data.get("product_name", "product")
        target = product_data.get("target_demographic", "users")
        
        prompt = (
            f"Viral TikTok campaign thumbnail for {name}. "
            f"Designed for {target}. "
            f"Bold, eye-catching, trend-forward aesthetic. "
            f"High contrast, vibrant colors, dynamic composition. "
            f"Trending style, generation Z friendly. "
            f"Perfect for short-form video content. 4K quality, maximum visual impact."
        )
        return prompt

    def generate_image(self, prompt: str) -> Dict[str, Any]:
        """Generate image using Bytez SDK."""
        try:
            model = self.client.model(self.model_id)
            result = model.run(prompt)
            
            return {
                "output": result.output,
                "error": result.error
            }
        except Exception as e:
            return {"error": str(e), "output": None}

    def __call__(self, state: AgentState) -> AgentState:
        """
        Generate multiple campaign images for different platforms.
        """
        print("\n[IMAGE GENERATOR] Creating social media campaign images...")
        
        try:
            product_data = state.get("product_data", {})
            if not product_data:
                raise ValueError("No product data found in state")
            
            if "generated_images" not in state:
                state["generated_images"] = []
            
            # Generate different image types
            image_types = [
                ("fashion_model", self.generate_fashion_prompt(product_data)),
                ("product_showcase", self.generate_product_showcase_prompt(product_data)),
                ("instagram_campaign", self.generate_instagram_campaign_prompt(product_data)),
                ("facebook_campaign", self.generate_facebook_campaign_prompt(product_data)),
                ("tiktok_campaign", self.generate_tiktok_campaign_prompt(product_data))
            ]
            
            generated_count = 0
            
            for image_type, prompt in image_types:
                print(f"\n  [GENERATING] {image_type.replace('_', ' ')} image...")
                print(f"     Prompt: {prompt[:80]}...")
                
                result = self.generate_image(prompt)
                
                if result.get("error"):
                    print(f"     [WARNING] Error: {result['error']}")
                    continue
                
                image_url = result.get("output")
                if image_url:
                    state["generated_images"].append({
                        "type": image_type,
                        "url": image_url,
                        "prompt": prompt
                    })
                    print(f"     [OK] Generated successfully!")
                    generated_count += 1
            
            if generated_count == 0:
                raise Exception("No images were generated successfully")
            
            state["current_step"] = "image_generation_complete"
            state["messages"].append(
                SystemMessage(content=f"Generated {generated_count} campaign images for social media")
            )
            
            print(f"\n[OK] Image generation complete! Generated {generated_count} images:")
            for img in state["generated_images"]:
                print(f"   - {img['type']}: {img['url'][:50]}...")
            
        except Exception as e:
            error_msg = f"Image Generator Error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"\n[ERROR] {error_msg}")
            
        return state
