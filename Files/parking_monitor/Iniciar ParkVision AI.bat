@echo off
cd /d "%~dp0"
python main_app.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR al iniciar. Asegurate de tener Python instalado.
    pause
)
