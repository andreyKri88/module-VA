@echo off
echo ========================================
echo SentinelVA Controller Diagnostics
echo ========================================
echo.

echo [1/6] System Information...
echo Python version:
python --version 2>nul || echo Python not found in PATH
echo.

echo [2/6] Python Path Check...
where python
echo.

echo [3/6] Dependencies Check...
echo Checking Flask:
pip show flask 2>nul || echo Flask not installed
echo.
echo Checking tendo:
pip show tendo 2>nul || echo tendo not installed
echo.
echo Checking kafka-python:
pip show kafka-python 2>nul || echo kafka-python not installed
echo.
echo Checking websockets:
pip show websockets 2>nul || echo websockets not installed
echo.
echo Checking requests:
pip show requests 2>nul || echo requests not installed
echo.

echo [4/6] Configuration Files Check...
if exist "settings.ini" (
    echo settings.ini: FOUND
) else (
    echo settings.ini: NOT FOUND
)
if exist "devices.json" (
    echo devices.json: FOUND
) else (
    echo devices.json: NOT FOUND
)
if exist "logs" (
    echo logs directory: FOUND
) else (
    echo logs directory: NOT FOUND (will be created automatically)
)
echo.

echo [5/6] Port Availability Check...
netstat -an | findstr ":600" >nul 2>&1
if errorlevel 1 (
    echo Port 600: AVAILABLE
) else (
    echo Port 600: IN USE
    echo Another application may be using this port
)
echo.

echo [6/6] Import Test...
echo Testing Python imports...
python -c "import sys; print('Python path:', sys.path[0])" 2>nul
python -c "from app_va import app_run; print('Import test: SUCCESS')" 2>nul || echo Import test: FAILED
echo.

echo ========================================
echo Diagnostics Complete
echo ========================================
echo.
echo If any tests failed:
echo 1. Install missing dependencies: pip install -r requirements.txt
echo 2. Check Python installation and PATH
echo 3. Ensure configuration files exist
echo 4. Check if port 600 is available
echo.
pause
