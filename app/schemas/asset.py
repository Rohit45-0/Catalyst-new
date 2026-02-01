from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AssetOut(BaseModel):
    id: str
    project_id: str
    asset_type: str  # linkedin_post, ad_copy, blog, video
    content: Optional[str] = None
    file_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
