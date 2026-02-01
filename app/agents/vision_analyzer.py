"""
Vision Analyzer Agent

This agent uses multimodal LLMs to analyze product images and extract
structured marketing-relevant information.
"""

import os
import base64
import json
from pathlib import Path
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from openai import AzureOpenAI
from app.agents.state import AgentState, ProductData


class VisionAnalyzerAgent:
    """
    Analyzes product images using GPT-4o vision capabilities.
    
    Extracts:
    - Product category and name
    - Visual characteristics (colors, style, material)
    - Target demographic
    - Key selling points
    """
    
    def __init__(self, model_name: str = None, temperature: float = 0.7):
        """
        Initialize the Vision Analyzer Agent.
        
        Args:
            model_name: The deployment name (default: from env AZURE_DEPLOYMENT_NAME)
            temperature: Creativity level (0-1)
        """
        # Get Azure OpenAI configuration from environment
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_key = os.getenv("AZURE_OPENAI_KEY")
        self.deployment_name = model_name or os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")
        api_version = os.getenv("AZURE_API_VERSION", "2024-02-15-preview")
        self.temperature = temperature
        
        if not azure_endpoint or not azure_key:
            raise ValueError(
                "Azure OpenAI credentials not found. "
                "Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY in your .env file"
            )
        
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=azure_key,
            api_version=api_version,
        )
        
    def encode_image(self, image_path: str) -> str:
        """
        Encode image to base64 for API transmission.
        
        Args:
            image_path: Path to the product image
            
        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_product_image(self, image_path: str, description: str = "", category: str = None) -> Dict[str, Any]:
        """
        Analyze a product image and extract marketing-relevant data.
        
        Args:
            image_path: Path to the product image
            description: Optional user-provided product description
            category: Detected product category (optional)
            
        Returns:
            Structured product data dictionary
        """
        # Encode the image
        base64_image = self.encode_image(image_path)
        
        # Construct the analysis prompt
        try:
            from app.agents.prompts.category_prompts import CATEGORY_PROMPTS
            category_prompt = None
            if category and category in CATEGORY_PROMPTS:
                print(f"  Using specialized vision prompt for: {category}")
                category_prompt = CATEGORY_PROMPTS[category]["vision_system"]
        except ImportError:
            category_prompt = None

        base_fields = """
Analyze the image and provide a structured JSON response with the following fields:
- product_name: A catchy, descriptive name for the product
- category: The product category (e.g., "Electronics", "Fashion", "Home Decor")
- primary_colors: List of 2-3 dominant colors in the image
- color_psychology: Briefly explain the emotional impact of the color palette (e.g. "matte black suggests luxury")
- material: The apparent material(s) the product is made from
- key_features: List of 3-5 visible features or characteristics
- target_demographic: Who would buy this product (age, lifestyle, interests)
- visual_style: The aesthetic style (e.g., "minimalist", "luxury", "playful", "professional")
- lifestyle_context: Suggested usage scenarios based on visual cues (e.g., "gym workout", "office desk")
- selling_points: List of 3-5 unique selling points based on visual analysis
- visual_hooks: Specific visual elements that grab attention

Be specific, creative, and marketing-focused in your analysis."""

        if category_prompt:
            system_prompt = f"{category_prompt}\n\n{base_fields}"
        else:
            system_prompt = f"You are an expert marketing analyst and visual designer. Your job is to analyze product images and extract detailed information that will be used to create compelling marketing content.\n\n{base_fields}"

        user_prompt = f"""Analyze this product image in detail.
        
{f'User Description: {description}' if description else ''}

Provide your analysis as a valid JSON object."""

        # Create the message with image
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        # Get the analysis
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        try:
            content = response.choices[0].message.content
            product_data = json.loads(content)
            return product_data
        except json.JSONDecodeError:
            # Fallback: return raw content
            return {
                "raw_analysis": response.choices[0].message.content,
                "error": "Failed to parse JSON response"
            }
    
    def __call__(self, state: AgentState) -> AgentState:
        """
        LangGraph node function - processes the state and returns updated state.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state with vision analysis results
        """
        print("Vision Analyzer Agent: Analyzing product image...")
        
        try:
            # Extract inputs from state
            image_path = state["product_image_path"]
            description = state.get("product_description", "")
            
            # Perform analysis
            product_data = self.analyze_product_image(image_path, description)
            
            # Update state
            state["product_data"] = product_data
            state["current_step"] = "vision_complete"
            
            # Add a message to the conversation history
            state["messages"].append(
                SystemMessage(content=f"Vision analysis complete. Identified product: {product_data.get('product_name', 'Unknown')}")
            )
            
            print(f"Analysis complete: {product_data.get('product_name', 'Unknown')}")
            
        except Exception as e:
            error_msg = f"Vision Analyzer Error: {str(e)}"
            state["errors"].append(error_msg)
            state["current_step"] = "error"
            print(f"Error: {error_msg}")
        
        return state


# Convenience function for direct usage
def create_vision_agent(deployment_name: str = None) -> VisionAnalyzerAgent:
    """Factory function to create a Vision Analyzer Agent."""
    return VisionAnalyzerAgent(model_name=deployment_name)
