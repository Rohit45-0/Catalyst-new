"""
Clean API endpoint for campaign generation.
Frontend can call this to create a complete marketing campaign.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
import logging
import json
from datetime import datetime
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models import Project, User
from app.api.auth import get_current_user

# Configure logging - remove debug logs in production
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

router = APIRouter(
    prefix="/api/v1/campaigns",
    tags=["campaigns"]
)

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/videos", exist_ok=True)


# Response Models
class CampaignResponse(BaseModel):
    """Response model for campaign generation"""
    campaign_id: str
    product_name: str
    category: str
    content: dict
    poster_url: str
    video_url: Optional[str] = None
    status: str
    created_at: str
    
    class Config:
        from_attributes = True


class CampaignRequest(BaseModel):
    """Request model for campaign generation"""
    product_name: str
    brand_name: Optional[str] = "Your Brand"
    price: Optional[str] = "$99.99"
    description: Optional[str] = ""
    campaign_goal: Optional[str] = "brand awareness"
    target_audience: Optional[str] = "Everyone"
    brand_persona: Optional[str] = "Professional"
    generate_video: bool = False


@router.post("/generate", response_model=dict)
async def generate_campaign(
    product_name: str = None,
    brand_name: Optional[str] = "Your Brand",
    price: Optional[str] = None,
    description: Optional[str] = None,
    campaign_goal: Optional[str] = "brand awareness",
    target_audience: Optional[str] = None,
    brand_persona: Optional[str] = None,
    generate_video: bool = False,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Generate a complete marketing campaign for a product.
    
    **Parameters:**
    - `product_name`: Name of the product (required)
    - `image`: Product image file (JPG, PNG, WebP) (required)
    - `brand_name`: Brand name
    - `price`: Product price
    - `description`: Product description
    - `generate_video`: Whether to generate Sora video
    
    **Returns:**
    - Complete campaign with content, poster, and optional video
    """
    try:
        # Validate inputs
        if not product_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="product_name is required"
            )
        
        # Save uploaded image
        image_filename = f"{uuid.uuid4()}_{image.filename}"
        image_path = os.path.join("uploads", image_filename)
        
        with open(image_path, "wb") as f:
            f.write(await image.read())
        
        # Create project record
        project = Project(
            id=uuid.uuid4(),
            user_id=current_user.id,
            product_name=product_name,
            brand_name=brand_name,
            price=price,
            description=description,
            image_path=image_path,
            status="processing",
            campaign_goal=campaign_goal,
            target_audience=target_audience,
            brand_persona=brand_persona
        )
        db.add(project)
        db.commit()
        
        # Import here to avoid circular imports
        from end_to_end_workflow import run_workflow
        
        # Run the workflow
        results = run_workflow(
            project_id=str(project.id),
            image_path=image_path,
            generate_video=generate_video
        )
        
        # Update project status
        project.status = "completed"
        db.commit()
        
        return {
            "success": True,
            "campaign_id": str(project.id),
            "product_name": project.product_name,
            "category": results.get("category", {}).get("category", "unknown"),
            "content": results.get("content", {}),
            "poster_url": f"/static/images/{results.get('poster_filename', '')}",
            "video_url": f"/static/videos/{results.get('video_filename', '')}" if generate_video else None,
            "status": "completed",
            "created_at": project.created_at.isoformat() if project.created_at else datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        if os.path.exists(image_path):
            os.remove(image_path)
        
        logging.error(f"Campaign generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Campaign generation failed: {str(e)}"
        )


@router.get("/campaigns/{campaign_id}", response_model=dict)
async def get_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get campaign details by ID.
    """
    try:
        project = db.query(Project).filter(
            Project.id == campaign_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return {
            "success": True,
            "campaign_id": str(project.id),
            "product_name": project.product_name,
            "status": project.status,
            "created_at": project.created_at.isoformat() if project.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving campaign: {str(e)}"
        )


@router.get("/list", response_model=dict)
async def list_campaigns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10
) -> dict:
    """
    List all campaigns for current user.
    """
    try:
        campaigns = db.query(Project).filter(
            Project.user_id == current_user.id
        ).offset(skip).limit(limit).all()
        
        return {
            "success": True,
            "total": len(campaigns),
            "campaigns": [
                {
                    "campaign_id": str(c.id),
                    "product_name": c.product_name,
                    "status": c.status,
                    "created_at": c.created_at.isoformat() if c.created_at else None
                }
                for c in campaigns
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing campaigns: {str(e)}"
        )
