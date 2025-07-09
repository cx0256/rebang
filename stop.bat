@echo off
chcp 65001 >nul
echo ========================================
echo           Rebang Project Stop
echo ========================================
echo.

echo [1/4] Stopping backend service...
echo Stopping Docker backend service...
docker compose stop backend >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker backend service stopped
) else (
    echo [INFO] No Docker backend service running
)

echo Stopping smart-built Docker backend...
docker stop rebang-backend-smart >nul 2>&1
docker rm rebang-backend-smart >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Smart-built Docker backend stopped
) else (
    echo [INFO] No smart-built Docker backend running
)

echo Stopping fallback Docker backend...
docker stop rebang-backend-fallback >nul 2>&1
docker rm rebang-backend-fallback >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Fallback Docker backend stopped
) else (
    echo [INFO] No fallback Docker backend running
)

echo Stopping local backend service...
taskkill /f /im python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Local backend service stopped
) else (
    echo [INFO] No local Python processes found
)

echo.
echo [2/4] Stopping database services...
docker compose stop postgres redis >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Database services stopped
) else (
    echo [WARNING] Warning occurred while stopping database
)

echo.
echo [3/4] Stopping frontend service...
taskkill /f /im node.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend service stopped
) else (
    echo [INFO] No running Node.js processes found
)

echo.
echo [4/4] Cleaning up Docker containers...
docker compose down >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] All Docker containers cleaned up
) else (
    echo [INFO] No Docker containers to clean up
)

echo.
echo ========================================
echo           Stop Complete!
echo ========================================
echo.
echo All services stopped. To restart, run start.bat
echo.
echo Press any key to exit...
pause >nul