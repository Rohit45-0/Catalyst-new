from sqlalchemy import Column, Text, Boolean, TIMESTAMP, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.session import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    product_name = Column(Text)
    brand_name = Column(Text)
    price = Column(Text)
    description = Column(Text)
    image_path = Column(Text)
    status = Column(Text, default="created")  # created, processing, completed, failed
    
    # Marketing strategy fields (aligned with LangGraph AgentState)
    campaign_goal = Column(Text)  # e.g., "brand awareness", "product launch"
    target_audience = Column(Text)  # Target demographic
    brand_persona = Column(Text)  # Brand personality/voice
    
    # Category Intelligence (Phase 1)
    category = Column(Text)
    subcategory = Column(Text)
    category_confidence = Column(Float)
    
    # Competitive Intelligence (Phase 2)
    competitor_data = Column(JSONB)
    emotional_data = Column(JSONB)  # Phase 2.2
    hook_data = Column(JSONB)       # Phase 2.3
    performance_prediction = Column(JSONB) # Phase 3.1
    
    created_at = Column(TIMESTAMP, server_default=func.now())


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    job_type = Column(Text, nullable=False)
    status = Column(Text, default="pending")
    input_payload = Column(JSONB)
    output_payload = Column(JSONB)
    error_message = Column(Text)
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(Text, unique=True, nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    asset_type = Column(Text, nullable=False)  # linkedin_post, ad_copy, blog, video
    content = Column(Text)
    file_url = Column(Text)
    performance_metrics = Column(JSONB) # Phase 3.2: Likes, Shares, CTR
    created_at = Column(TIMESTAMP, server_default=func.now())
