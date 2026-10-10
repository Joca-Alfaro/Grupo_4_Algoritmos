@echo off
rem ============================================================
rem  Crea SistemaAcademico.exe a partir del codigo fuente.
rem
rem  Requisitos: tener Python instalado y conexion a internet
rem  (solo para descargar PyInstaller, la herramienta que
rem  empaqueta el programa; el programa en si no usa nada externo).
rem
rem  Uso: doble clic en este archivo. Al terminar aparece
rem  SistemaAcademico.exe en esta misma carpeta.
rem ============================================================
chcp 65001 >nul
cd /d "%~dp0"

rem --- Elegir el comando de Python disponible ---
set PY=python
where py >nul 2>nul && set PY=py -3

%PY% --version >nul 2>nul
if errorlevel 1 (
    echo No se encontro Python en este equipo.
    echo Instalelo desde https://www.python.org/downloads/
    echo IMPORTANTE: marque la casilla "Add Python to PATH" al instalar.
    echo.
    pause
    exit /b 1
)

echo [1/3] Instalando PyInstaller...
%PY% -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo.
    echo No se pudo instalar PyInstaller. Revise su conexion a internet.
    pause
    exit /b 1
)

echo.
echo [2/3] Creando el ejecutable (puede tardar un minuto)...
%PY% -m PyInstaller --onefile --console --clean --noconfirm --name SistemaAcademico main.py
if errorlevel 1 (
    echo.
    echo Ocurrio un error al crear el ejecutable.
    pause
    exit /b 1
)

echo.
echo [3/3] Finalizando y limpiando archivos temporales...
copy /Y "dist\SistemaAcademico.exe" "SistemaAcademico.exe" >nul
rmdir /S /Q build
rmdir /S /Q dist
del /Q SistemaAcademico.spec

echo.
echo ============================================================
echo  Listo: SistemaAcademico.exe fue creado en esta carpeta.
echo  Los datos se guardan en la carpeta "datos" junto al .exe.
echo  Si lo mueve a otro lugar, mueva tambien la carpeta "datos".
echo ============================================================
echo.
pause
