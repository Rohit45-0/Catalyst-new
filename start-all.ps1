# Catalyst AI - Full Stack Startup Script (Windows PowerShell)
# Run with: powershell -ExecutionPolicy Bypass -File start-all.ps1

param(
    [string]$Service = "all"
)

$services = @{
    "python" = @{
        "name" = "Python Backend (FastAPI)"
        "path" = "D:\Downloads\LLM-Pr\catalyst-ai-backend"
        "command" = "python"
        "args" = @("-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000")
        "port" = 8000
    }
    "nodejs" = @{
        "name" = "Node.js Backend (Express)"
        "path" = "D:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\backend"
        "command" = "npm"
        "args" = @("start")
        "port" = 5000
    }
    "frontend" = @{
        "name" = "React Frontend (Vite)"
        "path" = "D:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\frontend"
        "command" = "npm"
        "args" = @("run", "dev")
        "port" = 5173
    }
}

function Start-Service {
    param([string]$ServiceName)
    
    $service = $services[$ServiceName]
    if (-not $service) {
        Write-Host "❌ Unknown service: $ServiceName" -ForegroundColor Red
        return
    }
    
    Write-Host "🚀 Starting $($service.name) on port $($service.port)..." -ForegroundColor Cyan
    Write-Host "📁 Working directory: $($service.path)" -ForegroundColor Gray
    
    Push-Location $service.path
    
    try {
        & $service.command @($service.args)
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    } finally {
        Pop-Location
    }
}

function Show-Help {
    Write-Host "`n" -ForegroundColor Magenta
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║  Catalyst AI - Full Stack Setup            ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "Usage: powershell -ExecutionPolicy Bypass -File start-all.ps1 [service]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Available services:" -ForegroundColor Green
    Write-Host "  all       - Start all services (Python, Node.js, React)" -ForegroundColor Green
    Write-Host "  python    - Start Python backend only" -ForegroundColor Cyan
    Write-Host "  nodejs    - Start Node.js backend only" -ForegroundColor Green
    Write-Host "  frontend  - Start React frontend only" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Magenta
    Write-Host "  powershell -ExecutionPolicy Bypass -File start-all.ps1 all" -ForegroundColor Gray
    Write-Host "  powershell -ExecutionPolicy Bypass -File start-all.ps1 python" -ForegroundColor Gray
    Write-Host ""
}

function Show-Status {
    Write-Host "`n" -ForegroundColor Magenta
    Write-Host "════════════════════════════════════════════" -ForegroundColor Magenta
    Write-Host "✅ All services started!" -ForegroundColor Green
    Write-Host "════════════════════════════════════════════" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "📍 Services running at:" -ForegroundColor Yellow
    Write-Host "   Frontend:      http://localhost:5173" -ForegroundColor Cyan
    Write-Host "   Node.js:       http://localhost:5000" -ForegroundColor Green
    Write-Host "   Python:        http://localhost:8000" -ForegroundColor Yellow
    Write-Host "   API Docs:      http://localhost:8000/docs" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔍 To open browser:" -ForegroundColor Magenta
    Write-Host "   start http://localhost:5173" -ForegroundColor Gray
    Write-Host ""
}

# Main execution
if ($Service -eq "all") {
    Write-Host "🔄 Starting all services..." -ForegroundColor Magenta
    
    # Start services in separate windows for Windows
    $python_path = "D:\Downloads\LLM-Pr\catalyst-ai-backend"
    $nodejs_path = "D:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\backend"
    $frontend_path = "D:\Downloads\LLM-Pr\catalyst-ai-backend\making ai project neural ai - Copy\Catalyst-ai\frontend"
    
    # Create batch scripts to run in separate windows
    $pythonScript = @"
@echo off
cd /d "$python_path"
cmd /k "venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
"@
    
    $nodejsScript = @"
@echo off
cd /d "$nodejs_path"
cmd /k "npm start"
"@
    
    $frontendScript = @"
@echo off
cd /d "$frontend_path"
cmd /k "npm run dev"
"@
    
    $pythonScript | Out-File -FilePath "$env:TEMP\start-python.bat" -Encoding ASCII -Force
    $nodejsScript | Out-File -FilePath "$env:TEMP\start-nodejs.bat" -Encoding ASCII -Force
    $frontendScript | Out-File -FilePath "$env:TEMP\start-frontend.bat" -Encoding ASCII -Force
    
    # Start processes
    Start-Process "$env:TEMP\start-python.bat" -WindowStyle Normal
    Start-Sleep -Seconds 2
    Start-Process "$env:TEMP\start-nodejs.bat" -WindowStyle Normal
    Start-Sleep -Seconds 2
    Start-Process "$env:TEMP\start-frontend.bat" -WindowStyle Normal
    
    Show-Status
    
} elseif ($Service -eq "python" -or $Service -eq "nodejs" -or $Service -eq "frontend") {
    Start-Service -ServiceName $Service
} elseif ($Service -eq "" -or $Service -eq "help" -or $Service -eq "-h" -or $Service -eq "--help") {
    Show-Help
} else {
    Write-Host "❌ Unknown service: $Service" -ForegroundColor Red
    Show-Help
}
