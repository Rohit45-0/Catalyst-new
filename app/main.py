from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, projects, uploads, jobs, assets, analytics, results, campaigns
from app.db.session import get_engine, Base
from app.db import models  # Import models to register them with Base
import logging

# Suppress verbose logging in production
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

app = FastAPI(
    title="Catalyst AI Backend",
    version="0.1.0",
    description="Agent-orchestrated marketing intelligence platform"
)

# Add CORS middleware to fix Swagger OAuth2 "Failed to fetch" error
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    """Initialize database tables on application startup"""
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logging.error(f"Database connection warning: {e}")

@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "Catalyst AI Backend"}

# Include all API routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(campaigns.router)
app.include_router(uploads.router)
app.include_router(jobs.router)
app.include_router(assets.router)
app.include_router(analytics.router)
app.include_router(results.router)

# Mount static directory to serve images/videos
from fastapi.staticfiles import StaticFiles
import os
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
