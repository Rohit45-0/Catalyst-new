from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Project, Asset, User
from app.api.auth import get_current_user
from typing import Dict, Any, Optional
from pydantic import BaseModel
import uuid

router = APIRouter()

class FeedbackPayload(BaseModel):
    metrics: Dict[str, Any]  # e.g., {"likes": 100, "clicks": 50}
    qualitative_feedback: Optional[str] = None

@router.post("/projects/{project_id}/assets/{asset_id}/feedback")
def submit_feedback(
    project_id: str,
    asset_id: str,
    payload: FeedbackPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit actual performance metrics (feedback) for a specific generated asset.
    This data closes the loop for future ML training.
    """
    # 1. Verify Project Access
    project = db.query(Project).filter(
        Project.id == project_id, 
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Find Asset
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.project_id == project_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    # 3. Update Metrics
    # Merge with existing metrics if any, or overwrite
    current_metrics = asset.performance_metrics or {}
    updated_metrics = {**current_metrics, **payload.metrics}
    
    if payload.qualitative_feedback:
        updated_metrics["_qualitative"] = payload.qualitative_feedback
        
    asset.performance_metrics = updated_metrics
    db.commit()
    db.refresh(asset)
    
    return {
        "status": "success",
        "message": "Feedback recorded",
        "asset_id": str(asset.id),
        "updated_metrics": asset.performance_metrics
    }
