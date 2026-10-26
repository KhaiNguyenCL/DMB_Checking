# Copilot Instructions — DMB Device Monitor

## Project Overview

Dịch vụ monitor màn hình menu (DMB) chạy bằng Docker trên Linux: fetch API
YouFrame mỗi 5 phút, lưu PostgreSQL, cảnh báo Bitrix24, xem bằng Grafana.

Không phải project học tập, không có Selenium, không có cookie auth, không có
email. Nếu bạn thấy tài liệu nào nói về những thứ đó thì nó đã lỗi thời.

## Architecture

```
app/settings.py   → đọc toàn bộ cấu hình từ biến môi trường
app/dmb_api.py    → GET /api/cloneList, parse mảng 14 phần tử thành dict
app/db.py         → psycopg3, UPSERT devices + query event
app/notifier.py   → POST im.message.add lên Bitrix webhook
app/monitor.py    → vòng lặp: fetch → lọc → ghi DB → gửi tin → sleep
sql/001_schema.sql → devices, status_events, fetch_runs + trigger + 2 view
```

Luồng: `monitor.run_cycle()` gọi `dmb_api.fetch_devices()`, lọc theo
`settings.REGIONS` và `data/Exception_list.txt`, rồi `db.sync_devices()`.
Trigger `devices_log_status_trg` trong PostgreSQL tự sinh `status_events` khi
status đổi — **không** tự phát hiện transition trong Python.

## Quy tắc khi sửa code

- **Cấu hình chỉ qua biến môi trường.** Không hardcode URL, token, mật khẩu.
  Thêm biến mới thì phải thêm vào cả `app/settings.py` và `.env.example`.
- **Không gửi params `columns[]` khi gọi API.** Gửi vào sẽ kích hoạt phân trang
  không ổn định và mất ~1% record mỗi lần fetch. Hiện tại 1 request lấy hết 1786.
- **Khoá thiết bị là index 12**, không phải 13 (có bản ghi 2 cột này lệch nhau).
- **Phát hiện chuyển trạng thái để ở DB trigger**, đừng chuyển sang Python.
- **`status_changed_at` là lúc monitor ghi nhận**, không phải lúc thiết bị rớt.
  Muốn tính thời gian offline thực tế thì dùng `last_seen`.
- Thiết bị không còn trong feed thì hạ `is_present`, **không** đổi `status`.
- Fetch lỗi không được phép làm mất dữ liệu đang có trong `devices`.
- Comment và log viết bằng tiếng Việt không dấu, khớp với code hiện có.

## Index của record API

Mỗi record là mảng 14 phần tử:

| idx | nội dung | idx | nội dung |
|---|---|---|---|
| 1 | name | 7 | brand |
| 2 | status (On/Off) | 8 | region |
| 3 | device_type | 9 | model |
| 4 | fw_version | 10 | menu |
| 5 | health | 12 | **device_id (khoá)** |
| 6 | last_seen (giờ local thiết bị) | 13 | device_id phụ, không tin |

## Lệnh hay dùng

```bash
docker compose up -d --build
docker compose logs -f monitor
docker compose exec postgres psql -U dmb -d dmb -c "SELECT * FROM v_offline_now;"
docker compose exec monitor python -c "from app import notifier; print(notifier.send_test())"
```

Chạy một chu trình đơn lẻ để debug:

```bash
docker compose exec -T monitor python - <<'EOF'
from app import db, monitor
monitor.setup_logging()
conn = db.connect()
r = monitor.run_cycle(conn, monitor.load_exception_list(), first_run=False)
print(r["stored"], "thiet bi,", len(r["events"]), "event")
EOF
```
