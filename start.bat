@echo off
title NeuroAI v3.0 Launcher
color 0B
cd /d "%~dp0"

echo.
echo  NEUROAI v3.0 - Jarvis AI Agent
echo  ================================
echo.

echo [1/4] Starting Temporal Server...
start "Temporal Server" cmd /k "temporal.exe server start-dev"
timeout /t 4 /nobreak >nul

echo [2/4] Starting Temporal Worker...
start "NeuroAI Worker" cmd /k "venv\Scripts\activate && python -m temporal.worker"
timeout /t 3 /nobreak >nul

echo [3/4] Starting FastAPI Backend...
start "NeuroAI Backend" cmd /k "venv\Scripts\activate && python main.py"
timeout /t 3 /nobreak >nul

echo [4/4] Starting React Frontend...
start "NeuroAI Frontend" cmd /k "cd ui && npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo  All services started!
echo  UI:       http://localhost:3000
echo  API:      http://localhost:8000
echo  Temporal: http://localhost:8233
echo.
pause
