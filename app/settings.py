"""
Cau hinh doc tu environment variables (12-factor).
Khong hardcode secret trong source nua - xem file .env.example
"""

import os
import re
from datetime import time as time_cls
from zoneinfo import ZoneInfo


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "y", "on")


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


# ---------------- Nguon du lieu ----------------
# API nay KHONG yeu cau authentication (da kiem chung) -> khong con login/Selenium
API_URL = os.getenv("DMB_API_URL", "https://34.64.189.31/api/cloneList")
API_VERIFY_SSL = _bool("DMB_API_VERIFY_SSL", False)  # server dung self-signed cert
API_TIMEOUT = _int("DMB_API_TIMEOUT", 60)
API_RETRIES = _int("DMB_API_RETRIES", 3)

# Timezone cua truong last_seen. Thiet bi bao gio local:
# Vietnam/Thailand/Cambodia = UTC+7, Singapore = UTC+8
SOURCE_TZ = ZoneInfo(os.getenv("DMB_SOURCE_TZ", "Asia/Ho_Chi_Minh"))
LOCAL_TZ = ZoneInfo(os.getenv("TZ", "Asia/Ho_Chi_Minh"))

# ---------------- Pham vi monitor ----------------
# Chi luu + canh bao region nay. De trong = tat ca region.
REGIONS = [r.strip() for r in os.getenv("DMB_REGIONS", "Vietnam").split(",") if r.strip()]
EXCEPTION_LIST_FILE = os.getenv("DMB_EXCEPTION_LIST", "data/Exception_list.txt")

# ---------------- Vong lap ----------------
INTERVAL = _int("DMB_INTERVAL_SECONDS", 300)


def _hhmm(name: str, default: str) -> time_cls:
    raw = os.getenv(name, default).strip()
    try:
        hh, mm = raw.split(":")
        return time_cls(int(hh), int(mm))
    except (ValueError, AttributeError):
        hh, mm = default.split(":")
        return time_cls(int(hh), int(mm))


# Khung gio GUI notification. Ngoai khung nay van fetch va ghi DB day du,
# chi khong gui tin - thiet bi nao con offline se nam trong tong hop dau ngay.
# Dat bang nhau (vi du 00:00-00:00) de gui 24/7.
NOTIFY_FROM = _hhmm("DMB_NOTIFY_FROM", "08:00")
NOTIFY_TO = _hhmm("DMB_NOTIFY_TO", "18:00")

# Khi monitor dung lau hon so phut nay roi chay lai, lan fetch dau tien duoc
# coi la DONG BO LAI chu khong phai phat hien chuyen trang thai: cac thiet bi
# rot trong luc khong ai quan sat se khong gui bao rieng le, thay vao do gui
# mot tin tong hop trang thai. Dat du lon de restart nhanh khong bi coi la gap.
RESYNC_GAP_MINUTES = _int("DMB_RESYNC_GAP_MINUTES", 15)

# Tong hop dau ngay: liet ke tat ca thiet bi dang Off (thay cho co che
# xoa state file cu - khong con can xoa state vi DB da persistent)
DAILY_SUMMARY_AT = os.getenv("DMB_DAILY_SUMMARY_AT", "08:00").strip()
DAILY_SUMMARY_ENABLED = _bool("DMB_DAILY_SUMMARY_ENABLED", True)

# Sau khi dong bo lai (chay lan dau, hoac dung lau roi chay lai): co gui
# mot tin tong hop trang thai hien tai khong? Tin nay thay cho viec bao rieng
# le tung thiet bi, de khong nhan nham "vua rot" voi "rot tu luc khong ai xem".
NOTIFY_STATE_ON_RESYNC = _bool("DMB_NOTIFY_STATE_ON_RESYNC", True)

# So thiet bi toi da liet ke trong mot tin nhan; phan con lai gom thanh
# mot dong "va N thiet bi khac" de tin khong dai vo tan khi co su co lon.
MAX_DEVICES_IN_MESSAGE = _int("DMB_MAX_DEVICES_IN_MESSAGE", 30)

# Canh bao len Bitrix khi fetch that bai lien tiep N lan
ALERT_AFTER_FAILURES = _int("DMB_ALERT_AFTER_FAILURES", 3)

# Event Off chua gui duoc thi thu lai trong bao nhieu gio; qua han thi bo qua
# (tranh viec bat monitor sau nhieu ngay tat roi gui mot loat tin cu).
PENDING_MAX_AGE_HOURS = _int("DMB_PENDING_MAX_AGE_HOURS", 6)

# ---------------- Database ----------------
# Tham so ket noi de RIENG, khong ghep thanh URI.
#
# Truoc day ghep "postgresql://user:pass@host:port/db" bang string format, va
# no vo ngay khi mat khau co ky tu dac biet. Vi du mat khau sinh boi
# `openssl rand -base64 24` chua dau "/", thi URI
#   postgresql://dmb:R/b+C1...@postgres:5432/dmb
# duoc libpq parse thanh host='dmb', port='R', dbname='b+C1...@postgres:5432/dmb'
# vi dau "/" ket thuc phan authority -> loi "Servname not supported for ai_socktype".
#
# Truyen tham so roi cho psycopg thi khong con van de trich dan voi bat ky
# mat khau nao.
DB_PARAMS = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "user": os.getenv("POSTGRES_USER", "dmb"),
    "password": os.getenv("POSTGRES_PASSWORD", "dmb"),
    "dbname": os.getenv("POSTGRES_DB", "dmb"),
}

# Tuy chon: dat DMB_DB_DSN de dung nguyen mot connection string tu viet
# (vi du can thong so sslmode). De trong thi dung DB_PARAMS o tren.
DB_DSN = os.getenv("DMB_DB_DSN", "").strip()

# ---------------- Bitrix24 ----------------
BITRIX_ENABLED = _bool("BITRIX_ENABLED", True)
BITRIX_WEBHOOK_URL = os.getenv("BITRIX_WEBHOOK_URL", "").rstrip("/") + "/"
BITRIX_TIMEOUT = _int("BITRIX_TIMEOUT", 30)

# DIALOG_ID cua im.message.add nhan 3 dang:
#   chat<ID>  chat thuong, hoac chat cua workgroup
#   sg<ID>    chat cua group / project (sg + group ID, vi du sg169)
#   <ID>      chat rieng 1-1 voi user co ID do
_DIALOG_RE = re.compile(r"^(chat|sg)?(\d+)$", re.IGNORECASE)


def _resolve_dialog_id() -> str:
    """
    BITRIX_DIALOG_ID: dat gi dung nguyen cai do (chat911 / sg169 / 42).
    BITRIX_CHAT_ID  : giu de tuong thich ban cu, so tran duoc hieu la chat<ID>.

    Gia tri khong khop dinh dang thi tra ve nguyen van de Bitrix bao loi ro
    rang, thay vi am tham sua thanh mot dialog khac.
    """
    for name, default_prefix in (("BITRIX_DIALOG_ID", ""), ("BITRIX_CHAT_ID", "chat")):
        raw = os.getenv(name, "").strip()
        if not raw:
            continue
        match = _DIALOG_RE.match(raw)
        if not match:
            return raw
        prefix, number = match.groups()
        return (prefix.lower() if prefix else default_prefix) + number
    return ""


BITRIX_DIALOG_ID = _resolve_dialog_id()

# Ma webhook = doan cuoi cua URL (.../rest/<user_id>/<ma>/).
# Giu rieng de xoa khoi thong bao loi: requests nhet nguyen URL vao message
# cua exception, nen loi mang se ghi ca ma webhook vao log neu khong che di.
_url_parts = [p for p in BITRIX_WEBHOOK_URL.split("/") if p]
BITRIX_WEBHOOK_CODE = (
    _url_parts[-1] if len(_url_parts) >= 2 and _url_parts[-2].isdigit() else ""
)

LOG_LEVEL = os.getenv("DMB_LOG_LEVEL", "INFO").upper()
