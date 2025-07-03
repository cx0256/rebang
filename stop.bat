@echo off
chcp 65001 >nul
echo ========================================
echo           Rebang Project Stop
echo ========================================
echo.

echo [1/3] Stopping database services...
docker compose down
if %errorlevel% equ 0 (
    echo [OK] Database services stopped
) else (
    echo [WARNING] Warning occurred while stopping database
)

echo.
echo [2/3] Stopping frontend service...
taskkill /f /im node.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend service stopped
) else (
    echo [INFO] No running Node.js processes found
)

echo.
echo [3/3] Stopping backend service...
taskkill /f /im python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend service stopped
) else (
    echo [INFO] No running Python processes found
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