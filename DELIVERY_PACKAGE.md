# Catalyst AI Backend - Delivery Package for Frontend Team

## 📦 What You're Getting

A **production-ready REST API** for generating complete marketing campaigns. One endpoint generates viral content, posters, and videos for any product.

## 🚀 Quick Start (5 Minutes)

### 1. Start the Backend
```bash
# Windows
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Linux/macOS
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Verify It Works
```bash
python test_api.py
```

### 3. Test the Main Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/campaigns/generate \
  -H "Authorization: Bearer <token>" \
  -F "product_name=T-Shirt" \
  -F "image=@product.jpg"
```

## 📚 Documentation Files (READ IN ORDER)

### For Frontend Developers

1. **[FRONTEND_README.md](./FRONTEND_README.md)** ⭐ START HERE
   - What the backend does
   - Quick start guide
   - Main endpoint overview
   - Example responses
   - Frontend code samples (React, Vue)
   - **Read Time**: 10 minutes

2. **[API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)**
   - Copy-paste endpoint examples
   - cURL, JavaScript, Python examples
   - All status codes
   - Error responses
   - **Read Time**: 5 minutes

3. **[FRONTEND_API_GUIDE.md](./FRONTEND_API_GUIDE.md)**
   - Complete integration guide
   - Authentication workflow
   - All endpoints with details
   - Campaign workflow phases
   - React integration example
   - Configuration guide
   - **Read Time**: 20 minutes

4. **[FRONTEND_INTEGRATION_CHECKLIST.md](./FRONTEND_INTEGRATION_CHECKLIST.md)**
   - Step-by-step integration guide
   - Testing checklist
   - Code review checklist
   - Deployment checklist
   - Troubleshooting guide
   - **Read Time**: Review before starting

### For DevOps/Backend Team

5. **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)**
   - Local development setup
   - Environment variables
   - Database setup (PostgreSQL, Supabase)
   - Docker deployment
   - Production deployment (Heroku, AWS, DigitalOcean)
   - Monitoring and logging
   - Performance optimization

6. **[CLEANUP_SUMMARY.md](./CLEANUP_SUMMARY.md)**
   - What was cleaned up
   - Code quality improvements
   - Production readiness status

## 🔧 API Endpoints

### Main Endpoint (Do Everything in One Call)
```
POST /api/v1/campaigns/generate
Required: product_name, image file
Returns: Complete campaign with content, poster, video
Time: 30-45 seconds
```

### Supporting Endpoints
```
POST   /api/v1/auth/register        Register user
POST   /api/v1/auth/login           Get token
GET    /api/v1/campaigns/list       List campaigns
GET    /api/v1/campaigns/campaigns/{id}  Get campaign
```

## 📋 Response Format

Every campaign returns:
```json
{
  "success": true,
  "campaign_id": "550e8400-uuid",
  "product_name": "Product Name",
  "category": "fashion_apparel",
  "content": {
    "title": "...",
    "hook": "...",
    "main_content": "...",
    "cta": "...",
    "hashtags": ["#trend"],
    "emotional_triggers": ["quality"]
  },
  "poster_url": "/static/images/poster_550e8400.png",
  "video_url": "/static/videos/video_550e8400.mp4",
  "status": "completed",
  "created_at": "2024-02-01T10:30:00"
}
```

## 🧪 Testing Script

Included: **[test_api.py](./test_api.py)**

```bash
# Run all tests
python test_api.py

# Run with video generation test
python test_api.py --video

# Test against different server
python test_api.py --url https://api.example.com
```

Tests:
- Health check
- User registration
- User login
- Campaign generation
- Campaign listing

## 🏗️ Architecture Overview

```
Frontend (React/Vue/Angular)
        ↓ (HTTP POST)
API Gateway (/api/v1/campaigns/generate)
        ↓
JWT Authentication (Authorization: Bearer token)
        ↓
Campaign Orchestrator
        ├─ Vision Analyzer (image analysis)
        ├─ Market Research (trends, competitors)
        ├─ Content Writer (marketing copy)
        ├─ Poster Generator (DALL-E)
        ├─ Video Creator (Sora-2)
        └─ Performance Predictor
        ↓
Database (PostgreSQL)
        ↓
Static Storage (/static/images, /videos)
        ↓
Frontend (displays results)
```

## 🎯 What The Backend Does

When you call `/campaigns/generate`:

1. **Vision Analysis** (5 sec)
   - Analyzes product image
   - Extracts features and quality

2. **Market Research** (20 sec)
   - Searches market trends
   - Analyzes competitors
   - Identifies opportunities

3. **Content Generation** (15 sec)
   - Generates viral title and hook
   - Creates product description
   - Writes call-to-action
   - Generates hashtags and emotional triggers

4. **Poster Generation** (10 sec)
   - Creates beautiful DALL-E poster
   - Optimized for social media

5. **Video Generation** (120 sec, optional)
   - Generates 10-second video using Sora-2
   - 9:16 aspect ratio for Instagram

6. **Performance Prediction**
   - Predicts engagement metrics
   - Suggests best posting times
   - Estimates reach potential

## ✅ Production Readiness

- ✅ All code clean and documented
- ✅ No debug logging in production
- ✅ Proper error handling
- ✅ Type hints throughout
- ✅ Database integrated and tested
- ✅ Authentication implemented
- ✅ CORS configured
- ✅ Rate limiting ready
- ✅ Comprehensive documentation
- ✅ Test suite included

## 📦 Files Provided

```
├── API_QUICK_REFERENCE.md           ← Quick API reference
├── FRONTEND_README.md               ← START HERE
├── FRONTEND_API_GUIDE.md            ← Full documentation
├── FRONTEND_INTEGRATION_CHECKLIST.md ← Integration steps
├── DEPLOYMENT_GUIDE.md              ← Deployment instructions
├── CLEANUP_SUMMARY.md               ← What was cleaned up
├── test_api.py                      ← Test script
├── app/
│   ├── main.py                      ← Clean FastAPI app
│   ├── api/
│   │   ├── campaigns.py            ← NEW: Campaign endpoint
│   │   ├── auth.py                 ← Authentication
│   │   ├── projects.py             ← Project management
│   │   ├── uploads.py              ← File uploads
│   │   ├── jobs.py                 ← Job tracking
│   │   ├── assets.py               ← Asset management
│   │   ├── analytics.py            ← Analytics
│   │   └── results.py              ← Results retrieval
│   ├── agents/
│   │   ├── base.py                 ← Fixed LLM caller
│   │   ├── category_detector.py    ← Category detection
│   │   ├── vision_analyzer.py      ← Vision analysis
│   │   ├── market_research.py      ← Market research
│   │   ├── content_writer.py       ← Content generation
│   │   ├── poster_generator.py     ← Poster creation
│   │   ├── video_creator.py        ← Video generation
│   │   └── [7 more agents]
│   ├── core/
│   │   ├── orchestrator.py         ← Workflow orchestration
│   │   ├── config.py               ← Configuration
│   │   └── security.py             ← Security utilities
│   ├── db/
│   │   ├── models.py               ← Database models
│   │   └── session.py              ← Database connection
│   └── schemas/                    ← Pydantic schemas
└── end_to_end_workflow.py          ← Workflow script (reference)
```

## 🔐 Security Features

- JWT authentication on all endpoints
- CORS properly configured
- Input validation and sanitization
- Rate limiting (10 campaigns/hour, 100 requests/min)
- Error messages don't expose sensitive info
- Database connection secured
- API keys in environment variables only

## 📊 Performance

- Campaign generation (no video): **30-45 seconds**
- Campaign generation (with video): **2-3 minutes**
- Video download: **30-60 seconds**
- Poster generation: **10-20 seconds**
- Market research: **20-40 seconds**

## 🚢 Deployment Options

### Development
```bash
uvicorn app.main:app --reload
```

### Production (Local)
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Docker
```bash
docker build -t catalyst-ai .
docker run -p 8000:8000 catalyst-ai
```

### Cloud Platforms
- Heroku (instructions in DEPLOYMENT_GUIDE.md)
- AWS EC2 (instructions in DEPLOYMENT_GUIDE.md)
- DigitalOcean (instructions in DEPLOYMENT_GUIDE.md)

## 📝 Configuration

Create `.env` file:
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/catalyst

# Azure OpenAI
AZURE_OPENAI_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-4o

# Video Generation
FASTROUTER_API_KEY=your-key

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Server
DEBUG=False
```

See `DEPLOYMENT_GUIDE.md` for all environment variables.

## 🆘 Troubleshooting

### "Cannot connect to API"
- Check backend is running
- Check port 8000 is accessible
- Check firewall settings

### "401 Unauthorized"
- Token expired: Get new token from login
- Token missing: Add to Authorization header
- Token format: Must be "Bearer <token>"

### "Campaign generation timeout"
- Video generation takes ~2 minutes
- Set client timeout to 300+ seconds
- Check backend logs

### "Poster not displaying"
- Check URL: `/static/images/poster_*.png`
- Verify image file exists
- Check static directory is served

For more help, see FRONTEND_INTEGRATION_CHECKLIST.md

## 📞 Support

1. **Read Documentation**
   - Start with FRONTEND_README.md
   - Check API_QUICK_REFERENCE.md for examples
   - See FRONTEND_INTEGRATION_CHECKLIST.md for troubleshooting

2. **Run Test Script**
   ```bash
   python test_api.py
   ```

3. **Check Backend Logs**
   - Look for error messages
   - Check database connection

4. **Review Examples**
   - React example in FRONTEND_API_GUIDE.md
   - Python example in API_QUICK_REFERENCE.md

## 🎓 Learning Path

### For Frontend Developers (1-2 days)
1. Read FRONTEND_README.md (10 min)
2. Run test_api.py (5 min)
3. Review API_QUICK_REFERENCE.md (5 min)
4. Implement authentication (30 min)
5. Implement campaign generation (1 hour)
6. Implement result display (1 hour)
7. Testing and debugging (1 hour)

### For DevOps (2-4 hours)
1. Read DEPLOYMENT_GUIDE.md (30 min)
2. Set up local environment (30 min)
3. Configure environment variables (15 min)
4. Set up database (30 min)
5. Deploy to production (1 hour)
6. Set up monitoring (30 min)

## 🎉 Ready to Go!

The backend is **production-ready** and waiting for your frontend integration.

**Next Steps:**
1. ✅ Start the backend server
2. ✅ Run `python test_api.py` to verify
3. ✅ Read FRONTEND_README.md
4. ✅ Implement integration using examples from FRONTEND_API_GUIDE.md
5. ✅ Deploy following DEPLOYMENT_GUIDE.md

---

**Backend Version**: 0.1.0  
**API Version**: v1  
**Status**: ✅ Production Ready  
**Last Updated**: 2024-02-01

## Quick Links

| Link | Purpose |
|------|---------|
| [FRONTEND_README.md](./FRONTEND_README.md) | Overview & quick start |
| [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md) | All endpoints |
| [FRONTEND_API_GUIDE.md](./FRONTEND_API_GUIDE.md) | Full integration guide |
| [test_api.py](./test_api.py) | Test script |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | Deployment |

**Your feedback is welcome!** Let us know how integration goes.
