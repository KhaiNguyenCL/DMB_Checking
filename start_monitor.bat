@echo off
REM ============================================
REM Device Monitoring Automation Script
REM ============================================
REM This script automates the full workflow:
REM 1. Activate Python virtual environment
REM 2. Auto-login to get fresh cookie
REM 3. Run device monitor with Bitrix notifications
REM ============================================

echo ================================================================================
echo        DEVICE MONITORING SYSTEM - AUTO START
echo ================================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup_venv.bat first to create the environment.
    pause
    exit /b 1
)

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat
echo     - OK

echo.
echo [2/3] Auto-login to get fresh session cookie...
echo     - This will open Chrome briefly to login
python auto_login_selenium.py
if errorlevel 1 (
    echo [ERROR] Login failed!
    echo Please check config_auto.py credentials or login manually.
    pause
    exit /b 1
)
echo     - OK

echo.
echo [3/3] Starting device monitor...
echo     - Monitoring every 5 minutes
echo     - Bitrix notifications enabled
echo     - Press Ctrl+C to stop
echo.
echo ================================================================================
python monitor_devices.py

REM If monitor stops or crashes
echo.
echo ================================================================================
echo Monitor stopped.
echo ================================================================================
pause
