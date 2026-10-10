@echo off
rem ============================================================
rem  Inicia el Sistema de Gestion Academica (doble clic).
rem  Busca Python en el equipo y ejecuta main.py.
rem ============================================================
chcp 65001 >nul
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 main.py
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        python main.py
    ) else (
        echo No se encontro Python en este equipo.
        echo Instalelo desde https://www.python.org/downloads/
        echo IMPORTANTE: marque la casilla "Add Python to PATH" al instalar.
    )
)

echo.
pause
