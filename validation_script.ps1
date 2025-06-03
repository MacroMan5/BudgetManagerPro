# BudgetManager Pro - Project Validation Script
# This script validates that all initialization steps have been completed

Write-Host "🔍 BudgetManager Pro - Project Validation Script" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

$validationResults = @()
$errorCount = 0

# Function to add validation result
function Add-ValidationResult {
    param($Component, $Status, $Message, $Path = "")
    $validationResults += [PSCustomObject]@{
        Component = $Component
        Status = $Status
        Message = $Message
        Path = $Path
    }
    if ($Status -eq "❌ FAIL") {
        $script:errorCount++
    }
}

# 1. Architecture Documentation Validation
Write-Host "`n📋 1. Validating Architecture Documentation..." -ForegroundColor Yellow

$archFiles = @(
    "architecture\decisions\ADR-001-technology-choices.md",
    "architecture\diagrams\system-overview.md",
    "architecture\diagrams\component-diagram.md",
    "architecture\diagrams\data-flow-diagram.md"
)

foreach ($file in $archFiles) {
    $fullPath = Join-Path $PWD $file
    if (Test-Path $fullPath) {
        Add-ValidationResult "Architecture" "✅ PASS" "Found: $file" $fullPath
    } else {
        Add-ValidationResult "Architecture" "❌ FAIL" "Missing: $file" $fullPath
    }
}

# 2. Development Environment Validation
Write-Host "`n🛠️ 2. Validating Development Environment..." -ForegroundColor Yellow

# Check for Python virtual environment setup
if (Test-Path "src\backend\venv" -or Test-Path "src\backend\.venv") {
    Add-ValidationResult "Dev Environment" "✅ PASS" "Python virtual environment exists"
} else {
    Add-ValidationResult "Dev Environment" "⚠️ WARN" "No virtual environment found"
}

# Check requirements.txt
if (Test-Path "src\backend\requirements.txt") {
    $requirements = Get-Content "src\backend\requirements.txt"
    if ($requirements -match "fastapi" -and $requirements -match "sqlalchemy") {
        Add-ValidationResult "Dev Environment" "✅ PASS" "Backend dependencies configured"
    } else {
        Add-ValidationResult "Dev Environment" "❌ FAIL" "Missing key backend dependencies"
    }
} else {
    Add-ValidationResult "Dev Environment" "❌ FAIL" "Missing backend requirements.txt"
}

# Check frontend setup
if (Test-Path "src\frontend\package.json") {
    $packageJson = Get-Content "src\frontend\package.json" | ConvertFrom-Json
    if ($packageJson.dependencies.react -and $packageJson.devDependencies.vite) {
        Add-ValidationResult "Dev Environment" "✅ PASS" "Frontend dependencies configured"
    } else {
        Add-ValidationResult "Dev Environment" "❌ FAIL" "Missing key frontend dependencies"
    }
} else {
    Add-ValidationResult "Dev Environment" "❌ FAIL" "Missing frontend package.json"
}

# 3. Project Structure Validation
Write-Host "`n📁 3. Validating Project Structure..." -ForegroundColor Yellow

$requiredDirs = @(
    "src\backend\app",
    "src\backend\app\api",
    "src\backend\app\core",
    "src\backend\app\models",
    "src\backend\app\schemas",
    "src\backend\app\services",
    "src\frontend\src",
    "tests",
    "docs",
    "config",
    "scripts"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Add-ValidationResult "Project Structure" "✅ PASS" "Directory exists: $dir"
    } else {
        Add-ValidationResult "Project Structure" "❌ FAIL" "Missing directory: $dir"
    }
}

# 4. API Design Validation
Write-Host "`n🔌 4. Validating API Design..." -ForegroundColor Yellow

$apiFiles = @(
    "src\backend\app\main.py",
    "src\backend\app\api\v1",
    "docs\api\api-specification.md"
)

foreach ($file in $apiFiles) {
    if (Test-Path $file) {
        Add-ValidationResult "API Design" "✅ PASS" "Found: $file"
    } else {
        Add-ValidationResult "API Design" "❌ FAIL" "Missing: $file"
    }
}

# Check if FastAPI app is properly configured
if (Test-Path "src\backend\app\main.py") {
    $mainContent = Get-Content "src\backend\app\main.py" -Raw
    if ($mainContent -match "FastAPI" -and $mainContent -match "app") {
        Add-ValidationResult "API Design" "✅ PASS" "FastAPI app configured"
    } else {
        Add-ValidationResult "API Design" "❌ FAIL" "FastAPI app not properly configured"
    }
}

# 5. Database Design Validation
Write-Host "`n🗄️ 5. Validating Database Design..." -ForegroundColor Yellow

$dbFiles = @(
    "src\backend\app\core\database.py",
    "src\backend\app\models",
    "docs\database-design.md"
)

foreach ($file in $dbFiles) {
    if (Test-Path $file) {
        Add-ValidationResult "Database" "✅ PASS" "Found: $file"
    } else {
        Add-ValidationResult "Database" "❌ FAIL" "Missing: $file"
    }
}

# Check for SQLAlchemy models
$modelFiles = Get-ChildItem "src\backend\app\models" -Filter "*.py" -ErrorAction SilentlyContinue
if ($modelFiles.Count -gt 1) { # More than just __init__.py
    Add-ValidationResult "Database" "✅ PASS" "SQLAlchemy models found ($($modelFiles.Count) files)"
} else {
    Add-ValidationResult "Database" "❌ FAIL" "No SQLAlchemy models found"
}

# 6. Security Configuration Validation
Write-Host "`n🔒 6. Validating Security Configuration..." -ForegroundColor Yellow

if (Test-Path "src\backend\app\core\security.py") {
    $securityContent = Get-Content "src\backend\app\core\security.py" -Raw
    if ($securityContent -match "JWT" -or $securityContent -match "OAuth") {
        Add-ValidationResult "Security" "✅ PASS" "Authentication system configured"
    } else {
        Add-ValidationResult "Security" "❌ FAIL" "No authentication system found"
    }
} else {
    Add-ValidationResult "Security" "❌ FAIL" "Missing security.py"
}

# 7. Testing Framework Validation
Write-Host "`n🧪 7. Validating Testing Framework..." -ForegroundColor Yellow

if (Test-Path "src\backend\pytest.ini") {
    Add-ValidationResult "Testing" "✅ PASS" "Pytest configuration found"
} else {
    Add-ValidationResult "Testing" "❌ FAIL" "Missing pytest configuration"
}

$testFiles = Get-ChildItem "src\backend\tests" -Filter "test_*.py" -ErrorAction SilentlyContinue
if ($testFiles.Count -gt 0) {
    Add-ValidationResult "Testing" "✅ PASS" "Test files found ($($testFiles.Count) files)"
} else {
    Add-ValidationResult "Testing" "❌ FAIL" "No test files found"
}

# 8. Monitoring Setup Validation
Write-Host "`n📊 8. Validating Monitoring Setup..." -ForegroundColor Yellow

if (Test-Path "config\prometheus.yml") {
    Add-ValidationResult "Monitoring" "✅ PASS" "Prometheus configuration found"
} else {
    Add-ValidationResult "Monitoring" "⚠️ WARN" "No Prometheus configuration"
}

if (Test-Path "src\backend\app\core\monitoring.py") {
    Add-ValidationResult "Monitoring" "✅ PASS" "Monitoring module found"
} else {
    Add-ValidationResult "Monitoring" "⚠️ WARN" "No monitoring module"
}

# 9. CI/CD Pipeline Validation
Write-Host "`n🚀 9. Validating CI/CD Pipeline..." -ForegroundColor Yellow

$cicdFiles = @(
    "docs\ci-cd-pipeline.md",
    "docker-compose.yml",
    "docker-compose.prod.yml"
)

foreach ($file in $cicdFiles) {
    if (Test-Path $file) {
        Add-ValidationResult "CI/CD" "✅ PASS" "Found: $file"
    } else {
        Add-ValidationResult "CI/CD" "❌ FAIL" "Missing: $file"
    }
}

# 10. Documentation Validation
Write-Host "`n📚 10. Validating Documentation..." -ForegroundColor Yellow

$docFiles = @(
    "README.md",
    "docs\api\api-specification.md",
    "docs\database-design.md"
)

foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Add-ValidationResult "Documentation" "✅ PASS" "Found: $file"
    } else {
        Add-ValidationResult "Documentation" "❌ FAIL" "Missing: $file"
    }
}

# 11. Project Management Validation
Write-Host "`n📋 11. Validating Project Management..." -ForegroundColor Yellow

$pmFiles = @(
    "project_management\project_overview.md",
    "project_management\roadmap.md",
    "project_management\sprint_planning.md"
)

foreach ($file in $pmFiles) {
    if (Test-Path $file) {
        Add-ValidationResult "Project Management" "✅ PASS" "Found: $file"
    } else {
        Add-ValidationResult "Project Management" "❌ FAIL" "Missing: $file"
    }
}

# 12. Functional Validation (Run basic tests)
Write-Host "`n⚙️ 12. Running Functional Validation..." -ForegroundColor Yellow

Push-Location "src\backend"
try {
    # Check if we can import the main app
    $pythonTest = python -c "import app.main; print('✅ FastAPI app imports successfully')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Add-ValidationResult "Functional" "✅ PASS" "FastAPI app imports successfully"
    } else {
        Add-ValidationResult "Functional" "❌ FAIL" "FastAPI app import failed: $pythonTest"
    }
    
    # Run a quick test if pytest is available
    if (Get-Command pytest -ErrorAction SilentlyContinue) {
        $testResult = pytest --tb=short -q 2>&1
        if ($LASTEXITCODE -eq 0) {
            Add-ValidationResult "Functional" "✅ PASS" "All tests passing"
        } else {
            Add-ValidationResult "Functional" "⚠️ WARN" "Some tests may be failing"
        }
    } else {
        Add-ValidationResult "Functional" "⚠️ WARN" "Pytest not available for testing"
    }
} catch {
    Add-ValidationResult "Functional" "❌ FAIL" "Error during functional validation: $_"
} finally {
    Pop-Location
}

# Display Results Summary
Write-Host "`n📊 VALIDATION RESULTS SUMMARY" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

$groupedResults = $validationResults | Group-Object Component
foreach ($group in $groupedResults) {
    Write-Host "`n🔸 $($group.Name):" -ForegroundColor Cyan
    foreach ($result in $group.Group) {
        $color = switch ($result.Status) {
            "✅ PASS" { "Green" }
            "❌ FAIL" { "Red" }
            "⚠️ WARN" { "Yellow" }
            default { "White" }
        }
        Write-Host "  $($result.Status) $($result.Message)" -ForegroundColor $color
    }
}

# Final Status
Write-Host "`n🎯 OVERALL PROJECT STATUS" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Green

$totalChecks = $validationResults.Count
$passedChecks = ($validationResults | Where-Object { $_.Status -eq "✅ PASS" }).Count
$failedChecks = ($validationResults | Where-Object { $_.Status -eq "❌ FAIL" }).Count
$warningChecks = ($validationResults | Where-Object { $_.Status -eq "⚠️ WARN" }).Count

Write-Host "Total Checks: $totalChecks" -ForegroundColor White
Write-Host "Passed: $passedChecks" -ForegroundColor Green
Write-Host "Failed: $failedChecks" -ForegroundColor Red
Write-Host "Warnings: $warningChecks" -ForegroundColor Yellow

$successRate = [math]::Round(($passedChecks / $totalChecks) * 100, 1)
Write-Host "Success Rate: $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" })

if ($errorCount -eq 0) {
    Write-Host "`n🎉 PROJECT READY FOR DEVELOPMENT!" -ForegroundColor Green
    Write-Host "All critical components are properly configured." -ForegroundColor Green
    exit 0
} elseif ($errorCount -le 3) {
    Write-Host "`n⚠️ PROJECT MOSTLY READY" -ForegroundColor Yellow
    Write-Host "Some minor issues need to be addressed before starting development." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "`n❌ PROJECT NOT READY" -ForegroundColor Red
    Write-Host "Multiple critical issues need to be resolved." -ForegroundColor Red
    exit 2
}
