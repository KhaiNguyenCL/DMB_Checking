# 📚 API Scraping Learning Project

## 🎯 Chào mừng!

Đây là bộ tài liệu học tập hoàn chỉnh về cách **lấy dữ liệu từ trang web có đăng nhập** (Cookie Authentication).

---

## 📖 Bắt Đầu Từ Đâu?

### 🚀 Nếu bạn muốn bắt đầu NGAY (5 phút):
→ Đọc [QUICKSTART.md](QUICKSTART.md)

### 🤖 Nếu bạn muốn LẤY COOKIE TỰ ĐỘNG:
→ Đọc [AUTO_COOKIE.md](AUTO_COOKIE.md) ⭐ MỚI!

### 📚 Nếu bạn muốn hiểu CHI TIẾT:
→ Đọc [README.md](README.md)

### 🖼️ Nếu bạn thích học bằng HÌNH ẢNH:
→ Đọc [VISUAL_GUIDE.md](VISUAL_GUIDE.md)

### 🎓 Nếu bạn muốn THỰC HÀNH:
→ Làm bài tập trong [EXERCISES.md](EXERCISES.md)

---

## 📁 Cấu Trúc Dự Án

```
learning_api_scraping/
│
├── 📘 INDEX.md                    ← Bạn đang ở đây
├── 📘 QUICKSTART.md               ← Bắt đầu nhanh (5 phút)
├── 📘 README.md                   ← Hướng dẫn chi tiết đầy đủ
├── 📘 VISUAL_GUIDE.md             ← Hướng dẫn có hình ảnh
├── 📘 AUTO_COOKIE.md              ← Lấy cookie tự động ⭐ MỚI!
├── 📘 EXERCISES.md                ← Bài tập thực hành
├── 📘 REQUIREMENTS.md             ← Hướng dẫn cài đặt
│
├── 🐍 config.py                   ← Cấu hình (cookie, API URL)
├── 🐍 config_auto.py              ← Cấu hình auto login ⭐ MỚI!
├── 🐍 fetch_data.py               ← Script lấy dữ liệu
├── 🐍 compare_data.py             ← Script so sánh dữ liệu
├── 🐍 auto_login_selenium.py      ← Auto login với Selenium ⭐ MỚI!
├── 🐍 extract_browser_cookie.py   ← Extract cookie từ browser ⭐ MỚI!
├── 🐍 login_with_requests.py      ← Login với POST request ⭐ MỚI!
│
├── 📦 run_daily.bat               ← Chạy tự động (cookie thủ công)
├── 📦 run_auto.bat                ← Chạy tự động (auto cookie) ⭐ MỚI!
├── 📦 requirements.txt            ← Python dependencies ⭐ MỚI!
├── 🔒 .gitignore                  ← Bảo vệ cookie
│
├── 📂 data/                       ← Thư mục chứa dữ liệu
│   ├── sample_data.json           ← Dữ liệu mẫu (ví dụ)
│   ├── clone_list_sample.json     ← Dữ liệu để so sánh
│   └── clone_list_latest.json     ← Dữ liệu mới nhất
│
└── 📂 logs/                       ← Thư mục log
    └── run_history.log            ← Lịch sử chạy
```

---

## 🎯 Bạn Sẽ Học Được Gì?

✅ **Cookie Authentication** - Cách hoạt động và ứng dụng  
✅ **Python Requests** - Gọi API với authentication  
✅ **Pagination** - Xử lý phân trang tự động  
✅ **JSON Processing** - So sánh và phân tích dữ liệu  
✅ **Task Automation** - Tự động hóa với Task Scheduler  
✅ **Error Handling** - Xử lý lỗi thường gặp  

---

## 🚀 Quy Trình Học Tập Đề Xuất

### Ngày 1: Làm quen cơ bản
1. Đọc [QUICKSTART.md](QUICKSTART.md)
2. Cài đặt Python và requests
3. Lấy cookie và cấu hình
4. Chạy thử `fetch_data.py`

### Ngày 2: Hiểu sâu hơn
1. Đọc [README.md](README.md)
2. Đọc code trong `fetch_data.py` và `compare_data.py`
3. Hiểu cách cookie authentication hoạt động
4. Hiểu cách xử lý phân trang

### Ngày 3: Thực hành
1. Làm bài tập 1-3 trong [EXERCISES.md](EXERCISES.md)
2. Thử nghiệm với các tham số khác nhau
3. Xử lý các lỗi thường gặp

### Ngày 4: Tự động hóa
1. Làm bài tập 4-5 trong [EXERCISES.md](EXERCISES.md)
2. Tạo Task Scheduler task
3. Test và kiểm tra log

### Ngày 5: Nâng cao
1. Làm bài tập 6 (nâng cao)
2. Thêm tính năng mới
3. Áp dụng vào dự án thực tế

---

## 📋 Checklist Tổng Thể

### ☑️ Chuẩn Bị
- [ ] Cài Python
- [ ] Cài thư viện requests
- [ ] Có tài khoản đăng nhập

### ☑️ Thiết Lập
- [ ] Lấy cookie từ trình duyệt
- [ ] Cấu hình `config.py`
- [ ] Chạy thử `fetch_data.py`

### ☑️ Sử Dụng
- [ ] Tạo file sample
- [ ] Chạy và so sánh dữ liệu
- [ ] Hiểu kết quả

### ☑️ Tự Động Hóa
- [ ] Tạo Task Scheduler task
- [ ] Test chạy tự động
- [ ] Kiểm tra log

### ☑️ Nâng Cao
- [ ] Hoàn thành ít nhất 1 bài tập nâng cao
- [ ] Áp dụng vào dự án thực tế

---

## 🆘 Cần Giúp Đỡ?

### Gặp lỗi?
→ Xem phần "Xử Lý Lỗi" trong [README.md](README.md#xử-lý-lỗi-thường-gặp)

### Không hiểu cách lấy cookie?
→ Xem hình ảnh trong [VISUAL_GUIDE.md](VISUAL_GUIDE.md#cách-lấy-cookie-từ-chrome)

### Muốn thực hành?
→ Làm bài tập trong [EXERCISES.md](EXERCISES.md)

### Cần bắt đầu nhanh?
→ Đọc [QUICKSTART.md](QUICKSTART.md)

---

## 🎯 Mục Tiêu Cuối Cùng

Sau khi hoàn thành khóa học này, bạn sẽ:

✅ Hiểu cách cookie authentication hoạt động  
✅ Tự tin gọi API với Python  
✅ Xử lý được phân trang và lỗi  
✅ Tự động hóa việc lấy dữ liệu hàng ngày  
✅ Áp dụng được vào các dự án thực tế  

---

## 📞 Liên Hệ & Đóng Góp

Nếu bạn:
- Tìm thấy lỗi trong tài liệu
- Có ý tưởng cải thiện
- Muốn thêm tính năng mới

Hãy tạo issue hoặc pull request!

---

## 📜 License

Tài liệu này được tạo ra cho mục đích học tập.  
Bạn có thể tự do sử dụng và chia sẻ.

---

**Chúc bạn học tốt! 🚀**

Bắt đầu ngay với [QUICKSTART.md](QUICKSTART.md) →
