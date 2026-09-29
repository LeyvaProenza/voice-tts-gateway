@echo off
title Pruebas Automatizadas Voice-TTS
cd /d "%~dp0"
echo ========================================================
echo        Ejecutando Suite de Pruebas Voice-TTS
echo ========================================================
echo.
.venv\Scripts\python.exe -m pytest tests/ -v
echo.
pause
