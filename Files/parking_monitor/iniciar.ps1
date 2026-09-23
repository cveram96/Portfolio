$Host.UI.RawUI.WindowTitle = "🅿️ Smart Parking Monitor"
Set-Location $PSScriptRoot

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  🅿️ INICIANDO SISTEMA INTELIGENTE DE MONITOREO DE PARQUEADERO" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "[ERROR] No se encontro el entorno virtual .venv en esta carpeta." -ForegroundColor Red
    Write-Host "Ejecuta: py -3.13 -m venv .venv && .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir..."
    exit 1
}

# Free port 8000 if occupied
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}

# Open browser in 2 seconds
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8000"
} | Out-Null

Write-Host "[*] Iniciando servidor y cargando modelos de vision artificial..." -ForegroundColor Yellow
Write-Host "[*] Interfaz web disponible en: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

& $pythonExe run.py
