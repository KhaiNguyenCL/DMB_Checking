#!/bin/bash

# ========================================
# Auto Fetch Script for Linux
# ========================================

# Chuyển đến thư mục script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Kích hoạt virtual environment
source venv/bin/activate

# Tạo thư mục logs nếu chưa có
mkdir -p logs

# Log file
LOG_FILE="logs/run_history.log"

echo "========================================" | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting auto fetch..." | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Bước 1: Auto login (lấy cookie)
echo "" | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Getting cookie..." | tee -a "$LOG_FILE"
python auto_login_selenium.py 2>&1 | tee -a "$LOG_FILE"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Failed to get cookie!" | tee -a "$LOG_FILE"
    deactivate
    exit 1
fi

# Bước 2: Fetch data
echo "" | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Fetching data..." | tee -a "$LOG_FILE"
python fetch_data.py 2>&1 | tee -a "$LOG_FILE"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Failed to fetch data!" | tee -a "$LOG_FILE"
    deactivate
    exit 1
fi

# Bước 3: Compare và gửi email
echo "" | tee -a "$LOG_FILE"
if [ -f "data/clone_list_sample.json" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Comparing data..." | tee -a "$LOG_FILE"
    python compare_data.py 2>&1 | tee -a "$LOG_FILE"
    
    echo "" | tee -a "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sending email notification..." | tee -a "$LOG_FILE"
    python send_email_notification.py 2>&1 | tee -a "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Creating sample file..." | tee -a "$LOG_FILE"
    cp data/clone_list_latest.json data/clone_list_sample.json
    echo "Sample file created." | tee -a "$LOG_FILE"
fi

# Hoàn thành
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Completed successfully!" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Tắt venv
deactivate

exit 0
