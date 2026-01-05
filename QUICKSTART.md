# 🚀 Quick Start Guide

## Bắt đầu nhanh trong 5 phút!

### Bước 1: Cài Python
```bash
# Kiểm tra Python đã cài chưa
python --version

# Nếu chưa có, download tại: https://www.python.org/downloads/
```

### Bước 2: Cài thư viện
```bash
pip install requests
```

### Bước 3: Lấy Cookie

1. Mở Chrome, truy cập `https://34.64.189.31`
2. Đăng nhập
3. Nhấn `F12` → Tab **Network**
4. Reload trang (`F5`)
5. Click vào request đầu tiên
6. Tìm **Request Headers** → **Cookie**
7. Click chuột phải → **Copy value**

### Bước 4: Cấu hình

Mở file `config.py`, tìm dòng:
```python
COOKIE = "YOUR_COOKIE_HERE"
```

Thay bằng cookie vừa copy:
```python
COOKIE = "PHPSESSID=abc123; user_id=789; ..."
```

Lưu file.

### Bước 5: Chạy!

```bash
# Lấy dữ liệu
python fetch_data.py

# Tạo file mẫu
copy data\clone_list_latest.json data\clone_list_sample.json

# Chạy lại và so sánh
python fetch_data.py
python compare_data.py
```

---

## 🎯 Kết quả mong đợi

Sau khi chạy `fetch_data.py`:
```
🔄 Đang lấy dữ liệu từ API...
📄 Trang 1: Lấy được 100 records (0-100 / 1204)
📄 Trang 2: Lấy được 100 records (100-200 / 1204)
...
✅ Hoàn thành! Tổng cộng: 1204 records
💾 Đã lưu vào: data/clone_list_latest.json
```

Sau khi chạy `compare_data.py`:
```
📊 SO SÁNH DỮ LIỆU
✅ DỮ LIỆU GIỐNG NHAU HOÀN TOÀN!
```

---

## ❓ Gặp lỗi?

### Lỗi: "Cookie chưa cấu hình"
→ Bạn chưa thay `YOUR_COOKIE_HERE` trong `config.py`

### Lỗi: "Status code 401"
→ Cookie sai hoặc hết hạn, lấy cookie mới

### Lỗi: "Module not found: requests"
→ Chạy: `pip install requests`

---

## 📚 Đọc thêm

- [README.md](README.md) - Hướng dẫn chi tiết
- [EXERCISES.md](EXERCISES.md) - Bài tập thực hành

**Chúc bạn thành công! 🎉**
