# 📧 Email Notification - Hướng Dẫn

## 🎯 Tính Năng

Script sẽ tự động gửi email thông báo:
- ✅ **Khi có thay đổi dữ liệu** (quan trọng)
- ✅ **Báo cáo hàng ngày** (tùy chọn)

Email có định dạng HTML đẹp với:
- 📊 Thống kê tổng quan
- ➕ Danh sách records thêm mới
- ➖ Danh sách records bị xóa
- 🎨 Màu sắc dễ nhìn

---

## 🚀 Cài Đặt Nhanh

### Bước 1: Lấy App Password từ Gmail

1. Truy cập: https://myaccount.google.com/security
2. Bật **"2-Step Verification"** (nếu chưa bật)
3. Tìm **"App passwords"** (hoặc search "App passwords")
4. Chọn app: **"Mail"**
5. Chọn device: **"Windows Computer"**
6. Click **"Generate"**
7. Copy **16 ký tự** password (dạng: `xxxx xxxx xxxx xxxx`)

### Bước 2: Cấu Hình Email

Mở file `config_email.py`, điền thông tin:

```python
# Email gửi đi (Gmail)
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "xxxx xxxx xxxx xxxx"  # App Password vừa lấy

# Email nhận (có thể giống sender)
RECEIVER_EMAIL = "your_email@gmail.com"

# Gửi email khi có thay đổi
NOTIFY_ON_CHANGE = True

# Gửi email hàng ngày (dù có thay đổi hay không)
NOTIFY_DAILY_SUMMARY = False  # Đặt True nếu muốn nhận báo cáo hàng ngày
```

### Bước 3: Test

```powershell
# Kích hoạt venv
.\venv\Scripts\activate

# Test gửi email
python send_email_notification.py
```

Nếu thành công, bạn sẽ nhận email! ✅

---

## 📧 Ví Dụ Email

### Email khi có thay đổi:

```
Tiêu đề: ⚠️ Cảnh báo: Phát hiện thay đổi dữ liệu

Nội dung:
┌─────────────────────────────────┐
│  ⚠️ PHÁT HIỆN THAY ĐỔI          │
│  Báo cáo tự động từ API Scraping│
└─────────────────────────────────┘

📊 Thống Kê
- Thời gian lấy dữ liệu mẫu: 2026-01-05 08:00:00
- Thời gian lấy dữ liệu mới: 2026-01-05 09:00:00
- Số lượng records (mẫu): 1204
- Số lượng records (mới): 1206

🔍 Chi Tiết Thay Đổi
➕ Thêm mới: 2 records
➖ Xóa đi: 0 records

Records Thêm Mới:
• 17082 New Store MB 01
• 17083 New Store MB 02
```

### Email không có thay đổi:

```
Tiêu đề: 📊 Báo cáo hàng ngày: API Scraping

Nội dung:
┌─────────────────────────────────┐
│  ✅ KHÔNG CÓ THAY ĐỔI           │
│  Báo cáo tự động từ API Scraping│
└─────────────────────────────────┘

📊 Thống Kê
- Số lượng records: 1204
- Dữ liệu giống nhau hoàn toàn
```

---

## 🔧 Cấu Hình Nâng Cao

### Chỉ gửi email khi có thay đổi (Khuyên dùng):

```python
NOTIFY_ON_CHANGE = True
NOTIFY_DAILY_SUMMARY = False
```

### Gửi email hàng ngày (dù có thay đổi hay không):

```python
NOTIFY_ON_CHANGE = True
NOTIFY_DAILY_SUMMARY = True
```

### Không gửi email:

```python
NOTIFY_ON_CHANGE = False
NOTIFY_DAILY_SUMMARY = False
```

---

## 🔄 Tích Hợp Với Workflow

Script đã được tích hợp vào `run_auto.bat`:

```batch
1. Auto login (lấy cookie)
2. Fetch data
3. Compare data
4. Send email notification  ← Tự động gửi email
5. Lưu log
```

Khi chạy Task Scheduler, email sẽ tự động gửi mỗi ngày!

---

## ⚠️ Troubleshooting

### Lỗi: "SMTPAuthenticationError"

**Nguyên nhân:** Email hoặc password sai

**Giải pháp:**
1. Kiểm tra `SENDER_EMAIL` có đúng không
2. Kiểm tra `SENDER_PASSWORD` có phải App Password không (16 ký tự)
3. Đảm bảo đã bật 2-Step Verification

### Lỗi: "Connection refused"

**Nguyên nhân:** Firewall chặn hoặc SMTP server sai

**Giải pháp:**
1. Kiểm tra kết nối internet
2. Tắt firewall/antivirus tạm thời để test
3. Đảm bảo `SMTP_SERVER = "smtp.gmail.com"` và `SMTP_PORT = 465`

### Không nhận được email

**Kiểm tra:**
1. Folder **Spam/Junk** trong Gmail
2. Email `RECEIVER_EMAIL` có đúng không
3. Chạy script thủ công để xem lỗi: `python send_email_notification.py`

---

## 🔒 Bảo Mật

### ⚠️ QUAN TRỌNG:

1. **KHÔNG commit `config_email.py` lên Git**
   - File đã được thêm vào `.gitignore`

2. **Dùng App Password, KHÔNG dùng password Gmail thường**
   - App Password an toàn hơn
   - Có thể revoke bất cứ lúc nào

3. **Dùng Environment Variables (Khuyên dùng):**

```python
import os
SENDER_EMAIL = os.getenv("EMAIL_SENDER")
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")
```

Set environment variables:
```powershell
setx EMAIL_SENDER "your_email@gmail.com"
setx EMAIL_PASSWORD "your_app_password"
setx EMAIL_RECEIVER "your_email@gmail.com"
```

---

## 📊 Workflow Hoàn Chỉnh

```
Mỗi ngày lúc 9:00 AM:
  ↓
1. Auto login (Selenium)
  ↓
2. Fetch 1204 records
  ↓
3. Compare với dữ liệu ngày hôm trước
  ↓
4. Nếu có thay đổi:
   → Gửi email cảnh báo 📧
  ↓
5. Lưu log
  ↓
Hoàn thành! ✅
```

---

## 🎉 Hoàn Thành!

Bây giờ bạn sẽ nhận email tự động mỗi khi có thay đổi dữ liệu!

**Test ngay:**
```powershell
.\venv\Scripts\activate
python send_email_notification.py
```

**Xem thêm:**
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [Python smtplib Documentation](https://docs.python.org/3/library/smtplib.html)
