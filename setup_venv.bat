@echo off
REM Batch file để setup virtual environment
REM Sử dụng: setup_venv.bat

echo ========================================
echo SETUP VIRTUAL ENVIRONMENT
echo ========================================
echo.

REM Tạo virtual environment với Python 3.10
echo Dang tao virtual environment...
C:\Users\khain\AppData\Local\Programs\Python\Python310\python.exe -m venv venv

if %ERRORLEVEL% NEQ 0 (
    echo Loi khi tao venv!
    pause
    exit /b 1
)

echo.
echo ========================================
echo.

REM Kích hoạt venv
echo Dang kich hoat venv...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Dang upgrade pip...
python -m pip install --upgrade pip

REM Cài dependencies
echo Dang cai dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo HOAN THANH!
echo ========================================
echo.
echo Virtual environment da duoc tao va kich hoat!
echo.
echo Cac buoc tiep theo:
echo   1. Chay: venv\Scripts\activate
echo   2. Chay: python auto_login_selenium.py
echo.
echo De tat venv: deactivate
echo.

pause
