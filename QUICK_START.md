# 🚀 QUICK START - Connect Frontend + Backend (5 Minutes)

## The Situation

You have:
- **Python Backend** (port 8000) ✅ Ready
- **React Frontend** (port 5173) ✅ Ready
- **Frontend needs to be updated** to talk to backend

## The Fix (1 Change, 1 Line)

### Edit This File:
```
making ai project neural ai - Copy/Catalyst-ai/frontend/src/api/client.js
```

### Change This Line:
```javascript
// BEFORE:
baseURL: 'http://127.0.0.1:8001',

// AFTER:
baseURL: 'http://127.0.0.1:8000',
```

That's it! ✅

---

## Start Everything (3 Commands)

### Terminal 1: Python Backend
```bash
cd d:\Downloads\LLM-Pr\catalyst-ai-backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: React Frontend
```bash
cd "d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\frontend"
npm install
npm run dev
```

### Terminal 3: Open Browser
```
http://localhost:5173
```

---

## What You Should See

✅ **Terminal 1 (Backend):**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

✅ **Terminal 2 (Frontend):**
```
➜  Local:   http://localhost:5173/
```

✅ **Browser:**
- Login page shows
- Can register account
- Can upload image
- Can generate campaigns

---

## Done! 🎉

The frontend will now communicate with the Python backend automatically.

### Next: Test It
1. Open `http://localhost:5173`
2. Click "Register"
3. Create account
4. Upload product image
5. Generate campaign

---

## If It Doesn't Work

### Problem: "Cannot connect to server"
**Solution:** Check that Python backend is actually running on port 8000
```bash
curl http://localhost:8000/
# Should return: {"status": "ok"}
```

### Problem: "Port 8000 already in use"
**Solution:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Problem: Frontend dependencies error
**Solution:**
```bash
cd frontend
rm -r node_modules package-lock.json
npm install
npm run dev
```

---

## Full Documentation

For detailed setup information, see:

📚 **[EXACT_CHANGES_NEEDED.md](./EXACT_CHANGES_NEEDED.md)** ← Copy-paste ready changes  
📚 **[FRONTEND_CONNECTION_GUIDE.md](./FRONTEND_CONNECTION_GUIDE.md)** ← Complete connection guide  
📚 **[FULL_STACK_SETUP.md](./FULL_STACK_SETUP.md)** ← All services (Python + Node.js + React)  
📚 **[FRONTEND_API_GUIDE.md](./FRONTEND_API_GUIDE.md)** ← API documentation

---

## Architecture

```
Your Computer (Local Machine)
├─ Python Backend
│  └─ Port 8000
│     ├─ Azure OpenAI
│     ├─ Sora API
│     └─ PostgreSQL
│
└─ React Frontend
   └─ Port 5173
      └─ Calls backend APIs
```

---

## Files Changed

✅ 1 line changed in: `frontend/src/api/client.js`

That's literally it. No other changes needed!

---

## Startup Shortcuts (Windows)

### Option 1: Use PowerShell Script
```powershell
powershell -ExecutionPolicy Bypass -File start-all.ps1 all
```
This starts all services in separate windows automatically.

### Option 2: Use Node Script
```bash
node setup-services.js all
```

### Option 3: Manual (3 terminals)
```bash
# Terminal 1
cd d:\Downloads\LLM-Pr\catalyst-ai-backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Terminal 2
cd "d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\frontend"
npm install && npm run dev

# Terminal 3
start http://localhost:5173
```

---

## Verify It's Working

### Check 1: Backend is running
```bash
curl http://localhost:8000/
# Expected: {"status": "ok", "service": "Catalyst AI Backend"}
```

### Check 2: Frontend loads
```
Open http://localhost:5173 in browser
```

### Check 3: Login works
1. Register new account
2. Try logging in
3. Check browser DevTools (F12) Network tab
4. Should see requests to `http://localhost:8000/api/...`

---

## Success! 🎉

When everything works, you'll see:
- Frontend at `http://localhost:5173`
- Python backend handling all AI processing
- Campaign generation working
- Images and videos being generated

---

## Support

**Question?** → Check files in order:
1. `EXACT_CHANGES_NEEDED.md` - Copy-paste ready
2. `FRONTEND_CONNECTION_GUIDE.md` - Connection details
3. `FULL_STACK_SETUP.md` - Complete setup
4. `FRONTEND_API_GUIDE.md` - API reference

**Still stuck?** 
- Check terminal logs
- Open browser DevTools (F12)
- Verify ports are correct
- Make sure you updated the 1 line in `client.js`

---

## Summary

| Step | Action | Time |
|------|--------|------|
| 1 | Update 1 line in `client.js` | 1 min |
| 2 | `npm install` frontend | 2 min |
| 3 | Start Python backend | 1 min |
| 4 | Start React frontend | 1 min |
| **Total** | **Connection Complete** | **~5 min** |

---

**You're ready to go! Start from "Terminal 1: Python Backend" above.** 🚀
