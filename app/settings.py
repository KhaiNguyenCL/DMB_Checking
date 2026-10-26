"""
Cau hinh doc tu environment variables (12-factor).
Khong hardcode secret trong source nua - xem file .env.example
"""

import os
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

# Quiet hours: ghi DB binh thuong nhung khong gui notification
QUIET_START = _int("DMB_QUIET_START_HOUR", 22)
QUIET_END = _int("DMB_QUIET_END_HOUR", 5)

# Tong hop dau ngay: liet ke tat ca thiet bi dang Off (thay cho co che
# xoa state file cu - khong con can xoa state vi DB da persistent)
DAILY_SUMMARY_AT = os.getenv("DMB_DAILY_SUMMARY_AT", "08:00").strip()
DAILY_SUMMARY_ENABLED = _bool("DMB_DAILY_SUMMARY_ENABLED", True)

# Lan dau chay tren DB rong: co gui notification cho toan bo thiet bi Off khong?
# Mac dinh False de khong spam ~23 tin luc khoi dong.
NOTIFY_ON_FIRST_RUN = _bool("DMB_NOTIFY_ON_FIRST_RUN", False)

# Canh bao len Bitrix khi fetch that bai lien tiep N lan
ALERT_AFTER_FAILURES = _int("DMB_ALERT_AFTER_FAILURES", 3)

# Event Off chua gui duoc thi thu lai trong bao nhieu gio; qua han thi bo qua
# (tranh viec bat monitor sau nhieu ngay tat roi gui mot loat tin cu).
PENDING_MAX_AGE_HOURS = _int("DMB_PENDING_MAX_AGE_HOURS", 6)

# ---------------- Database ----------------
_DEFAULT_DSN = "postgresql://{u}:{p}@{h}:{port}/{db}".format(
    u=os.getenv("POSTGRES_USER", "dmb"),
    p=os.getenv("POSTGRES_PASSWORD", "dmb"),
    h=os.getenv("POSTGRES_HOST", "postgres"),
    port=os.getenv("POSTGRES_PORT", "5432"),
    db=os.getenv("POSTGRES_DB", "dmb"),
)
DB_DSN = os.getenv("DMB_DB_DSN", _DEFAULT_DSN)

# ---------------- Bitrix24 ----------------
BITRIX_ENABLED = _bool("BITRIX_ENABLED", True)
BITRIX_WEBHOOK_URL = os.getenv("BITRIX_WEBHOOK_URL", "").rstrip("/") + "/"
BITRIX_CHAT_ID = os.getenv("BITRIX_CHAT_ID", "")
BITRIX_TIMEOUT = _int("BITRIX_TIMEOUT", 30)

LOG_LEVEL = os.getenv("DMB_LOG_LEVEL", "INFO").upper()
