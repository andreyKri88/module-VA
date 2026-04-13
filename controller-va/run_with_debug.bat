@echo off
echo ========================================
echo SentinelVA Controller Debug Launcher
echo ========================================
echo.

echo [1/7] Running Debug Diagnostics...
echo This will help identify why the app closes immediately
echo.

python debug_run.py

echo.
echo [2/7] Debug Results:
echo If debug passed above, try running normally:
echo.

python run_server.py

echo.
echo [3/7] If still having issues:
echo 1. Check if Python 3.8+ is installed
echo 2. Run: pip install -r requirements.txt
echo 3. Check if port 600 is available
echo 4. Make sure settings.ini and devices.json exist
echo 5. Check Windows Defender/antivirus isn't blocking
echo.
echo [4/7] Contact support with debug output
echo.

pause
