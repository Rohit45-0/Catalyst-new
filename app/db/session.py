from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:StrongPassword123!@localhost:5432/catalyst_ai"
)

Base = declarative_base()

# Lazy initialization of engine and session
_engine = None
_SessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        try:
            _engine = create_engine(DATABASE_URL, echo=True)
        except Exception as e:
            raise ImportError(
                f"Failed to create database engine. This is likely due to a broken psycopg2-binary installation.\n"
                f"Error: {e}\n"
                f"Please run: pip uninstall psycopg2-binary && pip install psycopg2-binary\n"
                f"Or if that fails, try: pip install --upgrade --force-reinstall psycopg2-binary"
            ) from e
    return _engine

def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
    return _SessionLocal

def get_db():
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()
