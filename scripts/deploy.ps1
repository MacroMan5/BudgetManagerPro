# PowerShell Deployment Script for BudgetManager Pro
# Windows equivalent of deploy.sh

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("deploy", "rollback", "health-check", "backup", "cleanup")]
    [string]$Action,
    
    [Parameter()]
    [ValidateSet("staging", "production")]
    [string]$Environment,
    
    [Parameter()]
    [string]$Tag = "latest",
    
    [Parameter()]
    [string]$Host = "localhost"
)

# Configuration
$DEPLOY_USER = "deploy"
$PROD_HOST = "budgetmanager.example.com"
$STAGING_HOST = "staging.budgetmanager.example.com"
$APP_DIR = "/opt/budgetmanager"
$BACKUP_DIR = "/opt/budgetmanager-backups"

# Logging functions
function Write-InfoLog {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-WarnLog {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-ErrorLog {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if command exists
function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# Validate prerequisites
function Test-Prerequisites {
    Write-InfoLog "Validating prerequisites..."
    
    if (-not (Test-Command "docker")) {
        Write-ErrorLog "Docker is not installed"
        exit 1
    }
    
    if (-not (Test-Command "docker-compose")) {
        Write-ErrorLog "Docker Compose is not installed"
        exit 1
    }
    
    if (-not (Test-Command "git")) {
        Write-ErrorLog "Git is not installed"
        exit 1
    }
    
    Write-InfoLog "Prerequisites validated successfully"
}

# Create backup
function New-Backup {
    param([string]$Environment)
    
    Write-InfoLog "Creating backup for $Environment environment..."
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "$BACKUP_DIR/backup_${Environment}_${timestamp}.tar.gz"
    
    # Create backup directory if it doesn't exist
    if (-not (Test-Path $BACKUP_DIR)) {
        New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
    }
    
    # Use tar (available in Windows 10+) or 7-Zip for backup
    $appPath = "$APP_DIR-$Environment"
    
    try {
        if (Test-Command "tar") {
            tar -czf $backupFile -C $appPath docker-compose.prod.yml .env data/ 2>$null
        } else {
            Write-WarnLog "tar command not available, using Compress-Archive"
            $tempPath = "$env:TEMP\budgetmanager_backup_$timestamp"
            Copy-Item -Path "$appPath\docker-compose.prod.yml", "$appPath\.env" -Destination $tempPath -Force
            Copy-Item -Path "$appPath\data" -Destination $tempPath -Recurse -Force -ErrorAction SilentlyContinue
            Compress-Archive -Path "$tempPath\*" -DestinationPath "$backupFile.zip" -Force
            Remove-Item -Path $tempPath -Recurse -Force
        }
        
        Write-InfoLog "Backup created: $backupFile"
        
        # Keep only last 10 backups
        Get-ChildItem -Path $BACKUP_DIR -Filter "backup_${Environment}_*" | 
            Sort-Object LastWriteTime -Descending | 
            Select-Object -Skip 10 | 
            Remove-Item -Force
            
    } catch {
        Write-ErrorLog "Failed to create backup: $_"
        return $false
    }
    
    return $true
}

# Health check
function Test-Health {
    param([string]$HostToCheck)
    
    Write-InfoLog "Performing health check for $HostToCheck..."
    
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://${HostToCheck}:8000/health" -Method GET -TimeoutSec 10 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-InfoLog "Health check passed"
                return $true
            }
        } catch {
            # Ignore errors and continue retrying
        }
        
        Write-WarnLog "Health check attempt $attempt/$maxAttempts failed, retrying in 10 seconds..."
        Start-Sleep -Seconds 10
        $attempt++
    }
    
    Write-ErrorLog "Health check failed after $maxAttempts attempts"
    return $false
}

# Deploy to environment
function Start-Deployment {
    param(
        [string]$Environment,
        [string]$Tag
    )
    
    Write-InfoLog "Deploying to $Environment environment with tag: $Tag"
    
    # Set environment-specific variables
    switch ($Environment) {
        "staging" {
            $targetHost = $STAGING_HOST
            $appPath = "$APP_DIR-staging"
        }
        "production" {
            $targetHost = $PROD_HOST
            $appPath = "$APP_DIR-prod"
        }
        default {
            Write-ErrorLog "Unknown environment: $Environment"
            exit 1
        }
    }
    
    # Create backup before deployment
    if (-not (New-Backup $Environment)) {
        Write-ErrorLog "Failed to create backup, aborting deployment"
        exit 1
    }
    
    try {
        # Change to app directory
        Push-Location $appPath
        
        # Backup current docker-compose file
        Copy-Item "docker-compose.prod.yml" "docker-compose.prod.yml.backup" -Force
        
        # Update docker-compose file with new image tags
        Write-InfoLog "Updating docker-compose configuration..."
        $composeContent = Get-Content "docker-compose.prod.yml" -Raw
        $composeContent = $composeContent -replace "image: ghcr\.io/.*/budgetmanager-backend:.*", "image: ghcr.io/username/budgetmanager-backend:$Tag"
        $composeContent = $composeContent -replace "image: ghcr\.io/.*/budgetmanager-frontend:.*", "image: ghcr.io/username/budgetmanager-frontend:$Tag"
        Set-Content "docker-compose.prod.yml" $composeContent
        
        # Pull new images
        Write-InfoLog "Pulling new Docker images..."
        docker-compose -f docker-compose.prod.yml pull
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to pull Docker images"
        }
        
        # Start services
        Write-InfoLog "Starting services..."
        docker-compose -f docker-compose.prod.yml up -d
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to start services"
        }
        
        # Wait for services to be ready
        Start-Sleep -Seconds 30
        
        # Perform health check
        if (-not (Test-Health "localhost")) {
            Write-ErrorLog "Deployment failed - health check failed"
            Start-Rollback $Environment
            exit 1
        }
        
        Write-InfoLog "Deployment to $Environment completed successfully"
        
    } catch {
        Write-ErrorLog "Deployment failed: $_"
        Start-Rollback $Environment
        exit 1
    } finally {
        Pop-Location
    }
}

# Rollback to previous version
function Start-Rollback {
    param([string]$Environment)
    
    Write-WarnLog "Rolling back $Environment environment..."
    
    switch ($Environment) {
        "staging" {
            $appPath = "$APP_DIR-staging"
        }
        "production" {
            $appPath = "$APP_DIR-prod"
        }
        default {
            Write-ErrorLog "Unknown environment: $Environment"
            exit 1
        }
    }
    
    try {
        Push-Location $appPath
        
        # Stop current services
        docker-compose -f docker-compose.prod.yml down
        
        # Restore from backup
        if (Test-Path "docker-compose.prod.yml.backup") {
            Copy-Item "docker-compose.prod.yml.backup" "docker-compose.prod.yml" -Force
            Write-InfoLog "Configuration restored from backup"
        } else {
            Write-ErrorLog "No backup configuration found"
            exit 1
        }
        
        # Start services with previous configuration
        docker-compose -f docker-compose.prod.yml up -d
        
        # Wait and check health
        Start-Sleep -Seconds 30
        if (Test-Health "localhost") {
            Write-InfoLog "Rollback completed successfully"
        } else {
            Write-ErrorLog "Rollback failed - manual intervention required"
            exit 1
        }
        
    } catch {
        Write-ErrorLog "Rollback failed: $_"
        exit 1
    } finally {
        Pop-Location
    }
}

# Cleanup old images and containers
function Start-Cleanup {
    Write-InfoLog "Cleaning up old Docker images and containers..."
    
    try {
        # Remove stopped containers
        docker container prune -f
        
        # Remove unused images
        docker image prune -f
        
        # Remove unused networks
        docker network prune -f
        
        # Note: Be careful with volume pruning in production
        # docker volume prune -f
        
        Write-InfoLog "Cleanup completed"
    } catch {
        Write-ErrorLog "Cleanup failed: $_"
        exit 1
    }
}

# Main execution
function Main {
    switch ($Action) {
        "deploy" {
            if (-not $Environment) {
                Write-ErrorLog "Environment parameter is required for deploy action"
                exit 1
            }
            Test-Prerequisites
            Start-Deployment $Environment $Tag
        }
        "rollback" {
            if (-not $Environment) {
                Write-ErrorLog "Environment parameter is required for rollback action"
                exit 1
            }
            Test-Prerequisites
            Start-Rollback $Environment
        }
        "health-check" {
            Test-Health $Host
        }
        "backup" {
            if (-not $Environment) {
                Write-ErrorLog "Environment parameter is required for backup action"
                exit 1
            }
            New-Backup $Environment
        }
        "cleanup" {
            Start-Cleanup
        }
        default {
            Write-Host "Usage: .\deploy.ps1 -Action <action> [-Environment <env>] [-Tag <tag>] [-Host <host>]"
            Write-Host ""
            Write-Host "Actions:"
            Write-Host "  deploy          - Deploy to staging or production"
            Write-Host "  rollback        - Rollback to previous version"
            Write-Host "  health-check    - Perform health check"
            Write-Host "  backup          - Create backup"
            Write-Host "  cleanup         - Clean up old Docker resources"
            Write-Host ""
            Write-Host "Examples:"
            Write-Host "  .\deploy.ps1 -Action deploy -Environment staging -Tag v1.2.0"
            Write-Host "  .\deploy.ps1 -Action deploy -Environment production -Tag v1.2.0"
            Write-Host "  .\deploy.ps1 -Action rollback -Environment production"
            Write-Host "  .\deploy.ps1 -Action health-check -Host localhost"
            Write-Host "  .\deploy.ps1 -Action backup -Environment production"
            exit 1
        }
    }
}

# Run main function
Main
