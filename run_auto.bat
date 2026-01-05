@echo off
REM Batch file để chạy tự động với auto cookie extraction
REM Sử dụng: Double-click file này hoặc lên lịch với Task Scheduler

echo ========================================
echo AUTO FETCH WITH COOKIE REFRESH
echo ========================================
echo.

REM Chuyển đến thư mục chứa script
cd /d "%~dp0"

REM Kích hoạt virtual environment
echo Kich hoat virtual environment...
call venv\Scripts\activate.bat

echo.
echo ========================================
echo.

REM Bước 1: Lấy cookie mới (tự động)
echo [%date% %time%] Dang lay cookie moi...
python auto_login_selenium.py

REM Kiểm tra kết quả
if %ERRORLEVEL% NEQ 0 (
    echo [%date% %time%] Loi khi lay cookie! >> logs\run_history.log
    echo Loi khi lay cookie! Vui long kiem tra.
    pause
    exit /b 1
)

echo.
echo ========================================
echo.

REM Bước 2: Lấy dữ liệu mới
echo [%date% %time%] Dang lay du lieu moi...
python fetch_data.py

echo.
echo ========================================
echo.

REM Bước 3: So sánh với dữ liệu mẫu (nếu có)
if exist "data\clone_list_sample.json" (
    echo [%date% %time%] Dang so sanh du lieu...
    python compare_data.py
    
    echo.
    echo Dang gui email thong bao...
    python send_email_notification.py
) else (
    echo Chua co file mau de so sanh.
    echo Tao file mau...
    copy data\clone_list_latest.json data\clone_list_sample.json
)

echo.
echo ========================================
echo HOAN THANH!
echo ========================================
echo.

REM Lưu log
echo [%date% %time%] Script completed successfully >> logs\run_history.log

REM Tắt venv
call venv\Scripts\deactivate.bat

REM Không pause khi chạy tự động
REM pause
