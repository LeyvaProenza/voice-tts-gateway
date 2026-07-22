@echo off
title Detener Servidor XTTS API
cd /d "%~dp0"

echo ========================================================
echo        Deteniendo Servidor XTTS API (Puerto 8020)
echo ========================================================
echo.

set "PID_FOUND="
:: Find PID of the process listening on port 8020
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8020 ^| findstr LISTENING') do (
    set "PID_FOUND=%%a"
)

if defined PID_FOUND (
    echo [INFO] Servidor detectado ejecutandose con PID: %PID_FOUND%
    echo Finalizando proceso...
    taskkill /F /PID %PID_FOUND%
    if %errorlevel% equ 0 (
        echo [OK] Servidor XTTS API detenido con exito.
    ) else (
        echo [ERROR] No se pudo detener el proceso %PID_FOUND%.
    )
) else (
    echo [INFO] No se encontro ningun servidor activo escuchando en el puerto 8020.
)
echo.
