@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

REM =============================================
REM   Aether - Homelab Dashboard (Windows)
REM   Simple launcher with automatic venv
REM =============================================

cd /d "%~dp0"

echo.
echo ============================================
echo   Aether - Sadova Network Dashboard
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH!
    echo Please install Python 3.10 or newer and add it to system PATH.
    pause
    exit /b 1
)

REM Create venv if it does not exist
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
    echo.
)

REM Activate the virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Ensure dependencies are installed (in case setup was skipped)
echo [INFO] Ensuring dependencies are installed...
pip install --only-binary :all: -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Could not install or verify dependencies.
    echo Please run setup.bat first.
    pause
    exit /b 1
)

echo.
echo [INFO] Starting Aether server...
echo Open in your browser: http://localhost:8090 (локальна розробка; на сервері - просто IP без порту)
echo Press Ctrl+C to stop the server.
echo.

python run.py

echo.
echo [INFO] Aether has stopped.
pause
