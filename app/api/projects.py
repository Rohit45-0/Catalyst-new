from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Header, Request, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
import os
import uuid
from datetime import datetime
from app.db.session import get_db
from app.db.models import Project, Job, User, Asset
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate, ProjectDetail
from app.api.auth import get_current_user
from app.core.security import decode_access_token

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)

def get_user_from_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract user from Bearer token.
    Works with both Swagger UI OAuth2 and manual Authorization headers.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization required. Please login using the 'Authorize' button.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    product_name: str = Form(..., description="Product name"),
    brand_name: Optional[str] = Form(None, description="Brand name"),
    price: Optional[str] = Form(None, description="Product price"),
    description: Optional[str] = Form(None, description="Product description"),
    campaign_goal: Optional[str] = Form(None, description="Campaign objective (e.g., 'brand awareness')"),
    target_audience: Optional[str] = Form(None, description="Target demographic"),
    brand_persona: Optional[str] = Form(None, description="Brand personality/voice"),
    image: Optional[UploadFile] = File(None, description="Product image (optional at creation)"),
    current_user: User = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Create a new project with optional image upload.
    
    This initializes a project that will be processed by the agent pipeline:
    1. Vision Analysis (if image provided)
    2. Market Research
    3. Content Generation
    """
    
    file_path = None
    
    # Handle image upload if provided and not empty
    if image and hasattr(image, "filename") and image.filename:
        # Validate image file
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Generate unique filename
        file_extension = os.path.splitext(image.filename)[1] if image.filename else '.jpg'
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save image file
        try:
            with open(file_path, "wb") as buffer:
                content = image.file.read()
                buffer.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save image: {str(e)}"
            )
    
    # Create project
    try:
        project = Project(
            user_id=current_user.id,
            product_name=product_name,
            brand_name=brand_name,
            price=price,
            description=description,
            image_path=file_path,
            campaign_goal=campaign_goal,
            target_audience=target_audience,
            brand_persona=brand_persona,
            status="created"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
    except Exception as e:
        db.rollback()
        print(f"DATABASE ERROR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    return ProjectOut(
        id=str(project.id),
        user_id=str(project.user_id),
        product_name=project.product_name,
        brand_name=project.brand_name,
        price=project.price,
        description=project.description,
        campaign_goal=project.campaign_goal,
        target_audience=project.target_audience,
        brand_persona=project.brand_persona,
        image_path=project.image_path,
        status=project.status,
        created_at=project.created_at
    )

@router.get("/", response_model=List[ProjectOut])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all projects for the current user"""
    projects = db.query(Project).filter(
        Project.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return [
        ProjectOut(
            id=str(p.id),
            user_id=str(p.user_id),
            product_name=p.product_name,
            brand_name=p.brand_name,
            price=p.price,
            description=p.description,
            campaign_goal=p.campaign_goal,
            target_audience=p.target_audience,
            brand_persona=p.brand_persona,
            image_path=p.image_path,
            status=p.status,
            created_at=p.created_at
        )
        for p in projects
    ]

@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific project by ID with detailed information"""
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    project = db.query(Project).filter(
        Project.id == project_uuid,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get related counts
    jobs_count = db.query(Job).filter(Job.project_id == project_uuid).count()
    assets_count = db.query(Asset).filter(Asset.project_id == project_uuid).count()
    
    # Get latest job status
    latest_job = db.query(Job).filter(
        Job.project_id == project_uuid
    ).order_by(Job.created_at.desc()).first()
    
    return ProjectDetail(
        id=str(project.id),
        user_id=str(project.user_id),
        product_name=project.product_name,
        brand_name=project.brand_name,
        price=project.price,
        description=project.description,
        campaign_goal=project.campaign_goal,
        target_audience=project.target_audience,
        brand_persona=project.brand_persona,
        image_path=project.image_path,
        status=project.status,
        created_at=project.created_at,
        jobs_count=jobs_count,
        assets_count=assets_count,
        latest_job_status=latest_job.status if latest_job else None
    )

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a project"""
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    project = db.query(Project).filter(
        Project.id == project_uuid,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update only provided fields
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    return ProjectOut(
        id=str(project.id),
        user_id=str(project.user_id),
        product_name=project.product_name,
        brand_name=project.brand_name,
        price=project.price,
        description=project.description,
        campaign_goal=project.campaign_goal,
        target_audience=project.target_audience,
        brand_persona=project.brand_persona,
        image_path=project.image_path,
        status=project.status,
        created_at=project.created_at
    )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project and all related data (jobs, assets)"""
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    project = db.query(Project).filter(
        Project.id == project_uuid,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Delete image file if exists
    if project.image_path and os.path.exists(project.image_path):
        try:
            os.remove(project.image_path)
        except Exception as e:
            print(f"Warning: Could not delete image file: {e}")
    
    # Delete project (cascade will handle jobs and assets)
    db.delete(project)
    db.commit()
    
    return None

@router.get("/{project_id}/jobs")
def get_project_jobs(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all jobs for a specific project"""
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
    
    jobs = db.query(Job).filter(Job.project_id == project_uuid).all()
    
    from app.schemas.job import JobOut
    return {
        "jobs": [
            JobOut(
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
            for job in jobs
        ]
    }

@router.get("/{project_id}/assets")
def get_project_assets(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all generated assets for a specific project"""
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
    
    from app.schemas.asset import AssetOut
    
    assets = db.query(Asset).filter(Asset.project_id == project_uuid).all()
    
    return {
        "assets": [
            AssetOut(
                id=str(asset.id),
                project_id=str(asset.project_id),
                asset_type=asset.asset_type,
                content=asset.content,
                file_url=asset.file_url,
                created_at=asset.created_at
            )
            for asset in assets
        ]
    }
