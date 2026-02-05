# 🐧 Quick Start: Deploy Lên Linux VM

## 🚀 Cài Đặt Nhanh (5 phút)

### Bước 1: Copy Files

```bash
# Từ máy Windows (PowerShell)
scp -r E:\Script\learning_api_scraping user@your-vm-ip:/home/user/

# Hoặc SSH vào VM và clone từ Git
ssh user@your-vm-ip
git clone <your-repo-url>
cd learning_api_scraping
```

### Bước 2: Cài Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Cài Python và Chrome
sudo apt install -y python3 python3-pip python3-venv wget unzip0
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install -y
```

### Bước 3: Setup Environment

```bash
cd ~/learning_api_scraping

<div class="intranet-auth-cover-header">
				<?=Loc::getMessage("INTRANET_LOGIN_AIR_PROMO");?>
			</div>

# Tạo venv
python3 -m venv venv

# Kích hoạt
source venv/bin/activate

# Cài packages
pip install -r requirements.txt
```

### Bước 4: Cấu Hình

```bash
# Chỉnh sửa config
nano config_auto.py
# Điền username, password, đặt HEADLESS_MODE = True

nano config_email.py
# Điền email, app password

# Lưu: Ctrl+X, Y, Enter
```

### Bước 5: Test

```bash
source venv/bin/activate

# Test auto login
python auto_login_selenium.py

# Test fetch
python fetch_data.py
```

### Bước 6: Lên Lịch Cron

```bash
# Cho phép execute
chmod +x run_auto.sh

# Mở crontab
crontab -e

# Thêm dòng (chạy mỗi ngày 9:00 AM)
0 9 * * * /home/user/learning_api_scraping/run_auto.sh

# Lưu và thoát
```

### Bước 7: Kiểm Tra

```bash
# Xem cron jobs
crontab -l

# Xem log
tail -f logs/run_history.log
```

---

## ✅ Hoàn Thành!

Script sẽ tự động chạy mỗi ngày lúc 9:00 AM!

**Xem chi tiết:** [DEPLOY_TO_VM.md](DEPLOY_TO_VM.md)
