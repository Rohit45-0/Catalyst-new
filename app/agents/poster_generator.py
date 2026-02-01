from typing import Dict, Any, Optional
import os
import base64
import uuid
from app.agents.base import BaseAgent
from openai import OpenAI

class PosterGeneratorAgent(BaseAgent):
    """
    Generates promotional posters to accompany video content.
    Phase 3 extension.
    """
    
    def execute(self, product_data: Dict[str, Any], emotional_data: Dict[str, Any] = None, hook_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a poster image using direct HTTP request to ensure compatibility."""
        import requests
        
        api_key = os.getenv("FASTROUTER_API_KEY")
        if not api_key:
             return {"error": "FASTROUTER_API_KEY missing"}
             
        try:
            # Construct Prompt
            product_name = product_data.get("product_name", "Product")
            desc = product_data.get("description", "")
            emotion = emotional_data.get("primary_emotion", "Excitement") if emotional_data else "Excitement"
            hook = hook_data.get("best_hook", "") if hook_data else ""
            
            prompt = (
                f"A high-quality advertisement poster for '{product_name}'. "
                f"Context: {desc}. "
                f"Mood: {emotion}. "
                f"Headline text style: '{hook}'. "
                f"Visual style: Cinematic, Vibrant, 4k resolution, professional photography."
            )
            
            # Remove emojis just in case
            import re
            prompt = re.sub(r'[\U00010000-\U0010ffff]', '', prompt)
            
            print(f" Generating Poster (Requests)... Prompt: {prompt[:50]}...")
            
            # Use direct API call (Standard OpenAI format)
            url = "https://go.fastrouter.ai/api/v1/images/generations"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code != 200:
                print(f" API Error: {response.status_code} - {response.text}")
                return {"status": "failed", "error": f"API {response.status_code}: {response.text}"}
                
            # Parse Response
            j = response.json()
            image_data = None
            
            if "data" in j and len(j["data"]) > 0:
                item = j["data"][0]
                if "b64_json" in item:
                    image_data = base64.b64decode(item["b64_json"])
                elif "url" in item:
                    print(f" Downloading from URL: {item['url'][:50]}...")
                    img_r = requests.get(item['url'])
                    image_data = img_r.content
            
            if image_data:
                # Save to static/images
                output_dir = os.path.join(os.getcwd(), "static", "images")
                os.makedirs(output_dir, exist_ok=True)
                filename = f"poster_{uuid.uuid4().hex[:8]}.png"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(image_data)
                    
                print(f" Poster generated: {filepath}")
                return {
                    "status": "success",
                    "poster_path": filepath,
                    "prompt": prompt
                }
            else:
                return {"status": "failed", "error": "No image data returned"}
                
        except Exception as e:
            print(f" Poster Generation Failed: {e}")
            return {"status": "failed", "error": str(e)}
