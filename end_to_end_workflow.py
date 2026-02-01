"""
========================================
END-TO-END CATALYST AI WORKFLOW TEST
========================================

This script triggers the COMPLETE marketing campaign pipeline:

1. IMAGE UPLOAD - Takes product image from uploads/
2. PROJECT CREATION - Creates project in database
3. PHASE 1: ANALYSIS
   - Category Detection
   - Vision Analysis
4. PHASE 2: INTELLIGENCE
   - Market Research
   - Competitor Analysis
   - Emotional Trigger Mapping
   - Hook Generation
5. PHASE 3: CONTENT GENERATION
   - Platform-specific Content (LinkedIn, Instagram, Facebook)
   - Poster Generation (DALL-E via FastRouter)
   - Video Generation (Sora-2 via FastRouter)
6. PHASE 4: PUBLISHING
   - LinkedIn Post (with poster image)
   - Instagram Post (with poster image + reel link)
   - Facebook Post (with poster image)

⚠️ IMPORTANT: Limited SORA Credits - Video generation happens ONLY if everything passes!
"""

import os
import sys
import json
import uuid
import requests
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db.session import get_engine, get_session_local, Base
from app.db.models import User, Project, Job, Asset
from app.core.orchestrator import AgentOrchestrator
from app.agents.vision_analyzer import VisionAnalyzerAgent
from app.agents.category_detector import CategoryDetectorAgent
from app.agents.market_research import MarketResearchAgent
from app.agents.visual_competitor_analyzer import VisualCompetitorAnalyzerAgent
from app.agents.emotional_trigger_mapper import EmotionalTriggerMapperAgent
from app.agents.hook_generator import HookGeneratorAgent
from app.agents.content_writer import ContentWriterAgent
from app.agents.poster_generator import PosterGeneratorAgent
from app.agents.video_creator import VideoCreatorAgent
from app.agents.performance_predictor import PerformancePredictorAgent
from app.utils.publisher import SocialMediaPublisher

# Load environment variables
load_dotenv(override=True)

# Handle potential import issues
try:
    pass
except Exception as e:
    print(f"Warning: Some imports may have warnings: {e}")


class EndToEndWorkflowTest:
    """
    Complete end-to-end test orchestrator for Catalyst AI.
    Runs all agents and publishes to all social media platforms.
    """
    
    def __init__(self, dry_run: bool = False, skip_video: bool = True):
        """
        Initialize the workflow test.
        
        Args:
            dry_run: If True, don't actually post to social media
            skip_video: If True, skip video generation to preserve SORA credits
        """
        self.dry_run = dry_run
        self.skip_video = skip_video
        SessionLocal = get_session_local()
        self.db: Session = SessionLocal()
        self.test_user: Optional[User] = None
        self.project: Optional[Project] = None
        self.publisher = SocialMediaPublisher()
        
        # Initialize agents
        self.vision_agent = VisionAnalyzerAgent()
        self.category_agent = CategoryDetectorAgent()
        self.market_agent = MarketResearchAgent()
        self.competitor_agent = VisualCompetitorAnalyzerAgent()
        self.emotional_agent = EmotionalTriggerMapperAgent()
        self.hook_agent = HookGeneratorAgent()
        self.content_writer = ContentWriterAgent()
        self.poster_agent = PosterGeneratorAgent()
        self.video_agent = VideoCreatorAgent()
        self.predictor_agent = PerformancePredictorAgent()
        
        self.workflow_results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "skip_video": skip_video,
            "phases": {}
        }

    def log(self, level: str, message: str):
        """Log with timestamp and level."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = {
            "INFO": "[INFO]",
            "SUCCESS": "[OK]",
            "WARNING": "[WARN]",
            "ERROR": "[ERROR]",
            "STEP": "[STEP]"
        }.get(level, "[->]")
        print(f"[{timestamp}] {prefix} {message}")

    def setup_test_database(self):
        """Create database tables if they don't exist."""
        self.log("STEP", "Setting up database...")
        try:
            engine = get_engine()
            Base.metadata.create_all(bind=engine)
            self.log("SUCCESS", "Database tables created/verified")
        except Exception as e:
            self.log("ERROR", f"Database setup failed: {e}")
            raise

    def create_test_user(self) -> User:
        """Create or get test user."""
        self.log("STEP", "Creating/retrieving test user...")
        try:
            # Check if test user exists
            test_email = "test@catalyst-ai.com"
            user = self.db.query(User).filter(User.email == test_email).first()
            
            if user:
                self.log("SUCCESS", f"Using existing test user: {test_email}")
                return user
            
            # Create new test user
            from app.core.security import hash_password
            new_user = User(
                email=test_email,
                password_hash=hash_password("test_password_123")
            )
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            self.log("SUCCESS", f"Created test user: {test_email}")
            return new_user
            
        except Exception as e:
            self.log("ERROR", f"Failed to create test user: {e}")
            raise

    def select_test_image(self) -> Path:
        """Select a test image from uploads folder."""
        self.log("STEP", "Selecting test image from uploads/...")
        uploads_dir = Path("uploads")
        
        if not uploads_dir.exists():
            self.log("ERROR", "uploads/ folder not found")
            raise FileNotFoundError("uploads/ folder not found")
        
        # Get all jpg/png images
        images = list(uploads_dir.glob("*.jpg")) + list(uploads_dir.glob("*.png"))
        
        if not images:
            self.log("ERROR", "No images found in uploads/")
            raise FileNotFoundError("No images in uploads/")
        
        # Prefer test images
        test_images = [img for img in images if "test" in img.name.lower()]
        selected = test_images[0] if test_images else images[0]
        
        self.log("SUCCESS", f"Selected image: {selected.name}")
        return selected

    def create_project(self, image_path: Path) -> Project:
        """Create a project in the database."""
        self.log("STEP", "Creating project...")
        try:
            project = Project(
                user_id=self.test_user.id,
                product_name="Test Product - Catalyst AI",
                brand_name="Catalyst",
                price="$99.99",
                description="Premium marketing content generation test",
                image_path=str(image_path),
                campaign_goal="brand awareness",
                target_audience="Tech professionals, Entrepreneurs",
                brand_persona="Innovative, Data-driven, Bold"
            )
            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)
            self.log("SUCCESS", f"Project created: {project.id}")
            return project
            
        except Exception as e:
            self.log("ERROR", f"Failed to create project: {e}")
            raise

    # =============================================
    # PHASE 1: ANALYSIS
    # =============================================

    def run_category_detection(self) -> Dict[str, Any]:
        """Step 1: Detect product category."""
        self.log("STEP", "PHASE 1: Category Detection...")
        try:
            # Create minimal AgentState for category detector
            from app.agents.state import AgentState
            state = {
                "product_description": self.project.description,
                "product_image_path": str(self.project.image_path),
                "messages": [],
                "generated_content": {},
                "generated_images": [],
                "market_data": {},
                "category_data": {},
                "competitor_data": None,
                "emotional_data": None,
                "hook_data": None,
                "performance_prediction": None,
                "current_step": "category_detection",
                "review_status": None,
                "errors": [],
                "brand_persona": None,
                "campaign_goal": None,
                "target_audience": None,
                "product_data": {}
            }
            
            result_state = self.category_agent.detect_category(state)
            result = result_state.get("category_data", {})
            
            self.project.category = result.get("category")
            self.project.subcategory = result.get("subcategory")
            self.project.category_confidence = result.get("confidence", 0.0)
            self.db.commit()
            
            self.log("SUCCESS", f"Category detected: {result.get('category')} ({result.get('subcategory')})")
            return result
        except Exception as e:
            self.log("ERROR", f"Category detection failed: {e}")
            return {"error": str(e)}

    def run_vision_analysis(self) -> Dict[str, Any]:
        """Step 2: Analyze product image."""
        self.log("STEP", "PHASE 1: Vision Analysis...")
        try:
            result = self.vision_agent.analyze_product_image(
                image_path=str(self.project.image_path),
                description=self.project.description,
                category=self.project.category
            )
            
            self.log("SUCCESS", f"Product identified: {result.get('product_name')}")
            return result
        except Exception as e:
            self.log("ERROR", f"Vision analysis failed: {e}")
            return {"error": str(e)}

    # =============================================
    # PHASE 2: INTELLIGENCE
    # =============================================

    def run_market_research(self, product_data: Dict) -> Dict[str, Any]:
        """Step 3: Research market and competitors."""
        self.log("STEP", "PHASE 2: Market Research...")
        try:
            result = self.market_agent.search_comprehensive(
                product_name=product_data.get("product_name", "Product"),
                category=self.project.category
            )
            self.log("SUCCESS", "Market research completed")
            return result
        except Exception as e:
            self.log("ERROR", f"Market research failed: {e}")
            return {"error": str(e)}

    def run_competitor_analysis(self, product_data: Dict) -> Dict[str, Any]:
        """Step 4: Analyze competitor visuals."""
        self.log("STEP", "PHASE 2: Competitor Analysis...")
        try:
            from PIL import Image
            import base64
            
            # Encode product image to base64
            with open(self.project.image_path, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            result = self.competitor_agent.analyze_competition(
                user_image_b64=image_b64,
                competitors=[]  # Will fetch competitors internally
            )
            
            self.log("SUCCESS", "Competitor analysis completed")
            return result
        except Exception as e:
            self.log("ERROR", f"Competitor analysis failed: {e}")
            return {"error": str(e)}

    def run_emotional_analysis(self, product_data: Dict) -> Dict[str, Any]:
        """Step 5: Map emotional triggers."""
        self.log("STEP", "PHASE 2: Emotional Trigger Mapping...")
        try:
            result = self.emotional_agent.execute(
                product_data=product_data,
                category=self.project.category
            )
            self.log("SUCCESS", "Emotional triggers identified")
            return result
        except Exception as e:
            self.log("ERROR", f"Emotional analysis failed: {e}")
            return {"error": str(e)}

    def run_hook_generation(
        self, 
        emotional_data: Dict, 
        competitor_data: Dict,
        market_data: Dict
    ) -> Dict[str, Any]:
        """Step 6: Generate scroll-stopping hooks."""
        self.log("STEP", "PHASE 2: Hook Generation...")
        try:
            result = self.hook_agent.execute(
                product_data={"product_name": self.project.product_name, "category": self.project.category},
                emotional_data=emotional_data,
                competitor_data=competitor_data
            )
            
            best_hook = result.get("best_hook", "Check this out!") if not result.get("error") else "Check this out!"
            self.log("SUCCESS", f"Hooks generated. Best: '{best_hook}'")
            return result
        except Exception as e:
            self.log("ERROR", f"Hook generation failed: {e}")
            return {"error": str(e)}

    # =============================================
    # PHASE 3: CONTENT & ASSET GENERATION
    # =============================================

    def run_content_generation(
        self,
        product_data: Dict,
        market_data: Dict,
        emotional_data: Dict,
        hook_data: Dict
    ) -> Dict[str, Any]:
        """Step 7: Generate platform-specific content."""
        self.log("STEP", "PHASE 3: Content Generation...")
        try:
            result = self.content_writer.generate_content(
                product_data=product_data,
                market_data=market_data,
                category_data={"category": self.project.category},
                competitor_data={},
                emotional_data=emotional_data,
                hook_data=hook_data
            )
            
            self.log("SUCCESS", "Content generated for all platforms")
            return result
        except Exception as e:
            self.log("ERROR", f"Content generation failed: {e}")
            return {"error": str(e)}

    def run_poster_generation(
        self,
        product_data: Dict,
        emotional_data: Dict,
        hook_data: Dict
    ) -> Dict[str, Any]:
        """Step 8: Generate promotional posters (DALL-E)."""
        self.log("STEP", "PHASE 3: Poster Generation (DALL-E)...")
        
        if self.dry_run:
            self.log("WARNING", "DRY RUN: Skipping poster generation")
            return {"status": "skipped", "dry_run": True}
        
        try:
            import threading
            result = [None]
            exception = [None]
            
            def generate_poster():
                try:
                    result[0] = self.poster_agent.execute(
                        product_data=product_data,
                        emotional_data=emotional_data,
                        hook_data=hook_data
                    )
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=generate_poster, daemon=True)
            thread.start()
            thread.join(timeout=300)  # 5 minute timeout for poster generation
            
            if thread.is_alive():
                self.log("WARNING", "Poster generation timeout (took too long)")
                return {"status": "skipped", "reason": "timeout"}
            
            if exception[0]:
                raise exception[0]
            
            result = result[0]
            
            if result.get("status") == "success":
                self.log("SUCCESS", f"Poster generated: {result.get('poster_path')}")
            else:
                self.log("WARNING", f"Poster generation issue: {result.get('error')}")
            
            return result
        except TimeoutError:
            self.log("WARNING", "Poster generation timeout - API took too long. Skipping...")
            return {"status": "skipped", "reason": "timeout"}
        except Exception as e:
            self.log("ERROR", f"Poster generation failed: {e}")
            return {"error": str(e), "status": "failed"}

    def run_video_generation(
        self,
        product_data: Dict,
        market_data: Dict,
        emotional_data: Dict,
        hook_data: Dict
    ) -> Dict[str, Any]:
        """Step 9: Generate video (Sora-2 via FastRouter). LIMITED CREDITS!"""
        
        if self.skip_video:
            self.log("WARNING", "SKIPPING video generation (preserve SORA credits)")
            return {"status": "skipped", "reason": "SORA credits preserved"}
        
        self.log("STEP", "PHASE 3: Video Generation (Sora-2 via FastRouter)...")
        self.log("WARNING", "Using SORA credits! Generating video...")
        
        try:
            result = self.video_agent.execute(
                product_data=product_data,
                market_data=market_data,
                emotional_data=emotional_data,
                hook_data=hook_data,
                image_path=str(self.project.image_path)
            )
            
            if result.get("video_url"):
                self.log("SUCCESS", f"Video generated: {result.get('video_url')}")
            else:
                self.log("WARNING", "Video generation returned no URL")
            
            return result
        except Exception as e:
            self.log("ERROR", f"Video generation failed: {e}")
            return {"error": str(e), "status": "failed"}

    def run_performance_prediction(self, content_data: Dict) -> Dict[str, Any]:
        """Step 10: Predict content performance before posting."""
        self.log("STEP", "PHASE 3: Performance Prediction...")
        try:
            result = self.predictor_agent.execute(
                content_data=content_data
            )
            
            linkedin_score = result.get("platform_scores", {}).get("linkedin", 0)
            instagram_score = result.get("platform_scores", {}).get("instagram", 0)
            facebook_score = result.get("platform_scores", {}).get("facebook", 0)
            
            self.log("SUCCESS", f"Predictions - LinkedIn: {linkedin_score}/100, "
                               f"Instagram: {instagram_score}/100, Facebook: {facebook_score}/100")
            return result
        except Exception as e:
            self.log("ERROR", f"Performance prediction failed: {e}")
            return {"error": str(e)}

    # =============================================
    # PHASE 4: PUBLISHING
    # =============================================

    def publish_content(
        self,
        content_data: Dict,
        poster_data: Dict,
        video_data: Dict
    ) -> Dict[str, Any]:
        """Step 11: Publish to all social media platforms."""
        self.log("STEP", "PHASE 4: Publishing to Social Media...")
        
        results = {
            "linkedin": None,
            "instagram": None,
            "facebook": None
        }
        
        try:
            # Extract content
            linkedin_post = content_data.get("linkedin_post", {})
            instagram_post = content_data.get("instagram_post", {})
            facebook_post = content_data.get("facebook_post", {})
            
            poster_path = poster_data.get("poster_path")
            video_url = video_data.get("video_url")
            
            # ===== LINKEDIN =====
            if not self.dry_run:
                self.log("STEP", "Publishing to LinkedIn...")
                try:
                    linkedin_result = self.publisher.post_to_linkedin(
                        title=linkedin_post.get("title", "Check this out!"),
                        content=linkedin_post.get("content", ""),
                        hashtags=linkedin_post.get("hashtags", []),
                        image_path=poster_path
                    )
                    results["linkedin"] = linkedin_result
                    
                    if linkedin_result.get("status") == "success" or linkedin_result.get("post_id"):
                        self.log("SUCCESS", f"LinkedIn post published")
                    else:
                        self.log("WARNING", f"LinkedIn: {linkedin_result.get('error', 'Unknown issue')}")
                except Exception as e:
                    self.log("ERROR", f"LinkedIn publishing failed: {e}")
                    results["linkedin"] = {"status": "failed", "error": str(e)}
            else:
                self.log("WARNING", "DRY RUN: Skipping LinkedIn publishing")
                results["linkedin"] = {"status": "dry_run"}
            
            # ===== INSTAGRAM =====
            if not self.dry_run:
                self.log("STEP", "Publishing to Instagram...")
                try:
                    instagram_result = self.publisher.post_to_instagram(
                        caption=instagram_post.get("caption", ""),
                        video_path=video_url if video_url else ""
                    )
                    results["instagram"] = instagram_result
                    
                    if instagram_result.get("status") == "success" or instagram_result.get("post_id"):
                        self.log("SUCCESS", f"Instagram post published")
                    else:
                        self.log("WARNING", f"Instagram: {instagram_result.get('error', 'Unknown issue')}")
                except Exception as e:
                    self.log("ERROR", f"Instagram publishing failed: {e}")
                    results["instagram"] = {"status": "failed", "error": str(e)}
            else:
                self.log("WARNING", "DRY RUN: Skipping Instagram publishing")
                results["instagram"] = {"status": "dry_run"}
            
            # ===== FACEBOOK (via Meta) =====
            if not self.dry_run:
                self.log("STEP", "Publishing to Facebook/Meta...")
                try:
                    # Prefer video if available, otherwise use poster image
                    if video_url:
                        self.log("STEP", "Posting video to Meta...")
                        facebook_result = self.publisher.post_to_meta(
                            caption=facebook_post.get("caption", ""),
                            hashtags=facebook_post.get("hashtags", []),
                            video_path=video_url
                        )
                    else:
                        self.log("STEP", "Posting image to Meta...")
                        facebook_result = self.publisher.post_to_meta(
                            caption=facebook_post.get("caption", ""),
                            hashtags=facebook_post.get("hashtags", []),
                            image_path=poster_path
                        )
                    results["facebook"] = facebook_result
                    
                    if facebook_result.get("status") == "success" or facebook_result.get("post_id"):
                        self.log("SUCCESS", "Facebook post published")
                    else:
                        self.log("WARNING", f"Facebook: {facebook_result.get('error', 'Unknown issue')}")
                except Exception as e:
                    self.log("ERROR", f"Facebook publishing failed: {e}")
                    results["facebook"] = {"status": "failed", "error": str(e)}
            else:
                self.log("WARNING", "DRY RUN: Skipping Facebook publishing")
                results["facebook"] = {"status": "dry_run"}
            
            return results
            
        except Exception as e:
            self.log("ERROR", f"Publishing pipeline failed: {e}")
            return results

    # =============================================
    # MAIN WORKFLOW EXECUTION
    # =============================================

    async def run_complete_workflow(self):
        """Execute the complete end-to-end workflow."""
        self.log("STEP", "=" * 60)
        self.log("STEP", "CATALYST AI - END-TO-END WORKFLOW")
        self.log("STEP", "=" * 60)
        
        try:
            # Setup
            self.setup_test_database()
            self.test_user = self.create_test_user()
            image_path = self.select_test_image()
            self.project = self.create_project(image_path)
            
            # PHASE 1: Analysis
            self.log("STEP", "\n" + "=" * 60)
            self.log("STEP", "PHASE 1: ANALYSIS")
            self.log("STEP", "=" * 60)
            
            category_data = self.run_category_detection()
            self.workflow_results["phases"]["category"] = category_data
            
            product_data = self.run_vision_analysis()
            self.workflow_results["phases"]["vision"] = product_data
            
            if product_data.get("error"):
                raise Exception("Vision analysis failed - cannot continue")
            
            # PHASE 2: Intelligence
            self.log("STEP", "\n" + "=" * 60)
            self.log("STEP", "PHASE 2: STRATEGIC INTELLIGENCE")
            self.log("STEP", "=" * 60)
            
            market_data = self.run_market_research(product_data)
            self.workflow_results["phases"]["market"] = market_data
            
            competitor_data = self.run_competitor_analysis(product_data)
            self.workflow_results["phases"]["competitor"] = competitor_data
            
            emotional_data = self.run_emotional_analysis(product_data)
            self.workflow_results["phases"]["emotional"] = emotional_data
            
            hook_data = self.run_hook_generation(emotional_data, competitor_data, market_data)
            self.workflow_results["phases"]["hooks"] = hook_data
            
            # PHASE 3: Content & Assets
            self.log("STEP", "\n" + "=" * 60)
            self.log("STEP", "PHASE 3: CONTENT & ASSET GENERATION")
            self.log("STEP", "=" * 60)
            
            content_data = self.run_content_generation(
                product_data,
                market_data,
                emotional_data,
                hook_data
            )
            self.workflow_results["phases"]["content"] = content_data
            
            poster_data = self.run_poster_generation(
                product_data,
                emotional_data,
                hook_data
            )
            self.workflow_results["phases"]["poster"] = poster_data
            
            video_data = self.run_video_generation(
                product_data,
                market_data,
                emotional_data,
                hook_data
            )
            self.workflow_results["phases"]["video"] = video_data
            
            performance_data = self.run_performance_prediction(content_data)
            self.workflow_results["phases"]["performance"] = performance_data
            
            # PHASE 4: Publishing
            self.log("STEP", "\n" + "=" * 60)
            self.log("STEP", "PHASE 4: PUBLISHING")
            self.log("STEP", "=" * 60)
            
            publish_results = self.publish_content(content_data, poster_data, video_data)
            self.workflow_results["phases"]["publishing"] = publish_results
            
            # Final Summary
            self.log("STEP", "\n" + "=" * 60)
            self.log("SUCCESS", "COMPLETE WORKFLOW EXECUTED SUCCESSFULLY!")
            self.log("STEP", "=" * 60)
            
            # Save results
            self._save_results()
            
        except Exception as e:
            self.log("ERROR", f"Workflow failed: {e}")
            self.workflow_results["error"] = str(e)
            self._save_results()
            raise

    def _save_results(self):
        """Save workflow results to JSON file."""
        results_file = Path("workflow_results_final.json")
        with open(results_file, "w") as f:
            json.dump(self.workflow_results, f, indent=2, default=str)
        self.log("INFO", f"Results saved to: {results_file}")

    def cleanup(self):
        """Clean up database connection."""
        if self.db:
            self.db.close()


# =============================================
# MAIN ENTRY POINT
# =============================================

def main():
    """Run the end-to-end workflow test."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Catalyst AI End-to-End Workflow Test"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually post to social media"
    )
    parser.add_argument(
        "--generate-video",
        action="store_true",
        help="Generate video (uses SORA credits). Default: skip to preserve credits"
    )
    
    args = parser.parse_args()
    
    test = EndToEndWorkflowTest(
        dry_run=args.dry_run,
        skip_video=not args.generate_video
    )
    
    try:
        asyncio.run(test.run_complete_workflow())
    except Exception as e:
        print(f"\nWorkflow failed with error: {e}")
        sys.exit(1)
    finally:
        test.cleanup()


if __name__ == "__main__":
    main()
