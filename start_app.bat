@echo off
title Aplicacion de Control Voice-TTS
cd /d "%~dp0"

echo ========================================================
echo        Aplicacion de Control Voice-TTS - Interfaz
echo ========================================================
echo.

echo [1/2] Verificando entorno virtual (.venv)...
if not exist .venv (
    echo [ERROR] No se encontro el entorno virtual .venv.
    echo Por favor, ejecuta la instalacion de dependencias primero.
    pause
    exit /b
)

echo [2/2] Levantando servidor web en el puerto 8000...
echo (Este terminal muestra la actividad en tiempo real. Dejalo abierto)
echo.

:: Automatically open browser after 2 seconds (when the server is up)
start /min cmd /c "timeout /t 2 > nul && start http://127.0.0.1:8000"

:: Run FastAPI control panel via uvicorn with auto-reload
.venv\Scripts\python.exe -m uvicorn app:app --port 8000 --host 127.0.0.1 --reload

echo.
echo Servidor cerrado.
pause
