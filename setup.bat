@echo off
chcp 65001 >nul 2>&1
setlocal

cd /d "%~dp0"

echo ============================================
echo   Aether - Initial Setup (Windows)
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH!
    echo Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

echo [INFO] Creating fresh virtual environment...
if exist "venv" rmdir /s /q venv
python -m venv venv

if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

echo [OK] Virtual environment created.
echo.

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Upgrading pip and tools...
python -m pip install --upgrade pip setuptools wheel

echo [INFO] Installing dependencies (using prebuilt wheels only)...
pip install --only-binary :all: -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies!
    echo.
    echo Possible reasons:
    echo   - No space left on device (free up disk space on C:)
    echo   - Corrupted pip cache - try deleting %LOCALAPPDATA%\pip\Cache
    echo   - Antivirus blocking build tools
    echo.
    echo Try running this again after freeing space, or manually:
    echo   pip install --only-binary :all: -r requirements.txt
    pause
    exit /b 1
)

echo.
echo [OK] Setup completed successfully!
echo.
echo You can now run the dashboard with:
echo     run.bat
echo.
echo Open http://localhost:8090 after starting (для локальної розробки). На проді/Docker - без порту (порт 80).
pause
