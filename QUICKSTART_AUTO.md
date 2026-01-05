# 🚀 Quick Start: Auto Cookie

## Cách nhanh nhất để lấy cookie tự động

### Bước 1: Cài đặt
```bash
pip install selenium webdriver-manager
```

### Bước 2: Cấu hình
Mở `config_auto.py`, sửa:
```python
USERNAME = "your_username"  # Thay bằng username thật
PASSWORD = "your_password"  # Thay bằng password thật
```

### Bước 3: Chạy
```bash
python auto_login_selenium.py
```

Script sẽ:
- ✅ Tự động mở Chrome
- ✅ Đăng nhập
- ✅ Lấy cookie
- ✅ Cập nhật `config.py`

### Bước 4: Fetch data
```bash
python fetch_data.py
```

---

## 🎯 Hoàn toàn tự động

Dùng `run_auto.bat` để chạy tất cả:
```bash
run_auto.bat
```

Lên lịch với Task Scheduler → Tự động 100%!

---

## 🔄 3 Phương án

| Phương án | Lệnh | Tốc độ | Tự động |
|-----------|------|--------|---------|
| **Selenium** | `python auto_login_selenium.py` | 🐢 | ✅ 100% |
| **Browser Extract** | `python extract_browser_cookie.py` | ⚡ | ⚠️ Cần login trước |
| **POST Request** | `python login_with_requests.py` | ⚡⚡ | ⚠️ Tùy trang web |

**Khuyên dùng: Selenium** (tự động 100%)

---

Đọc thêm: [AUTO_COOKIE.md](AUTO_COOKIE.md)
