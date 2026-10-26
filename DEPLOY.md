# DMB Device Monitor — Triển khai trên Linux server bằng Docker

Theo dõi màn hình DMB qua API YouFrame, lưu lịch sử vào PostgreSQL, cảnh báo
Bitrix24 khi thiết bị rớt, và xem dữ liệu bằng Grafana.

## Kiến trúc

```
                   ┌──────────────────────────────────┐
                   │  34.64.189.31/api/cloneList      │
                   │  (public, không cần đăng nhập)   │
                   └───────────────┬──────────────────┘
                                   │ 1 request / 5 phút
                                   ▼
  ┌────────────────┐      ┌──────────────────┐      ┌──────────────────┐
  │   Bitrix24     │◄─────│  dmb-monitor     │─────►│  dmb-postgres    │
  │   chat 911     │      │  (python)        │      │  devices         │
  └────────────────┘      └──────────────────┘      │  status_events   │
                                                     │  fetch_runs      │
                          ┌──────────────────┐      └────────┬─────────┘
                          │  dmb-grafana     │◄──────────────┘
                          │  :3000           │
                          └──────────────────┘
```

## Yêu cầu

- Linux server (bất kỳ distro có Docker)
- Docker Engine + Docker Compose v2
- Server phải tiếp cận được `34.64.189.31` (HTTPS) và `erp.dnsvn.com`

Không cần Chrome, chromedriver, Selenium hay X server — đã bỏ hoàn toàn.

## Cài đặt

```bash
git clone <repo> dmb-monitor && cd dmb-monitor

cp .env.example .env
nano .env            # xem phần "Cấu hình bắt buộc" bên dưới

docker compose up -d --build
docker compose logs -f monitor
```

Log chạy đúng sẽ trông như:

```
DMB DEVICE MONITOR
API       : https://34.64.189.31/api/cloneList
Region    : Vietnam
Chu ky    : 300s
Quiet     : 22:00 - 05:00 (Asia/Ho_Chi_Minh)
Schema da san sang
DB dang rong - day la lan chay dau tien
Run #1 | API 1786 record | trong pham vi 533 | loai 9 | online 508 | offline 16 | event cho gui 16
Lan chay dau tien: danh dau 16 event la da xu ly, khong gui
```

## Cấu hình bắt buộc trong `.env`

| Biến | Ghi chú |
|---|---|
| `POSTGRES_PASSWORD` | Bắt buộc, compose sẽ từ chối chạy nếu để trống. `openssl rand -base64 24` |
| `GRAFANA_ADMIN_PASSWORD` | Bắt buộc, tương tự |
| `BITRIX_WEBHOOK_URL` | **Tạo token mới** — token cũ đã bị commit lên git, xem phần Bảo mật |
| `BITRIX_CHAT_ID` | `911` (workgroup DMD Checking Notification) |

Các biến khác đều có giá trị mặc định hợp lý, xem chú thích trong `.env.example`.

## Kiểm tra sau khi chạy

```bash
# Monitor có fetch được không
docker compose logs monitor | grep "Run #"

# Thiết bị đang offline
docker compose exec postgres psql -U dmb -d dmb -c "SELECT * FROM v_offline_now;"

# Thiết bị hay rớt 7 ngày qua
docker compose exec postgres psql -U dmb -d dmb -c "SELECT * FROM v_flapping_7d LIMIT 20;"

# Test gửi Bitrix (gửi tin thật vào chat, cẩn thận)
docker compose exec monitor python -c "from app import notifier; print(notifier.send_test())"
```

Grafana: `http://<server-ip>:3000`, đăng nhập bằng `GRAFANA_ADMIN_USER` /
`GRAFANA_ADMIN_PASSWORD`. Dashboard **DMB / DMB Device Monitor** đã được
provision sẵn, datasource cũng vậy — không cần cấu hình tay.

## Vận hành

| Việc | Lệnh |
|---|---|
| Xem log | `docker compose logs -f monitor` |
| Restart monitor | `docker compose restart monitor` |
| Dừng toàn bộ | `docker compose down` |
| Dừng và **xoá sạch dữ liệu** | `docker compose down -v` |
| Cập nhật code | `git pull && docker compose up -d --build` |
| Sửa blacklist | sửa `data/Exception_list.txt`, không cần restart (đọc lại mỗi chu trình) |
| Đổi cấu hình | sửa `.env` rồi `docker compose up -d` |

Cả 3 service đều `restart: unless-stopped` nên tự lên lại sau khi reboot server.
Không cần cron, systemd unit hay Task Scheduler — monitor tự loop.

### Backup

Dữ liệu nằm trong docker volume `checkdmb_pgdata`:

```bash
# Dump
docker compose exec -T postgres pg_dump -U dmb dmb | gzip > dmb-$(date +%F).sql.gz

# Restore
gunzip -c dmb-2026-10-26.sql.gz | docker compose exec -T postgres psql -U dmb -d dmb
```

Dung lượng rất nhỏ (~1 MB/ngày) vì chỉ lưu trạng thái hiện tại + các lần chuyển
trạng thái, không lưu snapshot toàn bộ mỗi 5 phút.

## Mô hình dữ liệu

| Bảng | Nội dung | Tốc độ tăng |
|---|---|---|
| `devices` | Trạng thái hiện tại, 1 dòng / thiết bị, UPSERT mỗi chu trình | cố định ~524 dòng |
| `status_events` | Chỉ ghi khi status đổi On↔Off | vài trăm dòng/ngày |
| `fetch_runs` | Metadata mỗi lần fetch (dùng cho timeseries + debug) | 288 dòng/ngày |

Việc phát hiện chuyển trạng thái do **trigger trong PostgreSQL** đảm nhiệm
(`devices_log_status_trg`), không phải Python — nên không thể bỏ sót event kể cả
khi process chết giữa chu trình.

Hai view tiện dụng: `v_offline_now`, `v_flapping_7d`.

> Lưu ý về `status_changed_at`: đây là lúc **monitor ghi nhận** thay đổi, không
> phải lúc thiết bị thật sự rớt. Thời gian offline thực tế tính từ `last_seen`
> (view `v_offline_now` và dashboard đã làm đúng việc này).

## Hành vi notification

| Tình huống | Hành vi |
|---|---|
| Thiết bị On → Off | Gửi Bitrix ngay chu trình kế tiếp |
| Thiết bị lần đầu thấy đã Off | Gửi, có ghi chú `(lan dau thay)` |
| Thiết bị vẫn Off nhiều chu trình | **Không** gửi lại |
| Chạy lần đầu trên DB rỗng | Không gửi (đổi `DMB_NOTIFY_ON_FIRST_RUN=true` nếu muốn) |
| Trong giờ 22:00–05:00 | Ghi DB bình thường, không gửi; sẽ xuất hiện trong tổng hợp đầu ngày |
| 08:00 mỗi ngày | Gửi tổng hợp toàn bộ thiết bị đang Off |
| Gửi Bitrix thất bại | Giữ `notified=false`, tự thử lại chu trình sau (trong 6 giờ) |
| Fetch lỗi 3 lần liên tiếp | Gửi cảnh báo "monitor không lấy được dữ liệu" |

Restart container **không** làm gửi lại thông báo cũ, vì state nằm trong DB chứ
không phải file bị xoá lúc khởi động như bản cũ.

## Bảo mật — việc cần làm

1. **Revoke webhook Bitrix cũ.** Webhook dùng trước đây được hardcode trong
   `config_bitrix.py`, và file đó **đã được commit lên git** — giá trị vẫn còn
   trong history của các commit trước. Ai đọc được repo là gửi/đọc được Bitrix.
   Vào Bitrix24 → Developer resources → Other → Incoming webhook, **revoke
   webhook cũ**, tạo cái mới và chỉ đặt giá trị vào `.env`.
2. **Không mở port Postgres ra internet.** `docker-compose.yml` mặc định không
   publish 5432. Nếu cần truy cập từ xa thì dùng SSH tunnel.
3. **Chặn Grafana.** Port 3000 đang mở. Đặt sau reverse proxy có TLS, hoặc giới
   hạn bằng firewall / chỉ bind `127.0.0.1` rồi SSH tunnel.
4. **`config_auto.py` không còn được dùng** (API không cần đăng nhập). File này
   chứa mật khẩu dạng plaintext — nên xoá.
5. `.env` nằm trong `.gitignore`. Đừng commit.

## Ghi chú về API nguồn

Hai điều đã kiểm chứng bằng thực nghiệm ngày 2026-10-26, cần biết nếu sau này
API đổi hành vi:

1. **Endpoint không yêu cầu authentication.** `curl` không cookie vẫn trả đủ
   1786 record. Dữ liệu toàn bộ màn hình đang công khai với bất kỳ ai tiếp cận
   được IP — vấn đề phía vendor, nên báo họ.
2. **Không gửi `columns[]` thì server trả toàn bộ record trong 1 request.** Nếu
   gửi đầy đủ params DataTables kèm `order` theo cột không unique (ví dụ cột
   Status), phân trang trở nên không ổn định: đo được **18 record trùng và 18
   record bị mất** trên 1786. Bản cũ (`fetch_data.py`) sort theo cột Status nên
   mỗi lần fetch mất ~1% thiết bị khỏi tầm nhìn.

`app/dmb_api.py` sẽ log WARNING nếu số record nhận được khác `recordsTotal` —
đó là dấu hiệu server đã đổi hành vi và cần xem lại cách gọi.

## So với bản chạy trên Windows

| | Bản cũ | Bản này |
|---|---|---|
| Nền tảng | Windows + Task Scheduler | Linux + Docker |
| Đăng nhập | Selenium mở Chrome | không cần (API public) |
| Số request / chu trình | 18 (phân trang) | 1 |
| Mất dữ liệu do phân trang | ~18/1786 mỗi lần | không |
| Lưu trạng thái | `device_states.json` | PostgreSQL |
| Lịch sử | chỉ file log text | truy vấn được bằng SQL |
| Restart | gửi lại toàn bộ thiết bị Off | không gửi lại |
| Trùng device_id | ghi đè nhau trong dict state | khoá chính, giữ bản đầu |
| Fetch lỗi | im lặng, retry vô hạn | cảnh báo Bitrix sau 3 lần |
| Secret | hardcode trong .py đã commit | biến môi trường trong `.env` |
| Dashboard | không có | Grafana |
