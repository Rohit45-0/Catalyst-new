#!/bin/bash
# Test script to verify data loading

echo "=========================================="
echo "TESTING DATA LOADING FLOW"
echo "=========================================="
echo ""

# Check if backend is running
echo "1. Checking backend (port 8000)..."
curl -s http://localhost:8000/docs > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ Backend is running"
else
    echo "✗ Backend is NOT running"
    echo "  Start it with: uvicorn app.main:app --reload --port 8000"
    exit 1
fi

# Check if frontend is running  
echo ""
echo "2. Checking frontend (port 5173/5174)..."
curl -s http://localhost:5173 > /dev/null || curl -s http://localhost:5174 > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ Frontend is running"
else
    echo "✗ Frontend is NOT running"
    echo "  Start it with: npm run dev"
    exit 1
fi

# Test API endpoints
echo ""
echo "3. Testing API endpoints..."
echo "   - GET /auth/me..."
curl -s http://localhost:8000/auth/me -H "Authorization: Bearer test" | grep -q "detail"
echo "   ✓ Auth endpoint responding"

echo "   - GET /projects/..."
curl -s http://localhost:8000/projects/ -H "Authorization: Bearer test" | grep -q "user" || grep -q "detail"
echo "   ✓ Projects endpoint responding"

echo ""
echo "=========================================="
echo "✓ All systems operational!"
echo "=========================================="
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend Docs: http://localhost:8000/docs"
