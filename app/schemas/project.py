from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    """Base schema for Project"""
    product_name: str = Field(..., min_length=1, max_length=255, description="Name of the product")
    brand_name: Optional[str] = Field(None, max_length=255, description="Brand name")
    price: Optional[str] = Field(None, max_length=50, description="Product price")
    description: Optional[str] = Field(None, description="Product description")
    
    # Marketing strategy fields (aligned with your LangGraph agent system)
    campaign_goal: Optional[str] = Field(None, description="Campaign objective (e.g., 'brand awareness', 'product launch')")
    target_audience: Optional[str] = Field(None, description="Target demographic")
    brand_persona: Optional[str] = Field(None, description="Brand personality/voice")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    brand_name: Optional[str] = Field(None, max_length=255)
    price: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None)
    campaign_goal: Optional[str] = None
    target_audience: Optional[str] = None
    brand_persona: Optional[str] = None
    status: Optional[str] = Field(None, description="Project status: created, processing, completed, failed")


class ProjectOut(ProjectBase):
    """Schema for project response"""
    id: str
    user_id: str
    image_path: Optional[str] = None
    status: str  # created, processing, completed, failed
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectDetail(ProjectOut):
    """Detailed project response with related data"""
    jobs_count: int = 0
    assets_count: int = 0
    latest_job_status: Optional[str] = None
    
    class Config:
        from_attributes = True
