@echo off
title Iniciar Servidor XTTS API
cd /d "%~dp0"

echo ========================================================
echo        Iniciador de XTTS API Server (Aceleracion GPU)
echo ========================================================
echo.

echo [1/3] Creando directorios locales necesarios...
if not exist speakers mkdir speakers
if not exist models mkdir models
if not exist output mkdir output

echo [2/3] Verificando entorno virtual (.venv)...
if not exist .venv (
    echo [ERROR] No se encontro el entorno virtual .venv.
    echo Por favor, ejecuta la instalacion de dependencias primero.
    exit /b 1
)

echo [3/3] Iniciando XTTS API Server en segundo plano...
echo Puerto: 8020
echo Carpeta de Voces: speakers/
echo Carpeta del Modelo: models/
echo Modo: GPU (lowvram activado)
echo.

:: Start in a minimized window and redirect outputs to tts_server.log
start "XTTS API Server Background" /min cmd /c ".venv\Scripts\python.exe -m xtts_api_server --port 8020 --host 127.0.0.1 --speaker-folder speakers --model-folder models --lowvram > tts_server.log 2>&1"

echo [OK] El servidor se ha iniciado en segundo plano.
echo - Los registros (logs) se estan escribiendo en: tts_server.log
echo - Puedes comprobar el estado o ver la API interactiva en:
echo   http://localhost:8020/docs
echo.
echo Para apagar el servidor, ejecuta stop_tts.bat
echo.
