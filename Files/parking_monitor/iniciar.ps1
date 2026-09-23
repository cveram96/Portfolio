$Host.UI.RawUI.WindowTitle = "Smart Parking Monitor"
Set-Location $PSScriptRoot

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  STARTING SMART PARKING MONITOR SYSTEM" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "[ERROR] Virtual environment .venv not found in this folder." -ForegroundColor Red
    Write-Host "Run: py -3.13 -m venv .venv && .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Press Enter to exit..."
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

Write-Host "[*] Starting server and loading computer vision models..." -ForegroundColor Yellow
Write-Host "[*] Web interface available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

& $pythonExe run.py
