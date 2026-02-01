"""
Agent Orchestrator - Manages the multi-agent workflow

This orchestrator integrates with your existing LangGraph agents:
1. Vision Analyzer
2. Market Research Agent
3. Content Writer Agent
4. Image Generator Agent

It manages job creation, execution, and result storage.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import os
from sqlalchemy.orm import Session
from app.db.models import Project, Job, Asset
import uuid
import json
import asyncio
import functools
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


class AgentOrchestrator:
    """
    Orchestrates the multi-agent marketing content generation pipeline.
    
    Workflow:
    1. VISION_ANALYSIS - Analyze product image
    2. MARKET_RESEARCH - Research market and competitors
    3. CONTENT_GENERATION - Generate platform-specific content
    4. IMAGE_GENERATION - Create marketing images (optional)
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def start_workflow(self, project_id: uuid.UUID) -> Dict[str, Any]:
        """
        Start the complete agent workflow for a project.
        
        Args:
            project_id: UUID of the project to process
            
        Returns:
            Dict with workflow status and job IDs
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            return {"status": "error", "message": "Project not found"}
        
        # Update project status
        project.status = "processing"
        self.db.commit()
        
        try:
            # Step 1: Category Detection
            category_job = await self._run_category_detection(project)

            # Step 2: Vision Analysis
            vision_job = await self._run_vision_analysis(project)
            
            if vision_job.status == "failed":
                project.status = "failed"
                self.db.commit()
                return {
                    "status": "failed",
                    "message": "Vision analysis failed",
                    "error": vision_job.error_message
                }
            
            
            # Step 3: Competitor Analysis (Phase 2)
            competitor_job = await self._run_competitor_analysis(project, vision_job)
            
            if competitor_job.status == "failed":
                print(" Competitor analysis failed, continuing workflow...")
            
            # Step 3.1: Emotional Trigger Analysis (Phase 2.2)
            emotional_job = await self._run_emotional_analysis(project, vision_job, category_job)
            if emotional_job.status == "failed":
                print(" Emotional analysis failed, continuing workflow...")
                
            # Step 3.2: Hook Generation (Phase 2.3)
            hook_job = await self._run_hook_generation(project, vision_job, emotional_job, competitor_job)
            if hook_job.status == "failed":
                print(" Hook Generation failed, continuing workflow...")
            
            # Step 4: Market Research
            research_job = await self._run_market_research(project, vision_job, category_job)
            
            if research_job.status == "failed":
                project.status = "failed"
                self.db.commit()
                return {
                    "status": "failed",
                    "message": "Market research failed",
                    "error": research_job.error_message
                }
            
            # Step 5: Video & Poster Generation (Parallel)
            print(" Launching Parallel Creation (Video + Poster)...")
            video_task = self._run_video_generation(project, research_job, emotional_job, hook_job)
            poster_task = self._run_poster_generation(project, emotional_job, hook_job)
            
            results = await asyncio.gather(video_task, poster_task)
            video_job = results[0]
            poster_job = results[1]

            video_url = video_job.output_payload.get("video_url") if video_job and video_job.output_payload else None
            poster_path = poster_job.output_payload.get("poster_path") if poster_job and poster_job.output_payload else None

            # Step 6: Content Generation
            content_job = await self._run_content_generation(project, vision_job, research_job, hook_job)
            
            if content_job.status == "failed":
                project.status = "failed"
                self.db.commit()
                return {
                    "error": content_job.error_message
                }

            # Step 6.1: Performance Prediction (Phase 3.1)
            prediction_job = await self._run_performance_prediction(project, content_job, emotional_job)
            if prediction_job.status == "failed":
                print(" Performance Prediction failed, continuing workflow...")

            # Step 7: Social Media Publishing (Phase 3.3)
            publishing_job = await self._run_social_media_publishing(project, content_job, video_url, poster_path)
            if publishing_job.status == "failed":
                print(" Social Media Publishing failed, continuing workflow...")
            
            # Step 8: Image Generation (optional)
            image_job = None
            if project.image_path:  # Only if we have a base image
                image_job = await self._run_image_generation(project, vision_job, research_job)
            
            # Update project status
            project.status = "completed"
            self.db.commit()
            
            return {
                "status": "success",
                "message": "Workflow completed successfully",
                "jobs": {
                    "vision_analysis": str(vision_job.id),
                    "competitor_analysis": str(competitor_job.id),
                    "emotional_analysis": str(emotional_job.id),
                    "hook_generation": str(hook_job.id), # Phase 2.3
                    "market_research": str(research_job.id),
                    "content_generation": str(content_job.id),
                    "video_generation": str(video_job.id) if video_job else None,
                    "poster_generation": str(poster_job.id) if poster_job else None,
                    "performance_prediction": str(prediction_job.id), # Phase 3.1
                    "social_media_publishing": str(publishing_job.id), # Phase 3.3
                    "image_generation": str(image_job.id) if image_job else None
                }
            }
            
        except Exception as e:
            project.status = "failed"
            self.db.commit()
            return {
                "status": "error",
                "message": f"Workflow failed: {str(e)}"
            }
    
    async def _run_vision_analysis(self, project: Project) -> Job:
        """
        Run Vision Analysis Agent
        
        This agent analyzes the product image to extract:
        - Product name and category
        - Visual features (colors, style)
        - Target demographic
        - Key selling points
        """
        job = Job(
            project_id=project.id,
            job_type="VISION_ANALYSIS",
            status="running",
            input_payload={
                "image_path": project.image_path,
                "product_name": project.product_name,
                "description": project.description
            },
            started_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        try:
            # Use real agent via wrapper
            from app.core.agent_wrapper import get_agent_wrapper
            agent_wrapper = get_agent_wrapper()
            
            output = agent_wrapper.run_vision_analysis(
                image_path=project.image_path or "",
                product_name=project.product_name,
                description=project.description or "",
                category=project.category
            )
            
            job.output_payload = output
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            self.db.commit()
            
            return job
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            return job
    
    async def _run_category_detection(self, project: Project) -> Job:
        """
        Run Category Detection Agent
        Classifies product into specific marketing categories.
        """
        job = Job(
            project_id=project.id,
            job_type="CATEGORY_DETECTION",
            status="running",
            input_payload={
                "image_path": project.image_path,
                "description": project.description
            },
            started_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        try:
            from app.core.agent_wrapper import get_agent_wrapper
            agent_wrapper = get_agent_wrapper()
            
            output = agent_wrapper.run_category_detection(
                image_path=project.image_path,
                description=project.description
            )
            
            job.output_payload = output
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            
            # Update Project with category info
            if output.get("category"):
                project.category = output.get("category")
                project.subcategory = output.get("subcategory")
                project.category_confidence = output.get("confidence")
            
            self.db.commit()
            return job
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            return job

    async def _run_competitor_analysis(self, project: Project, vision_job: Job) -> Job:
        """
        Run Visual Competitor Analyzer Agent.
        """
        job = Job(
            project_id=project.id,
            job_type="COMPETITOR_ANALYSIS",
            status="running",
            input_payload={
                "product_name": project.product_name,
                "category": project.category,
                "vision_data": vision_job.output_payload
            },
            started_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        try:
            from app.core.agent_wrapper import get_agent_wrapper
            agent_wrapper = get_agent_wrapper()
            
            output = agent_wrapper.run_competitor_analysis(
                image_path=project.image_path,
                product_data=vision_job.output_payload,
                category_data={"category": project.category, "subcategory": project.subcategory}
            )
            
            job.output_payload = output
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            
            # Update Project with competitor data
            if output:
                 project.competitor_data = output
                 
            self.db.commit()
            return job
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            return job

    async def _run_emotional_analysis(self, project: Project, vision_job: Job, category_job: Job) -> Job:
        """Phase 2.2: Identify emotional triggers."""
        print(" Running Emotional Trigger Analysis...")
        
        job = Job(
            project_id=project.id,
            job_type="EMOTIONAL_ANALYSIS",
            status="running",
            input_payload={
                "product_data": vision_job.output_payload,
                "category": category_job.output_payload.get("category")
            },
            started_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        try:
            from app.core.agent_wrapper import get_agent_wrapper
            agent_wrapper = get_agent_wrapper()

            product_data = vision_job.output_payload
            category = category_job.output_payload.get("category")
            
            output = agent_wrapper.run_emotional_analysis(product_data, category)
            
            job.output_payload = output
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            
            # Save to DB
            project.emotional_data = output
            self.db.add(project)
            self.db.commit()
            print("Emotional Analysis Complete")
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            print(f"Emotional Analysis Failed: {e}")
            
        return job

    async def _run_hook_generation(self, project: Project, vision_job: Job, emotional_job: Job, competitor_job: Job) -> Job:
        """Phase 2.3: Generate viral hooks."""
        print(" Running Hook Generator Agent...")
        
        job = Job(
            project_id=project.id,
            job_type="HOOK_GENERATION",
            status="running",
            input_payload={
                "product_data": vision_job.output_payload,
                "emotional_data": emotional_job.output_payload,
                "competitor_data": competitor_job.output_payload
            },
            started_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        try:
            from app.core.agent_wrapper import get_agent_wrapper
            agent_wrapper = get_agent_wrapper()
            
            output = agent_wrapper.run_hook_generation(
                product_data=vision_job.output_payload,
                emotional_data=emotional_job.output_payload,
                competitor_data=competitor_job.output_payload
            )
            
            job.output_payload = output
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            
            # Save to DB
            project.hook_data = output
            self.db.add(project)
            self.db.commit()
            print("Hook Generation Complete")
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            print(f"Hook Generation Failed: {e}")
            
        return job

    async def _run_market_research(self, project: Project, vision_job: Job, category_job: Job) -> Job:
        """
        Run Market Research Agent
        
        This agent researches:
        - Competitor products
        - Market trends
        - Customer reviews and pain points
        - Pricing strategies
        """
        job = Job(
            project_id=project.id,
            job_type="MARKET_RESEARCH",
            status="running",
            input_payload={
                "product_name": project.product_name,
                "brand_name": project.brand_name,
                "vision_data": vision_job.output_payload
            },
            started_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        try:
            # Use real agent via wrapper
            from app.core.agent_wrapper import get_agent_wrapper
            agent_wrapper = get_agent_wrapper()
            
            output = agent_wrapper.run_market_research(
                product_name=project.product_name,
                brand_name=project.brand_name or "",
                product_data=vision_job.output_payload,
                category=project.category
            )
            
            job.output_payload = output
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            self.db.commit()
            
            return job
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            return job
    
    async def _run_content_generation(
        self, 
        project: Project, 
        vision_job: Job, 
        research_job: Job,
        hook_job: Job = None  # Phase 2.3
    ) -> Job:
        """
        Run Content Writer Agent
        
        This agent generates platform-specific content:
        - LinkedIn posts
        - Facebook/Instagram posts
        - Blog posts for Medium
        - Ad copy
        """
        
        hook_data = hook_job.output_payload if hook_job and hook_job.status == "completed" else None
        
        job = Job(
            project_id=project.id,
            job_type="CONTENT_GENERATION",
            status="running",
            input_payload={
                "product_data": vision_job.output_payload,
                "market_data": research_job.output_payload,
                "hook_data": hook_data,
                "campaign_goal": project.campaign_goal,
                "target_audience": project.target_audience,
                "brand_persona": project.brand_persona
            },
            started_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        try:
            # Use real agent via wrapper
            from app.core.agent_wrapper import get_agent_wrapper
            agent_wrapper = get_agent_wrapper()
            
            generated_content = agent_wrapper.run_content_generation(
                product_data=vision_job.output_payload,
                market_data=research_job.output_payload,
                campaign_goal=project.campaign_goal,
                target_audience=project.target_audience,
                brand_persona=project.brand_persona,
                product_image_path=project.image_path,
                category=project.category,
                hook_data=hook_data  # Phase 2.3
            )
            
            job.output_payload = generated_content
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            self.db.commit()
            
            # Create assets from generated content
            await self._create_assets_from_content(project.id, generated_content)
            
            return job
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            return job

    async def _run_performance_prediction(
        self,
        project: Project,
        content_job: Job,
        emotional_job: Job
    ) -> Job:
        """Phase 3.1: Predict content performance."""
        print(" Running Performance Predictor Agent...")
        
        job = Job(
            project_id=project.id,
            job_type="PERFORMANCE_PREDICTION",
            status="running",
            input_payload={
                "content_data": content_job.output_payload,
                "emotional_data": emotional_job.output_payload
            },
            started_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        try:
            from app.core.agent_wrapper import get_agent_wrapper
            agent_wrapper = get_agent_wrapper()
            
            output = agent_wrapper.run_performance_prediction(
                content_data=content_job.output_payload,
                emotional_data=emotional_job.output_payload
            )
            
            job.output_payload = output
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            
            # Save to DB
            project.performance_prediction = output
            self.db.add(project)
            self.db.commit()
            print(" Performance Prediction Complete")
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            print(f" Performance Prediction Failed: {e}")
            
        return job
    
    async def _run_social_media_publishing(
        self,
        project: Project,
        content_job: Job,
        video_url: str = None,
        poster_path: str = None
    ) -> Job:
        """Phase 3.3: Publish content to social media platforms."""
        print(" Running Social Media Publisher...")
        
        job = Job(
            project_id=project.id,
            job_type="SOCIAL_MEDIA_PUBLISHING",
            status="running",
            input_payload={
                "content_data": content_job.output_payload,
                "video_url": video_url,
                "poster_path": poster_path
            },
            started_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        try:
            from app.utils.publisher import SocialMediaPublisher
            publisher = SocialMediaPublisher()
            
            content_data = content_job.output_payload
            results = {}

            # Prepare Video Path (Local or Download)
            video_path = None
            should_cleanup = False
            
            if video_url:
                if os.path.exists(video_url):
                    print(f"   Using generated video file: {video_url}")
                    video_path = video_url
                else:
                    try:
                        import requests
                        import tempfile
                        # import os (removed to avoid scope issue)
                        print(f"   Downloading video from {video_url}...")
                        
                        # Create a temp file
                        fd, temp_path = tempfile.mkstemp(suffix=".mp4")
                        os.close(fd)
                        
                        with requests.get(video_url, stream=True) as r:
                            r.raise_for_status()
                            with open(temp_path, 'wb') as f:
                                for chunk in r.iter_content(chunk_size=8192):
                                    f.write(chunk)
                        
                        video_path = temp_path
                        should_cleanup = True
                        print(f"   Video downloaded to {video_path}")
                    except Exception as e:
                        print(f"   Failed to download video: {e}")

            # Publish to LinkedIn
            if "linkedin_post" in content_data:
                linkedin_post = content_data["linkedin_post"]
                print("   Publishing to LinkedIn...")
                
                # If we have a video, don't send the image to avoid ambiguity
                li_image_path = project.image_path if not video_path else None
                
                linkedin_result = publisher.post_to_linkedin(
                    title=linkedin_post.get("title", ""),
                    content=linkedin_post.get("content", ""),
                    hashtags=linkedin_post.get("hashtags", []),
                    image_path=li_image_path,
                    video_path=video_path
                )
                results["linkedin"] = linkedin_result
                
            # Publish to Meta (Facebook)
            if "meta_post" in content_data:
                meta_post = content_data["meta_post"]
                print("   Publishing to Meta (Facebook)...")
                
                # If we have a video, don't send the image
                fb_image_path = project.image_path if not video_path else None
                
                meta_result = publisher.post_to_meta(
                    caption=meta_post.get("caption", ""),
                    hashtags=meta_post.get("hashtags", []),
                    image_path=fb_image_path,
                    video_path=video_path
                )
                results["meta"] = meta_result
                
                # Publish to Instagram (if video)
                if video_path and "caption" in meta_post:
                    print("   Publishing to Instagram (Reels)...")
                    ig_result = publisher.post_to_instagram(
                        caption=meta_post.get("caption", ""),
                        video_path=video_path
                    )
                    results["instagram"] = ig_result
            
            # Publish to X (Twitter)
            # if "twitter_post" in content_data or "meta_post" in content_data:
            #     # Fallback to meta content if specific twitter content not generated
            #     t_content = content_data.get("twitter_post", {}).get("content") or content_data.get("meta_post", {}).get("caption", "")
            #     t_hashtags = content_data.get("twitter_post", {}).get("hashtags", [])
                
            #     print("   Publishing to X (Twitter)...")
            #     twitter_result = publisher.post_to_twitter(
            #         content=t_content,
            #         hashtags=t_hashtags,
            #         media_path=video_path or project.image_path
            #     )
            #     results["twitter"] = twitter_result

            # ---------------------------------------------------------
            # BONUS: Publish Poster if available (As requested by User)
            # ---------------------------------------------------------
            if poster_path and os.path.exists(poster_path):
                print(f"   Found Poster ({poster_path}). Publishing as secondary post...")
                
                # LinkedIn Poster
                if "linkedin_post" in content_data:
                    li_p = content_data["linkedin_post"]
                    # Clean title/content for poster variant
                    p_title = li_p.get("title", "") + " [Official Poster]"
                    p_content = "Check out our official campaign poster! #Poster #Design " + li_p.get("hashtags", [""])[0]
                    
                    print("   Publishing Poster to LinkedIn...")
                    publisher.post_to_linkedin(
                        title=p_title,
                        content=p_content,
                        hashtags=[], # embedded in content
                        image_path=poster_path, 
                        video_path=None # Explicitly image
                    )
                
                # Meta Poster
                if "meta_post" in content_data:
                    m_p = content_data["meta_post"]
                    p_caption = "Official Campaign Poster  " + m_p.get("caption", "")[:50] + "... #Poster"
                    
                    print("   Publishing Poster to Meta...")
                    publisher.post_to_meta(
                        caption=p_caption,
                        hashtags=[],
                        image_path=poster_path,
                        video_path=None
                    )

            # Cleanup video (only if temp)
            if should_cleanup and video_path and os.path.exists(video_path):
                try:
                    os.remove(video_path)
                except:
                    pass

            job.output_payload = results
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            self.db.commit()
            print(" Social Media Publishing Complete")
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            print(f" Social Media Publishing Failed: {e}")
            
        return job
    
    
    async def _run_image_generation(
        self, 
        project: Project, 
        vision_job: Job, 
        research_job: Job
    ) -> Job:
        """
        Run Image Generator Agent (Optional)
        
        This agent generates marketing images using DALL-E
        """
        job = Job(
            project_id=project.id,
            job_type="IMAGE_GENERATION",
            status="running",
            input_payload={
                "product_data": vision_job.output_payload,
                "market_data": research_job.output_payload
            },
            started_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        try:
            # TODO: Integrate with your ImageGeneratorAgent
            # from agents.image_generator import ImageGeneratorAgent
            # image_agent = ImageGeneratorAgent()
            # result = image_agent.generate_images(state)
            
            # Mock output for now
            output = {
                "generated_images": [
                    {
                        "type": "social_media_post",
                        "url": "https://example.com/image1.jpg",
                        "prompt": "Marketing image for social media"
                    }
                ]
            }
            
            job.output_payload = output
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            self.db.commit()
            
            return job
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            return job
    
    async def _create_assets_from_content(
        self, 
        project_id: uuid.UUID, 
        generated_content: Dict[str, Any]
    ):
        """
        Create Asset records from generated content
        """
        # LinkedIn post
        if "linkedin_post" in generated_content:
            linkedin_asset = Asset(
                project_id=project_id,
                asset_type="linkedin_post",
                content=json.dumps(generated_content["linkedin_post"])
            )
            self.db.add(linkedin_asset)
        
        # Meta (Facebook/Instagram) post
        if "meta_post" in generated_content:
            meta_asset = Asset(
                project_id=project_id,
                asset_type="meta_post",
                content=json.dumps(generated_content["meta_post"])
            )
            self.db.add(meta_asset)
        
        # Blog post
        if "blog_post" in generated_content:
            blog_asset = Asset(
                project_id=project_id,
                asset_type="blog_post",
                content=json.dumps(generated_content["blog_post"])
            )
            self.db.add(blog_asset)
        
        self.db.commit()
    
    def get_workflow_status(self, project_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get the current status of the workflow for a project
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            return {"status": "error", "message": "Project not found"}
        
        jobs = self.db.query(Job).filter(Job.project_id == project_id).all()
        
        return {
            "project_status": project.status,
            "jobs": [
                {
                    "id": str(job.id),
                    "type": job.job_type,
                    "status": job.status,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "error": job.error_message
                }
                for job in jobs
            ]
        }

    async def _run_video_generation(self, project: Project, research_job: Job, emotional_job: Job, hook_job: Job) -> Job:
        """Run the video generation agent."""
        print(" Running Video Generator...")
        
        job = Job(
            project_id=project.id,
            job_type="VIDEO_GENERATION",
            status="running"
        )
        self.db.add(job)
        self.db.commit()
        
        try:
            from app.core.agent_wrapper import get_agent_wrapper
            agent_wrapper = get_agent_wrapper()
            
            # Get data from previous jobs
            market_data = research_job.output_payload or {}
            emotional_data = project.emotional_data or {}
            hook_data = project.hook_data or {}
            
            product_data = {
                "product_name": project.product_name,
                "description": project.description
            }
            
            # Run Agent in ThreadPool (Non-blocking)
            import asyncio
            import functools
            loop = asyncio.get_running_loop()
            func = functools.partial(
                agent_wrapper.run_video_creation,
                product_data=product_data,
                market_data=market_data,
                emotional_data=emotional_data,
                hook_data=hook_data,
                image_path=project.image_path
            )
            result = await loop.run_in_executor(None, func)
            
            # Save Job Output
            job.output_payload = result
            job.status = "completed"
            
            # Save as Asset if URL exists (or even if just script)
            video_url = result.get("video_url")
            cloud_url = result.get("cloud_url")
            script = result.get("video_script", {})
            
            if cloud_url:
                script["cloud_url"] = cloud_url

            content_json = json.dumps(script) if script else "{}"
            
            if video_url:
                # Convert filesystem path to URL for frontend access
                # video_url might be like: /path/to/static/videos/video_xyz.mp4
                # We want to store: /static/videos/video_xyz.mp4
                if video_url.startswith(os.path.join(os.getcwd(), "static")):
                    # It's an absolute path, convert to relative URL
                    relative_path = os.path.relpath(video_url, os.getcwd())
                    frontend_url = "/" + relative_path.replace("\\", "/")  # Windows path compatibility
                else:
                    frontend_url = video_url
                
                asset = Asset(
                    project_id=project.id,
                    asset_type="video_short",
                    content=content_json, # Store script as content
                    file_url=frontend_url  # Store URL for frontend
                )
                self.db.add(asset)
                print(f"    Saved Video Asset: {frontend_url}")
                print(f"    Local file: {video_url}")
                if cloud_url:
                    print(f"   ☁ Cloud URL: {cloud_url}")
            
            self.db.commit()
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            self.db.commit()
            print(f" Video Generation Failed: {e}")
            import traceback
            traceback.print_exc()
            
        return job

    async def _run_poster_generation(self, project: Project, emotional_job: Job, hook_job: Job) -> Job:
        print(" Running Poster Generation...")
        job = Job(
            project_id=project.id,
            job_type="POSTER_GENERATION",
            status="running"
        )
        self.db.add(job)
        self.db.commit()

        try:
            from app.core.agent_wrapper import get_agent_wrapper
            agent_wrapper = get_agent_wrapper()
            
            product_data = {
                "product_name": project.product_name,
                "description": project.description
            }
            emotional_data = project.emotional_data or {}
            hook_data = project.hook_data or {}
            
            # Run Agent in ThreadPool
            import asyncio
            import functools
            loop = asyncio.get_running_loop()
            func = functools.partial(
                agent_wrapper.run_poster_generation,
                product_data=product_data,
                emotional_data=emotional_data,
                hook_data=hook_data
            )
            result = await loop.run_in_executor(None, func)
            
            job.output_payload = result
            job.status = "completed"
            
            if result.get("poster_path"):
                asset = Asset(
                    project_id=project.id,
                    asset_type="image_poster",
                    content=json.dumps({"prompt": result.get("prompt")}),
                    file_url=result.get("poster_path")
                )
                self.db.add(asset)
                print(f"    Saved Poster Asset: {result.get('poster_path')}")
            
            self.db.commit()
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            self.db.commit()
            print(f" Poster Generation Failed: {e}")
            
        return job
