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
                          │  (khong mo port) │
                          └────────▲─────────┘
                                   │
                          ┌────────┴─────────┐
                          │  dmb-caddy       │  HTTPS + chan IP
                          │  :80 :443        │
                          └──────────────────┘
                                   ▲
                             nguoi xem (browser)
```

## Yêu cầu

- Ubuntu Server 22.04 / 24.04 LTS (hoặc distro khác có Docker)
- Docker Engine + Docker Compose v2
- Server phải tiếp cận được `34.64.189.31` (HTTPS) và `erp.dnsvn.com` (HTTPS)
- Để cài đặt: cần thêm `archive.ubuntu.com`, `download.docker.com`, `github.com`

Không cần Chrome, chromedriver, Selenium hay X server — đã bỏ hoàn toàn.

## Cài đặt từ đầu

Runbook cho VM mới. Làm theo đúng thứ tự; bước 1 là bước dễ bị bỏ qua nhất và
cũng là bước làm toàn bộ phần sau trở nên vô nghĩa nếu bỏ.

### 1. Kiểm tra kết nối ra ngoài trước tiên

Hệ thống này không host gì cho ai — nó chỉ đi lấy dữ liệu và đi gửi tin. Nếu
outbound bị chặn (rất thường gặp với VM đặt ở DMZ) thì không có gì chạy được.

```bash
curl -sk -o /dev/null -w "YouFrame API  : %{http_code}\n" --max-time 15 \
  "https://34.64.189.31/api/cloneList?draw=1&start=0"
curl -s  -o /dev/null -w "Bitrix        : %{http_code}\n" --max-time 15 \
  "https://erp.dnsvn.com/"
curl -s  -o /dev/null -w "Docker repo   : %{http_code}\n" --max-time 15 \
  "https://download.docker.com/linux/ubuntu/gpg"
curl -s  -o /dev/null -w "GitHub        : %{http_code}\n" --max-time 15 \
  "https://github.com/"
```

Hai dòng đầu phải ra `200`. Nếu không thì xin mở firewall trước khi làm tiếp.
Nếu `github.com` bị chặn thì bỏ qua — bước 5 có cách copy code không cần git.

### 2. Thiết lập hệ điều hành

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y open-vm-tools ca-certificates curl git
sudo timedatectl set-timezone Asia/Ho_Chi_Minh
timedatectl          # kiem tra "NTP service: active" va dung mui gio
```

Đồng hồ đúng là điều kiện bắt buộc: khung giờ gửi tin, tổng hợp đầu ngày và
việc tính giờ `last_seen` đều dựa vào nó.

Nếu VM chạy trên VMware, `open-vm-tools` giúp vCenter shutdown đúng cách và
nhìn thấy IP của VM.

### 3. Mount đĩa dữ liệu vào /var/lib/docker

Bỏ bước này thì Docker ghi hết vào đĩa hệ thống, còn đĩa dữ liệu nằm không.
Làm **trước khi** cài Docker để thư mục còn rỗng.

```bash
lsblk                      # xac dinh dia du lieu, thuong la /dev/sdb
sudo mkfs.ext4 /dev/sdb    # CHI chay khi chac chan dia nay con trong
sudo mkdir -p /var/lib/docker

# Dung UUID thay vi /dev/sdb, vi ten device co the doi sau khi reboot
echo "UUID=$(sudo blkid -s UUID -o value /dev/sdb) /var/lib/docker ext4 defaults 0 2" \
  | sudo tee -a /etc/fstab
sudo mount -a
df -h /var/lib/docker      # phai thay dung dung luong cua dia du lieu
```

### 4. Cài Docker Engine

Dùng repo chính thức của Docker, **không** dùng gói `docker.io` của Ubuntu —
gói đó cũ và thiếu plugin Compose v2.

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER && newgrp docker

docker run --rm hello-world
docker info | grep "Docker Root Dir"   # phai la /var/lib/docker tren dia du lieu
```

### 5. Lấy code

```bash
git clone https://github.com/KhaiNguyenCL/DMB_Checking.git ~/dmb && cd ~/dmb
```

Nếu server không ra được GitHub, đóng gói từ máy khác rồi copy qua:

```bash
# tren may co code
git archive --format=tar.gz -o dmb.tar.gz HEAD
scp dmb.tar.gz user@<ip-server>:~/

# tren server
mkdir -p ~/dmb && tar -xzf ~/dmb.tar.gz -C ~/dmb && cd ~/dmb
```

### 6. Cấu hình

```bash
cp .env.example .env
nano .env
```

Bắt buộc điền (xem bảng ở mục dưới). Sinh mật khẩu mạnh **chỉ gồm chữ và số**:

```bash
openssl rand -base64 32 | tr -dc 'A-Za-z0-9' | head -c 32; echo
```

Dùng `tr -dc 'A-Za-z0-9'` để loại các ký tự như `/`, `+`, `$`, `@`. Code đã xử
lý được mật khẩu có ký tự đặc biệt, nhưng `$` vẫn có thể bị Docker Compose hoặc
Grafana provisioning hiểu thành biến môi trường. Chữ và số thì không bao giờ
gặp vấn đề ở bất kỳ lớp nào.

### 7. Sinh cert cho HTTPS

Caddy dùng cert tự ký có IP (và hostname nếu có) nằm trong SAN. Truyền đúng địa
chỉ mà người xem sẽ mở trên browser:

```bash
./caddy/make-cert.sh 10.0.0.10                      # chi IP
./caddy/make-cert.sh 10.0.0.10 dmb.dnsvn.local      # IP + hostname noi bo
```

Cert có hiệu lực 10 năm, nằm trong `caddy/certs/` và **không** được commit lên git.

Không dùng `tls internal` của Caddy vì cert tự động cho địa chỉ IP có nhiều ca
lỗi đã biết (client không đặt IP vào SNI nên phải thêm `default_sni`, và có báo
cáo handshake thất bại). Cert sinh sẵn thì xác định hơn.

Browser sẽ cảnh báo cert tự ký một lần — bình thường với hệ thống nội bộ. Muốn
hết cảnh báo thì cài `caddy/certs/cert.pem` vào trust store của máy client, hoặc
thay bằng cert do CA nội bộ của công ty phát hành.

### 8. Chạy

```bash
docker compose up -d --build
docker compose logs -f monitor
```

Lần đầu build mất vài phút. Log chạy đúng sẽ trông như:

```
DMB DEVICE MONITOR
API       : https://34.64.189.31/api/cloneList
Region    : Vietnam
Chu ky    : 300s
Gui tin   : 08:00:00 - 18:00:00 (Asia/Ho_Chi_Minh)
Schema da san sang
DB dang rong - lan chay dau tien, se dong bo lai
Run #1 | API 1799 record | trong pham vi 533 | loai 9 | online 495 | offline 29 | event cho gui 29
Dong bo lai (lan chay dau tien): khong bao rieng le 29 event, gui tong hop trang thai
```

Dòng cuối là điều cần thấy: DB mới **không** làm nó gửi 29 tin riêng lẻ, chỉ một
tin tổng hợp trạng thái.

### 9. Firewall và quyền xem Grafana

Hai việc riêng biệt: **ai vào được** (mạng) và **vào rồi làm được gì** (Grafana).

**Ai vào được.** Grafana không publish port nào — chỉ Caddy publish 80/443, và
Caddy chặn theo `GRAFANA_ALLOWED_IPS` trong `.env`:

```
GRAFANA_ALLOWED_IPS=10.10.0.0/24 10.20.5.17/32
```

Chặn ở Caddy chứ không ở ufw, vì **port do Docker publish đi vòng qua ufw** —
đây là cái bẫy hay gặp. ufw chỉ còn việc bảo vệ SSH:

```bash
sudo ufw allow OpenSSH
sudo ufw enable
```

Ai bị chặn thì tra IP mà Caddy thực sự thấy:

```bash
docker compose logs caddy | grep '"status": 403'
```

Lưu ý khi tự test trên server: `curl` từ chính server sẽ hiện IP của Docker
gateway (`172.x`) chứ không phải IP thật, nên dễ bị 403. Hãy test từ máy client.

**Vào rồi làm được gì.** Tạo cho mỗi người một tài khoản role **Viewer** trong
Grafana (Administration → Users). Đã kiểm chứng bằng thực nghiệm, Viewer:

- xem được mọi dashboard (HTTP 200)
- **không** lưu được dashboard (HTTP 403)
- **không** thêm sửa được datasource
- bị ẩn Explore trên UI, **nhưng vẫn gọi được API `/api/ds/query` với SQL tự do**

Điểm cuối là chỗ dễ hiểu sai và quan trọng nhất. Grafana cho phép Viewer
"query data sources directly", và nó chuyển nguyên SQL xuống Postgres mà không
kiểm duyệt. Nếu datasource dùng user chủ sở hữu database thì **một Viewer có thể
`DROP TABLE`** — đã thử và tạo được bảng thật.

Vì vậy datasource **phải** dùng role chỉ đọc `grafana_ro`, do monitor tự tạo lúc
khởi động (`db.ensure_readonly_role`): chỉ có `SELECT`, bị thu hồi `CREATE` trên
schema public. Sau khi đổi, Viewer vẫn đọc được dữ liệu nhưng `CREATE TABLE` và
`DELETE` đều trả `permission denied`.

Đặt `GRAFANA_DB_PASSWORD` trong `.env`; không có nó thì compose từ chối chạy.

Tài khoản `admin` chỉ bạn giữ. `GF_USERS_VIEWERS_CAN_EDIT` đã khoá `false`.

Muốn người xem không phải đăng nhập gì cả thì đặt `GRAFANA_ANONYMOUS=true`:
ai trong dải IP cho phép mở link là thấy dashboard với quyền Viewer, không phải
quản lý mật khẩu cho từng người. Chỉ nên bật khi đã chặn IP.

### 10. Backup tự động

```bash
mkdir -p ~/dmb-backup
( crontab -l 2>/dev/null; echo '0 2 * * * cd ~/dmb && /usr/bin/docker compose exec -T postgres pg_dump -U dmb dmb | gzip > ~/dmb-backup/dmb-$(date +\%F).sql.gz && find ~/dmb-backup -name "dmb-*.sql.gz" -mtime +30 -delete' ) | crontab -
crontab -l
```

Dump chỉ vài MB, giữ 30 ngày.

### 11. Hoàn tất

```bash
sudo reboot              # kiem tra moi thu tu len lai
# sau khi reboot:
docker compose ps        # ca 3 container phai Up
df -h /var/lib/docker    # dia du lieu van mount dung
```

Nhớ **tháo ISO** khỏi CD/DVD của VM trong vCenter, nếu không có lần nó sẽ boot
lại vào installer.

Không cần cron, systemd unit hay Task Scheduler cho chính monitor — cả 3 service
đều `restart: unless-stopped` nên tự lên lại sau reboot.

## Cấu hình bắt buộc trong `.env`

| Biến | Ghi chú |
|---|---|
| `POSTGRES_PASSWORD` | Bắt buộc, compose từ chối chạy nếu trống. Chỉ dùng chữ và số |
| `GRAFANA_ADMIN_PASSWORD` | Bắt buộc, tương tự. **Chỉ áp dụng lúc khởi tạo lần đầu** — xem mục Sự cố |
| `BITRIX_WEBHOOK_URL` | **Tạo webhook mới** — cái cũ đã bị commit lên git, xem phần Bảo mật |
| `GRAFANA_ALLOWED_IPS` | Bắt buộc, dải IP được phép xem Grafana, cách nhau bằng dấu cách |
| `GRAFANA_ROOT_URL` | URL thật người dùng mở, ví dụ `https://10.0.0.10/` |
| `GRAFANA_DB_PASSWORD` | Bắt buộc. Mật khẩu role chỉ đọc `grafana_ro` mà Grafana dùng |
| `BITRIX_CHAT_ID` | `911` (workgroup DMD Checking Notification), hoặc dùng `BITRIX_DIALOG_ID` |

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

Grafana: `https://<server-ip>/` (qua Caddy), đăng nhập bằng `GRAFANA_ADMIN_USER` /
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

## Bitrix24: inbound webhook và quyền

1. **Developer resources → Other → Inbound webhook** (bản cũ ghi "Incoming webhook").
   Không phải *Outbound webhook* — cái đó là Bitrix gọi ra ngoài.
2. Quyền cần tick: **chỉ `im`** (Instant messaging / Chat và cuộc gọi). Code chỉ
   gọi duy nhất `im.message.add`, không cần `crm`, `user` hay gì khác.
3. **Webhook chạy dưới danh nghĩa user đã tạo ra nó**, và user đó phải là thành
   viên của chat đích. Nếu không sẽ nhận `403 INVALID_CREDENTIALS` dù scope đã
   đúng — đây là lỗi hay gặp nhất và thông báo lỗi không gợi ý gì về nguyên nhân.
   Nên tạo webhook bằng một account dịch vụ đã được thêm vào workgroup, để
   notification không chết khi người tạo rời công ty.
4. Không cần dựng lại bot. `BOT_ID` / `BOT_CLIENT_ID` / `BOT_HANDLER_URL` trong
   config cũ thuộc Bot API (`imbot`, cần server nhận handler) và không còn dùng.

### Chọn nơi nhận tin

`im.message.add` nhận `DIALOG_ID` theo ba dạng, cấu hình qua `BITRIX_DIALOG_ID`:

| Giá trị | Ý nghĩa |
|---|---|
| `chat911` | chat thường, hoặc chat của workgroup |
| `sg169` | chat của group / project (`sg` + group ID) |
| `42` | chat riêng 1-1 với user ID 42 |

`BITRIX_CHAT_ID=911` (dạng cũ) vẫn hoạt động, số trần được hiểu là `chat911`.
Nếu đặt cả hai thì `BITRIX_DIALOG_ID` thắng. Chữ hoa và khoảng trắng thừa được
chuẩn hoá; giá trị không đúng định dạng thì giữ nguyên để Bitrix báo lỗi rõ ràng
thay vì âm thầm gửi sang dialog khác.

Nếu `chat911` báo không tìm thấy dialog thì thử `BITRIX_DIALOG_ID=sg169` —
workgroup DMD Checking Notification có group ID 169.

Dialog đang dùng được in trong banner lúc khởi động:

```
Bitrix    : bat (dialog chat911)
```

### Sửa dashboard

`GRAFANA_ALLOW_UI_UPDATES` trong `.env` quyết định cách sửa:

| Giá trị | Admin sửa trên UI | Viewer | Nguồn sự thật |
|---|---|---|---|
| `true` (mặc định) | được | vẫn không, do role | DB của Grafana |
| `false` | **không**, hiện "cannot be saved from the Grafana UI" | không | file JSON trong git |

Để `true` thì admin sửa thoải mái; Viewer vẫn bị role chặn nên yêu cầu "không ai
đổi được gì" vẫn giữ nguyên.

Để `false` thì dashboard được quản lý như code — kể cả admin cũng không lưu được
từ UI. Lúc đó muốn sửa thì làm thế này:

1. Sửa trên UI cho vừa ý, rồi **Export → View JSON → Copy**
2. Dán vào `grafana/dashboards/dmb-overview.json`
3. Grafana tự nạp lại trong khoảng 10 giây khi nội dung file đổi

Lưu ý khi để `true`: thay đổi trên UI nằm trong volume `grafana-data`, còn file
JSON trong git sẽ cũ dần. Nếu xoá volume đó (cách sửa lỗi mật khẩu admin ở mục
Sự cố) thì **mất các thay đổi UI**, Grafana dựng lại từ file. Nên sau khi sửa
xong trên UI, vẫn nên export JSON về file và commit.

## Hành vi notification

| Tình huống | Hành vi |
|---|---|
| Thiết bị On → Off, trong khung giờ gửi | Gửi Bitrix ngay chu trình kế tiếp |
| Thiết bị lần đầu thấy đã Off | Gửi, có ghi chú `lần đầu ghi nhận` |
| Thiết bị vẫn Off nhiều chu trình | **Không** gửi lại |
| **Ngoài khung giờ gửi** (mặc định ngoài 08:00–18:00) | Ghi DB bình thường, không gửi; thiết bị còn Off sẽ nằm trong tổng hợp đầu ngày |
| **Vừa chạy lại sau khi dừng > 15 phút** | **Không** báo riêng lẻ. Gửi một tin tổng hợp trạng thái hiện tại |
| Chạy lần đầu trên DB rỗng | Như trên: một tin tổng hợp, không báo riêng lẻ |
| 08:00 mỗi ngày | Gửi tổng hợp toàn bộ thiết bị đang Off |
| Gửi Bitrix thất bại | Giữ `notified=false`, tự thử lại chu trình sau (trong 6 giờ) |
| Fetch lỗi 3 lần liên tiếp | Gửi cảnh báo "monitor không lấy được dữ liệu" |
| Quá 30 thiết bị trong một tin | Liệt kê 30, phần còn lại gộp thành "… và N thiết bị khác" |

### Khung giờ gửi

`DMB_NOTIFY_FROM` / `DMB_NOTIFY_TO`, mặc định `08:00`–`18:00`. Ngoài khung này
hệ thống **vẫn fetch và ghi DB đầy đủ** (Grafana thấy hết), chỉ không gửi tin.

Lý do có khung giờ: các cửa hàng tắt màn hình khi đóng cửa, tạo ra một tràng
thông báo mỗi chiều — và đó chính là thứ làm người ta bắt đầu bỏ qua cảnh báo.

Đặt `DMB_NOTIFY_FROM` bằng `DMB_NOTIFY_TO` (ví dụ cả hai là `00:00`) để gửi 24/7.
Khung vắt qua nửa đêm cũng được, ví dụ `20:00`–`06:00`.

### Đồng bộ lại sau khi dừng

`changed_at` của event là lúc **monitor nhìn thấy** thay đổi, không phải lúc
thiết bị rớt. Nếu monitor dừng qua đêm, các thiết bị rớt tối hôm trước sẽ bị dồn
thành một chùm "vừa offline" vào lúc khởi động — sai và gây hiểu nhầm.

Nên khi khoảng trống giữa hai lần fetch thành công vượt `DMB_RESYNC_GAP_MINUTES`
(mặc định 15 phút), chu trình đầu tiên được coi là **đồng bộ lại**: ghi đầy đủ
vào DB nhưng không báo riêng lẻ, chỉ gửi một tin tổng hợp trạng thái kèm ghi chú
giải thích. Cột "thấy lần cuối" trong tin cho biết thời điểm rớt thật.

Restart nhanh (dưới 15 phút) vẫn chạy tiếp bình thường và báo riêng lẻ như thường.

## Bảo mật — việc cần làm

1. **Revoke webhook Bitrix cũ.** Webhook dùng trước đây được hardcode trong
   `config_bitrix.py`, và file đó **đã được commit lên git** — giá trị vẫn còn
   trong history của các commit trước. Ai đọc được repo là gửi/đọc được Bitrix.
   Vào Bitrix24 → Developer resources → Other → Incoming webhook, **revoke
   webhook cũ**, tạo cái mới và chỉ đặt giá trị vào `.env`.
2. **Không mở port Postgres ra internet.** `docker-compose.yml` mặc định không
   publish 5432. Nếu cần truy cập từ xa thì dùng SSH tunnel.
3. **Grafana đã nằm sau Caddy** với HTTPS và chặn IP, và không publish port
   riêng. Kiểm tra `GRAFANA_ALLOWED_IPS` đúng dải mạng của bạn, đừng để
   `0.0.0.0/0`.
4. **`config_auto.py` không còn được dùng** (API không cần đăng nhập). File này
   chứa mật khẩu dạng plaintext — nên xoá.
5. `.env` nằm trong `.gitignore`. Đừng commit.

## Sự cố thường gặp

### Mật khẩu đúng mà không đăng nhập được Grafana

`GF_SECURITY_ADMIN_PASSWORD` **chỉ có tác dụng lúc Grafana khởi tạo database lần
đầu**. Sau đó user `admin` nằm trong volume `grafana-data`, và mật khẩu trong DB
thắng biến môi trường — sửa `.env` rồi restart sẽ không đổi được gì.

Xảy ra khi `up` một lần với mật khẩu placeholder rồi mới sửa `.env`.

```bash
docker compose exec grafana grafana cli admin reset-admin-password 'mat-khau-moi'
```

Hoặc xoá volume cho khởi tạo lại. An toàn: volume này chỉ chứa tài khoản user và
tuỳ chọn UI; datasource và dashboard provision lại từ file, lịch sử thiết bị nằm
ở volume Postgres riêng.

```bash
docker compose down
docker volume rm <project>_grafana-data    # docker volume ls de xem ten
docker compose up -d
```

`POSTGRES_PASSWORD` cũng y như vậy — chỉ áp dụng lúc khởi tạo. Nếu đã đổi `.env`
sau lần `up` đầu:

```bash
docker compose exec postgres psql -U dmb -d dmb -c "ALTER USER dmb PASSWORD 'mat-khau-trong-env';"
docker compose up -d
```

Lệnh trên chạy được không cần mật khẩu vì socket nội bộ của image Postgres dùng
`trust`.

### Monitor báo `failed to resolve host 'dmb'` / `Cho Postgres...` mãi

Đã sửa trong code. Nguyên nhân cũ: mật khẩu chứa dấu `/` làm vỡ cú pháp URI của
connection string, khiến libpq hiểu username thành host:

```
postgresql://dmb:R/b+C1...@postgres:5432/dmb
  -> host='dmb'  port='R'  dbname='b+C1...@postgres:5432/dmb'
```

Nay `app/db.py` truyền tham số rời cho psycopg nên mọi ký tự đều an toàn. Nếu
vẫn gặp thì bạn đang chạy code cũ — `git pull` rồi `docker compose up -d --build`.

### Grafana trống trơn không có dữ liệu

Chẩn đoán theo thứ tự:

```bash
docker compose ps
docker compose logs monitor --tail 40

# DB co du lieu khong (khong can mat khau)
docker compose exec postgres psql -U dmb -d dmb -c   "SELECT (SELECT count(*) FROM devices) AS devices, (SELECT count(*) FROM fetch_runs) AS runs;"

# Grafana noi duoc voi Postgres khong
curl -sk -u admin:<mat-khau> https://<ip-server>/api/datasources/uid/dmb-postgres/health
```

Lệnh cuối phải ra `{"message":"Database Connection OK","status":"OK"}`.

- `Chu trinh that bai` trong log → outbound bị chặn, xem lại bước 1
- `devices=0` → monitor chưa fetch thành công lần nào
- Có dữ liệu nhưng datasource lỗi → lệch mật khẩu Postgres, xem mục trên
- 4 ô số có hiện nhưng biểu đồ trống → chỉ là khung thời gian. Đổi sang
  **Last 1 hour**. Kiểm tra luôn `timedatectl` vì đồng hồ lệch làm Grafana lọc
  theo "now" không thấy gì
- Panel *Thiết bị hay rớt (7 ngày)* trống là bình thường, cần vài ngày dữ liệu

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
