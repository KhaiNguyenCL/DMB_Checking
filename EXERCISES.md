# 🎯 Bài Tập Thực Hành

## Mục tiêu
Giúp bạn làm quen với việc lấy dữ liệu từ API có authentication.

---

## 📝 Bài 1: Lấy Dữ liệu Cơ Bản

### Yêu cầu:
1. Lấy cookie từ trang web `https://34.64.189.31`
2. Cấu hình file `config.py`
3. Chạy `fetch_data.py` thành công
4. Kiểm tra file `data/clone_list_latest.json`

### Kiểm tra:
- [ ] File JSON có dữ liệu không?
- [ ] Có bao nhiêu records?
- [ ] Thời gian fetch là khi nào?

---

## 📝 Bài 2: So Sánh Dữ Liệu

### Yêu cầu:
1. Copy file latest làm sample
2. Đợi vài phút
3. Chạy lại `fetch_data.py`
4. Chạy `compare_data.py`

### Câu hỏi:
- Có thay đổi gì không?
- Nếu có, thay đổi ở đâu?

---

## 📝 Bài 3: Xử Lý Lỗi

### Thử nghiệm:
1. Xóa cookie trong `config.py` (để trống)
2. Chạy `fetch_data.py`
3. Quan sát lỗi

### Câu hỏi:
- Script báo lỗi gì?
- Làm sao khắc phục?

---

## 📝 Bài 4: Tùy Chỉnh Script

### Thử thay đổi:
1. Mở `config.py`
2. Thay `length: 100` thành `length: 10`
3. Chạy lại `fetch_data.py`

### Quan sát:
- Script chạy nhanh hơn hay chậm hơn?
- Tại sao?

---

## 📝 Bài 5: Tự Động Hóa

### Yêu cầu:
1. Tạo Task Scheduler task
2. Lên lịch chạy mỗi ngày lúc 9:00 AM
3. Kiểm tra log file

### Kiểm tra:
- [ ] Task chạy đúng giờ?
- [ ] Có lỗi gì không?
- [ ] Log file có ghi nhận không?

---

## 🎓 Bài Nâng Cao

### Bài 6: Thêm Tính Năng Mới

Thử thêm các tính năng sau vào script:

1. **Email Notification:**
   - Gửi email khi phát hiện thay đổi
   - Sử dụng `smtplib` của Python

2. **Database Storage:**
   - Lưu dữ liệu vào SQLite
   - So sánh với database thay vì file JSON

3. **Retry Logic:**
   - Tự động retry khi lỗi network
   - Tối đa 3 lần

4. **Better Logging:**
   - Sử dụng module `logging`
   - Lưu log chi tiết hơn

---

## 💡 Gợi Ý

### Bài 1-2:
- Đọc kỹ README.md
- Làm từng bước một
- Không vội vàng

### Bài 3-4:
- Thử nghiệm và quan sát
- Hiểu tại sao lại như vậy
- Ghi chú lại những gì học được

### Bài 5:
- Tham khảo phần "Tự Động Hóa" trong README.md
- Test thử bằng cách "Run" task thủ công trước

### Bài Nâng Cao:
- Google để tìm hướng dẫn
- Tham khảo Python documentation
- Hỏi AI nếu gặp khó khăn

---

## ✅ Checklist Hoàn Thành

- [ ] Bài 1: Lấy dữ liệu thành công
- [ ] Bài 2: So sánh dữ liệu thành công
- [ ] Bài 3: Hiểu cách xử lý lỗi
- [ ] Bài 4: Hiểu về pagination
- [ ] Bài 5: Tự động hóa thành công
- [ ] Bài 6: Hoàn thành ít nhất 1 tính năng nâng cao

**Chúc bạn học tốt! 🚀**
