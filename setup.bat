@echo off
echo ============================================
echo   NeuroAI Agent - Setup Script (Windows)
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install from https://python.org
    pause & exit /b 1
)
echo [OK] Python found

:: Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Install from https://nodejs.org
    pause & exit /b 1
)
echo [OK] Node.js found

:: Check Ollama
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [WARN] Ollama not found. Download from https://ollama.ai
    echo        After installing, run: ollama pull llama3
) else (
    echo [OK] Ollama found
)

echo.
echo [1/4] Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/4] Installing Python dependencies...
pip install -r requirements.txt --quiet

echo [3/4] Installing Playwright browsers...
playwright install chromium

echo [4/4] Installing frontend dependencies...
cd ui
npm install --silent
cd ..

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo To start NeuroAI:
echo   1. Run Ollama:    ollama serve
echo   2. Pull model:    ollama pull llama3
echo   3. Start backend: python main.py
echo   4. Start UI:      cd ui ^&^& npm run dev
echo   5. Open browser:  http://localhost:3000
echo.
pause
