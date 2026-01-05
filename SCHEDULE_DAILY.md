# ⏰ Lên Lịch Chạy Tự Động Hàng Ngày

## 🎯 Mục Tiêu
Tự động chạy script mỗi ngày để:
- Lấy cookie mới (tự động đăng nhập)
- Fetch dữ liệu từ API
- So sánh với dữ liệu ngày hôm trước
- Lưu log

---

## 📋 Chuẩn Bị

### 1. Kiểm tra batch file đã sẵn sàng

File `run_auto.bat` đã được tạo sẵn và sẽ chạy tất cả:
- ✅ Auto login (lấy cookie)
- ✅ Fetch data
- ✅ Compare data
- ✅ Lưu log

### 2. Test batch file

Trước khi lên lịch, hãy test:

```powershell
.\run_auto.bat
```

Nếu chạy thành công → Tiếp tục bước tiếp theo!

---

## 🔧 Cách 1: Task Scheduler (Windows) - Khuyên Dùng

### Bước 1: Mở Task Scheduler

1. Nhấn `Win + R`
2. Gõ: `taskschd.msc`
3. Nhấn Enter

### Bước 2: Tạo Task Mới

1. Click **"Create Basic Task..."** (bên phải)
2. Hoặc **"Create Task..."** (nâng cao hơn)

### Bước 3: Đặt Tên và Mô Tả

- **Name:** `Auto Fetch Clone List Daily`
- **Description:** `Tự động lấy dữ liệu từ API mỗi ngày`
- Click **Next**

### Bước 4: Chọn Trigger (Khi Nào Chạy)

1. Chọn **"Daily"**
2. Click **Next**
3. Chọn thời gian (ví dụ: `09:00 AM`)
4. Chọn ngày bắt đầu (hôm nay)
5. Click **Next**

### Bước 5: Chọn Action (Làm Gì)

1. Chọn **"Start a program"**
2. Click **Next**

### Bước 6: Cấu Hình Program

- **Program/script:** 
  ```
  E:\Script\learning_api_scraping\run_auto.bat
  ```

- **Start in (optional):**
  ```
  E:\Script\learning_api_scraping
  ```

- Click **Next**

### Bước 7: Hoàn Tất

1. Review thông tin
2. Tick **"Open the Properties dialog..."** (để cấu hình thêm)
3. Click **Finish**

### Bước 8: Cấu Hình Nâng Cao (Quan Trọng!)

Trong Properties dialog:

#### Tab "General":
- ✅ Tick **"Run whether user is logged on or not"**
- ✅ Tick **"Run with highest privileges"**

#### Tab "Conditions":
- ❌ Bỏ tick **"Start the task only if the computer is on AC power"**
- ✅ Tick **"Wake the computer to run this task"** (nếu muốn)

#### Tab "Settings":
- ✅ Tick **"Allow task to be run on demand"**
- ✅ Tick **"Run task as soon as possible after a scheduled start is missed"**
- Chọn **"Stop the existing instance"** nếu task đang chạy

Click **OK** để lưu.

### Bước 9: Test Task

1. Tìm task vừa tạo trong danh sách
2. Click chuột phải → **"Run"**
3. Kiểm tra:
   - File `data\clone_list_latest.json` có cập nhật không
   - File `logs\run_history.log` có ghi log không

---

## 🔧 Cách 2: Dùng PowerShell Script

Tạo file `schedule_task.ps1`:

```powershell
# Tạo Scheduled Task bằng PowerShell

$taskName = "Auto Fetch Clone List Daily"
$scriptPath = "E:\Script\learning_api_scraping\run_auto.bat"
$workingDir = "E:\Script\learning_api_scraping"

# Tạo action
$action = New-ScheduledTaskAction -Execute $scriptPath -WorkingDirectory $workingDir

# Tạo trigger (mỗi ngày lúc 9:00 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM

# Tạo settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Đăng ký task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Tự động lấy dữ liệu từ API mỗi ngày"

Write-Host "✅ Đã tạo task thành công!"
Write-Host "Task sẽ chạy mỗi ngày lúc 9:00 AM"
```

Chạy PowerShell as Administrator:
```powershell
.\schedule_task.ps1
```

---

## 📊 Kiểm Tra Task Đang Chạy

### Xem lịch sử chạy:

1. Mở Task Scheduler
2. Tìm task của bạn
3. Click vào tab **"History"** (bên dưới)

### Xem log file:

```powershell
# Xem log
cat logs\run_history.log

# Xem log realtime
Get-Content logs\run_history.log -Wait -Tail 10
```

---

## 🔔 Nhận Thông Báo (Tùy Chọn)

### Gửi email khi có thay đổi:

Thêm vào cuối file `run_auto.bat`:

```batch
REM Nếu có thay đổi, gửi email
python send_email_notification.py
```

Tạo file `send_email_notification.py`:

```python
import smtplib
from email.mime.text import MIMEText
import json

# Đọc kết quả so sánh
with open('data/clone_list_latest.json') as f:
    latest = json.load(f)

with open('data/clone_list_sample.json') as f:
    sample = json.load(f)

# Nếu có thay đổi
if latest['data'] != sample['data']:
    # Gửi email
    msg = MIMEText(f"Phát hiện thay đổi dữ liệu!\nThời gian: {latest['fetch_time']}")
    msg['Subject'] = '⚠️ Cảnh báo: Dữ liệu thay đổi'
    msg['From'] = 'your_email@gmail.com'
    msg['To'] = 'your_email@gmail.com'
    
    # Gửi qua Gmail
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('your_email@gmail.com', 'your_app_password')
        smtp.send_message(msg)
```

---

## 🐛 Troubleshooting

### Task không chạy:

1. **Kiểm tra Last Run Result:**
   - `0x0` = Thành công
   - `0x1` = Lỗi
   
2. **Kiểm tra quyền:**
   - Task phải chạy với "highest privileges"
   
3. **Kiểm tra đường dẫn:**
   - Đảm bảo đường dẫn tuyệt đối đúng
   
4. **Test thủ công:**
   - Click chuột phải → Run
   - Xem lỗi gì

### Cookie hết hạn:

- Script sẽ tự động lấy cookie mới mỗi ngày
- Nếu vẫn lỗi, kiểm tra `config_auto.py`

---

## 📝 Checklist

- [ ] Test `run_auto.bat` chạy thành công
- [ ] Tạo Scheduled Task
- [ ] Cấu hình trigger (Daily, 9:00 AM)
- [ ] Cấu hình settings (Run with highest privileges)
- [ ] Test task bằng cách "Run" thủ công
- [ ] Kiểm tra log file
- [ ] Đợi ngày mai để xem task tự chạy

---

## 🎉 Hoàn Thành!

Bây giờ mỗi ngày lúc 9:00 AM, hệ thống sẽ tự động:

1. ✅ Mở Chrome (ẩn)
2. ✅ Đăng nhập tự động
3. ✅ Lấy cookie mới
4. ✅ Fetch 1204 records từ API
5. ✅ So sánh với dữ liệu ngày hôm trước
6. ✅ Lưu log
7. ✅ Đóng Chrome

**Hoàn toàn tự động, không cần thao tác gì!** 🚀

---

## 📚 Tham Khảo

- [Task Scheduler Documentation](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)
- [PowerShell Scheduled Tasks](https://docs.microsoft.com/en-us/powershell/module/scheduledtasks/)
