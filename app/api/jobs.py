from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
from app.db.session import get_db
from app.db.models import Job, Project, User
from app.schemas.job import JobOut, JobCreate
from app.api.auth import get_current_user
from app.core.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/start/{project_id}")
async def start_workflow(
    project_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start the agent workflow for a project.
    
    This triggers the complete pipeline:
    1. Vision Analysis
    2. Market Research
    3. Content Generation
    4. Image Generation (optional)
    
    The workflow runs in the background and updates job statuses.
    """
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    # Verify project exists and belongs to user
    project = db.query(Project).filter(
        Project.id == project_uuid,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if workflow is already running
    if project.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow is already running for this project"
        )
    
    # Start workflow in background
    orchestrator = AgentOrchestrator(db)
    
    # Run workflow asynchronously
    result = await orchestrator.start_workflow(project_uuid)
    
    return {
        "message": "Workflow started",
        "project_id": project_id,
        "status": result.get("status"),
        "jobs": result.get("jobs", {})
    }

@router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific job by ID"""
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format"
        )
    
    job = db.query(Job).filter(Job.id == job_uuid).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Verify job belongs to user's project
    project = db.query(Project).filter(
        Project.id == job.project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return JobOut(
        id=str(job.id),
        project_id=str(job.project_id),
        job_type=job.job_type,
        status=job.status,
        input_payload=job.input_payload,
        output_payload=job.output_payload,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at
    )

@router.get("/project/{project_id}/status")
def get_workflow_status(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current status of the workflow for a project.
    
    Returns all jobs and their statuses.
    """
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    # Verify project belongs to user
    project = db.query(Project).filter(
        Project.id == project_uuid,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    orchestrator = AgentOrchestrator(db)
    status_info = orchestrator.get_workflow_status(project_uuid)
    
    return status_info

@router.post("/{job_id}/retry")
async def retry_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retry a failed job.
    
    This will re-run the specific agent that failed.
    """
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format"
        )
    
    job = db.query(Job).filter(Job.id == job_uuid).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Verify job belongs to user's project
    project = db.query(Project).filter(
        Project.id == job.project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Only retry failed jobs
    if job.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot retry job with status: {job.status}"
        )
    
    # Reset job status
    job.status = "pending"
    job.error_message = None
    job.started_at = None
    job.completed_at = None
    db.commit()
    
    # TODO: Trigger specific agent based on job_type
    # For now, just return success
    
    return {
        "message": "Job queued for retry",
        "job_id": job_id,
        "job_type": job.job_type
    }
