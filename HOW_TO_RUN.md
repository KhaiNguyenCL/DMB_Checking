# 🚀 Chạy Auto Login - Hướng Dẫn Nhanh

## ✅ Bạn Đã Hoàn Thành:
- ✅ Setup virtual environment
- ✅ Cài đặt dependencies (selenium, webdriver-manager, etc.)
- ✅ Lấy được 1204 records từ API
- ✅ Điền email/password vào `config_auto.py`

## 🎯 Bước Tiếp Theo: Chạy Auto Login

### Trong Terminal (PowerShell):

```powershell
# Bước 1: Kích hoạt virtual environment
.\venv\Scripts\activate

# Bước 2: Chạy auto login script
python auto_login_selenium.py
```

### Script sẽ:
1. 🌐 Mở Chrome tự động
2. 🔐 Truy cập trang login
3. ⌨️ Tự động điền email/password
4. 🖱️ Click nút đăng nhập
5. 🍪 Lấy cookie
6. 💾 Lưu vào `cookies.json`
7. ✏️ Cập nhật `config.py`

---

## ⚠️ Nếu Gặp Lỗi

### Lỗi: "No module named 'selenium'"
→ Bạn chưa kích hoạt venv, chạy: `.\venv\Scripts\activate`

### Lỗi: "Không tìm thấy input username"
→ Trang web load chậm hoặc form khác, script sẽ cho phép đăng nhập thủ công

### Chrome không mở
→ Kiểm tra Chrome đã cài đặt chưa, script sẽ tự download ChromeDriver

---

## 🔄 Workflow Hoàn Chỉnh

### Lần đầu tiên:
```powershell
# Setup (chỉ cần làm 1 lần)
.\setup_venv.bat

# Kích hoạt venv
.\venv\Scripts\activate

# Lấy cookie tự động
python auto_login_selenium.py

# Fetch data
python fetch_data.py
```

### Lần sau (hàng ngày):
```powershell
# Kích hoạt venv
.\venv\Scripts\activate

# Chạy tất cả (auto cookie + fetch + compare)
python auto_login_selenium.py
python fetch_data.py
python compare_data.py
```

### Hoặc dùng batch file:
```powershell
.\run_auto.bat
```

---

## 📊 Kết Quả Mong Đợi

```
============================================================
🤖 TỰ ĐỘNG LẤY COOKIE VỚI SELENIUM
============================================================

🚀 Đang khởi động Chrome...
🌐 Đang truy cập: https://34.64.189.31/login
🔍 Đang tìm form đăng nhập...
✅ Tìm thấy email/username input: #inputEmailAddress
✅ Tìm thấy password input: #inputPassword
⌨️  Đang nhập email: your_email@example.com
⌨️  Đang nhập password...
✅ Tìm thấy submit button: button[type='submit']
🖱️  Đang click nút đăng nhập...
⏳ Đang đợi đăng nhập...
✅ Đăng nhập thành công!

============================================================
✅ LẤY COOKIE THÀNH CÔNG!
============================================================

🍪 Cookies:
   PHPSESSID = abc123...
   user_id = 789...

💾 Đã lưu cookies vào: cookies.json
✅ Đã cập nhật config.py với cookie mới!

📌 Bước tiếp theo:
   1. Chạy: python fetch_data.py
   2. Kiểm tra dữ liệu trong data/
```

---

## 🎉 Hoàn Toàn Tự Động

Sau khi test thành công, lên lịch với Task Scheduler:

1. Mở Task Scheduler
2. Create Basic Task
3. Trigger: Daily, 9:00 AM
4. Action: Start a program
5. Program: `E:\Script\learning_api_scraping\run_auto.bat`

→ Mỗi ngày 9:00 AM, script sẽ tự động:
- Lấy cookie mới
- Fetch dữ liệu
- So sánh với ngày hôm trước
- Lưu log

---

**Bây giờ hãy thử chạy trong terminal! 🚀**

```powershell
.\venv\Scripts\activate
python auto_login_selenium.py
```
