# 🤖 Lấy Cookie Tự Động

## 🎯 Tổng Quan

Có 3 cách để lấy cookie tự động:

1. ✅ **Selenium WebDriver** (Khuyên dùng) - Tự động đăng nhập và lấy cookie
2. ✅ **Browser Cookie Extractor** - Đọc cookie từ trình duyệt đang chạy
3. ✅ **Requests Session** - Đăng nhập bằng POST request

---

## 🚀 Phương Án 1: Selenium WebDriver (Khuyên Dùng)

### Ưu điểm:
- ✅ Tự động đăng nhập hoàn toàn
- ✅ Xử lý được JavaScript, CAPTCHA (nếu có)
- ✅ Giống hành vi người dùng thật
- ✅ Lấy cookie mới mỗi khi chạy

### Nhược điểm:
- ❌ Cần cài Chrome Driver
- ❌ Chậm hơn (vì phải mở trình duyệt)

### Cài đặt:

```bash
pip install selenium webdriver-manager
```

### Code mẫu:

Xem file `auto_login_selenium.py`

---

## 🔍 Phương Án 2: Browser Cookie Extractor

### Ưu điểm:
- ✅ Rất nhanh
- ✅ Không cần đăng nhập lại
- ✅ Lấy cookie từ Chrome/Firefox đang chạy

### Nhược điểm:
- ❌ Cần đăng nhập thủ công lần đầu
- ❌ Phụ thuộc vào trình duyệt

### Cài đặt:

```bash
pip install browser-cookie3
```

### Code mẫu:

Xem file `extract_browser_cookie.py`

---

## 📮 Phương Án 3: Requests Session (POST Login)

### Ưu điểm:
- ✅ Rất nhanh
- ✅ Không cần trình duyệt
- ✅ Nhẹ nhất

### Nhược điểm:
- ❌ Phải biết form login
- ❌ Không xử lý được JavaScript
- ❌ Có thể bị CAPTCHA chặn

### Code mẫu:

Xem file `login_with_requests.py`

---

## 🎯 So Sánh

| Tính năng | Selenium | Browser Cookie | Requests |
|-----------|----------|----------------|----------|
| Tốc độ | 🐢 Chậm | ⚡ Nhanh | ⚡ Rất nhanh |
| Tự động 100% | ✅ Có | ❌ Không | ⚠️ Tùy |
| Xử lý JS | ✅ Có | N/A | ❌ Không |
| Độ phức tạp | 🔴 Cao | 🟢 Thấp | 🟡 Trung bình |
| Khuyên dùng | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 💡 Khuyến Nghị

### Dùng Selenium khi:
- ✅ Muốn tự động hóa hoàn toàn
- ✅ Trang web có JavaScript phức tạp
- ✅ Có CAPTCHA (có thể xử lý thủ công)
- ✅ Chạy định kỳ (hàng ngày)

### Dùng Browser Cookie khi:
- ✅ Đã đăng nhập sẵn trên trình duyệt
- ✅ Muốn test nhanh
- ✅ Cookie còn hạn lâu

### Dùng Requests khi:
- ✅ Form login đơn giản
- ✅ Không có CAPTCHA
- ✅ Cần tốc độ cao

---

## 🚀 Bắt Đầu Nhanh

### Bước 1: Chọn phương án

Tôi khuyên bạn dùng **Selenium** vì tự động 100%.

### Bước 2: Cài đặt

```bash
pip install selenium webdriver-manager
```

### Bước 3: Cấu hình

Mở file `config_auto.py`, điền username và password:

```python
LOGIN_URL = "https://34.64.189.31/login"
USERNAME = "your_username"
PASSWORD = "your_password"
```

### Bước 4: Chạy

```bash
python auto_login_selenium.py
```

Script sẽ:
1. Mở Chrome tự động
2. Đăng nhập
3. Lấy cookie
4. Lưu vào file `cookies.json`
5. Cập nhật `config.py`

### Bước 5: Sử dụng

```bash
python fetch_data.py
```

---

## 🔄 Tự Động Hóa Hoàn Toàn

Kết hợp với `run_daily.bat`:

```batch
@echo off
REM Lấy cookie mới
python auto_login_selenium.py

REM Fetch dữ liệu
python fetch_data.py

REM So sánh
python compare_data.py
```

Lên lịch chạy hàng ngày → Hoàn toàn tự động!

---

## ⚠️ Lưu Ý Bảo Mật

### QUAN TRỌNG:

1. **KHÔNG commit username/password lên Git**
2. **Dùng environment variables:**

```python
import os
USERNAME = os.getenv("API_USERNAME")
PASSWORD = os.getenv("API_PASSWORD")
```

3. **Mã hóa credentials:**

```bash
# Set environment variables (Windows)
setx API_USERNAME "your_username"
setx API_PASSWORD "your_password"
```

---

## 🎓 Bài Tập

1. Thử cả 3 phương án
2. So sánh tốc độ
3. Chọn phương án phù hợp nhất
4. Tích hợp vào workflow

---

**Xem các file code mẫu để bắt đầu! 🚀**
