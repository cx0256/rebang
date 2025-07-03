@echo off
chcp 65001 >nul
echo ========================================
echo           Rebang Project Startup
echo ========================================
echo.

echo [1/4] Checking Docker Desktop...

:: Check if Docker Desktop is running
tasklist /FI "IMAGENAME eq Docker Desktop.exe" | find "Docker Desktop.exe" >nul
if %errorlevel% neq 0 (
    echo [INFO] Docker Desktop is not running, attempting to start it...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo [INFO] Waiting for Docker Desktop to initialize...
    timeout /t 30 /nobreak >nul
) else (
    echo [INFO] Docker Desktop is already running.
)

echo [INFO] Docker Desktop is running, checking engine status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker engine is not ready
    echo Please wait for Docker Desktop to fully load and try again
    pause
    exit /b 1
)
echo [OK] Docker check passed

echo.
echo [2/4] Starting database services...
if not exist docker-compose.yml (
    echo [ERROR] docker-compose.yml not found!
    pause
    exit /b 1
)

:: Try with docker-compose first
docker-compose up -d postgres redis
if %errorlevel% neq 0 (
    echo [INFO] 'docker-compose' command failed, trying with 'docker compose'...
    docker compose up -d postgres redis
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to start database services with both 'docker-compose' and 'docker compose'.
        pause
        exit /b 1
    )
)
echo [OK] Database services started successfully

echo.
echo [3/4] Waiting for database initialization...
timeout /t 5 /nobreak >nul
echo [OK] Database initialization completed

echo.
echo [4/4] Starting application services...
echo Starting backend service...
start "Backend Service" cmd /k "cd /d backend && python -m venv .venv && .venv\Scripts\activate && set http_proxy= && set https_proxy= && set HTTP_PROXY= && set HTTPS_PROXY= && pip config unset global.proxy >nul 2>nul && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend service to start...
timeout /t 10 /nobreak >nul

echo Starting frontend service...
start "Frontend Service" cmd /k "cd /d frontend && npm install && npm run dev"

echo.
echo ========================================
echo           Startup Complete!
echo ========================================
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to exit...
pause >nul