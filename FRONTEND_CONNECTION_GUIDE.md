# Connection Guide - Frontend + Backend Integration

## Your Project Structure

You have **2 separate projects**:

### Project 1: catalyst-ai-backend (Current)
- Location: `d:\Downloads\LLM-Pr\catalyst-ai-backend`
- **Python Backend** (FastAPI) - Port 8000
- Database: PostgreSQL
- AI Processing: Azure OpenAI + Sora API

### Project 2: Catalyst-ai (Attached)
- Location: `...\making ai project neural ai - Copy\Catalyst-ai`
- **React Frontend** (Vite) - Port 5173
- **Node.js Backend** (Express) - Port 5000
- Database: MongoDB

## How They're Connected

```
┌──────────────────────┐
│ React Frontend (5173)│
└──────────┬───────────┘
           │ (HTTP API calls)
           │
    ┌──────▼──────────┐
    │ Node.js (5000)  │◄──── Optional: Can be proxy
    │ (Express)       │
    └──────┬──────────┘
           │ (Can call Python backend OR handle directly)
           │
    ┌──────▼──────────┐
    │ Python (8000)   │◄──── Main AI Engine
    │ (FastAPI)       │
    └─────────────────┘
```

## Option A: Use Python Backend Only (RECOMMENDED)

**Simplest setup - Use only what you need:**

### Step 1: Update Frontend Configuration

Edit: `frontend/src/api/client.js`

Change this:
```javascript
const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8001',  // ❌ Wrong
```

To this:
```javascript
const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000',  // ✅ Point to Python backend
```

### Step 2: Update CORS in Python Backend

Edit: `app/main.py`

Ensure CORS is configured for React frontend:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 3: Start Services

**Terminal 1 - Python Backend:**
```bash
cd d:\Downloads\LLM-Pr\catalyst-ai-backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - React Frontend:**
```bash
cd "d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\frontend"
npm install
npm run dev
```

### Step 4: Open Browser
```
http://localhost:5173
```

**That's it! ✅**

---

## Option B: Use All 3 Services (Full Stack)

**If you want Node.js backend + MongoDB for additional features:**

### Step 1: Install MongoDB

**Windows:**
```bash
# Download from https://www.mongodb.com/try/download/community
# Run installer
# Verify installation:
mongosh
```

**Or use MongoDB Atlas (Cloud):**
```bash
# Sign up at https://www.mongodb.com/cloud/atlas
# Get connection string
```

### Step 2: Configure Node.js Backend

Edit: `backend/.env`
```bash
PORT=5000
FRONTEND_URL=http://localhost:5173
MONGODB_URI=mongodb://localhost:27017/catalyst
DB_NAME=catalyst_ai_db
```

### Step 3: Keep Frontend Pointing to Node.js

Frontend already configured to use port `8001` or you can change it to `5000`:

Edit: `frontend/src/api/client.js`
```javascript
const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:5000',  // ✅ Point to Node.js backend
```

### Step 4: Start All Services

**Terminal 1 - Python Backend:**
```bash
cd d:\Downloads\LLM-Pr\catalyst-ai-backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Node.js Backend:**
```bash
cd "d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\backend"
npm install
npm start
```

**Terminal 3 - React Frontend:**
```bash
cd "d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\frontend"
npm install
npm run dev
```

### Step 5: Open Browser
```
http://localhost:5173
```

---

## Quick Start (Option A - Recommended)

### 1. First Time Setup (5 minutes)

```bash
# Update frontend to use Python backend
# Edit: frontend/src/api/client.js
# Change baseURL from 'http://127.0.0.1:8001' to 'http://127.0.0.1:8000'

# Install frontend dependencies
cd "d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\frontend"
npm install
```

### 2. Start Backend

```bash
# Terminal 1
cd d:\Downloads\LLM-Pr\catalyst-ai-backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Start Frontend

```bash
# Terminal 2
cd "d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\frontend"
npm run dev

# You should see:
# ➜  Local:   http://localhost:5173/
```

### 4. Open Browser

```
http://localhost:5173
```

Register → Upload Image → Generate Campaign ✅

---

## Using Startup Scripts

### Option A: PowerShell (Windows - Easiest)

```powershell
# Start all services in separate windows
powershell -ExecutionPolicy Bypass -File start-all.ps1 all

# Or start individual services:
powershell -ExecutionPolicy Bypass -File start-all.ps1 python
powershell -ExecutionPolicy Bypass -File start-all.ps1 frontend
```

### Option B: Node.js Script

```bash
# Start all services
node setup-services.js all

# Or start individual:
node setup-services.js python
node setup-services.js frontend
```

---

## API Endpoints

### Frontend Calls These Endpoints:

**Authentication:**
```
POST /api/v1/auth/login
POST /api/v1/auth/register
GET  /api/v1/auth/me
```

**Campaign Generation:**
```
POST /api/v1/campaigns/generate
GET  /api/v1/campaigns/campaigns/{id}
GET  /api/v1/campaigns/list
```

**File Upload:**
```
POST /uploads/upload
```

**Results:**
```
GET /results/{project_id}
```

All endpoints available at: `http://localhost:8000/docs` (Swagger UI)

---

## Troubleshooting

### Frontend shows "Cannot connect to server"

**Check:**
1. Python backend is running on port 8000
2. Frontend is pointing to correct URL in `client.js`
3. CORS is enabled in `app/main.py`

**Fix:**
```bash
# Verify Python backend is running
curl http://localhost:8000/

# Should return: {"status": "ok", "service": "Catalyst AI Backend"}
```

### Port already in use

```bash
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <PID> /F
```

### Import errors in frontend

```bash
# Reinstall dependencies
cd frontend
rm -r node_modules package-lock.json
npm install
npm run dev
```

### Python dependencies missing

```bash
# Reinstall Python dependencies
cd d:\Downloads\LLM-Pr\catalyst-ai-backend
pip install -r requirements.txt
```

---

## File Changes Made

### 1. **FULL_STACK_SETUP.md** (NEW)
Complete setup guide for all 3 services

### 2. **start-all.ps1** (NEW)
PowerShell script to start all services in Windows

### 3. **setup-services.js** (NEW)
Node.js script to start services cross-platform

### 4. **frontend/src/api/client.js** (NEEDS UPDATE)
Change `baseURL` from `8001` to `8000`

---

## Recommended Workflow

### Local Development:

```bash
# Terminal 1: Python Backend
cd catalyst-ai-backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: React Frontend
cd Catalyst-ai/frontend
npm run dev

# Terminal 3: Monitor Logs (Optional)
tail -f python-backend.log
```

### Production Deployment:

```bash
# Python Backend → Heroku/Railway/DigitalOcean
# React Frontend → Vercel/Netlify
# Node.js (Optional) → Render/Fly.io/Railway
```

---

## Next Steps

1. ✅ **Choose your setup:**
   - Option A (Recommended): Python backend only
   - Option B: Full stack with Node.js

2. ✅ **Update frontend configuration:**
   - Edit `frontend/src/api/client.js`
   - Point to correct backend URL

3. ✅ **Start services:**
   - Use startup scripts OR
   - Run in separate terminals

4. ✅ **Test:**
   - Open `http://localhost:5173`
   - Register account
   - Upload image
   - Generate campaign

5. ✅ **Verify everything works:**
   - Check backend logs
   - Check frontend console
   - Upload test image

---

## Support

- **Python Backend Docs:** `http://localhost:8000/docs`
- **Frontend Issues:** Check browser console (F12)
- **Backend Logs:** Check terminal output
- **Full Setup Guide:** `FULL_STACK_SETUP.md`

---

**Status: Ready to Connect! 🚀**

**Recommended:** Start with Option A (Python backend only) - It's simpler and has all the features you need.
