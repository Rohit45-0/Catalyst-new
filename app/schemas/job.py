from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class JobCreate(BaseModel):
    job_type: str
    input_payload: Optional[Dict[str, Any]] = None

class JobOut(BaseModel):
    id: str
    project_id: str
    job_type: str
    status: str
    input_payload: Optional[Dict[str, Any]] = None
    output_payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
