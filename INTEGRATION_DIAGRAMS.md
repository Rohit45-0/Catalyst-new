# Visual Integration Guide

## Before (Disconnected)
```
Frontend (Vite)              Backend (FastAPI)
Port 5173                    Port 8000
✓ Running                    ✓ Running
✗ Not Connected              ✗ Not Connected

       ❌ NO COMMUNICATION
```

## After (Connected)
```
Frontend (Vite)              Backend (FastAPI)
Port 5173                    Port 8000
✓ Running                    ✓ Running
✓ Connected                  ✓ Connected

       ✅ API CALLS WORKING
```

---

## The Change

```
FILE: frontend/src/api/client.js
LINE: 4

BEFORE:                      AFTER:
┌──────────────────┐         ┌──────────────────┐
│ baseURL:         │         │ baseURL:         │
│ 'http://127...'  │    →    │ 'http://127...'  │
│ :8001            │         │ :8000            │
└──────────────────┘         └──────────────────┘
     ❌ Wrong              ✅ Correct
```

---

## Data Flow

### User Action
```
User clicks "Generate Campaign"
         ↓
React Component handles click
         ↓
Calls: POST /api/v1/campaigns/generate
         ↓
Frontend sends request to:
http://localhost:8000/api/v1/campaigns/generate
         ↓
Python Backend receives request
         ↓
AI Agents process image:
  1. Vision Analysis
  2. Market Research
  3. Content Generation
  4. Poster Generation
  5. Video Generation (optional)
         ↓
Backend returns results:
{
  campaign_id: "...",
  content: {...},
  poster_url: "/static/images/...",
  video_url: "/static/videos/..."
}
         ↓
Frontend displays results
         ↓
User sees generated campaign
```

---

## Service Ports

```
┌─────────────────────────────────────────────────┐
│               Local Machine (Your PC)           │
├─────────────────────────────────────────────────┤
│                                                 │
│  localhost:5173  ← React Frontend (Vite)       │
│  localhost:8000  ← Python Backend (FastAPI)    │
│  localhost:27017 ← MongoDB (if used)           │
│  localhost:5432  ← PostgreSQL (if used)        │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Request/Response Example

### Request from Frontend
```
POST http://localhost:8000/api/v1/campaigns/generate
Headers:
  Content-Type: multipart/form-data
  Authorization: Bearer <token>

Body:
  {
    product_name: "Cotton T-Shirt",
    brand_name: "MyBrand",
    image: <file>,
    generate_video: true
  }
```

### Response from Backend
```
200 OK
{
  "success": true,
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "product_name": "Cotton T-Shirt",
  "category": "fashion_apparel",
  "content": {
    "title": "Premium Cotton Comfort",
    "hook": "Discover the perfect shirt",
    "main_content": "High-quality cotton blend...",
    "cta": "Shop now",
    "hashtags": ["#fashion", "#comfort"]
  },
  "poster_url": "/static/images/poster_550e8400.png",
  "video_url": "/static/videos/video_550e8400.mp4",
  "status": "completed"
}
```

### Frontend Displays
```
┌─────────────────────────────────┐
│    Campaign Results             │
├─────────────────────────────────┤
│                                 │
│  Premium Cotton Comfort         │
│                                 │
│  [POSTER IMAGE]                │
│                                 │
│  Discover the perfect shirt... │
│  High-quality cotton blend...  │
│                                 │
│  [VIDEO PLAYER]                │
│                                 │
│  [Share to Social Media]        │
│                                 │
└─────────────────────────────────┘
```

---

## Component Interaction

```
User Interface
(React Components)
     ↓
API Client Layer
(axios interceptors)
     ↓
HTTP Request
(localhost:8000)
     ↓
FastAPI Server
(Python Backend)
     ↓
AI Agents
(LLM Processing)
     ↓
External APIs
(Azure OpenAI, Sora, Brave)
     ↓
Database
(PostgreSQL)
     ↓
Response to Frontend
     ↓
Display Results
```

---

## File Organization

```
catalyst-ai-backend/
├── app/
│   ├── main.py               ← Server starts here
│   ├── api/
│   │   ├── campaigns.py      ← Campaign endpoint
│   │   ├── auth.py           ← Auth endpoints
│   │   └── ...
│   ├── agents/
│   │   ├── base.py           ← Base agent
│   │   ├── vision_analyzer.py
│   │   ├── content_writer.py
│   │   └── ... (10+ agents)
│   └── db/
│       ├── models.py         ← Database schema
│       └── session.py        ← DB connection
│
└── Catalyst-ai/
    ├── frontend/             ← React app
    │   ├── src/
    │   │   ├── App.jsx       ← Main app
    │   │   ├── api/
    │   │   │   ├── client.js ← API client (UPDATED)
    │   │   │   └── endpoints.js
    │   │   ├── components/
    │   │   ├── pages/
    │   │   └── ...
    │   └── package.json      ← Dependencies
    │
    └── backend/              ← Node.js (optional)
        ├── server.js
        └── ...
```

---

## What Happens When You Click "Generate"

```
FRONTEND                          BACKEND

User clicks                       
"Generate"
  ↓
Check login ✓
  ↓
Validate image ✓
  ↓
Show "Loading..."
  ↓
Build request
  ↓
POST /campaigns/generate ────→ Receive request
                              ↓
                              Validate auth ✓
                              ↓
                              Save image
                              ↓
                              Run Phase 1: Analysis
                              ├─ Vision Analyzer
                              ├─ Category Detector
                              └─ Emotion Mapper
                              ↓
                              Run Phase 2: Intelligence
                              ├─ Market Research
                              ├─ Competitor Analysis
                              └─ Hook Generation
                              ↓
                              Run Phase 3: Creation
                              ├─ Content Writer
                              ├─ Poster Generator (DALL-E)
                              └─ Video Generator (Sora)
                              ↓
                              Run Phase 4: Publishing
                              └─ Publish to Social Media
                              ↓
                              Save to Database
                              ↓
                              Return results ←─ Receive response
  ↓
Parse JSON
  ↓
Display campaign
  ↓
Show poster image
  ↓
Show content
  ↓
Enable video playback
  ↓
✓ Done!
```

---

## Error Handling

```
Request Fails
  ↓
Check Status Code
  ↓
┌──────────────────────────┐
│ 400 Bad Request          │ → User entered invalid data
│ 401 Unauthorized         │ → Login expired, re-auth needed
│ 404 Not Found            │ → Endpoint doesn't exist
│ 429 Rate Limited         │ → Too many requests, wait
│ 500 Server Error         │ → Backend issue, check logs
│ CORS Error               │ → Wrong baseURL in client.js
│ Network Error (refused)  │ → Backend not running
└──────────────────────────┘
  ↓
Display appropriate error
to user
```

---

## Configuration Checklist

```
✅ Python Backend
   ├─ Port: 8000
   ├─ CORS: Enabled
   ├─ Database: PostgreSQL configured
   ├─ Auth: JWT configured
   └─ Ready: YES

✅ React Frontend
   ├─ Port: 5173
   ├─ baseURL: http://localhost:8000
   ├─ Token handling: localStorage
   └─ Ready: YES

✅ Connection
   ├─ Frontend → Backend: ✓
   ├─ API endpoints: ✓
   ├─ CORS allowed: ✓
   └─ Ready: YES
```

---

## Quick Reference

| What | Where | Port |
|------|-------|------|
| React Frontend | localhost:5173 | 5173 |
| Python Backend | localhost:8000 | 8000 |
| API Docs | localhost:8000/docs | 8000 |
| PostgreSQL | localhost:5432 | 5432 |

---

## Workflow After Connection

```
1. Open http://localhost:5173
2. Register account
3. Login
4. Upload product image
5. Fill product details
6. Click "Generate"
7. Backend processes (2-3 minutes)
8. See results:
   - Generated content
   - AI poster
   - Video
   - Performance metrics
9. Share to social media (optional)
10. Save campaign
```

---

## Key Files to Remember

1. **Frontend Config**: `frontend/src/api/client.js` (baseURL = 8000)
2. **Backend Server**: `app/main.py` (CORS enabled)
3. **Campaign API**: `app/api/campaigns.py` (main endpoint)
4. **Frontend App**: `frontend/src/App.jsx` (routing)
5. **Tests**: `test_api.py` (verify backend)

---

## Success Indicators

```
✅ Backend terminal shows: "Application startup complete"
✅ Frontend terminal shows: "Local: http://localhost:5173/"
✅ Browser loads http://localhost:5173 (no errors)
✅ Can register account
✅ Can login successfully
✅ Can upload image
✅ Can generate campaign
✅ See generated content, poster, video
```

---

**Everything is connected and ready to go!** 🚀
