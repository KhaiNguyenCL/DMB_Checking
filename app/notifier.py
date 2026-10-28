"""
Gui notification len Bitrix24 chat qua Incoming Webhook (im.message.add).
"""

import logging
from datetime import datetime

import requests
import urllib3

from . import settings

log = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _redact(text: str) -> str:
    """
    Xoa ma webhook khoi chuoi truoc khi log.
    requests dua nguyen URL vao message cua exception (vi du
    "Max retries exceeded with url: /rest/96/<ma>/im.message.add.json"),
    nen khong che di thi ma webhook se nam trong docker log.
    """
    text = str(text)
    code = settings.BITRIX_WEBHOOK_CODE
    if code:
        text = text.replace(code, "***")
    return text


def _post(message: str) -> dict:
    if not settings.BITRIX_ENABLED:
        log.info("Bitrix dang tat (BITRIX_ENABLED=false) - bo qua notification")
        return {"success": False, "error": "disabled"}

    if not settings.BITRIX_WEBHOOK_URL.strip("/") or not settings.BITRIX_DIALOG_ID:
        log.error("Thieu BITRIX_WEBHOOK_URL hoac BITRIX_DIALOG_ID/BITRIX_CHAT_ID")
        return {"success": False, "error": "missing config"}

    url = settings.BITRIX_WEBHOOK_URL + "im.message.add.json"
    payload = {
        "DIALOG_ID": settings.BITRIX_DIALOG_ID,
        "MESSAGE": message,
    }

    try:
        resp = requests.post(url, json=payload, timeout=settings.BITRIX_TIMEOUT, verify=True)
        data = resp.json()
    except Exception as exc:
        err = _redact(exc)
        log.error("Gui Bitrix that bai: %s", err)
        return {"success": False, "error": err}

    if data.get("result"):
        log.info("Da gui Bitrix (message_id=%s)", data["result"])
        return {"success": True, "message_id": data["result"]}

    err = _redact(data.get("error_description") or data.get("error") or "unknown")
    log.error("Bitrix tra loi: %s", err)
    return {"success": False, "error": err}


def _fmt_duration(delta) -> str:
    if delta is None:
        return "?"
    total = int(delta.total_seconds())
    if total < 3600:
        return "{} phút".format(total // 60)
    if total < 86400:
        return "{} giờ {:02d} phút".format(total // 3600, (total % 3600) // 60)
    return "{} ngày {} giờ".format(total // 86400, (total % 86400) // 3600)


def _fmt_last_seen(value) -> str:
    if not value:
        return "?"
    return value.astimezone(settings.LOCAL_TZ).strftime("%d/%m/%Y %H:%M:%S")


# Ten khu vuc trong API la tieng Anh, doi sang tieng Viet khi hien thi.
# Khu vuc khong co trong bang thi giu nguyen ten goc.
_REGION_VI = {
    "Vietnam": "Việt Nam",
    "Thailand": "Thái Lan",
    "Cambodia": "Campuchia",
    "Singapore": "Singapore",
    "Malaysia": "Malaysia",
    "Indonesia": "Indonesia",
}


def _regions_label() -> str:
    if not settings.REGIONS:
        return "TẤT CẢ KHU VỰC"
    return ", ".join(_REGION_VI.get(r, r) for r in settings.REGIONS).upper()


def notify_newly_offline(events: list, total_devices: int) -> dict:
    """Canh bao cac thiet bi vua chuyen sang Off."""
    if not events:
        return {"success": False, "error": "no events"}

    shown = events[:settings.MAX_DEVICES_IN_MESSAGE]
    lines = []
    for idx, e in enumerate(shown, 1):
        tag = " — lần đầu ghi nhận" if e["old_status"] is None else ""
        lines.append("{}. {} — thấy lần cuối: {}{}".format(
            idx, e["name"] or e["device_id"], _fmt_last_seen(e["last_seen"]), tag))

    rest = len(events) - len(shown)
    if rest > 0:
        lines.append("… và {} thiết bị khác (xem đầy đủ trên Grafana)".format(rest))

    message = (
        "🔴 THIẾT BỊ OFFLINE — {regions}\n\n"
        "Phát hiện {count} thiết bị vừa offline:\n"
        "{device_list}\n\n"
        "⏰ Thời gian: {ts}\n"
        "📊 Tổng thiết bị đang theo dõi: {total}"
    ).format(
        regions=_regions_label(),
        count=len(events),
        device_list="\n".join(lines),
        ts=datetime.now(settings.LOCAL_TZ).strftime("%d/%m/%Y %H:%M:%S"),
        total=total_devices,
    )
    return _post(message)


def _state_summary(offline_devices: list, total_devices: int,
                   title: str, note: str = "") -> dict:
    """
    Tin tong hop trang thai: liet ke TAT CA thiet bi dang Off kem thoi gian
    offline that su (tinh tu last_seen). Dung cho ca tong hop dau ngay va
    tong hop sau khi dong bo lai.
    """
    ts = datetime.now(settings.LOCAL_TZ).strftime("%d/%m/%Y %H:%M")
    tail = "\n\n" + note if note else ""

    if not offline_devices:
        return _post(
            "✅ {title} — {ts}\n\nTất cả {total} thiết bị đang online.{tail}".format(
                title=title, ts=ts, total=total_devices, tail=tail))

    shown = offline_devices[:settings.MAX_DEVICES_IN_MESSAGE]
    lines = []
    for idx, d in enumerate(shown, 1):
        lines.append("{}. {} — offline {} (thấy lần cuối: {})".format(
            idx,
            d["name"] or d["device_id"],
            _fmt_duration(d.get("offline_duration")),
            _fmt_last_seen(d.get("last_seen")),
        ))

    rest = len(offline_devices) - len(shown)
    if rest > 0:
        lines.append("… và {} thiết bị khác (xem đầy đủ trên Grafana)".format(rest))

    return _post(
        "⚠️ {title} — {ts}\n\n"
        "Đang có {count}/{total} thiết bị offline:\n"
        "{device_list}{tail}".format(
            title=title, ts=ts, count=len(offline_devices),
            total=total_devices, device_list="\n".join(lines), tail=tail))


def notify_daily_summary(offline_devices: list, total_devices: int) -> dict:
    """Tong hop dau ngay, gui mot lan moi ngay vao gio cau hinh."""
    return _state_summary(offline_devices, total_devices, "TỔNG HỢP ĐẦU NGÀY")


def notify_resync_summary(offline_devices: list, total_devices: int,
                          gap_text: str) -> dict:
    """
    Tong hop sau khi dong bo lai. Gui thay cho viec bao rieng le tung thiet bi,
    vi nhung thiet bi nay rot trong luc monitor khong chay nen khong the goi la
    "vua offline".
    """
    return _state_summary(
        offline_devices, total_devices,
        "TRẠNG THÁI SAU KHI KHỞI ĐỘNG LẠI",
        note=("ℹ️ Hệ thống vừa chạy lại sau {gap}. Các thiết bị rớt trong "
              "khoảng thời gian đó không gửi báo riêng lẻ — xem mốc \"thấy lần "
              "cuối\" ở trên để biết thời điểm rớt thật.").format(gap=gap_text))


def notify_fetch_failure(streak: int, error: str) -> dict:
    """
    Canh bao khi monitor khong lay duoc du lieu nhieu lan lien tiep.
    Truoc day loi nay im lang hoan toan - monitor chet ma khong ai biet.
    """
    message = (
        "❗ MONITOR KHÔNG LẤY ĐƯỢC DỮ LIỆU\n\n"
        "Thất bại {streak} lần liên tiếp.\n"
        "Lỗi cuối: {error}\n"
        "⏰ Thời gian: {ts}\n\n"
        "Cảnh báo thiết bị offline đang TẠM NGƯNG cho đến khi lấy được dữ liệu lại."
    ).format(streak=streak, error=_redact(error)[:500],
             ts=datetime.now(settings.LOCAL_TZ).strftime("%d/%m/%Y %H:%M:%S"))
    return _post(message)


def send_test() -> dict:
    return _post("🤖 KIỂM TRA KẾT NỐI — DMB monitor đã kết nối Bitrix thành công ({})".format(
        datetime.now(settings.LOCAL_TZ).strftime("%d/%m/%Y %H:%M:%S")))
