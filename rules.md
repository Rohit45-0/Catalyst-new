# Catalyst AI - Coding Rules & Guidelines

> Use this file with Antigravity, Claude, or any AI coding assistant to ensure clean, DRY, and maintainable code.

---

## 1. Project Architecture

### 1.1 Folder Structure
```
app/
├── agents/          # AI agent classes - MUST extend BaseAgent
├── api/             # FastAPI route handlers - keep thin
├── core/            # Config, security, shared constants
├── db/              # Database models & session
├── schemas/         # Pydantic models for validation
├── utils/           # Pure utility functions & shared helpers
└── main.py          # App entry point only
```

### 1.2 Module Responsibilities
| Module | Responsibility | Forbidden |
|--------|---------------|-----------|
| `api/` | HTTP handling, request/response only | No business logic |
| `agents/` | AI/LLM operations only | No DB queries, no HTTP |
| `utils/` | Pure functions, reusable helpers | No class state |
| `schemas/` | Data validation only | No methods with logic |
| `core/` | Config, constants, security | No business logic |

---

## 2. DRY Principles (CRITICAL)

### 2.1 Detect Duplication
**BEFORE writing new code, check for:**
- Similar functions in `utils/` or `agents/`
- Similar API patterns in `api/`
- Similar prompt templates
- Similar error handling blocks

### 2.2 Extract Common Patterns

```python
# ❌ BAD - Repeated error handling
try:
    result = api_call()
except Exception as e:
    logger.error(f"Error: {e}")
    raise HTTPException(status_code=500, detail=str(e))

# ✅ GOOD - Use decorator
from functools import wraps

def handle_api_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    return wrapper

@handle_api_errors
def api_call(): ...
```

### 2.3 Base Classes for Agents

```python
# app/agents/base.py - MUST exist
from abc import ABC, abstractmethod
from typing import Dict, Any
from openai import AzureOpenAI
import os

class BaseAgent(ABC):
    """Base class for all AI agents. Enforces DRY patterns."""
    
    def __init__(self, model_name: str = None, temperature: float = 0.7):
        self.client = self._init_openai_client()
        self.model = model_name or os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")
        self.temperature = temperature
    
    def _init_openai_client(self) -> AzureOpenAI:
        """Single source of truth for OpenAI client initialization."""
        return AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.getenv("AZURE_API_VERSION", "2024-02-15-preview")
        )
    
    def _call_llm(self, system_prompt: str, user_prompt: str, json_mode: bool = True) -> Dict[str, Any]:
        """Reusable LLM call with consistent error handling."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                response_format={"type": "json_object"} if json_mode else None
            )
            content = response.choices[0].message.content
            return json.loads(content) if json_mode else content
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Each agent implements this."""
        pass
```

### 2.4 Agent Implementation Pattern

```python
# ❌ BAD - Agent with duplicated client setup
class ContentWriterAgent:
    def __init__(self):
        self.client = AzureOpenAI(...)  # Repeated everywhere
        
    def generate(self, data):
        # Custom prompt building
        # Custom API call
        # Custom error handling

# ✅ GOOD - Extend base, focus on logic only
from app.agents.base import BaseAgent

class ContentWriterAgent(BaseAgent):
    """Generates platform-specific marketing content."""
    
    SYSTEM_PROMPT = """You are an expert Content Strategist..."""
    
    def execute(self, product_data: Dict, market_data: Dict) -> Dict[str, Any]:
        """Generate content for all platforms."""
        user_prompt = self._build_prompt(product_data, market_data)
        return self._call_llm(self.SYSTEM_PROMPT, user_prompt)
    
    def _build_prompt(self, product_data: Dict, market_data: Dict) -> str:
        """Pure function - easy to test."""
        return f"""PRODUCT DATA: {json.dumps(product_data)}
MARKET DATA: {json.dumps(market_data)}"""
```

---

## 3. Reusable Code Patterns

### 3.1 HTTP Client Utilities

```python
# app/utils/http.py
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class HTTPClient:
    """Reusable HTTP client with retries and error handling."""
    
    def __init__(self, base_url: str, headers: Optional[Dict] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)
    
    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP {method} to {url} failed: {e}")
            raise
    
    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        return self.request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        return self.request("POST", endpoint, **kwargs)
```

### 3.2 Prompt Templates

```python
# app/core/prompts.py
from string import Template

class PromptTemplates:
    """Centralized prompt templates. Use .substitute() for variables."""
    
    CONTENT_GENERATION = Template("""
You are an expert content strategist. Create $platform content for:
Product: $product_name
Features: $features
Target: $target_audience
Tone: $tone
""")
    
    MARKET_RESEARCH = Template("""
Analyze market data for $product_category.
Focus areas: $focus_areas
Competitors: $competitors
""")
    
    VISION_ANALYSIS = Template("""
Analyze this product image. Extract:
1. Key features
2. Target audience
3. Selling points
4. Visual style
""")

# Usage:
# prompt = PromptTemplates.CONTENT_GENERATION.substitute(platform="LinkedIn", ...)
```

### 3.3 Response Models

```python
# app/schemas/common.py - Shared response models
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Standard pagination wrapper."""
    items: list[T]
    total: int
    page: int
    page_size: int
    has_next: bool

# Usage in API:
# @router.get("/items", response_model=APIResponse[list[Item]])
```

---

## 4. Function Design Rules

### 4.1 Single Responsibility
```python
# ❌ BAD - Does too much
def process_and_save_user(data):
    validated = validate(data)
    transformed = transform(validated)
    saved = save_to_db(transformed)
    notify_user(saved)
    return saved

# ✅ GOOD - Compose single-purpose functions
def validate_user_data(data: dict) -> UserCreate:
    return UserCreate(**data)

def transform_to_model(schema: UserCreate) -> User:
    return User(**schema.dict())

def save_user(user: User, db: Session) -> User:
    db.add(user)
    db.commit()
    return user

# API layer composes them:
@router.post("/users")
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    user_model = transform_to_model(data)
    saved = save_user(user_model, db)
    return saved
```

### 4.2 Pure Functions Preferred
```python
# ✅ GOOD - Pure function, easily testable
def calculate_engagement_score(likes: int, comments: int, shares: int) -> float:
    """Pure calculation - no side effects."""
    return (likes * 1 + comments * 3 + shares * 5) / 100

# ❌ BAD - Hidden dependencies, hard to test
def get_engagement_score(post_id: str) -> float:
    post = db.query(Post).get(post_id)  # Hidden DB call
    return (post.likes * 1 + post.comments * 3) / 100
```

### 4.3 Maximum Function Length
- **15 lines** maximum for most functions
- **30 lines** absolute maximum (needs justification)
- Extract logic into helper methods

---

## 5. Class Design Rules

### 5.1 Composition Over Inheritance
```python
# ❌ BAD - Deep inheritance
class Agent: pass
class VisionAgent(Agent): pass
class EnhancedVisionAgent(VisionAgent): pass

# ✅ GOOD - Composition
class VisionAnalyzer:
    def __init__(self, llm_client: LLMClient, image_processor: ImageProcessor):
        self.llm = llm_client
        self.image = image_processor
```

### 5.2 Dependency Injection
```python
# ✅ GOOD - Dependencies injected, testable
class SocialMediaPublisher:
    def __init__(
        self,
        linkedin_client: Optional[LinkedInClient] = None,
        meta_client: Optional[MetaClient] = None,
        medium_client: Optional[MediumClient] = None
    ):
        self.linkedin = linkedin_client
        self.meta = meta_client
        self.medium = medium_client

# In tests:
publisher = SocialMediaPublisher(
    linkedin_client=MockLinkedInClient()
)
```

### 5.3 Class Size Limits
- **10 methods** maximum per class
- **200 lines** maximum per class
- If bigger, split into multiple classes

---

## 6. Error Handling

### 6.1 Custom Exceptions
```python
# app/core/exceptions.py
class CatalystAIError(Exception):
    """Base exception for all custom errors."""
    pass

class AgentError(CatalystAIError):
    """AI agent failures."""
    pass

class APIError(CatalystAIError):
    """External API failures."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code

class ValidationError(CatalystAIError):
    """Data validation failures."""
    pass
```

### 6.2 Consistent Error Responses
```python
# app/utils/error_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse

async def catalyst_exception_handler(request: Request, exc: CatalystAIError):
    """Global exception handler for custom exceptions."""
    status_code = getattr(exc, 'status_code', 500)
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": exc.__class__.__name__,
            "message": str(exc)
        }
    )

# In main.py:
# app.add_exception_handler(CatalystAIError, catalyst_exception_handler)
```

---

## 7. Configuration Management

### 7.1 Single Config Source
```python
# app/core/config.py - ONLY place for env vars
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """All configuration in one place."""
    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_key: str
    azure_deployment_name: str = "gpt-4o"
    azure_api_version: str = "2024-02-15-preview"
    
    # Database
    database_url: str
    
    # Social Media
    linkedin_access_token: str = ""
    meta_access_token: str = ""
    
    # App
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Singleton settings - cached."""
    return Settings()

settings = get_settings()
```

### 7.2 No Hardcoded Values
```python
# ❌ BAD
if environment == "production":  # Hardcoded
    timeout = 30

# ✅ GOOD
from app.core.config import settings

timeout = settings.api_timeout  # From config
```

---

## 8. Database Patterns

### 8.1 Repository Pattern
```python
# app/db/repositories/base.py
from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy.orm import Session

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Generic repository for CRUD operations."""
    
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db
    
    def get_by_id(self, id: str) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj: T) -> T:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, id: str) -> bool:
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

# Usage:
# user_repo = BaseRepository(User, db)
# user = user_repo.get_by_id("123")
```

### 8.2 Database Sessions
```python
# app/db/session.py - ONLY place for session management
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for DB sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 9. API Route Patterns

### 9.1 Thin Controllers
```python
# ❌ BAD - Business logic in route
@router.post("/content")
def create_content(request: ContentRequest):
    agent = ContentWriterAgent()
    result = agent.generate(request.data)
    validated = validate_result(result)
    saved = save_to_db(validated)
    return saved

# ✅ GOOD - Delegate to service layer
@router.post("/content", response_model=ContentResponse)
def create_content(
    request: ContentRequest,
    service: ContentService = Depends(get_content_service)
):
    """Create content - business logic in service."""
    return service.create(request)
```

### 9.2 Service Layer Pattern
```python
# app/services/content_service.py
class ContentService:
    """Business logic for content operations."""
    
    def __init__(
        self,
        agent: ContentWriterAgent,
        repository: ContentRepository,
        publisher: SocialMediaPublisher
    ):
        self.agent = agent
        self.repo = repository
        self.publisher = publisher
    
    def create(self, request: ContentRequest) -> Content:
        """Orchestrate content creation flow."""
        # 1. Generate with AI
        generated = self.agent.execute(request.product_data, request.market_data)
        
        # 2. Save to DB
        content = self.repo.create(generated)
        
        # 3. Optionally publish
        if request.auto_publish:
            self.publisher.publish(content)
        
        return content
```

---

## 10. Testing Rules

### 10.1 Test Structure
```python
# tests/test_agents/test_content_writer.py
import pytest
from unittest.mock import Mock, patch

class TestContentWriterAgent:
    """Test suite for ContentWriterAgent."""
    
    @pytest.fixture
    def agent(self):
        return ContentWriterAgent()
    
    @pytest.fixture
    def mock_llm_response(self):
        return {
            "linkedin": "Professional post content",
            "medium": "Blog article content",
            "meta": "Social media content"
        }
    
    def test_execute_returns_all_platforms(self, agent, mock_llm_response):
        """Agent should generate content for all platforms."""
        with patch.object(agent, '_call_llm', return_value=mock_llm_response):
            result = agent.execute({}, {})
            
        assert "linkedin" in result
        assert "medium" in result
        assert "meta" in result
```

### 10.2 Mock External Dependencies
```python
# Always mock external APIs in tests
@pytest.fixture
def mock_openai():
    with patch('app.agents.base.AzureOpenAI') as mock:
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content='{"result": "test"}'))]
        )
        mock.return_value = mock_client
        yield mock
```

---

## 11. Import Organization

### 11.1 Import Order
```python
# 1. Standard library
import os
import json
from typing import Dict, Any

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# 3. Local - absolute imports only
from app.core.config import settings
from app.db.session import get_db
from app.schemas.user import UserCreate
from app.agents.base import BaseAgent
```

### 11.2 No Relative Imports
```python
# ❌ BAD
from ..core.config import settings
from .base import BaseAgent

# ✅ GOOD
from app.core.config import settings
from app.agents.base import BaseAgent
```

---

## 12. Logging Standards

### 12.1 Logger Setup
```python
# app/core/logging.py
import logging
import sys
from app.core.config import settings

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )

# In each module:
import logging
logger = logging.getLogger(__name__)

logger.info("Processing request: %s", request_id)
logger.error("Failed to process: %s", error, exc_info=True)
```

---

## 13. Code Review Checklist

Before submitting code, verify:

- [ ] No duplicated code (check `utils/` and `agents/`)
- [ ] Functions under 15 lines
- [ ] Classes under 200 lines
- [ ] All agents extend `BaseAgent`
- [ ] No business logic in API routes
- [ ] All env vars in `core/config.py` only
- [ ] Error handling uses custom exceptions
- [ ] Imports are absolute
- [ ] Tests mock external dependencies
- [ ] No hardcoded values

---

## 14. Quick Reference

### Create New Agent
```python
# app/agents/my_agent.py
from app.agents.base import BaseAgent

class MyAgent(BaseAgent):
    SYSTEM_PROMPT = "..."
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        prompt = self._build_prompt(**kwargs)
        return self._call_llm(self.SYSTEM_PROMPT, prompt)
```

### Create New API Route
```python
# app/api/my_resource.py
from fastapi import APIRouter, Depends
from app.services.my_service import MyService

router = APIRouter(prefix="/my-resource", tags=["my-resource"])

@router.get("/")
def list_items(service: MyService = Depends(get_my_service)):
    return service.list()
```

### Create New Utility
```python
# app/utils/my_util.py
"""Pure function utility - no state, no side effects."""

def transform_data(input_data: dict) -> dict:
    """Transform input data to output format."""
    return {k: v.upper() for k, v in input_data.items()}
```

---

## 15. Anti-Patterns to Avoid

| Anti-Pattern | Solution |
|-------------|----------|
| Copy-pasting agent code | Extend `BaseAgent` |
| Multiple API client setups | Use `HTTPClient` utility |
| Hardcoded prompts | Use `PromptTemplates` |
| Business logic in routes | Create service layer |
| Direct DB queries everywhere | Use repository pattern |
| `print()` statements | Use `logger` |
| `except:` bare | Always catch specific exceptions |
| Mutable default arguments | Use `None` + check |
| Global state | Use dependency injection |
| String concatenation for SQL | Use ORM or parameterized queries |

---

*Last updated: 2026-01-30*
*Project: Catalyst AI*
*Stack: FastAPI, SQLAlchemy, Azure OpenAI, Pydantic*
