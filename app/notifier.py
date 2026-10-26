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


def _post(message: str) -> dict:
    if not settings.BITRIX_ENABLED:
        log.info("Bitrix dang tat (BITRIX_ENABLED=false) - bo qua notification")
        return {"success": False, "error": "disabled"}

    if not settings.BITRIX_WEBHOOK_URL.strip("/") or not settings.BITRIX_CHAT_ID:
        log.error("Thieu BITRIX_WEBHOOK_URL hoac BITRIX_CHAT_ID")
        return {"success": False, "error": "missing config"}

    url = settings.BITRIX_WEBHOOK_URL + "im.message.add.json"
    payload = {
        "DIALOG_ID": "chat{}".format(settings.BITRIX_CHAT_ID),
        "MESSAGE": message,
    }

    try:
        resp = requests.post(url, json=payload, timeout=settings.BITRIX_TIMEOUT, verify=True)
        data = resp.json()
    except Exception as exc:
        log.error("Gui Bitrix that bai: %s", exc)
        return {"success": False, "error": str(exc)}

    if data.get("result"):
        log.info("Da gui Bitrix (message_id=%s)", data["result"])
        return {"success": True, "message_id": data["result"]}

    err = data.get("error_description") or data.get("error") or "unknown"
    log.error("Bitrix tra loi: %s", err)
    return {"success": False, "error": err}


def _fmt_duration(delta) -> str:
    if delta is None:
        return "?"
    total = int(delta.total_seconds())
    if total < 3600:
        return "{} phut".format(total // 60)
    if total < 86400:
        return "{}h{:02d}m".format(total // 3600, (total % 3600) // 60)
    return "{} ngay {}h".format(total // 86400, (total % 86400) // 3600)


def _fmt_last_seen(value) -> str:
    if not value:
        return "?"
    return value.astimezone(settings.LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")


def notify_newly_offline(events: list, total_devices: int) -> dict:
    """Canh bao cac thiet bi vua chuyen sang Off."""
    if not events:
        return {"success": False, "error": "no events"}

    lines = []
    for idx, e in enumerate(events, 1):
        first = e["old_status"] is None
        tag = " (lan dau thay)" if first else ""
        lines.append("{}. {} - Last seen: {}{}".format(
            idx, e["name"] or e["device_id"], _fmt_last_seen(e["last_seen"]), tag))

    message = (
        "[OFF] THIET BI OFFLINE - {regions}\n\n"
        "Phat hien {count} thiet bi vua offline:\n"
        "{device_list}\n"
        "Thoi gian: {ts}\n"
        "Tong thiet bi dang theo doi: {total}"
    ).format(
        regions=", ".join(settings.REGIONS) if settings.REGIONS else "ALL",
        count=len(events),
        device_list="\n".join(lines),
        ts=datetime.now(settings.LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        total=total_devices,
    )
    return _post(message)


def notify_daily_summary(offline_devices: list, total_devices: int) -> dict:
    """
    Tong hop dau ngay: liet ke TAT CA thiet bi dang Off.
    Thay cho co che xoa state file cu de bao lai toan bo.
    """
    ts = datetime.now(settings.LOCAL_TZ).strftime("%Y-%m-%d %H:%M")

    if not offline_devices:
        message = (
            "[OK] TONG HOP DAU NGAY - {ts}\n\n"
            "Tat ca {total} thiet bi dang online."
        ).format(ts=ts, total=total_devices)
        return _post(message)

    lines = []
    for idx, d in enumerate(offline_devices, 1):
        lines.append("{}. {} - offline {} (last seen: {})".format(
            idx,
            d["name"] or d["device_id"],
            _fmt_duration(d.get("offline_duration")),
            _fmt_last_seen(d.get("last_seen")),
        ))

    message = (
        "[!] TONG HOP DAU NGAY - {ts}\n\n"
        "Dang co {count}/{total} thiet bi offline:\n"
        "{device_list}"
    ).format(ts=ts, count=len(offline_devices), total=total_devices,
             device_list="\n".join(lines))
    return _post(message)


def notify_fetch_failure(streak: int, error: str) -> dict:
    """
    Canh bao khi monitor khong lay duoc du lieu nhieu lan lien tiep.
    Truoc day loi nay im lang hoan toan - monitor chet ma khong ai biet.
    """
    message = (
        "[LOI] MONITOR KHONG LAY DUOC DU LIEU\n\n"
        "That bai {streak} lan lien tiep.\n"
        "Loi cuoi: {error}\n"
        "Thoi gian: {ts}\n\n"
        "Canh bao thiet bi offline dang TAM NGUNG cho den khi fetch lai duoc."
    ).format(streak=streak, error=error[:500],
             ts=datetime.now(settings.LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S"))
    return _post(message)


def send_test() -> dict:
    return _post("[TEST] DMB monitor ket noi Bitrix thanh cong - {}".format(
        datetime.now(settings.LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")))
