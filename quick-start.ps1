# Rebang Project Quick Start Script
# Simplified version

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "         Rebang Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check environment
Write-Host "Checking environment..." -ForegroundColor Yellow

# Check Docker
try {
    $null = docker --version
    Write-Host "[OK] Docker: Installed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker: Not installed or not running" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js
try {
    $null = node --version
    Write-Host "[OK] Node.js: Installed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js: Not installed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python
try {
    $null = python --version
    Write-Host "[OK] Python: Installed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python: Not installed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Starting database services..." -ForegroundColor Yellow
docker compose up -d postgres redis

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Database services started successfully" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to start database services" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Waiting for database initialization..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

Write-Host ""
Write-Host "Please follow these steps to start the application:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start Backend Service (open new PowerShell window):" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   python -m venv .venv" -ForegroundColor Gray
Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start Frontend Service (open another PowerShell window):" -ForegroundColor Yellow
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm install" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Access Application:" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Database started. Please start app services manually." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Read-Host "Press Enter to exit"