"""
Agent Wrapper - Adapts LangGraph agents to work with the backend

This module provides a simplified interface to your existing agents,
handling the conversion between backend data structures and agent state.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


class AgentWrapper:
    """
    Wrapper class that adapts your LangGraph agents to work with the backend.
    
    This handles:
    - Converting backend Project data to AgentState
    - Running agents with proper error handling
    - Extracting results from AgentState
    """
    
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.use_mock = os.getenv("USE_MOCK_AGENTS", "false").lower() == "true"
        
        # Only import agents if not using mocks
        if not self.use_mock:
            try:
                # Import your actual agents
                from app.agents.vision_analyzer import VisionAnalyzerAgent
                from app.agents.market_research import MarketResearchAgent
                from app.agents.content_writer import ContentWriterAgent
                from app.agents.image_generator import ImageGeneratorAgent
                from app.agents.category_detector import CategoryDetectorAgent  # New Agent
                from app.agents.visual_competitor_analyzer import VisualCompetitorAnalyzerAgent # Phase 2 Agent
                from app.agents.emotional_trigger_mapper import EmotionalTriggerMapperAgent     # Phase 2.2 Agent
                from app.agents.hook_generator import HookGeneratorAgent                        # Phase 2.3 Agent
                from app.agents.performance_predictor import PerformancePredictorAgent          # Phase 3.1 Agent
                from app.agents.video_creator import VideoCreatorAgent                          # Video Agent
                from app.agents.poster_generator import PosterGeneratorAgent                    # Poster Agent
                
                self.vision_agent = VisionAnalyzerAgent()
                self.research_agent = MarketResearchAgent()
                self.content_agent = ContentWriterAgent()
                self.image_agent = ImageGeneratorAgent()
                # self.image_agent = ImageGeneratorAgent() # Removed duplicate
                self.category_detector = CategoryDetectorAgent()  # Initialize
                # self.category_detector = CategoryDetectorAgent()  # Removed duplicate
                self.competitor_analyzer = VisualCompetitorAnalyzerAgent()
                self.emotional_mapper = EmotionalTriggerMapperAgent()
                self.hook_generator = HookGeneratorAgent()
                self.performance_predictor = PerformancePredictorAgent()
                self.video_creator = VideoCreatorAgent()
                self.poster_generator = PosterGeneratorAgent()
                
                print("Real agents loaded successfully")
            except Exception as e:
                print(f"Failed to load real agents: {e}")
                print("Falling back to mock agents")
                self.use_mock = True
    
    def run_category_detection(self, image_path: str, description: str) -> Dict[str, Any]:
        """
        Run category detection on a product.
        
        Args:
            image_path: Path to the product image
            description: Product description
            
        Returns:
            Category data dictionary
        """
        if self.use_mock:
            return self._mock_category_detection()
        
        try:
            from app.agents.state import AgentState
            
            # Create minimal state for classification
            state = AgentState(
                messages=[],
                product_image_path=image_path or "", 
                product_description=description or "",
                product_data={},
                market_data={},
                campaign_goal=None,
                target_audience=None,
                brand_persona=None,
                generated_images=[],
                generated_content={},
                category_data={},
                errors=[]
            )
            
            # Run the agent
            updated_state = self.category_detector.detect_category(state)
            return updated_state.get("category_data", {})
        except Exception as e:
            print(f"Category detection error: {e}")
            return self._mock_category_detection()
    
    def run_vision_analysis(self, image_path: str, product_name: str, description: str = "", category: str = None) -> Dict[str, Any]:
        """
        Run vision analysis on a product image.
        
        Args:
            image_path: Path to the product image
            product_name: Name of the product
            description: Optional product description
            category: Detected product category (optional)
            
        Returns:
            Product data dictionary
        """
        if self.use_mock:
            return self._mock_vision_analysis(product_name)
        
        try:
            # Use your actual agent
            result = self.vision_agent.analyze_product_image(image_path, description, category)
            return result
        except Exception as e:
            print(f"Vision analysis error: {e}")
            return self._mock_vision_analysis(product_name)

    def run_competitor_analysis(
        self,
        image_path: str,
        product_data: Dict[str, Any],
        category_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run visual competitor analysis.
        """
        if self.use_mock:
            return self._mock_competitor_analysis()
        
        try:
            from app.agents.state import AgentState
            
            # Create minimal state
            state = AgentState(
                messages=[],
                product_image_path=image_path,
                product_description="",
                product_data=product_data,
                category_data=category_data,
                competitor_data={},
                # ... others empty
                market_data={}, campaign_goal=None, target_audience=None, brand_persona=None,
                generated_images=[], generated_content={}, errors=[]
            )
            
            updated_state = self.competitor_analyzer(state)
            return updated_state.get("competitor_data", {})
            
        except Exception as e:
            print(f" Competitor analysis error: {e}")
            import traceback
            traceback.print_exc()
            print(" Falling back to mock data. Check Brave API key and Azure OpenAI credentials.")
            return self._mock_competitor_analysis()

    def run_emotional_analysis(self, product_data: Dict[str, Any], category: str = None) -> Dict[str, Any]:
        """Run emotional trigger analysis."""
        if self.use_mock:
            return self._mock_emotional_analysis()
        
        try:
             # Minimal state creation not strictly needed if agent just takes dicts,
             # but BaseAgent.execute takes kwargs.
             # EmotionalTriggerMapperAgent.execute takes (product_data, category).
             # We can call it directly if mapped correctly.
             result = self.emotional_mapper.execute(product_data=product_data, category=category)
             return result
        except Exception as e:
             print(f"Emotional analysis error: {e}")
             return self._mock_emotional_analysis()
    
    def run_hook_generation(self, product_data: Dict[str, Any], emotional_data: Dict[str, Any], competitor_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run hook generation."""
        if self.use_mock:
            return self._mock_hook_generation()
        
        try:
             result = self.hook_generator.execute(
                 product_data=product_data, 
                 emotional_data=emotional_data, 
                 competitor_data=competitor_data
             )
             return result
        except Exception as e:
             print(f"Hook generation error: {e}")
             return self._mock_hook_generation()
    
    def run_market_research(
        self, 
        product_name: str, 
        brand_name: str,
        product_data: Dict[str, Any],
        category: str = None
    ) -> Dict[str, Any]:
        """
        Run market research for a product.
        
        Args:
            product_name: Name of the product
            brand_name: Brand name
            product_data: Vision analysis results
            category: Product category (optional)
            
        Returns:
            Market research data dictionary
        """
        if self.use_mock:
            return self._mock_market_research(product_name)
        
        try:
            # Create minimal state for the agent
            from app.agents.state import AgentState
            
            state = AgentState(
                messages=[],
                product_image_path="",
                product_description="",
                product_data=product_data,
                category_data={"category": category} if category else {},
                market_data={},
                generated_images=[],
                generated_content={},
                errors=[]
            )
            
            # Run the agent
            updated_state = self.research_agent(state)
            return updated_state.get("market_data", {})
            
        except Exception as e:
            print(f"Market research error: {e}")
            return self._mock_market_research(product_name)
    
    def run_content_generation(
        self,
        product_data: Dict[str, Any],
        market_data: Dict[str, Any],
        campaign_goal: Optional[str] = None,
        target_audience: Optional[str] = None,
        brand_persona: Optional[str] = None,
        product_image_path: Optional[str] = None,
        category: str = None,
        hook_data: Optional[Dict[str, Any]] = None  # Phase 2.3
    ) -> Dict[str, Any]:
        """
        Generate marketing content.
        
        Args:
            product_data: Vision analysis results
            market_data: Market research results
            campaign_goal: Campaign objective
            target_audience: Target demographic
            brand_persona: Brand voice/personality
            product_image_path: Path to the product image file
            category: Product category
            hook_data: Generated viral hooks (optional)
            
        Returns:
            Generated content dictionary
        """
        if self.use_mock:
            return self._mock_content_generation(product_data.get("product_name", "Product"))
        
        try:
            from app.agents.state import AgentState
            
            state = AgentState(
                messages=[],
                product_image_path=product_image_path or "",  # Use the passed path!
                product_description="",
                product_data=product_data,
                market_data=market_data,
                category_data={"category": category} if category else {},
                campaign_goal=campaign_goal,
                target_audience=target_audience,
                brand_persona={"voice": brand_persona} if brand_persona else None,
                hook_data=hook_data,  # Phase 2.3
                generated_images=[],
                generated_content={},
                errors=[]
            )
            
            # Run the agent
            updated_state = self.content_agent(state)
            return updated_state.get("generated_content", {})
            
        except Exception as e:
            print(f"Content generation error: {e}")
            return self._mock_content_generation(product_data.get("product_name", "Product"))

    def run_performance_prediction(
        self,
        content_data: Dict[str, Any],
        emotional_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Run performance prediction."""
        if self.use_mock:
            return self._mock_performance_prediction()
            
        try:
            return self.performance_predictor.execute(content_data, emotional_data)
        except Exception as e:
            print(f"Performance prediction error: {e}")
            return self._mock_performance_prediction()
    
    def run_image_generation(
        self,
        product_data: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate marketing images (optional).
        
        Args:
            product_data: Vision analysis results
            market_data: Market research results
            
        Returns:
            Generated images data
        """
        if self.use_mock:
            return self._mock_image_generation()
        
        try:
            from app.agents.state import AgentState
            
            state = AgentState(
                messages=[],
                product_image_path="",
                product_description="",
                product_data=product_data,
                market_data=market_data,
                generated_images=[],
                generated_content={},
                errors=[]
            )
            
            # Run the agent
            updated_state = self.image_agent(state)
            return {
                "generated_images": updated_state.get("generated_images", [])
            }
            
        except Exception as e:
            print(f"Image generation error: {e}")
            return self._mock_image_generation()
    
    # ============================================
    # MOCK IMPLEMENTATIONS (Fallback)
    # ============================================
    
    def _mock_vision_analysis(self, product_name: str) -> Dict[str, Any]:
        """Mock vision analysis for testing without API keys"""
        return {
            "product_name": product_name,
            "category": "General Product",
            "primary_colors": ["Blue", "White"],
            "material": "Premium materials",
            "key_features": [
                "High quality construction",
                "Modern design",
                "User-friendly interface"
            ],
            "target_demographic": "General consumers",
            "visual_style": "Modern and professional",
            "selling_points": [
                "Quality craftsmanship",
                "Innovative features",
                "Great value"
            ]
        }
    
    def _mock_market_research(self, product_name: str) -> Dict[str, Any]:
        """Mock market research for testing"""
        return {
            "competitors": ["Competitor A", "Competitor B"],
            "market_trends": [
                "Growing demand for quality products",
                "Shift towards sustainable options"
            ],
            "customer_pain_points": [
                "Need for better quality",
                "Looking for value"
            ],
            "pricing_insights": {
                "average_price": "$500-$1000",
                "price_range": "Mid to premium"
            },
            "metadata": {
                "total_results": 10,
                "total_reviews": 50,
                "total_features": 15
            }
        }
    
    def _mock_content_generation(self, product_name: str) -> Dict[str, Any]:
        """Mock content generation for testing"""
        return {
            "linkedin_post": {
                "title": f"Introducing {product_name}",
                "content": f"We're excited to announce {product_name}! "
                          f"This innovative product combines quality, design, and functionality. "
                          f"Perfect for professionals who demand the best. #Innovation #Quality",
                "hashtags": ["#Innovation", "#Quality", "#NewProduct"]
            },
            "meta_post": {
                "caption": f" Check out {product_name}! The perfect blend of style and substance. "
                          f"Available now! #NewProduct #Innovation",
                "hashtags": ["#NewProduct", "#Innovation", "#Quality"]
            },
            "blog_post": {
                "title": f"Introducing {product_name}: Innovation Meets Design",
                "content": f"# {product_name}\n\n"
                          f"We're thrilled to introduce {product_name}, our latest innovation "
                          f"that combines cutting-edge technology with elegant design.\n\n"
                          f"## Key Features\n"
                          f"- Premium quality construction\n"
                          f"- Modern, user-friendly design\n"
                          f"- Exceptional value\n\n"
                          f"Experience the difference today!",
                "seo_keywords": ["innovation", "quality", product_name.lower()]
            }
        }
    
    def _mock_image_generation(self) -> Dict[str, Any]:
        """Mock image generation for testing"""
        return {
            "generated_images": [
                {
                    "type": "social_media_post",
                    "url": "https://via.placeholder.com/1200x630/4A90E2/ffffff?text=Social+Media+Post",
                    "prompt": "Marketing image for social media"
                },
                {
                    "type": "blog_header",
                    "url": "https://via.placeholder.com/1920x1080/7B68EE/ffffff?text=Blog+Header",
                    "prompt": "Blog post header image"
                }
            ]
        }
        
    def _mock_category_detection(self) -> Dict[str, Any]:
        """Mock category detection for testing"""
        return {
            "category": "tech_gadgets",
            "subcategory": "mock_device",
            "confidence": 0.99,
            "reasoning": "Mock detection based on random seed."
        }

    def _mock_competitor_analysis(self) -> Dict[str, Any]:
        """Mock competitor analysis"""
        return {
            "competitors_found": [
                {"title": "Mock Competitor 1", "image_url": "https://example.com/c1.jpg"},
                {"title": "Mock Competitor 2", "image_url": "https://example.com/c2.jpg"}
            ],
            "analysis": {
                "visual_trends": ["Minimalist", "White background"],
                "differentiation_score": 7,
                "swot": {
                    "strengths": ["Unique shape"],
                    "weaknesses": ["Dark lighting"],
                    "opportunities": ["Use brighter colors"],
                    "threats": ["Established brands"]
                },
                "strategic_advice": ["Increase exposure"]
            }
        }

    def _mock_emotional_analysis(self) -> Dict[str, Any]:
        """Mock emotional analysis"""
        return {
            "primary_emotion": "Trust",
            "secondary_emotion": "Confidence",
            "psychological_triggers": ["Authority", "Reliability"],
            "messaging_hooks": ["Experience the difference trusted by professionals."],
            "visual_cues": ["Blue color palette", "Clean lines"]
        }

    def _mock_hook_generation(self) -> Dict[str, Any]:
        """Mock hook generation"""
        return {
            "hooks": [
                {"type": "Curiosity", "text": "The one thing missing from your daily routine..."},
                {"type": "Problem-Agitation", "text": "Tired of slow connections?"}
            ],
            "best_hook": "The one thing missing from your daily routine..."
        }

    def _mock_performance_prediction(self) -> Dict[str, Any]:
        """Mock performance prediction"""
        return {
            "global_score": 85.0,
            "platform_predictions": {
                "linkedin": {
                    "score": 88,
                    "metrics": {"predicted_ctr": "1.5%", "reach_potential": "High"},
                    "strengths": ["Strong hook", "Good professional tone"],
                    "improvements": ["Add a question"]
                }
            },
            "analysis_version": "Mock 1.0"
        }

    def run_video_creation(self, product_data: Dict[str, Any], market_data: Dict[str, Any], emotional_data: Dict[str, Any], hook_data: Dict[str, Any], image_path: str = None) -> Dict[str, Any]:
        """Run video creation agent."""
        if self.use_mock:
            return self._mock_video_creation()
        
        try:
            return self.video_creator.execute(
                product_data=product_data,
                market_data=market_data,
                emotional_data=emotional_data,
                hook_data=hook_data,
                image_path=image_path
            )
        except Exception as e:
            print(f"Video creation error: {e}")
            return self._mock_video_creation()

    def run_poster_generation(self, product_data: Dict[str, Any], emotional_data: Dict[str, Any], hook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run poster generation agent."""
        if self.use_mock:
            # Mock implementation
            return {"status": "skipped", "message": "Mock Poster"}
        
        try:
            return self.poster_generator.execute(
                product_data=product_data,
                emotional_data=emotional_data,
                hook_data=hook_data
            )
        except Exception as e:
            print(f"Poster creation error: {e}")
            return {"status": "error", "message": str(e)}

    def _mock_video_creation(self) -> Dict[str, Any]:
        """Mock video creation"""
        return {
            "video_script": {
                "title": "Mock Video Script",
                "script_scenes": [{"seconds": "0-15", "visual": "Show product", "audio": "Music"}],
                "video_prompt": "Cinematic shot of product"
            },
            "video_url": "https://example.com/mock_video.mp4",
            "status": "mocked"
        }

# Global instance
_agent_wrapper = None

def get_agent_wrapper() -> AgentWrapper:
    """Get or create the global agent wrapper instance"""
    global _agent_wrapper
    if _agent_wrapper is None:
        _agent_wrapper = AgentWrapper()
    return _agent_wrapper
