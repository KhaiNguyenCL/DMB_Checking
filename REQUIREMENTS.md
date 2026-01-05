# 📦 Requirements

## Thư viện Python cần thiết

### Cơ bản (bắt buộc):
```bash
pip install requests
```

### Tự động lấy cookie:

#### Phương án 1: Selenium (Khuyên dùng)
```bash
pip install selenium webdriver-manager
```

#### Phương án 2: Browser Cookie Extractor
```bash
pip install browser-cookie3
```

### Tất cả trong một:
```bash
pip install -r requirements.txt
```

---

## File requirements.txt

Tạo file `requirements.txt` với nội dung:

```
requests>=2.31.0
urllib3>=2.0.0
selenium>=4.15.0
webdriver-manager>=4.0.0
browser-cookie3>=0.19.0
```

Sau đó cài đặt:
```bash
pip install -r requirements.txt
```

---

## Kiểm tra cài đặt

```bash
# Kiểm tra Python
python --version

# Kiểm tra pip
pip --version

# Kiểm tra thư viện đã cài
pip list | findstr requests
pip list | findstr selenium
pip list | findstr browser-cookie3
```

---

## Troubleshooting

### Lỗi: "pip is not recognized"
→ Cài lại Python, tick "Add Python to PATH"

### Lỗi: "Permission denied"
→ Chạy CMD as Administrator

### Lỗi: Chrome driver version mismatch
→ `webdriver-manager` sẽ tự động download đúng version

---

**Sau khi cài đặt xong, bắt đầu với AUTO_COOKIE.md! 🚀**
