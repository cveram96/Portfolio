@echo off
setlocal
echo ========================================================
echo   Compilando Hojas de Vida (Espanol e Ingles) a PDF...
echo ========================================================
echo.

set "TECTONIC=%LOCALAPPDATA%\Programs\tectonic\tectonic.exe"

if not exist "%TECTONIC%" (
    echo Error: No se encontro el compilador Tectonic en:
    echo %TECTONIC%
    pause
    exit /b 1
)

echo [1/2] Compilando CV en Espanol (CV_Christian_Vera_ES.tex)...
"%TECTONIC%" "%~dp0CV_Christian_Vera_ES.tex" --outdir "%~dp0"
if %ERRORLEVEL% equ 0 (
    echo      ^> Exito: CV_Christian_Vera_ES.pdf generado.
) else (
    echo      ^> Error al compilar version en espanol.
)

echo.
echo [2/2] Compilando Resume en Ingles (CV_Christian_Vera_EN.tex)...
"%TECTONIC%" "%~dp0CV_Christian_Vera_EN.tex" --outdir "%~dp0"
if %ERRORLEVEL% equ 0 (
    echo      ^> Exito: CV_Christian_Vera_EN.pdf generado.
) else (
    echo      ^> Error al compilar version en ingles.
)

echo.
echo ========================================================
echo   Compilacion finalizada.
echo ========================================================
pause
