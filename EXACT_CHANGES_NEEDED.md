# EXACT CHANGES NEEDED - Copy-Paste Ready

## Change #1: Frontend API Configuration

**File:** `making ai project neural ai - Copy/Catalyst-ai/frontend/src/api/client.js`

### BEFORE (Current):
```javascript
import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8001',
    headers: {
        'Content-Type': 'application/json',
    },
});
```

### AFTER (Updated):
```javascript
import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000',  // ✅ Changed from 8001 to 8000
    headers: {
        'Content-Type': 'application/json',
    },
});
```

**Why?** The Python backend runs on port 8000, not 8001.

---

## Change #2: Verify CORS in Python Backend

**File:** `catalyst-ai-backend/app/main.py`

### Current (Should be correct):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### For Production (Optional):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://your-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Why?** This allows the React frontend (running on port 5173) to make API calls to the Python backend (port 8000).

---

## Quick Setup (Copy-Paste Commands)

### Step 1: Update Frontend (1 file, 1 line change)

**Windows:**
```powershell
# Open the file in VS Code
code "d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\frontend\src\api\client.js"

# Change line 4:
# FROM: baseURL: 'http://127.0.0.1:8001',
# TO:   baseURL: 'http://127.0.0.1:8000',

# Save file (Ctrl+S)
```

### Step 2: Install Frontend Dependencies

```bash
cd "d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\frontend"
npm install
```

### Step 3: Start Python Backend

**Terminal 1:**
```bash
cd d:\Downloads\LLM-Pr\catalyst-ai-backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Start React Frontend

**Terminal 2:**
```bash
cd "d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\frontend"
npm run dev
```

### Step 5: Open Browser

```
http://localhost:5173
```

---

## That's It! ✅

No other changes needed. The two systems are now connected:

```
Frontend (React on 5173)
         ↓ API calls to
Python Backend (FastAPI on 8000)
         ↓ Uses
Azure OpenAI + Sora API + PostgreSQL
```

---

## Verification Checklist

- [ ] File `frontend/src/api/client.js` updated
- [ ] `baseURL` changed from `8001` to `8000`
- [ ] `npm install` ran in frontend directory
- [ ] Python backend running on port 8000
- [ ] React frontend running on port 5173
- [ ] Browser opens to `http://localhost:5173`
- [ ] Can register account
- [ ] Can upload image
- [ ] Campaign generation works

---

## If Something Goes Wrong

### "Cannot POST /api/v1/auth/login"
→ Frontend is not pointing to correct backend URL
→ Check line 4 in `frontend/src/api/client.js` - should be `8000` not `8001`

### "CORS error"
→ CORS not enabled in Python backend
→ Check `app/main.py` has CORSMiddleware configured

### "Port 8000 already in use"
```bash
# Find what's using it
netstat -ano | findstr :8000
# Kill it
taskkill /PID <PID> /F
```

### "Port 5173 already in use"
```bash
# Find what's using it
netstat -ano | findstr :5173
# Kill it
taskkill /PID <PID> /F
```

### Frontend dependencies errors
```bash
cd frontend
rm -r node_modules package-lock.json
npm install
npm run dev
```

---

## Success Indicators

✅ **Python Backend should show:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

✅ **React Frontend should show:**
```
➜  Local:   http://localhost:5173/
```

✅ **Browser should show:**
- Login page loads
- Can type email/password
- Can click register or login

✅ **Network tab should show:**
- Requests going to `http://localhost:8000/api/...`
- Status 200 for successful requests

---

## API Connection Diagram

```
┌─────────────────────────────────────┐
│  Browser                            │
│  http://localhost:5173              │
└────────────────┬────────────────────┘
                 │
                 │ HTTP Requests
                 │ (JSON)
                 │
        ┌────────▼────────┐
        │   React App     │
        │   (Vite)        │
        │   Port 5173     │
        └────────┬────────┘
                 │
     ┌───────────┴────────────┐
     │                        │
     │ API Calls to           │
     │ localhost:8000         │
     │                        │
     └───────────┬────────────┘
                 │
        ┌────────▼────────┐
        │  Python Backend │
        │  (FastAPI)      │
        │  Port 8000      │
        └────────┬────────┘
                 │
     ┌───────────┴────────────┐
     │                        │
   ▼ ▼ ▼                ▼ ▼ ▼
Azure  DB  Search    Files  Cache
OpenAI         API
```

---

## Testing the Connection

### Test 1: Backend Health Check
```bash
curl http://localhost:8000/
```
Should return:
```json
{"status": "ok", "service": "Catalyst AI Backend"}
```

### Test 2: Frontend Loads
```
Open browser to http://localhost:5173
```
Should see: Login page with email/password fields

### Test 3: API Connection
Open browser DevTools (F12) → Network tab
Then try to login with any credentials.

Should see request like:
```
POST http://localhost:8000/api/v1/auth/login
Status: 200 or 401 (depending on credentials)
```

If you see error about connection refused or CORS, something is wrong.

---

## No Other Changes Needed! 🎉

That's all. The frontend and backend will now work together seamlessly.

1. ✅ Update 1 line in `frontend/src/api/client.js`
2. ✅ Start Python backend on port 8000
3. ✅ Start React frontend on port 5173
4. ✅ Done!

**Ready to test?** → `http://localhost:5173`
