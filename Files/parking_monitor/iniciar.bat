@echo off
chcp 65001 >nul
title Smart Parking Monitor - Vision Artificial
color 0A
cd /d "%~dp0"

echo ======================================================================
echo   🅿️  INICIANDO SISTEMA INTELIGENTE DE MONITOREO DE PARQUEADERO
echo ======================================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No se encontro el entorno virtual .venv en esta carpeta.
    echo Asegurate de haber instalado las dependencias.
    pause
    exit /b 1
)

echo [*] Verificando puerto 8000 y liberando sesiones previas...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1

echo [1/2] Iniciando servidor de Vision por Computador y Aceleracion GPU...
echo [2/2] Abriendo automaticamente http://localhost:8000 en tu navegador...
echo.
echo Presiona CTRL+C en esta ventana cuando desees cerrar la aplicacion.
echo.

start "" powershell -NoProfile -Command "Start-Sleep -Seconds 2; Start-Process 'http://localhost:8000'"

".venv\Scripts\python.exe" run.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Hubo un error al ejecutar la aplicacion.
    pause
)
