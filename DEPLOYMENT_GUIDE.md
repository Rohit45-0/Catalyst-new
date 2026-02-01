# Catalyst AI Backend - Deployment Guide

## Local Development Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd catalyst-ai-backend
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
# See Configuration section below
```

5. **Initialize database**
```bash
python -c "from app.db.session import get_engine; from app.db.models import *; from app.db.session import Base; Base.metadata.create_all(bind=get_engine())"
```

6. **Start server**
```bash
# Development (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

## Configuration

### Environment Variables (.env)

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/catalyst_db

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
AZURE_DEPLOYMENT_NAME=gpt-4o
AZURE_API_VERSION=2024-02-15-preview

# Video Generation (Sora via FastRouter)
FASTROUTER_API_KEY=your-fastrouter-api-key

# Social Media APIs
LINKEDIN_ACCESS_TOKEN=your-linkedin-token
LINKEDIN_BUSINESS_ACCOUNT_ID=your-account-id

INSTAGRAM_BUSINESS_ACCOUNT_ID=your-instagram-id
INSTAGRAM_ACCESS_TOKEN=your-instagram-token

FACEBOOK_PAGE_TOKEN=your-facebook-token
FACEBOOK_PAGE_ID=your-page-id

# Search API
BRAVE_SEARCH_API_KEY=your-brave-api-key

# JWT Configuration
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Server Configuration
DEBUG=False
LOG_LEVEL=INFO
```

### Required API Keys

1. **Azure OpenAI**
   - Go to [Azure Portal](https://portal.azure.com)
   - Create OpenAI resource
   - Get endpoint and API key

2. **FastRouter (Sora API)**
   - Visit [FastRouter](https://www.fastrouter.ai/)
   - Sign up and get API key
   - Add balance for video generation

3. **Brave Search API**
   - Register at [Brave Search API](https://api.search.brave.com/)
   - Get API key

4. **LinkedIn**
   - Create LinkedIn App
   - Get access token with `w_member_social` scope

5. **Meta (Instagram/Facebook)**
   - Create Meta App
   - Get Business Account ID and access token

## Database Setup

### PostgreSQL Local Setup

```bash
# Windows - Using PostgreSQL installer
# Download from https://www.postgresql.org/download/windows/

# Linux
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start

# Create database
createdb catalyst_db
```

### Supabase Cloud Setup

```bash
# Sign up at https://supabase.com
# Create new project
# Copy connection string to DATABASE_URL in .env
```

## Docker Deployment

### Build Image

```bash
docker build -t catalyst-ai-backend .
```

### Run Container

```bash
docker run -d \
  --name catalyst \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/catalyst \
  -e AZURE_OPENAI_KEY=<key> \
  -e FASTROUTER_API_KEY=<key> \
  catalyst-ai-backend
```

### Docker Compose

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/catalyst
      - AZURE_OPENAI_KEY=${AZURE_OPENAI_KEY}
      - FASTROUTER_API_KEY=${FASTROUTER_API_KEY}
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=catalyst
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Production Deployment

### Heroku

```bash
# Install Heroku CLI
# heroku login
# heroku create your-app-name

# Add environment variables
heroku config:set AZURE_OPENAI_KEY=<key>
heroku config:set DATABASE_URL=<database-url>

# Deploy
git push heroku main
```

### AWS EC2

```bash
# SSH into instance
ssh -i key.pem ubuntu@your-instance.compute.amazonaws.com

# Install dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-venv postgresql

# Clone repo and set up
git clone <repo>
cd catalyst-ai-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file with production values

# Run with systemd
sudo systemctl start catalyst
```

### DigitalOcean App Platform

```bash
# Push to GitHub
git push origin main

# In DigitalOcean dashboard:
# 1. Create new App
# 2. Connect GitHub repository
# 3. Configure environment variables
# 4. Deploy
```

## Monitoring & Logging

### Application Logs

```bash
# View logs
tail -f logs/app.log

# Filter by level
grep ERROR logs/app.log
```

### Health Check

```bash
# Check server status
curl http://localhost:8000/

# Check specific endpoint
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/campaigns/list
```

### Database Monitoring

```bash
# Connect to PostgreSQL
psql -U user -d catalyst_db

# Check tables
\dt

# Check connections
SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;
```

## Performance Optimization

### Database Optimization

```sql
-- Create indexes for faster queries
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_assets_project_id ON assets(project_id);
```

### Caching

```python
# Add Redis caching for frequently accessed data
from redis import Redis
redis_client = Redis(host='localhost', port=6379, db=0)

# Cache campaign results
cache_key = f"campaign:{campaign_id}"
cached = redis_client.get(cache_key)
```

### Load Balancing

```nginx
# nginx configuration for load balancing
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```

## Backup & Recovery

### Database Backup

```bash
# PostgreSQL backup
pg_dump catalyst_db > backup_$(date +%Y%m%d).sql

# Restore from backup
psql catalyst_db < backup_20240201.sql
```

### Asset Backup

```bash
# Backup generated files
tar -czf assets_backup_$(date +%Y%m%d).tar.gz static/
```

## Troubleshooting

### Database Connection Error

```
Error: could not connect to database
Solution: Check DATABASE_URL in .env and PostgreSQL is running
```

### Azure OpenAI 401 Error

```
Error: Authentication failed
Solution: Verify AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT in .env
```

### Video Generation Timeout

```
Error: Video generation timeout
Solution: Check FASTROUTER_API_KEY and account has sufficient balance
```

## Support

- Documentation: See FRONTEND_API_GUIDE.md
- Issues: File on GitHub
- Contact: support@catalyst-ai.com
