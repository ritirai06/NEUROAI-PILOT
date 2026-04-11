@echo off
chcp 65001 >nul
title NeuroAI v3.0 — All Services
color 0B
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║   NEUROAI v3.0  —  Jarvis AI Agent       ║
echo  ║   Starting all services...               ║
echo  ╚══════════════════════════════════════════╝
echo.

:: ── Kill anything on ports 8000 / 7233 / 3000 ──────────────────────────────
echo [CLEANUP] Freeing ports 8000, 7233, 3000...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 " ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":7233 " ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":3000 " ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
echo [CLEANUP] Done.
echo.

:: ── 1. Temporal Server ──────────────────────────────────────────────────────
echo [1/4] Starting Temporal Server...
if exist temporal.exe (
    start "Temporal" cmd /c "temporal.exe server start-dev > logs\temporal.log 2>&1"
    echo       Temporal  ^>  http://localhost:8233
) else (
    echo       [SKIP] temporal.exe not found — running in DIRECT mode
)
timeout /t 3 /nobreak >nul

:: ── 2. Temporal Worker ──────────────────────────────────────────────────────
echo [2/4] Starting Temporal Worker...
if exist temporal.exe (
    start "Worker" cmd /c "venv\Scripts\activate && python -m temporal.worker > logs\worker.log 2>&1"
    echo       Worker log  ^>  logs\worker.log
) else (
    echo       [SKIP] No Temporal — worker not needed
)
timeout /t 2 /nobreak >nul

:: ── 3. FastAPI Backend ──────────────────────────────────────────────────────
echo [3/4] Starting FastAPI Backend...
if not exist logs mkdir logs
start "Backend" cmd /c "venv\Scripts\activate && python main.py > logs\backend.log 2>&1"
echo       Backend log  ^>  logs\backend.log
timeout /t 4 /nobreak >nul

:: ── 4. React Frontend ───────────────────────────────────────────────────────
echo [4/4] Starting React Frontend...
start "Frontend" cmd /c "cd ui && npm run dev > ..\logs\frontend.log 2>&1"
echo       Frontend log  ^>  logs\frontend.log
timeout /t 4 /nobreak >nul

:: ── Health check ────────────────────────────────────────────────────────────
echo.
echo [CHECK] Waiting for backend to be ready...
:WAIT_BACKEND
timeout /t 2 /nobreak >nul
curl -s http://localhost:8000/status >nul 2>&1
if errorlevel 1 (
    set /a TRIES+=1
    if !TRIES! lss 10 goto WAIT_BACKEND
    echo       [WARN] Backend not responding — check logs\backend.log
) else (
    echo       [OK] Backend is UP
)

:: ── Done ────────────────────────────────────────────────────────────────────
echo.
echo  ╔══════════════════════════════════════════╗
echo  ║   ALL SERVICES RUNNING                   ║
echo  ║                                          ║
echo  ║   UI       →  http://localhost:3000      ║
echo  ║   API      →  http://localhost:8000      ║
echo  ║   API Docs →  http://localhost:8000/docs ║
echo  ║   Temporal →  http://localhost:8233      ║
echo  ║                                          ║
echo  ║   Logs in: .\logs\                       ║
echo  ╚══════════════════════════════════════════╝
echo.
echo  Press any key to STOP all services...
pause >nul

:: ── Shutdown ────────────────────────────────────────────────────────────────
echo.
echo [STOP] Shutting down all services...
taskkill /FI "WINDOWTITLE eq Temporal" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Worker"   /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Backend"  /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend" /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 " ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":3000 " ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
echo [STOP] Done. Goodbye.
timeout /t 2 /nobreak >nul
