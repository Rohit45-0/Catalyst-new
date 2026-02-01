# Full Stack Local Setup Guide - Catalyst AI

## Architecture Overview

You have **3 separate services**:

```
┌─────────────────────────────────────────────────────────┐
│          FRONTEND (React + Vite)                        │
│          Port: 5173                                     │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐    ┌──────────────────┐
│ Node.js Backend  │    │ Python Backend   │
│ (Express)        │    │ (FastAPI)        │
│ Port: 5000       │    │ Port: 8000       │
└──────────────────┘    └──────────────────┘
        │                         │
        ▼                         ▼
  ┌──────────────┐         ┌──────────────┐
  │  MongoDB     │         │ PostgreSQL   │
  └──────────────┘         └──────────────┘
```

## Current Configuration

**Frontend** (`frontend/src/api/client.js`):
- Base URL: `http://127.0.0.1:8001` ← **Currently points to port 8001**

**Node.js Backend** (`backend/server.js`):
- Port: `5000` (default)
- CORS: Configured for `http://localhost:5173`

**Python Backend** (`app/main.py`):
- Port: `8000` (default)
- CORS: Configured for all origins

## Setup Steps

### Step 1: Install Dependencies

#### Python Backend
```bash
cd d:\Downloads\LLM-Pr\catalyst-ai-backend

# Activate conda environment (if using conda)
conda activate catalyst

# Or create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Node.js Backend
```bash
cd d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\backend

npm install
```

#### Frontend
```bash
cd d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\frontend

npm install
```

### Step 2: Configure Environment Variables

#### Python Backend (`.env`)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/catalyst_db

# Azure OpenAI
AZURE_OPENAI_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-4o

# Video Generation
FASTROUTER_API_KEY=your-key

# JWT
JWT_SECRET=your-secret-key

# Server
DEBUG=False
```

#### Node.js Backend (`.env`)
```bash
# Port
PORT=5000

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:5173

# MongoDB
MONGODB_URI=mongodb://localhost:27017/catalyst

# Database name
DB_NAME=catalyst_ai_db
```

#### Frontend (`.env` or `vite.config.js`)
The frontend currently expects the backend at `http://127.0.0.1:8001`.

**Option A: Update frontend to point to Node.js backend (port 5000)**
Edit `frontend/src/api/client.js`:
```javascript
const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:5000',  // Changed from 8001 to 5000
    headers: {
        'Content-Type': 'application/json',
    },
});
```

**Option B: Update Node.js backend to run on port 8001**
Edit `backend/server.js`:
```javascript
const PORT = process.env.PORT || 8001;  // Change from 5000 to 8001
```

### Step 3: Start Databases (One Time Setup)

#### PostgreSQL (for Python Backend)
```bash
# Windows: Open Services and start PostgreSQL
# Or use command line:
pg_ctl -D "C:\Program Files\PostgreSQL\15\data" start

# Create database
createdb catalyst_db
```

#### MongoDB (for Node.js Backend)
```bash
# Windows: Open Services and start MongoDB
# Or use WSL:
mongod

# In another terminal, verify connection:
mongosh
```

### Step 4: Start All Services

Open 3 terminals and run each in its own terminal:

#### Terminal 1: Python Backend
```bash
cd d:\Downloads\LLM-Pr\catalyst-ai-backend

# Activate environment
venv\Scripts\activate

# Start server (development with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

#### Terminal 2: Node.js Backend
```bash
cd d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\backend

npm start
# OR if start script not defined:
node server.js

# Expected output:
# Server is running on port 5000
# Connected to MongoDB
```

#### Terminal 3: React Frontend
```bash
cd d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\frontend

npm run dev

# Expected output:
#   Local:   http://localhost:5173/
```

### Step 5: Test the Full Stack

1. **Open browser**: `http://localhost:5173`
2. **Register new account**: Click "Register"
   - Email: `test@example.com`
   - Password: `Test123!`
   - Full Name: `Test User`

3. **Login**: Use credentials from step 2

4. **Upload image**: 
   - Go to Dashboard → Upload
   - Select product image
   - Fill in product details
   - Click "Generate"

5. **Monitor backend**:
   - Python Backend (8000): Handles AI processing
   - Node.js Backend (5000): Handles uploads & results storage

## API Flow Diagram

```
┌─────────────────────┐
│  React Frontend     │
│  (Port 5173)        │
└──────────┬──────────┘
           │
           │ HTTP Requests
           │
    ┌──────▼────────┐
    │   Node.js     │
    │   Backend     │
    │  (Port 5000)  │
    └──────┬────────┘
           │
           │ Calls Python Backend
           │
    ┌──────▼────────┐
    │   Python      │
    │   Backend     │
    │  (Port 8000)  │
    └──────┬────────┘
           │
      ┌────┴────┐
      │ AI Agents│ (LLM processing)
      └──────────┘
```

## Frontend Pages & Features

| Page | Path | Purpose |
|------|------|---------|
| Home | `/` | Landing page |
| Login | `/login` | Authentication |
| Register | `/register` | Create account |
| Dashboard | `/dashboard` | Main app |
| Upload | `/upload` | Upload product image |
| Service Selection | `/service` | Choose generation type |
| Generation | `/generation` | Processing status |
| Results | `/results` | View generated content |
| Projects | `/projects` | View all campaigns |
| Settings | `/settings` | User preferences |

## Troubleshooting

### "Cannot connect to backend"
```
Error: Network Error: connect ECONNREFUSED 127.0.0.1:5000
```

**Solutions:**
1. Verify Node.js backend is running on port 5000
2. Check firewall isn't blocking port 5000
3. Verify frontend is pointing to correct port in `client.js`
4. Check CORS configuration in Node.js backend

### "Database connection error"
```
Error: Error connecting to MongoDB / PostgreSQL
```

**Solutions:**
1. Verify MongoDB/PostgreSQL services are running
2. Check connection strings in `.env` files
3. Create databases if they don't exist:
   ```bash
   createdb catalyst_db  # PostgreSQL
   # MongoDB creates DB automatically on first connection
   ```

### "Port already in use"
```
Error: Port 5000 is already in use
```

**Solutions:**
```bash
# Find process using port
netstat -ano | findstr :5000

# Kill process
taskkill /PID <PID> /F

# Or change port in .env or server.js
```

### "CORS error"
```
Error: Access to XMLHttpRequest from origin 'http://localhost:5173' 
has been blocked by CORS policy
```

**Solutions:**
1. Verify CORS is enabled in Node.js backend (`backend/server.js`)
2. Check CORS configuration matches frontend URL
3. Frontend URL should be `http://localhost:5173`

### "Authentication failed"
```
Error: 401 Unauthorized
```

**Solutions:**
1. Ensure JWT_SECRET is set in Python backend `.env`
2. Check token is being stored in localStorage
3. Verify token format is correct: `Bearer <token>`

## Running Without MongoDB (Optional)

If you don't have MongoDB, the frontend and Python backend will still work:

1. Only Python Backend (8000):
   - Handles all AI processing
   - Stores data in PostgreSQL

2. Run without Node.js Backend:
   - Update frontend API to call Python directly
   - Modify `frontend/src/api/client.js`:
   ```javascript
   const apiClient = axios.create({
       baseURL: 'http://127.0.0.1:8000',  // Point directly to Python
   });
   ```

## Running Without Node.js Backend (Recommended)

Since you have the Python backend which is more complete, you can:

1. **Option 1: Use Python backend only**
   ```bash
   # Start only Python backend on port 8000
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Update frontend to use it:
   # Edit frontend/src/api/client.js:
   # baseURL: 'http://127.0.0.1:8000'
   
   # Start frontend
   npm run dev
   ```

2. **Option 2: Keep Node.js as proxy**
   - Node.js backend handles uploads to MongoDB
   - Calls Python backend for AI processing
   - More modular but adds complexity

## Production Deployment

For production, follow [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md):

### Frontend (Vercel/Netlify)
```bash
npm run build
# Deploy dist/ folder
```

### Python Backend (Heroku/Railway/DigitalOcean)
```bash
git push heroku main
```

### Node.js Backend (Render/Fly/Railway)
```bash
npm run build
git push render main
```

## Next Steps

1. **Setup**: Follow "Setup Steps" above
2. **Start Services**: Run all 3 services in separate terminals
3. **Test**: Go to `http://localhost:5173` and register
4. **Upload Image**: Test campaign generation
5. **Monitor Logs**: Check all 3 terminal windows for errors

## Quick Start Commands

```bash
# Python Backend
cd d:\Downloads\LLM-Pr\catalyst-ai-backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Node.js Backend (new terminal)
cd "d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\backend"
npm start

# Frontend (new terminal)
cd "d:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\frontend"
npm run dev

# Visit http://localhost:5173
```

---

**Need help?** Check the troubleshooting section or verify all services are running with correct ports.
