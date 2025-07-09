@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo ========================================
echo      Smart Docker Build Script
echo ========================================
echo.

echo [0/2] Cleaning Docker cache and old images...
docker rmi rebang-backend >nul 2>&1
docker builder prune -f >nul 2>&1
echo [OK] Cache cleaned
echo.

echo [1/2] Starting build process with Huawei Cloud mirror...

docker build -f backend/Dockerfile.huawei -t rebang-backend-huawei backend/

if !errorlevel! equ 0 (
    set "SUCCESS=1"
) else (
    set "SUCCESS=0"
)

echo.
echo ========================================
if !SUCCESS! equ 1 (
    echo           Build Successful!
    echo Successfully built with Dockerfile.huawei
) else (
    echo           Build Failed!
    echo All mirrors failed, please check network connection
    echo or configure Docker mirror accelerator manually
)
echo ========================================
echo.

if !SUCCESS! equ 0 (
    echo Suggested solutions:
    echo 1. Configure Docker Desktop mirror accelerator
    echo 2. Check network connection
    echo 3. Use local Python environment
    echo.
    pause
    exit /b 1
)

echo Image build completed, you can use start.bat to start services
pause