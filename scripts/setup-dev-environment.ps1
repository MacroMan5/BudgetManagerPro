# Setup Development Environment for BudgetManager Pro
# Windows PowerShell Script

param(
    [switch]$SkipFrontend,
    [switch]$SkipBackend,
    [switch]$SkipDocker
)

Write-Host "🚀 Setting up BudgetManager Pro Development Environment" -ForegroundColor Green

# Check prerequisites
Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = & python --version 2>&1
    if ($pythonVersion -match "Python 3\.1[2-9]") {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python 3.12+ required. Current: $pythonVersion" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Python not found. Please install Python 3.12+" -ForegroundColor Red
    exit 1
}

# Check Node.js
if (-not $SkipFrontend) {
    try {
        $nodeVersion = & node --version 2>&1
        if ($nodeVersion -match "v(18|19|20|21)\.") {
            Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
        } else {
            Write-Host "❌ Node.js 18+ required. Current: $nodeVersion" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
        exit 1
    }
}

# Check Docker
if (-not $SkipDocker) {
    try {
        $dockerVersion = & docker --version 2>&1
        Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Docker not found. Docker setup will be skipped." -ForegroundColor Yellow
        $SkipDocker = $true
    }
}

# Setup Backend
if (-not $SkipBackend) {
    Write-Host "`n🐍 Setting up Python Backend..." -ForegroundColor Yellow
    Set-Location "src\backend"
    
    # Create virtual environment
    Write-Host "Creating Python virtual environment..."
    python -m venv venv
    
    # Activate virtual environment
    Write-Host "Activating virtual environment..."
    & ".\venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    Write-Host "Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install dependencies
    Write-Host "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Setup database
    Write-Host "Setting up database..."
    if (Test-Path "alembic.ini") {
        alembic upgrade head
    }
    
    Set-Location "..\..\"
    Write-Host "✅ Backend setup complete!" -ForegroundColor Green
}

# Setup Frontend
if (-not $SkipFrontend) {
    Write-Host "`n⚛️ Setting up React Frontend..." -ForegroundColor Yellow
    Set-Location "src\frontend"
    
    # Install dependencies
    Write-Host "Installing Node.js dependencies..."
    npm install
    
    # Build development assets
    Write-Host "Building development assets..."
    npm run build:dev
    
    Set-Location "..\..\"
    Write-Host "✅ Frontend setup complete!" -ForegroundColor Green
}

# Setup Docker
if (-not $SkipDocker) {
    Write-Host "`n🐳 Setting up Docker environment..." -ForegroundColor Yellow
    
    # Build Docker images
    Write-Host "Building Docker images..."
    docker-compose build
    
    Write-Host "✅ Docker setup complete!" -ForegroundColor Green
}

# Create environment files
Write-Host "`n📝 Creating environment configuration..." -ForegroundColor Yellow

if (-not (Test-Path "src\backend\.env")) {
    Copy-Item "src\backend\.env.example" "src\backend\.env"
    Write-Host "Created backend .env file from template"
}

if (-not (Test-Path "src\frontend\.env")) {
    Copy-Item "src\frontend\.env.example" "src\frontend\.env"
    Write-Host "Created frontend .env file from template"
}

Write-Host "`n🎉 Development environment setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Review and update .env files with your configuration"
Write-Host "2. Run 'scripts\run-local.ps1' to start development servers"
Write-Host "3. Open http://localhost:3000 in your browser"
Write-Host "4. Check docs\development-setup.md for detailed instructions"
