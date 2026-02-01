from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Project, Job, Asset, User
from app.api.auth import get_current_user
from typing import Dict, Any
import uuid
import json

router = APIRouter(prefix="/results", tags=["results"])

@router.get("/projects/{project_id}/complete")
def get_complete_results(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete workflow results in JSON format.
    
    Returns all data from:
    - Project (predictions, competitor data, emotional data, hooks)
    - Jobs (all agent outputs including publishing results)
    - Assets (generated content + performance metrics)
    """
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    # Get project
    project = db.query(Project).filter(
        Project.id == project_uuid,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all jobs
    jobs = db.query(Job).filter(Job.project_id == project_uuid).all()
    
    # Get all assets
    assets = db.query(Asset).filter(Asset.project_id == project_uuid).all()
    
    # Build complete JSON response
    result = {
        "project_id": str(project.id),
        "status": project.status,
        "product_info": {
            "name": project.product_name,
            "brand": project.brand_name,
            "price": project.price,
            "description": project.description,
            "category": project.category,
            "subcategory": project.subcategory,
            "category_confidence": project.category_confidence
        },
        "strategy": {
            "campaign_goal": project.campaign_goal,
            "target_audience": project.target_audience,
            "brand_persona": project.brand_persona
        },
        "analysis": {
            "competitor_data": project.competitor_data,
            "emotional_data": project.emotional_data,
            "hook_data": project.hook_data,
            "performance_prediction": project.performance_prediction
        },
        "jobs": {},
        "generated_content": [],
        "publishing_results": {},
        "performance_metrics": []
    }
    
    # Process jobs
    for job in jobs:
        job_data = {
            "id": str(job.id),
            "type": job.job_type,
            "status": job.status,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "output": job.output_payload,
            "error": job.error_message
        }
        
        # Store by job type
        result["jobs"][job.job_type.lower()] = job_data
        
        # Extract publishing results specifically
        if job.job_type == "SOCIAL_MEDIA_PUBLISHING" and job.output_payload:
            result["publishing_results"] = job.output_payload
    
    # Process assets
    for asset in assets:
        asset_data = {
            "id": str(asset.id),
            "type": asset.asset_type,
            "created_at": asset.created_at.isoformat() if asset.created_at else None
        }
        
        # Parse content if it's JSON
        try:
            asset_data["content"] = json.loads(asset.content) if asset.content else None
        except:
            asset_data["content"] = asset.content
        
        # Add performance metrics if available
        if asset.performance_metrics:
            asset_data["performance_metrics"] = asset.performance_metrics
            result["performance_metrics"].append({
                "asset_id": str(asset.id),
                "asset_type": asset.asset_type,
                "metrics": asset.performance_metrics
            })
        
        result["generated_content"].append(asset_data)
    
    return result


@router.get("/projects/{project_id}/summary")
def get_results_summary(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a condensed summary of workflow results.
    """
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    project = db.query(Project).filter(
        Project.id == project_uuid,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get publishing job
    publishing_job = db.query(Job).filter(
        Job.project_id == project_uuid,
        Job.job_type == "SOCIAL_MEDIA_PUBLISHING"
    ).first()
    
    # Get assets with metrics
    assets = db.query(Asset).filter(Asset.project_id == project_uuid).all()
    
    return {
        "project_id": str(project.id),
        "product_name": project.product_name,
        "status": project.status,
        "performance_score": project.performance_prediction.get("global_score") if project.performance_prediction else None,
        "posts_published": {
            "linkedin": publishing_job.output_payload.get("linkedin", {}).get("status") if publishing_job and publishing_job.output_payload else None,
            "meta": publishing_job.output_payload.get("meta", {}).get("status") if publishing_job and publishing_job.output_payload else None
        },
        "total_assets": len(assets),
        "assets_with_metrics": len([a for a in assets if a.performance_metrics])
    }
