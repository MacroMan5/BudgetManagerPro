# Run Local Development Servers
# Windows PowerShell Script

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$Docker
)

Write-Host "🚀 Starting BudgetManager Pro Development Servers" -ForegroundColor Green

if ($Docker) {
    Write-Host "`n🐳 Starting Docker environment..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "✅ Docker services started!" -ForegroundColor Green
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    exit 0
}

# Function to start backend
function Start-Backend {
    Write-Host "`n🐍 Starting FastAPI Backend..." -ForegroundColor Yellow
    Set-Location "src\backend"
    
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    # Start FastAPI server
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    
    Set-Location "..\..\"
    Write-Host "✅ Backend started on http://localhost:8000" -ForegroundColor Green
}

# Function to start frontend
function Start-Frontend {
    Write-Host "`n⚛️ Starting React Frontend..." -ForegroundColor Yellow
    Set-Location "src\frontend"
    
    # Start Vite dev server
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"
    
    Set-Location "..\..\"
    Write-Host "✅ Frontend started on http://localhost:3000" -ForegroundColor Green
}

# Start services based on parameters
if ($BackendOnly) {
    Start-Backend
} elseif ($FrontendOnly) {
    Start-Frontend
} else {
    Start-Backend
    Start-Sleep -Seconds 3
    Start-Frontend
}

Write-Host "`n🎉 Development servers are starting!" -ForegroundColor Green
Write-Host "`nAvailable endpoints:" -ForegroundColor Yellow
if (-not $FrontendOnly) {
    Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "ReDoc: http://localhost:8000/redoc" -ForegroundColor Cyan
}
if (-not $BackendOnly) {
    Write-Host "Frontend App: http://localhost:3000" -ForegroundColor Cyan
}

Write-Host "`nPress Ctrl+C to stop servers" -ForegroundColor Yellow

# Wait for user input to keep script running
Read-Host "Press Enter to exit"
