@echo off
REM Batch file để chạy tự động hàng ngày
REM Sử dụng: Double-click file này hoặc lên lịch với Task Scheduler

echo ========================================
echo FETCH CLONE LIST - AUTO RUN
echo ========================================
echo.

REM Chuyển đến thư mục chứa script
cd /d "%~dp0"

REM Lấy dữ liệu mới
echo [%date% %time%] Dang lay du lieu moi...
python fetch_data.py

echo.
echo ========================================
echo.

REM So sánh với dữ liệu mẫu (nếu có)
if exist "data\clone_list_sample.json" (
    echo [%date% %time%] Dang so sanh du lieu...
    python compare_data.py
) else (
    echo Chua co file mau de so sanh.
    echo Chay lenh: copy data\clone_list_latest.json data\clone_list_sample.json
)

echo.
echo ========================================
echo HOAN THANH!
echo ========================================
echo.

REM Lưu log
echo [%date% %time%] Script completed >> logs\run_history.log

pause
