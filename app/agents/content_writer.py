import os
import json
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from openai import AzureOpenAI
from app.agents.state import AgentState
from app.utils.publisher import SocialMediaPublisher

class ContentWriterAgent:
    """
    Generates platform-specific marketing content using LLMs.
    
    Uses market research data and vision analysis to create:
    - LinkedIn Posts (Professional)
    - Medium/Blog Posts (SEO-optimized)
    - Meta (FB/IG) Posts (Engaging)
    """
    
    def __init__(self, model_name: str = None, temperature: float = 0.7):
        """Initialize with Azure OpenAI credentials."""
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_key = os.getenv("AZURE_OPENAI_KEY")
        self.deployment_name = model_name or os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")
        api_version = os.getenv("AZURE_API_VERSION", "2024-02-15-preview")
        self.temperature = temperature
        
        if not azure_endpoint or not azure_key:
            raise ValueError("Azure OpenAI credentials not found in environment.")
        
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=azure_key,
            api_version=api_version,
        )
        
        # Initialize the publisher for posting to social media
        self.publisher = SocialMediaPublisher()

    def generate_content(
        self, 
        product_data: Dict, 
        market_data: Dict, 
        category_data: Dict = None, 
        competitor_data: Dict = None,
        emotional_data: Dict = None,
        hook_data: Dict = None
    ) -> Dict[str, Any]:
        """Generate content for all platforms in one LLM call for efficiency."""
        
        # Category-specific Strategy
        category_instruction = ""
        platform_instructions = ""
        category_name = None
        
        if category_data and category_data.get("category"):
            try:
                from app.agents.prompts.category_prompts import CATEGORY_PROMPTS
                cat_key = category_data["category"]
                category_name = cat_key
                
                if cat_key in CATEGORY_PROMPTS:
                    prompts = CATEGORY_PROMPTS[cat_key]
                    category_instruction = f"""
CONTENT STRATEGY FOR {cat_key.upper().replace('_', ' ')}:
TONE: {prompts['content_tone']}
KEY ANGLES: {', '.join(prompts['key_angles'])}
KEYWORDS TO USE: {', '.join(prompts.get('keywords', []))}

HANDLING OBJECTIONS:
{json.dumps(prompts.get('objection_handlers', {}), indent=2)}
"""
                    # Overwrite platform adjustments if available
                    if "platform_adjustments" in prompts:
                         platform_instructions = json.dumps(prompts["platform_adjustments"], indent=2)

            except ImportError:
                pass
        
        # Competitor Intelligence Context
        competitor_context = ""
        if competitor_data and not competitor_data.get("error") and competitor_data.get("analysis"):
            try:
                analysis = competitor_data.get("analysis", {})
                competitor_context = f"""
COMPETITIVE INTELLIGENCE (PHASE 2):
The following insights were derived from visual analysis of top competitors:
- Common Visual Trends: {', '.join(analysis.get('visual_trends', []))}
- Differentiation Opportunities: {', '.join(analysis.get('swot', {}).get('opportunities', []))}
- STRATEGIC ADVICE: {', '.join(analysis.get('strategic_advice', []))}

CRITICAL: You MUST incorporate the 'Strategic Advice' into the content to ensure the product stands out against these competitors.
"""
            except Exception as e:
                print(f"Error processing competitor data: {e}")

        # Emotional Trigger Context
        emotional_context = ""
        if emotional_data and not emotional_data.get("error"):
            try:
                emotional_context = f"""
EMOTIONAL PSYCHOLOGY (PHASE 2.2):
The following psychological triggers have been identified for this product:
- Primary Emotion: {emotional_data.get('primary_emotion', 'Unknown')}
- Secondary Emotion: {emotional_data.get('secondary_emotion', 'Unknown')}
- Key Triggers: {', '.join(emotional_data.get('psychological_triggers', []))}
- Messaging Hooks:
{json.dumps(emotional_data.get('messaging_hooks', []), indent=2)}

GUIDANCE: Infuse the copy with these emotions. Use the triggers to create a deeper connection.
"""
            except Exception as e:
                print(f"Error processing emotional data: {e}")

        # Viral Hook Context (Phase 2.3)
        hook_context = ""
        if hook_data and not hook_data.get("error"):
            try:
                hooks = hook_data.get("hooks", [])
                best_hook = hook_data.get("best_hook", "N/A")
                hook_context = f"""
VIRAL HOOKS (PHASE 2.3):
Use one of these high-converting opening hooks for the social media posts:
- Best Option: "{best_hook}"
- Alternatives:
{json.dumps([h.get('text') for h in hooks], indent=2)}

GUIDANCE: Start the LinkedIn and Instagram captions with the 'Best Option' or a strong variation.
"""
            except Exception as e:
                print(f"Error processing hook data: {e}")
        
        system_prompt = f"""You are an expert Content Strategist and Copywriter. 
Your goal is to create high-converting, SEO-friendly marketing content for a product based on its visual analysis and market research.

{category_instruction}

{competitor_context}

{emotional_context}

{hook_context}

Platforms to cover:
1. LinkedIn: Professional, insightful. {f"Strategy: {json.loads(platform_instructions).get('linkedin', '')}" if platform_instructions else ""}
2. Medium/Blog: Informative, long-form, SEO-optimized.
3. Meta (Facebook/Instagram): Engaging, visual-focused. {f"Strategy: {json.loads(platform_instructions).get('instagram', '')}" if platform_instructions else ""}

Guidelines:
- Use the 'Key Features' and 'Selling Points' from the vision analysis.
- Incorporate 'Customer Pain Points' or 'Positive Feedback' found in market research.
- Ensure the tone is consistent with the product's visual style{f" AND the strategy for {category_name}" if category_name else ""}.
- Include SEO keywords naturally.
- Provide the output as a structured JSON object."""

        user_prompt = f"""
PRODUCT DATA:
{json.dumps(product_data, indent=2)}

CATEGORY DATA:
{json.dumps(category_data, indent=2) if category_data else "Not available"}

MARKET RESEARCH SUMMARY:
- Search Term: {market_data.get('search_term')}
- Top Features Found: {market_data.get('features', [])[:5]}
- Review Sentiment: {market_data.get('metadata', {}).get('total_reviews', 0)} reviews analyzed.

Generate the following in JSON format:
{{
  "linkedin_post": {{
    "title": "Catchy Headline",
    "content": "Professional post body...",
    "hashtags": ["#tag1", "#tag2"]
  }},
  "blog_post": {{
    "title": "SEO Optimized Title",
    "content": "Full blog content with markdown headings...",
    "seo_keywords": ["keyword1", "keyword2"]
  }},
  "meta_post": {{
    "caption": "Catchy caption...",
    "hashtags": ["#tag1", "#tag2"]
  }}
}}

CRITICAL: DO NOT include ANY emojis in the content. Use only plain text for all captions and posts.
"""

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)

    def __call__(self, state: AgentState) -> AgentState:
        """LangGraph node function."""
        print("Content Writer Agent: Generating marketing content...")
        
        try:
            product_data = state.get("product_data", {})
            market_data = state.get("market_data", {})
            
            if not product_data or not market_data:
                state["errors"].append("Content Writer: Missing product or market data.")
                return state
            
            category_data = state.get("category_data", {})
            competitor_data = state.get("competitor_data", {})
            emotional_data = state.get("emotional_data", {})
            hook_data = state.get("hook_data", {})
            
            generated = self.generate_content(product_data, market_data, category_data, competitor_data, emotional_data, hook_data)
            
            # Update state
            state["generated_content"] = generated
            state["current_step"] = "content_generation_complete"
            
            state["messages"].append(
                SystemMessage(content="Marketing content generated for LinkedIn, Blog, and Meta.")
            )
            
            print("Content generation complete!")
            
            # Post to LinkedIn
            print("\nContent Writer Agent: Posting to LinkedIn...")
            linkedin_post = generated.get("linkedin_post", {})
            if linkedin_post:
                image_path = state.get("product_image_path")
                # Remove emojis and special characters from content for LinkedIn
                title = linkedin_post.get("title", "").encode('ascii', 'ignore').decode('ascii')
                content = linkedin_post.get("content", "").encode('ascii', 'ignore').decode('ascii')
                linkedin_result = self.publisher.post_to_linkedin(
                    title=title,
                    content=content,
                    hashtags=linkedin_post.get("hashtags", []),
                    image_path=image_path
                )
                state["linkedin_post_result"] = linkedin_result
                
                if linkedin_result.get("status") == "success":
                    print(f"[OK] LinkedIn post published successfully!")
                    state["messages"].append(
                        SystemMessage(content=f"LinkedIn post published: {linkedin_result.get('data', {}).get('id', 'unknown')}")
                    )
                else:
                    error = linkedin_result.get("message", "Unknown error")
                    print(f"[ERROR] LinkedIn post failed: {error}")
                    state["errors"].append(f"LinkedIn posting error: {error}")
            
            # Post to Meta (Facebook/Instagram)
            print("\nContent Writer Agent: Posting to Meta...")
            
            try:
                # DEBUG LOGGING
                with open("meta_debug.log", "a", encoding="utf-8") as f:
                    f.write(f"\n\n--- Posting Attempt (Refactored) ---\n")
                    f.write(f"Generated Keys: {list(generated.keys())}\n")

                # Robust extraction
                meta_post = generated.get("meta_post")
                
                # Check for case sensitivity or alternative keys
                if not meta_post:
                    for key in generated.keys():
                        if "meta" in key.lower() or "facebook" in key.lower():
                            meta_post = generated[key]
                            break

                with open("meta_debug.log", "a", encoding="utf-8") as f:
                    f.write(f"Raw meta_post extracted: {meta_post}\n")

                if meta_post and isinstance(meta_post, dict):
                    caption = meta_post.get("caption", "")
                    # Fallback if no caption key
                    if not caption:
                        caption = meta_post.get("content", "")
                        
                    hashtags = meta_post.get("hashtags", [])
                    
                    with open("meta_debug.log", "a", encoding="utf-8") as f:
                        f.write(f"Final Caption: {caption[:50]}...\n")

                    if caption:
                        # Get image path from state (same as LinkedIn)
                        image_path = state.get("product_image_path")
                        
                        # INSTANTIATE FRESH PUBLISHER to match verify_integration.py behavior
                        from app.utils.publisher import SocialMediaPublisher
                        local_publisher = SocialMediaPublisher()
                        
                        meta_result = local_publisher.post_to_meta(
                            caption=caption,
                            hashtags=hashtags,
                            image_path=image_path  # Pass image path instead of URL
                        )
                        
                        with open("meta_debug.log", "a", encoding="utf-8") as f:
                            f.write(f"Publisher Result: {meta_result}\n")
                        
                        state["meta_post_result"] = meta_result
                        
                        if meta_result.get("status") == "success":
                            print(f"[OK] Meta post published successfully!")
                            state["messages"].append(
                                SystemMessage(content=f"Meta post published: {meta_result.get('data', {}).get('id', 'unknown')}")
                            )
                        else:
                            error = meta_result.get("message", "Unknown error")
                            print(f"[ERROR] Meta post failed: {error}")
                            state["errors"].append(f"Meta posting error: {error}")
                    else:
                        print("  ⚠️ Meta content found but caption is empty")
                        with open("meta_debug.log", "a", encoding="utf-8") as f:
                            f.write("FAIL: Empty caption\n")
                else:
                    print("  ⚠️ No valid 'meta_post' dictionary found in AI output")
                    with open("meta_debug.log", "a", encoding="utf-8") as f:
                        f.write("FAIL: meta_post missing or not a dict\n")
                        
            except Exception as e:
                print(f"  ❌ CRITIAL ERROR in Meta Block: {e}")
                with open("meta_debug.log", "a", encoding="utf-8") as f:
                    f.write(f"CRASH: {str(e)}\n")
            
        except Exception as e:
            error_msg = f"Content Writer Error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"Error: {error_msg}")
            
        return state
