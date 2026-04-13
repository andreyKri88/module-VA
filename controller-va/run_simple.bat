@echo off
echo ========================================
echo SentinelVA Controller - Simple Mode
echo ========================================
echo.

echo This is a minimal Flask app without:
echo - Kafka connections
echo - WebSocket connections  
echo - Complex initialization
echo - Database operations
echo.

echo [1/3] Testing basic functionality...
echo.

python run_simple.py

echo.
echo [2/3] If simple mode works:
echo The issue is in complex initialization
echo Check:
echo - Kafka connectivity (10.3.1.230:9093)
echo - WebSocket connectivity (wss://127.0.0.1:5050)
echo - API connectivity (10.3.1.230:3055)
echo - File permissions
echo.

echo [3/3] If simple mode fails:
echo The issue is basic:
echo - Python installation
echo - Port 600 availability
echo - System permissions
echo.

echo ========================================
echo Test Results:
echo ========================================
echo.
echo Simple server should be available at:
echo - http://localhost:600/
echo - http://localhost:600/ping
echo - http://localhost:600/status
echo.
pause
