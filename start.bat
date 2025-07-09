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
echo Starting backend service in Docker...
docker-compose up -d backend
if %errorlevel% neq 0 (
    echo [INFO] 'docker-compose' command failed, trying with 'docker compose'...
    docker compose up -d backend
    if %errorlevel% neq 0 (
        echo [WARNING] Docker backend startup failed, trying smart build with multiple mirror sources...
        echo Running smart build script...
        call build-backend.bat
        if %errorlevel% equ 0 (
            echo Smart build successful, starting backend with built image...
            docker run -d --name rebang-backend-smart -p 8000:8000 --network rebang_default rebang-backend
            if %errorlevel% equ 0 (
                echo [OK] Backend service started with smart-built Docker image
            ) else (
                echo [WARNING] Smart-built Docker failed to start, using local Python environment...
                start "Backend Service" cmd /k "cd /d backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
                echo [OK] Backend service started locally
            )
        ) else (
            echo [WARNING] Smart build failed!
            echo [INFO] This might be due to Docker cache issues.
            echo [INFO] You can run 'clean-docker.bat' to clear all cache and try again.
            echo [INFO] Falling back to local Python environment...
            start "Backend Service" cmd /k "cd /d backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
            echo [OK] Backend service started locally
        )
    ) else (
        echo [OK] Backend service started in Docker
    )
) else (
    echo [OK] Backend service started in Docker
)

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