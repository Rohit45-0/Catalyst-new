@echo off
echo ============================================================
echo Starting Catalyst AI Backend Server
echo ============================================================
echo.
echo Server will start on http://127.0.0.1:8001
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

uvicorn app.main:app --reload --port 8001
