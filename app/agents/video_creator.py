import os
import requests
import json
import shutil
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from gradio_client import Client, handle_file

class VideoCreatorAgent(BaseAgent):
    """
    Agent responsible for:
    1. Writing short-form video scripts (Reels/Shorts) based on strategy.
    2. Generating "Fitted" product images using VTON (Virtual Try-On).
    3. Generating the actual video using FastRouter (Sora-2).
    """

    def __init__(self):
        super().__init__()
        self.fastrouter_url = "https://go.fastrouter.ai/api/v1/videos"
        self.api_key = os.getenv("FASTROUTER_API_KEY")
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")

    def execute(self, product_data: Dict[str, Any], market_data: Dict[str, Any], emotional_data: Dict[str, Any], hook_data: Dict[str, Any], image_path: str = None) -> Dict[str, Any]:
        """
        Main execution flow:
        1. Generate Script using LLM.
        2. (Hybrid) Apply VTON to get a "Fitted" Model Image.
        3. Extract prompt and Refine for Video AI.
        4. Call FastRouter API (Image-to-Video) using the Fitted Image.
        """
        
        # 1. Generate the Script
        script_result = self._generate_script(product_data, market_data, emotional_data, hook_data)
        
        # 2. Extract specific prompt for video generation (visual description)
        video_prompt = script_result.get("video_prompt")
        
        # 3. Hybrid Pipeline: Try-On + Animate
        video_url = None
        cloud_url = None
        
        if self.api_key:
            try:
                # Step A: VTON (Virtual Try-On) - DISABLED for speed
                fitted_image_path = None
                # if image_path and self.replicate_token:
                #     print(f" Running Virtual Try-On for: {image_path}")
                #     try:
                #         fitted_image_path = self._generate_vton_image(image_path)
                #         if fitted_image_path:
                #             print(f"    VTON Success: {fitted_image_path}")
                #         else:
                #             print("    VTON returned no result, falling back to original image.")
                #     except Exception as e:
                #          print(f"    VTON Failed (Fallback to original): {e}")

                # Use original image for speed
                final_image_source = image_path 
                
                # Step B: Video Generation (Sora)
                print(f" Generating video with prompt: {video_prompt[:50]}...")
                if final_image_source:
                     print(f" Using reference image: {final_image_source}")
                
                video_url, cloud_url = self._generate_video_file(video_prompt, final_image_source)
            except Exception as e:
                print(f" Video Generation Failed: {e}")
                video_url = None
                cloud_url = None
        else:
            print(" FASTROUTER_API_KEY not found. Skipping video generation.")

        return {
            "video_script": script_result,
            "video_url": video_url,
            "cloud_url": cloud_url,
            "status": "completed" if video_url else "script_only"
        }

    def _generate_vton_image(self, product_image_path: str) -> str:
        """
        Call HuggingFace Spaces (yisol/IDM-VTON) to place the product on a model (Free Tier).
        Returns path to the saved fitted image, or None if failed.
        """
        # Configuration
        HF_SPACE_ID = "yisol/IDM-VTON"
        # Use product image as human model if no dedicated model image exists (for prototype)
        # In production: Download a high-res 'model_standing.jpg' to static/
        temp_human_path = product_image_path 
        
        if not os.path.exists(product_image_path):
             return None
             
        print(f"    Sending request to HuggingFace Space ({HF_SPACE_ID})...")
        
        try:
            from gradio_client import Client, handle_file
            import shutil
            
            client = Client(HF_SPACE_ID)
            
            # Verified Signature for yisol/IDM-VTON Space:
            # 1. dict (ImageEditor)
            # 2. garm_img
            # 3. garment_des
            # 4. is_checked (bool)
            # 5. is_checked_crop (bool)
            # 6. denoise_steps (int)
            # 7. seed (int)
            
            result = client.predict(
                    {"background": handle_file(temp_human_path), "layers": [], "composite": None},
                    handle_file(product_image_path),
                    "product image",
                    True,   # is_checked
                    False,  # is_checked_crop
                    30,     # denoise_steps
                    42,     # seed
                    api_name="/tryon"
            )
            
            # Result is tuple (output_path, masked_path)
            fitted_path = result[0]
            
            if fitted_path and os.path.exists(fitted_path):
                 filename = f"fitted_hf_{os.path.basename(product_image_path)}"
                 save_path = os.path.join("uploads", filename)
                 shutil.copy(fitted_path, save_path)
                 return os.path.abspath(save_path)
                 
        except Exception as e:
             # Just print error and return None -> Fallback to original image
             print(f"    VTON Failed (Free Tier might be busy): {e}")
             
        return None

    def _generate_script(self, product_data: Dict, market_data: Dict, emotional_data: Dict, hook_data: Dict) -> Dict[str, Any]:
        """Use LLM to write a viral short-form script."""
        
        product_name = product_data.get("product_name", "Our Product")
        best_hook = hook_data.get("best_hook", f"Check out {product_name}")
        emotions = emotional_data.get("primary_emotion", "Excitement")
        competitor_trends = market_data.get("market_trends", [])
        
        s_prompt = f"""
        You are an expert Video Marketing Director for Instagram Reels and YouTube Shorts.
        Create a 15-second viral video script for a product.
        
        PRODUCT: {product_name}
        HOOK: {best_hook}
        EMOTION: {emotions}
        MARKET CONTEXT: {', '.join(competitor_trends[:3])}
        
        REQUIREMENTS:
        1. Tone: "Gen-Z" style (trendy, fast-paced, authentic, TikTok/Reels native).
        2. Format: Short-form (9:16 aspect ratio focus).
        3. Structure: 
           - 0-3s: The Hook (Visual + Text Overlay).
           - 3-10s: The Value/Action (Fast cuts, dynamic).
           - 10-15s: The CTA (Call to Action).
            - "title": Video title.
            - "script_scenes": List of objects {{"seconds": "0-3", "visual": "...", "audio": "..."}}.
            - "video_prompt": A single, highly descriptive prompt optimized for OpenAI Sora (max 300 chars). CRITICAL: Include "The model is wearing the exact same t-shirt as the reference image. Do not change the t-shirt design, logo, or color. High fashion, cinematic lighting."
        
        CRITICAL: DO NOT include ANY emojis in the script title, scenes, or video prompt.
        """
        
        response = self._call_llm(
            system_prompt="You are a creative director for high-performing social media video ads.",
            user_prompt=s_prompt,
            json_mode=True
        )
        return response

    def _generate_video_file(self, prompt: str, image_path: str = None) -> tuple[str | None, str | None]:
        """Call FastRouter API to generate video."""
        
        payload = {
            "model": "openai/sora-2", # Or specific image-to-video model if different
            "length": 10, 
            "prompt": prompt,
            "aspect_ratio": "9:16"
        }
        
        # Add Image if provided
        if image_path and os.path.exists(image_path):
            import base64
            try:
                with open(image_path, "rb") as img_file:
                    b64_string = base64.b64encode(img_file.read()).decode('utf-8')
                    # Standard format for many APIs: Data URI or raw base64
                    payload["image"] = f"data:image/jpeg;base64,{b64_string}"
            except Exception as e:
                print(f" Failed to process image for video: {e}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.post(self.fastrouter_url, headers=headers, json=payload, timeout=300)
        
        if response.status_code == 200:
            try:
                data = response.json()
            except:
                print(f" Failed to parse JSON response: {response.text[:200]}")
                return None, None
                
            # Safe extraction of task_id
            task_id = data.get("id") if data else None
            if not task_id and data and isinstance(data, dict):
                data_obj = data.get("data")
                if isinstance(data_obj, dict):
                    task_id = data_obj.get("id")
            
            if not task_id:
                # Maybe it returned a URL directly?
                url = data.get("url") if data else None
                if not url and data and isinstance(data, dict):
                    data_obj = data.get("data")
                    if isinstance(data_obj, dict):
                        url = data_obj.get("url")
                return None, url if url else None
            
            print(f"   Video Task ID: {task_id}. Polling for result...")
            return self._poll_and_download_video(task_id)
        else:
            print(f" API Error {response.status_code}: {response.text[:200]}")
            return None, None

    def _poll_and_download_video(self, task_id: str) -> tuple[str | None, str | None]:
        """Poll the status and download video to local disk. Returns (local_url, cloud_url)."""
        import time
        
        poll_url = "https://go.fastrouter.ai/api/v1/getVideoResponse"
        output_dir = os.path.join(os.getcwd(), "static", "videos")
        os.makedirs(output_dir, exist_ok=True)
        filename = f"video_{task_id}.mp4"
        output_path = os.path.abspath(os.path.join(output_dir, filename))
        
        for i in range(20):
            print(f"   Still rendering video... (Check {i+1}/20)")
            time.sleep(10) 
            try:
                # The API returns the video binary directly on success
                response = requests.post(
                    poll_url,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={"taskId": task_id, "model": "openai/sora-2"},
                    stream=True,
                    timeout=300
                )
                
                # Check if we got a video file
                content_type = response.headers.get("Content-Type", "")
                if response.status_code == 200 and ("video" in content_type or "application/octet-stream" in content_type):
                    print(f"   Downloading video to {output_path}...")
                    
                    # Capture the Cloud URL (final URL after redirects)
                    cloud_url = response.url
                    
                    with open(output_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print("   Video download complete.")
                    
                    # Return the full filesystem path so it can be used for social media uploads
                    # The backend will use this to post to Instagram, etc.
                    return output_path, cloud_url
                else:
                    print(f"   Status: {response.status_code} (attempt {i+1}/20)...")
                    
            except Exception as e:
                print(f"   Polling error: {e}")
        
        # If we failed to get it after retries
        print("   Video generation timed out or failed.")
        return None, None

