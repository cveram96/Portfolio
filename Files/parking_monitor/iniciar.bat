@echo off
chcp 65001 >nul
title Smart Parking Monitor - Computer Vision
color 0A
cd /d "%~dp0"

echo ======================================================================
echo   STARTING SMART PARKING MONITOR SYSTEM
echo ======================================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment .venv not found in this folder.
    echo Please ensure dependencies are installed.
    pause
    exit /b 1
)

echo [*] Checking port 8000 and freeing previous sessions...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1

echo [1/2] Starting Computer Vision server with GPU acceleration...
echo [2/2] Opening http://localhost:8000 in your browser...
echo.
echo Press CTRL+C in this window when you wish to stop the application.
echo.

start "" powershell -NoProfile -Command "Start-Sleep -Seconds 2; Start-Process 'http://localhost:8000'"

".venv\Scripts\python.exe" run.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while running the application.
    pause
)
