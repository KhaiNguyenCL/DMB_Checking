# 🔧 Fix: Python Version Mismatch

## ❌ Vấn Đề

Bạn gặp lỗi:
```
ModuleNotFoundError: No module named 'selenium'
```

Mặc dù đã cài: `pip install selenium`

## 🎯 Nguyên Nhân

Bạn có **2 phiên bản Python** trên máy:
- **Python 3.13.7** - Đang dùng khi chạy `python`
- **Python 3.10.11** - Pip cài package vào đây

→ Khi chạy `python`, nó dùng Python 3.13 (không có selenium)
→ Khi chạy `pip`, nó cài vào Python 3.10 (có selenium)

## ✅ Giải Pháp

### Cách 1: Dùng Python 3.10 (Nhanh nhất - Khuyên dùng)

Thay vì chạy:
```bash
python auto_login_selenium.py
```

Chạy:
```bash
C:\Users\khain\AppData\Local\Programs\Python\Python310\python.exe auto_login_selenium.py
```

Hoặc tạo alias (xem bên dưới).

---

### Cách 2: Cài Selenium cho Python 3.13

```bash
# Cài pip cho Python 3.13
python -m ensurepip --upgrade

# Cài selenium
python -m pip install selenium webdriver-manager
```

---

### Cách 3: Tạo Batch File (Khuyên dùng nhất)

Tôi đã tạo file `run_with_python310.bat` cho bạn:

```batch
@echo off
C:\Users\khain\AppData\Local\Programs\Python\Python310\python.exe %*
```

Sau đó chạy:
```bash
.\run_with_python310.bat auto_login_selenium.py
```

---

## 🚀 Giải Pháp Lâu Dài

### Tạo Virtual Environment (Khuyên dùng)

```bash
# Tạo venv với Python 3.10
C:\Users\khain\AppData\Local\Programs\Python\Python310\python.exe -m venv venv

# Kích hoạt venv
.\venv\Scripts\activate

# Cài packages
pip install -r requirements.txt

# Chạy script
python auto_login_selenium.py
```

Sau khi kích hoạt venv, mọi lệnh `python` và `pip` sẽ dùng đúng phiên bản!

---

## 📝 Kiểm Tra

```bash
# Kiểm tra Python version
python --version

# Kiểm tra pip version
pip --version

# Kiểm tra selenium đã cài chưa
python -c "import selenium; print(selenium.__version__)"
```

---

## 🎯 Khuyến Nghị

**Dùng Virtual Environment** vì:
- ✅ Tách biệt dependencies giữa các dự án
- ✅ Tránh conflict giữa các Python versions
- ✅ Dễ quản lý và deploy

---

Xem file `run_with_python310.bat` hoặc `setup_venv.bat` để bắt đầu!
