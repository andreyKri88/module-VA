@echo off
echo ========================================
echo SentinelVA Controller Launcher
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add to PATH
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version

echo.
echo [2/4] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Dependencies are already installed
)

echo.
echo [3/4] Checking configuration files...
if not exist "settings.ini" (
    echo ERROR: settings.ini not found
    echo Please ensure configuration file exists
    pause
    exit /b 1
)
if not exist "devices.json" (
    echo ERROR: devices.json not found
    echo Please ensure device configuration file exists
    pause
    exit /b 1
)
echo Configuration files found

echo.
echo [4/4] Starting SentinelVA Controller...
echo Server will be available at: http://localhost:600
echo Press Ctrl+C to stop the server
echo.

python run_server.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo Controller stopped successfully
pause
