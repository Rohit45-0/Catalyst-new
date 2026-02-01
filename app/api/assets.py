from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from app.db.session import get_db
from app.db.models import Asset, Project, User
from app.schemas.asset import AssetOut
from app.api.auth import get_current_user

router = APIRouter(
    prefix="/assets",
    tags=["assets"]
)

@router.get("/{asset_id}", response_model=AssetOut)
def get_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific asset by ID"""
    try:
        asset_uuid = uuid.UUID(asset_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid asset ID format"
        )
    
    asset = db.query(Asset).filter(Asset.id == asset_uuid).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    # Verify project belongs to user
    project = db.query(Project).filter(
        Project.id == asset.project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return AssetOut(
        id=str(asset.id),
        project_id=str(asset.project_id),
        asset_type=asset.asset_type,
        content=asset.content,
        file_url=asset.file_url,
        created_at=asset.created_at
    )

@router.get("/")
def list_assets(
    project_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List assets, optionally filtered by project_id"""
    query = db.query(Asset)
    
    if project_id:
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
        
        query = query.filter(Asset.project_id == project_uuid)
    else:
        # Get all projects for user and filter assets
        user_projects = db.query(Project).filter(Project.user_id == current_user.id).all()
        project_ids = [p.id for p in user_projects]
        query = query.filter(Asset.project_id.in_(project_ids))
    
    assets = query.all()
    
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
