"""
Client cho API cloneList cua YouFrame.

Hai dieu da kiem chung bang thuc nghiem (2026-10-26):
  1. Endpoint KHONG yeu cau authentication - khong can cookie/login/Selenium.
  2. Neu KHONG gui bo params columns[] cua DataTables thi server bo qua
     `length` va tra ve toan bo record trong 1 request.
     -> khong can phan trang, va tranh han bug phan trang khong on dinh
        (sort theo cot Status khong unique lam mat ~1% record moi lan fetch).
"""

import logging
import time
from datetime import datetime
from typing import Any, Optional

import requests
import urllib3

from . import settings

log = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Vi tri cac truong trong mang 14 phan tu cua moi record
IDX_NAME = 1
IDX_STATUS = 2
IDX_TYPE = 3
IDX_FW = 4
IDX_HEALTH = 5
IDX_LAST_SEEN = 6
IDX_BRAND = 7
IDX_REGION = 8
IDX_MODEL = 9
IDX_MENU = 10
IDX_DEVICE_ID = 12   # khoa chinh. Luu y: idx 13 co ban ghi lech so idx 12, dung tin.
ROW_LEN = 14

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}


class FetchError(RuntimeError):
    """Khong lay duoc du lieu tu API."""


def _parse_last_seen(raw: str) -> Optional[datetime]:
    """Chuoi '2026-10-26 15:00:34' (gio local thiet bi) -> datetime co timezone."""
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        naive = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        log.debug("last_seen khong parse duoc: %r", raw)
        return None
    return naive.replace(tzinfo=settings.SOURCE_TZ)


def fetch_raw() -> dict:
    """Goi API mot lan, co retry + backoff. Tra ve JSON tho."""
    last_err = None

    for attempt in range(1, settings.API_RETRIES + 1):
        try:
            resp = requests.get(
                settings.API_URL,
                params={"draw": 1, "start": 0},  # co tinh bo columns[] de lay het 1 lan
                headers=HEADERS,
                verify=settings.API_VERIFY_SSL,
                timeout=settings.API_TIMEOUT,
                allow_redirects=False,
            )
            if resp.status_code != 200:
                raise FetchError("HTTP {}".format(resp.status_code))

            ctype = resp.headers.get("Content-Type", "")
            if "json" not in ctype.lower():
                raise FetchError("Content-Type khong phai JSON: {!r}".format(ctype))

            return resp.json()

        except Exception as exc:
            last_err = exc
            if attempt < settings.API_RETRIES:
                backoff = 2 ** attempt
                log.warning("Fetch that bai (lan %d/%d): %s - thu lai sau %ds",
                            attempt, settings.API_RETRIES, exc, backoff)
                time.sleep(backoff)

    raise FetchError("Fetch that bai sau {} lan: {}".format(settings.API_RETRIES, last_err))


def parse_rows(payload: dict) -> tuple:
    """
    Chuyen JSON tho thanh list dict da chuan hoa.

    Tra ve (danh sach device, recordsTotal).
    Canh bao neu so record nhan duoc khong khop recordsTotal - dau hieu
    server doi hanh vi va can xem lai cach goi API.
    """
    rows = payload.get("data") or []
    total = int(payload.get("recordsTotal") or 0)

    if total and len(rows) != total:
        log.warning("Nhan %d record nhung recordsTotal=%d - co the bi thieu du lieu!",
                    len(rows), total)

    devices = []
    seen = set()
    skipped = 0

    for row in rows:
        if not isinstance(row, list) or len(row) < ROW_LEN:
            skipped += 1
            continue

        device_id = str(row[IDX_DEVICE_ID]).strip()
        if not device_id or device_id in seen:
            skipped += 1   # trung thi giu ban dau tien
            continue
        seen.add(device_id)

        devices.append({
            "device_id": device_id,
            "name": str(row[IDX_NAME]).strip(),
            "status": str(row[IDX_STATUS]).strip(),
            "device_type": str(row[IDX_TYPE]).strip(),
            "fw_version": str(row[IDX_FW]).strip(),
            "health": str(row[IDX_HEALTH]).strip(),
            "last_seen": _parse_last_seen(str(row[IDX_LAST_SEEN])),
            "brand": str(row[IDX_BRAND]).strip(),
            "region": str(row[IDX_REGION]).strip(),
            "model": str(row[IDX_MODEL]).strip(),
            "menu": str(row[IDX_MENU]).strip(),
        })

    if skipped:
        log.warning("Bo qua %d record khong hop le/trung", skipped)

    return devices, total


def fetch_devices() -> tuple:
    """Fetch + parse trong mot buoc."""
    return parse_rows(fetch_raw())
