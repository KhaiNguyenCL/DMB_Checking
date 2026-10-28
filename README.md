# DMB Device Monitor

Theo dõi màn hình menu (digital menu board) Starbucks qua API YouFrame: phát hiện
thiết bị rớt mạng, cảnh báo vào chat Bitrix24, lưu lịch sử vào PostgreSQL và xem
bằng Grafana.

Chạy bằng Docker trên Linux server.

## Chạy nhanh

```bash
cp .env.example .env
nano .env                      # đặt POSTGRES_PASSWORD, GRAFANA_ADMIN_PASSWORD, BITRIX_WEBHOOK_URL

docker compose up -d --build
docker compose logs -f monitor
```

Grafana: `http://<server-ip>:3000` → dashboard **DMB / DMB Device Monitor** đã có sẵn.

Hướng dẫn đầy đủ (cấu hình, vận hành, backup, bảo mật): **[DEPLOY.md](DEPLOY.md)**

## Hoạt động

Mỗi 5 phút:

1. Gọi `https://34.64.189.31/api/cloneList` một request, lấy toàn bộ thiết bị
2. Lọc theo region (mặc định `Vietnam`), bỏ các ID trong `data/Exception_list.txt`
3. UPSERT vào bảng `devices`; trigger PostgreSQL tự ghi `status_events` khi status đổi
4. Thiết bị nào vừa chuyển sang `Off` thì gửi cảnh báo Bitrix24

Thiết bị đã báo rồi thì không báo lại. Chỉ gửi tin trong khung 08:00–18:00 (ngoài
khung vẫn ghi DB đầy đủ). Nếu monitor vừa dừng lâu rồi chạy lại thì không báo
riêng lẻ mà gửi một tin tổng hợp trạng thái.
08:00 mỗi ngày gửi tổng hợp toàn bộ thiết bị đang offline.

## Cấu trúc

```
app/
  settings.py   cấu hình từ biến môi trường
  dmb_api.py    gọi và parse API
  db.py         truy cập PostgreSQL
  notifier.py   gửi Bitrix24
  monitor.py    vòng lặp chính
sql/            schema: devices, status_events, fetch_runs + trigger + view
grafana/        datasource và dashboard provision sẵn
data/           Exception_list.txt (blacklist device ID)
```

## Mô hình dữ liệu

| Bảng | Nội dung | Tăng |
|---|---|---|
| `devices` | trạng thái hiện tại, 1 dòng / thiết bị | cố định |
| `status_events` | chỉ ghi khi status đổi On↔Off | vài trăm dòng/ngày |
| `fetch_runs` | metadata mỗi lần fetch | 288 dòng/ngày |

Khoảng 1 MB/ngày. Xem `v_offline_now` và `v_flapping_7d` để query nhanh.

## Lưu ý về API nguồn

- Endpoint **không yêu cầu authentication** — dữ liệu toàn bộ màn hình đang công
  khai với bất kỳ ai tiếp cận được IP. Vấn đề phía vendor.
- Không gửi params `columns[]` thì server trả hết trong 1 request. Nếu gửi đầy đủ
  params DataTables kèm `order` theo cột không unique thì phân trang mất dữ liệu
  (đo được 18 trùng + 18 mất trên 1786 record).
- `last_seen` là giờ local của thiết bị: Vietnam/Thailand/Cambodia UTC+7,
  Singapore UTC+8.

Chi tiết trong [DEPLOY.md](DEPLOY.md#ghi-chú-về-api-nguồn).
