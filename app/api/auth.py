from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Annotated, Optional
from app.db.session import get_db
from app.db.models import User, UserSession
from app.schemas.user import UserCreate, UserLogin, UserOut, Token
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.config import settings
import uuid

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    print(f"DEBUG: Attempting signup for email: {user.email}")
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        print(f"DEBUG: Signup failed - Email {user.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create new user
        hashed_password = hash_password(user.password)
        new_user = User(
            email=user.email,
            password_hash=hashed_password,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"DEBUG: User created successfully: {new_user.id}")
        return UserOut(id=str(new_user.id), email=new_user.email)
    except Exception as e:
        db.rollback()
        print(f"ERROR: Database error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/login", response_model=Token)
def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    grant_type: Annotated[str, Form(pattern="password")] = "password",
    scope: Annotated[str, Form()] = "",
    client_id: Annotated[Optional[str], Form()] = None,
    client_secret: Annotated[Optional[str], Form()] = None,
    db: Session = Depends(get_db)
):
    """
    OAuth2 password-flow compatible login endpoint.
    Standardized for perfect Swagger UI compatibility.
    """
    # Find user by email / username
    user = db.query(User).filter(User.email == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=expires_delta
    )
    
    # Store session in database
    expires_at = datetime.utcnow() + expires_delta
    session = UserSession(
        user_id=user.id,
        token=access_token,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    
    return Token(access_token=access_token, token_type="bearer")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Dependency to get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if token is None
    if token is None:
        raise credentials_exception
    
    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Verify session exists and is valid
    session = db.query(UserSession).filter(
        UserSession.token == token,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        raise credentials_exception
    
    # Get user
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    This endpoint requires a valid Bearer token.
    """
    return UserOut(id=str(current_user.id), email=current_user.email)

