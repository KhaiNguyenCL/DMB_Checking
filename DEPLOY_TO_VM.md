# 🖥️ Deploy Lên Máy Ảo (VM)

## 🎯 Tổng Quan

Bạn có thể deploy script lên:
- ✅ **Windows VM** - Dùng Task Scheduler (giống máy local)
- ✅ **Linux VM** - Dùng Cron (khuyên dùng vì nhẹ hơn)

---

## 🪟 Phương Án 1: Windows VM

### Bước 1: Copy Files

**Cách 1: Dùng RDP (Remote Desktop)**
1. Kết nối RDP vào Windows VM
2. Copy toàn bộ folder `learning_api_scraping` vào VM
3. Đặt ở: `C:\Scripts\learning_api_scraping`

**Cách 2: Dùng SCP/SFTP**
```powershell
# Từ máy local
scp -r E:\Script\learning_api_scraping user@vm-ip:C:\Scripts\
```

### Bước 2: Setup Environment

Trên Windows VM:

```powershell
# Di chuyển vào thư mục
cd C:\Scripts\learning_api_scraping

# Setup virtual environment
.\setup_venv.bat

# Test chạy
.\venv\Scripts\activate
python auto_login_selenium.py
python fetch_data.py
```

### Bước 3: Cài Chrome (Nếu chưa có)

1. Download Chrome: https://www.google.com/chrome/
2. Cài đặt bình thường
3. Script sẽ tự động download ChromeDriver

### Bước 4: Lên Lịch Task Scheduler

Làm giống như trên máy local (xem `SCHEDULE_DAILY.md`)

**Lưu ý:**
- Đảm bảo VM chạy 24/7
- Cấu hình "Run whether user is logged on or not"

---

## 🐧 Phương Án 2: Linux VM (Khuyên Dùng)

### Bước 1: Copy Files

```bash
# Từ máy local (PowerShell)
scp -r E:\Script\learning_api_scraping user@vm-ip:/home/user/

# Hoặc dùng Git
ssh user@vm-ip
cd ~
git clone <your-repo-url>
cd learning_api_scraping
```

### Bước 2: Cài Đặt Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Cài Python 3 và pip
sudo apt install python3 python3-pip python3-venv -y

# Cài Chrome và ChromeDriver
sudo apt install wget unzip -y

# Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install -y

# ChromeDriver (tự động bởi webdriver-manager)
```

### Bước 3: Setup Virtual Environment

```bash
cd ~/learning_api_scraping

# Tạo venv
python3 -m venv venv

# Kích hoạt
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt
```

### Bước 4: Cấu Hình Files

```bash
# Copy config mẫu
cp config_auto.py.example config_auto.py
cp config_email.py.example config_email.py

# Chỉnh sửa config
nano config_auto.py
# Điền username, password

nano config_email.py
# Điền email, app password
```

### Bước 5: Test Chạy

```bash
# Kích hoạt venv
source venv/bin/activate

# Test auto login
python auto_login_selenium.py

# Test fetch data
python fetch_data.py

# Test email
python send_email_notification.py
```

### Bước 6: Tạo Shell Script

Tạo file `run_auto.sh`:

```bash
#!/bin/bash

# Chuyển đến thư mục script
cd /home/user/learning_api_scraping

# Kích hoạt virtual environment
source venv/bin/activate

# Log file
LOG_FILE="logs/run_history.log"
mkdir -p logs

echo "========================================" >> $LOG_FILE
echo "[$(date)] Starting auto fetch..." >> $LOG_FILE

# Bước 1: Auto login
echo "[$(date)] Getting cookie..." >> $LOG_FILE
python auto_login_selenium.py >> $LOG_FILE 2>&1

if [ $? -ne 0 ]; then
    echo "[$(date)] Error getting cookie!" >> $LOG_FILE
    exit 1
fi

# Bước 2: Fetch data
echo "[$(date)] Fetching data..." >> $LOG_FILE
python fetch_data.py >> $LOG_FILE 2>&1

# Bước 3: Compare và gửi email
if [ -f "data/clone_list_sample.json" ]; then
    echo "[$(date)] Comparing data..." >> $LOG_FILE
    python compare_data.py >> $LOG_FILE 2>&1
    
    echo "[$(date)] Sending email..." >> $LOG_FILE
    python send_email_notification.py >> $LOG_FILE 2>&1
else
    echo "[$(date)] Creating sample file..." >> $LOG_FILE
    cp data/clone_list_latest.json data/clone_list_sample.json
fi

echo "[$(date)] Completed!" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# Tắt venv
deactivate
```

Cho phép execute:
```bash
chmod +x run_auto.sh
```

### Bước 7: Lên Lịch Cron

```bash
# Mở crontab
crontab -e

# Thêm dòng này (chạy mỗi ngày lúc 9:00 AM)
0 9 * * * /home/user/learning_api_scraping/run_auto.sh

# Lưu và thoát (Ctrl+X, Y, Enter)
```

**Giải thích Cron syntax:**
```
0 9 * * *
│ │ │ │ │
│ │ │ │ └─── Ngày trong tuần (0-7, 0=Sunday)
│ │ │ └───── Tháng (1-12)
│ │ └─────── Ngày trong tháng (1-31)
│ └───────── Giờ (0-23)
└─────────── Phút (0-59)
```

**Ví dụ khác:**
```bash
# Mỗi 6 giờ
0 */6 * * * /path/to/run_auto.sh

# Mỗi ngày lúc 9:00 AM và 6:00 PM
0 9,18 * * * /path/to/run_auto.sh

# Thứ 2 đến Thứ 6, lúc 9:00 AM
0 9 * * 1-5 /path/to/run_auto.sh
```

### Bước 8: Kiểm Tra Cron

```bash
# Xem danh sách cron jobs
crontab -l

# Xem log cron (Ubuntu/Debian)
grep CRON /var/log/syslog

# Xem log script
tail -f ~/learning_api_scraping/logs/run_history.log
```

---

## 🔧 Cấu Hình Headless Mode (Linux)

Vì Linux VM thường không có GUI, cần chạy Chrome ở chế độ headless:

**Cập nhật `config_auto.py`:**
```python
# Chạy headless (không hiển thị trình duyệt)
HEADLESS_MODE = True
```

**Hoặc cập nhật `auto_login_selenium.py`:**
```python
# Thêm options
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
```

---

## 📊 So Sánh Windows VM vs Linux VM

| Tiêu chí | Windows VM | Linux VM |
|----------|------------|----------|
| **Tài nguyên** | 2-4 GB RAM | 512 MB - 1 GB RAM |
| **Chi phí** | Cao hơn | Thấp hơn |
| **Setup** | Dễ (giống máy local) | Khó hơn (CLI) |
| **Hiệu năng** | Chậm hơn | Nhanh hơn |
| **Khuyên dùng** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🐛 Troubleshooting

### Linux: Chrome không chạy được

```bash
# Cài thêm dependencies
sudo apt install -y \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0
```

### Linux: Permission denied

```bash
# Cho phép execute
chmod +x run_auto.sh

# Kiểm tra owner
ls -la run_auto.sh

# Đổi owner nếu cần
sudo chown user:user run_auto.sh
```

### Cron không chạy

```bash
# Kiểm tra cron service
sudo systemctl status cron

# Restart cron
sudo systemctl restart cron

# Kiểm tra log
grep CRON /var/log/syslog | tail -20
```

---

## 🔒 Bảo Mật

### 1. Không để credentials trong code

Dùng environment variables:

```bash
# Thêm vào ~/.bashrc hoặc ~/.profile
export API_USERNAME="your_username"
export API_PASSWORD="your_password"
export EMAIL_SENDER="your_email@gmail.com"
export EMAIL_PASSWORD="your_app_password"

# Reload
source ~/.bashrc
```

### 2. Giới hạn quyền truy cập

```bash
# Chỉ owner mới đọc được config files
chmod 600 config_auto.py
chmod 600 config_email.py
```

### 3. Firewall

```bash
# Chỉ cho phép SSH và HTTPS
sudo ufw allow ssh
sudo ufw allow https
sudo ufw enable
```

---

## 📋 Checklist Deploy

### Windows VM:
- [ ] Copy files vào VM
- [ ] Setup virtual environment
- [ ] Cài Chrome
- [ ] Test chạy thủ công
- [ ] Tạo Task Scheduler task
- [ ] Test task chạy tự động

### Linux VM:
- [ ] Copy files vào VM
- [ ] Cài Python, Chrome
- [ ] Setup virtual environment
- [ ] Cấu hình config files
- [ ] Tạo run_auto.sh
- [ ] Test script chạy thủ công
- [ ] Setup cron job
- [ ] Kiểm tra log

---

## 🎉 Hoàn Thành!

Sau khi deploy lên VM:
- ✅ Script chạy 24/7
- ✅ Không phụ thuộc máy cá nhân
- ✅ Nhận email tự động mỗi ngày
- ✅ Hoàn toàn tự động

**Bước tiếp theo:**
- Monitor log files
- Kiểm tra email hàng ngày
- Backup dữ liệu định kỳ

---

**Chúc bạn deploy thành công! 🚀**
