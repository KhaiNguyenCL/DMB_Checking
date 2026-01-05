# 📚 Hướng dẫn: Lấy Data từ Trang Web có Đăng Nhập

## 🎯 Mục tiêu
Học cách lấy dữ liệu từ API yêu cầu authentication (đăng nhập) bằng Python.

## 📋 Bạn sẽ học được gì?

1. ✅ **Cookie Authentication hoạt động như thế nào**
2. ✅ **Cách lấy cookie từ trình duyệt**
3. ✅ **Sử dụng Python requests để gọi API**
4. ✅ **Xử lý phân trang (pagination)**
5. ✅ **So sánh dữ liệu JSON**
6. ✅ **Tự động hóa với Task Scheduler**

---

## 📦 Cài đặt

### Bước 1: Cài Python
1. Download Python từ: https://www.python.org/downloads/
2. **Quan trọng:** Tick vào "Add Python to PATH" khi cài đặt
3. Kiểm tra cài đặt thành công:
   ```bash
   python --version
   ```

### Bước 2: Cài thư viện cần thiết
Mở Command Prompt (CMD) và chạy:
```bash
pip install requests
```

---

## 🔐 Phần 1: Hiểu về Cookie Authentication

### Cookie là gì?
- Khi bạn đăng nhập vào một trang web, server tạo một **session** (phiên làm việc)
- Server gửi về trình duyệt một **cookie** chứa thông tin session
- Mỗi lần bạn gửi request, trình duyệt tự động gửi kèm cookie này
- Server nhận cookie → nhận diện bạn → cho phép truy cập

### Tại sao cần cookie?
API `https://34.64.189.31/api/cloneList` yêu cầu đăng nhập. Nếu không có cookie, server sẽ:
- Trả về lỗi 401 (Unauthorized)
- Hoặc redirect về trang login

### Giải pháp
Chúng ta sẽ "mượn" cookie từ trình duyệt (sau khi đã đăng nhập) để script Python có thể gọi API.

---

## 🍪 Phần 2: Lấy Cookie từ Trình Duyệt

### Cách 1: Dùng Chrome DevTools (Khuyên dùng)

1. **Đăng nhập vào trang web** `https://34.64.189.31`

2. **Mở Developer Tools:**
   - Nhấn `F12` hoặc
   - Click chuột phải → "Inspect" → Tab "Network"

3. **Reload trang:**
   - Nhấn `Ctrl + R` hoặc `F5`

4. **Tìm request đầu tiên:**
   - Trong tab Network, click vào request đầu tiên (thường là tên domain)
   - Hoặc click vào bất kỳ request nào

5. **Copy Cookie:**
   - Scroll xuống phần **Request Headers**
   - Tìm dòng `Cookie:`
   - Click chuột phải → **Copy value**

   Ví dụ cookie trông như thế này:
   ```
   PHPSESSID=abc123def456; user_id=789; auth_token=xyz789
   ```

### Cách 2: Dùng Tab Application (Chrome)

1. Mở DevTools (`F12`)
2. Vào tab **Application** (hoặc **Storage** trên Firefox)
3. Bên trái, click **Cookies** → chọn `https://34.64.189.31`
4. Bạn sẽ thấy danh sách cookies với cột **Name** và **Value**
5. Copy từng cookie theo format: `Name=Value; Name2=Value2`

### ⚠️ Lưu ý quan trọng
- Cookie có **thời hạn** (thường vài giờ đến vài ngày)
- Khi cookie hết hạn, bạn cần đăng nhập lại và lấy cookie mới
- **KHÔNG chia sẻ cookie** với người khác (giống như mật khẩu)

---

## 🐍 Phần 3: Sử dụng Python để Gọi API

### File 1: `config.py` - Cấu hình

```python
# File này chứa thông tin cấu hình
# QUAN TRỌNG: Thay YOUR_COOKIE_HERE bằng cookie thật

API_URL = "https://34.64.189.31/api/cloneList"

# Paste cookie của bạn vào đây
COOKIE = "YOUR_COOKIE_HERE"

# Headers giả lập trình duyệt
HEADERS = {
    "Cookie": COOKIE,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://34.64.189.31/",
}
```

### File 2: `fetch_data.py` - Lấy dữ liệu

Xem file `fetch_data.py` để hiểu chi tiết cách hoạt động.

### File 3: `compare_data.py` - So sánh dữ liệu

Xem file `compare_data.py` để hiểu cách so sánh JSON.

---

## 🚀 Phần 4: Chạy Script

### Bước 1: Chuẩn bị
1. Lấy cookie từ trình duyệt (theo hướng dẫn Phần 2)
2. Mở file `config.py`
3. Thay `YOUR_COOKIE_HERE` bằng cookie thật
4. Lưu file

### Bước 2: Lấy dữ liệu lần đầu
```bash
python fetch_data.py
```

Kết quả:
- File `data/clone_list_latest.json` sẽ được tạo
- Chứa toàn bộ dữ liệu từ API

### Bước 3: Tạo file mẫu để so sánh
```bash
# Copy file latest làm mẫu
copy data\clone_list_latest.json data\clone_list_sample.json
```

### Bước 4: Chạy lại và so sánh
```bash
# Lấy dữ liệu mới
python fetch_data.py

# So sánh với dữ liệu mẫu
python compare_data.py
```

---

## 📊 Phần 5: Hiểu Kết Quả

### Output của `fetch_data.py`:
```
🔄 Đang lấy dữ liệu từ API...
📄 Trang 1: Lấy được 10 records (0-10 / 1204)
📄 Trang 2: Lấy được 10 records (10-20 / 1204)
...
✅ Hoàn thành! Tổng cộng: 1204 records
💾 Đã lưu vào: data/clone_list_latest.json
```

### Output của `compare_data.py`:
```
📊 So sánh dữ liệu...
✅ Dữ liệu giống nhau hoàn toàn!

Hoặc:

⚠️ Tìm thấy 3 thay đổi:
  + Thêm mới: 2 records
  - Xóa đi: 1 record
  ~ Thay đổi: 0 records
```

---

## 🔧 Phần 6: Xử Lý Lỗi Thường Gặp

### Lỗi 1: SSL Certificate Error
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Nguyên nhân:** Server dùng self-signed certificate

**Giải pháp:** Script đã xử lý bằng `verify=False`

### Lỗi 2: 401 Unauthorized
```
Status code: 401
```

**Nguyên nhân:** Cookie hết hạn hoặc sai

**Giải pháp:**
1. Đăng nhập lại vào trang web
2. Lấy cookie mới
3. Cập nhật file `config.py`

### Lỗi 3: Connection Error
```
ConnectionError: Failed to establish connection
```

**Nguyên nhân:** 
- Không có internet
- Server đang down
- VPN/Firewall chặn

**Giải pháp:** Kiểm tra kết nối mạng

---

## ⏰ Phần 7: Tự Động Hóa (Chạy Hàng Ngày)

### Tạo Batch File

File `run_daily.bat` đã được tạo sẵn. Nó sẽ:
1. Chạy `fetch_data.py` để lấy dữ liệu mới
2. Chạy `compare_data.py` để so sánh
3. Lưu log vào file

### Lên Lịch với Task Scheduler (Windows)

1. **Mở Task Scheduler:**
   - Nhấn `Win + R`
   - Gõ `taskschd.msc`
   - Enter

2. **Tạo Task mới:**
   - Click "Create Basic Task"
   - Name: "Fetch Clone List Daily"
   - Trigger: Daily, chọn giờ (ví dụ: 9:00 AM)
   - Action: "Start a program"
   - Program: Duyệt đến file `run_daily.bat`

3. **Kiểm tra:**
   - Click chuột phải vào task → "Run"
   - Xem file log để kiểm tra kết quả

---

## 🎓 Phần 8: Kiến Thức Nâng Cao

### 1. Xử lý phân trang
API này dùng DataTables pagination:
- `start`: Vị trí bắt đầu (0, 10, 20, ...)
- `length`: Số lượng records mỗi trang (10, 50, 100)
- `recordsTotal`: Tổng số records

Script tự động lặp cho đến khi lấy hết dữ liệu.

### 2. Tối ưu hóa
- Tăng `length=100` để giảm số request
- Thêm retry logic khi network error
- Cache cookie để tránh phải lấy lại thường xuyên

### 3. Bảo mật
- Không commit file `config.py` lên Git
- Dùng environment variables cho cookie
- Mã hóa cookie khi lưu trữ

---

## 📚 Tài Liệu Tham Khảo

- [Python Requests Documentation](https://requests.readthedocs.io/)
- [HTTP Cookies - MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- [DataTables API](https://datatables.net/manual/server-side)

---

## ❓ Câu Hỏi Thường Gặp

**Q: Cookie có thời hạn bao lâu?**
A: Tùy server, thường từ vài giờ đến vài ngày. Khi script báo lỗi 401, bạn cần lấy cookie mới.

**Q: Có cách nào tự động đăng nhập không?**
A: Có, dùng Selenium hoặc Puppeteer để tự động hóa việc đăng nhập. Tôi sẽ hướng dẫn ở bài nâng cao.

**Q: API này có rate limit không?**
A: Chưa rõ. Nếu bị chặn, thêm `time.sleep()` giữa các request.

**Q: Làm sao biết cookie đã hết hạn?**
A: Script sẽ báo lỗi 401 hoặc redirect về trang login.

---

## 🎉 Kết Luận

Bạn đã học được:
- ✅ Cách cookie authentication hoạt động
- ✅ Lấy cookie từ trình duyệt
- ✅ Gọi API với Python
- ✅ Xử lý phân trang
- ✅ So sánh dữ liệu JSON
- ✅ Tự động hóa với Task Scheduler

**Bước tiếp theo:**
1. Thực hành với API này
2. Thử với các trang web khác
3. Học Selenium để tự động đăng nhập
4. Tích hợp vào các dự án thực tế

**Chúc bạn học tốt! 🚀**
