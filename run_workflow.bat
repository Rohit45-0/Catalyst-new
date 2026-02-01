@echo off
REM ============================================
REM Quick Start Script for Catalyst AI E2E Test
REM ============================================

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     Catalyst AI - End-to-End Workflow Test Launcher        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo ❌ ERROR: .env file not found!
    echo Please create .env with required API keys
    pause
    exit /b 1
)

REM Check if uploads folder exists
if not exist "uploads" (
    echo ⚠️ WARNING: uploads/ folder not found
    echo Please create uploads/ and add product images
    mkdir uploads
    echo Created empty uploads/ folder
    pause
)

echo.
echo Choose an option:
echo.
echo 1️⃣  DRY RUN (Test workflow, no posting, no video generation)
echo 2️⃣  FULL WORKFLOW (Generate content and post, no video)
echo 3️⃣  FULL WORKFLOW + VIDEO (Generate everything, use SORA credits)
echo 4️⃣  Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo 🧪 Starting DRY RUN...
    echo.
    python end_to_end_workflow.py --dry-run
    goto end
)

if "%choice%"=="2" (
    echo.
    echo 🚀 Starting FULL WORKFLOW (no video)...
    echo.
    python end_to_end_workflow.py
    goto end
)

if "%choice%"=="3" (
    echo.
    echo ⚠️  WARNING: This will generate VIDEO and use SORA credits!
    echo.
    set /p confirm="Are you sure? (yes/no): "
    if /i "%confirm%"=="yes" (
        echo.
        echo 🎬 Starting FULL WORKFLOW with VIDEO GENERATION...
        echo.
        python end_to_end_workflow.py --generate-video
    ) else (
        echo Cancelled.
    )
    goto end
)

if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
)

echo Invalid choice
goto end

:end
echo.
echo Check workflow_results_final.json for detailed results
echo.
pause
