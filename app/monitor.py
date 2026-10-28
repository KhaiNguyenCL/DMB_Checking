"""
Vong lap monitor chinh.

Khac biet so voi ban cu (monitor_devices.py):
  - Khong con Selenium / cookie / subprocess fetch_data.py
  - State luu trong Postgres thay vi device_states.json
  - Khong xoa state luc khoi dong (khong spam lai toan bo thiet bi Off)
  - Phat hien chuyen trang thai bang trigger DB -> khong bo sot
  - Co canh bao khi fetch that bai lien tiep (truoc day im lang)
  - Tong hop dau ngay thay cho co che reset state luc 08:00
"""

import logging
import signal
import sys
import time
from datetime import datetime, time as time_cls
from pathlib import Path

from . import db, dmb_api, notifier, settings

log = logging.getLogger("dmb.monitor")

_stop = False


def _handle_signal(signum, _frame):
    """Dung gon gang khi container nhan SIGTERM (docker stop)."""
    global _stop
    log.info("Nhan signal %s - se dung sau chu trinh hien tai", signum)
    _stop = True


def setup_logging():
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        stream=sys.stdout,
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def load_exception_list():
    """Doc blacklist device_id. File co the sua khi dang chay, doc lai moi chu trinh."""
    path = Path(settings.EXCEPTION_LIST_FILE)
    if not path.exists():
        return set()
    try:
        return {
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        }
    except OSError as exc:
        log.warning("Khong doc duoc exception list: %s", exc)
        return set()


def in_notify_window(now):
    """
    Co nam trong khung gio duoc phep gui notification khong.

    Ho tro khung vat qua nua dem (vi du 20:00 -> 06:00). Dat FROM == TO
    nghia la gui 24/7.
    """
    start = settings.NOTIFY_FROM
    end = settings.NOTIFY_TO
    if start == end:
        return True
    t = now.time()
    if start < end:
        return start <= t < end
    return t >= start or t < end


def _fmt_gap(minutes):
    """Mo ta khoang trong quan sat cho de doc trong tin nhan."""
    if minutes is None:
        return "lần chạy đầu tiên"
    minutes = int(minutes)
    if minutes < 60:
        return "{} phút không chạy".format(minutes)
    if minutes < 1440:
        return "{} giờ {:02d} phút không chạy".format(minutes // 60, minutes % 60)
    return "{} ngày {} giờ không chạy".format(minutes // 1440, (minutes % 1440) // 60)


def _parse_hhmm(value):
    try:
        hh, mm = value.split(":")
        return time_cls(int(hh), int(mm))
    except (ValueError, AttributeError):
        log.warning("DMB_DAILY_SUMMARY_AT khong hop le: %r - tat tong hop dau ngay", value)
        return None


def run_cycle(conn, exception_ids, resync, gap_minutes=None):
    """Mot chu trinh: fetch -> loc -> ghi DB -> tim event. Tra ve thong ke."""
    run_id = db.start_run(conn)

    try:
        devices, total_records = dmb_api.fetch_devices()
    except Exception as exc:
        db.finish_run(conn, run_id, ok=False, error_msg=str(exc))
        raise

    if settings.REGIONS:
        in_scope = [d for d in devices if d["region"] in settings.REGIONS]
    else:
        in_scope = list(devices)

    kept = [d for d in in_scope if d["device_id"] not in exception_ids]
    excluded = len(in_scope) - len(kept)

    offline = sum(1 for d in kept if d["status"] == "Off")
    online = len(kept) - offline

    vanished = db.sync_devices(conn, run_id, kept)
    db.discard_stale_events(conn, settings.PENDING_MAX_AGE_HOURS)
    events = db.pending_offline_events(conn, settings.PENDING_MAX_AGE_HOURS)

    db.finish_run(
        conn, run_id, ok=True,
        total_records=total_records, stored_count=len(kept),
        online_count=online, offline_count=offline, excluded_count=excluded,
    )

    log.info(
        "Run #%s | API %d record | trong pham vi %d | loai %d | online %d | offline %d | event cho gui %d%s",
        run_id, total_records, len(in_scope), excluded, online, offline, len(events),
        " | bien mat khoi feed {}".format(vanished) if vanished else "",
    )

    return {
        "run_id": run_id,
        "events": events,
        "stored": len(kept),
        "offline": offline,
        "vanished": vanished,
        "resync": resync,
        "gap_minutes": gap_minutes,
    }


def handle_notifications(conn, result):
    """
    Quyet dinh gui gi. Ba truong hop:

    1. Dong bo lai (chay lan dau, hoac vua dung lau roi chay lai): cac event
       sinh ra o day KHONG phai "vua offline" - thiet bi da rot tu luc monitor
       khong chay. Khong bao rieng le, chi gui mot tin tong hop trang thai.
    2. Ngoai khung gio gui: ghi DB day du nhung khong gui. Thiet bi con offline
       se xuat hien trong tong hop dau ngay.
    3. Binh thuong: bao rieng le tung thiet bi vua chuyen sang Off.
    """
    events = result["events"]
    now = datetime.now(settings.LOCAL_TZ)
    in_window = in_notify_window(now)

    if result["resync"]:
        if events:
            db.mark_notified(conn, [e["id"] for e in events])

        gap_text = _fmt_gap(result.get("gap_minutes"))

        if not settings.NOTIFY_STATE_ON_RESYNC:
            log.info("Dong bo lai (%s): bo qua %d event, khong gui "
                     "(DMB_NOTIFY_STATE_ON_RESYNC=false)", gap_text, len(events))
            return

        if not in_window:
            log.info("Dong bo lai (%s): bo qua %d event, ngoai khung gio gui "
                     "%s-%s nen khong gui tong hop", gap_text, len(events),
                     settings.NOTIFY_FROM, settings.NOTIFY_TO)
            return

        offline = db.offline_now(conn)
        log.info("Dong bo lai (%s): khong bao rieng le %d event, gui tong hop "
                 "trang thai (%d thiet bi dang offline)",
                 gap_text, len(events), len(offline))
        notifier.notify_resync_summary(offline, db.present_count(conn), gap_text)
        return

    if not events:
        return

    if not in_window:
        # Danh dau da xu ly thay vi de ton lai, neu khong thi dung dau khung
        # gio hom sau se ban ra mot loat tin don cua ca dem.
        db.mark_notified(conn, [e["id"] for e in events])
        log.info("Phat hien %d thiet bi vua offline nhung ngoai khung gio gui "
                 "(%s-%s) - khong gui, se nam trong tong hop dau ngay",
                 len(events), settings.NOTIFY_FROM, settings.NOTIFY_TO)
        return

    res = notifier.notify_newly_offline(events, result["stored"])
    if res.get("success"):
        db.mark_notified(conn, [e["id"] for e in events])
    else:
        log.warning("Chua gui duoc, giu notified=FALSE de thu lai: %s", res.get("error"))


def maybe_daily_summary(conn, last_sent_date, summary_time):
    """Gui tong hop dau ngay mot lan moi ngay, khi da qua gio cau hinh."""
    if summary_time is None or not settings.DAILY_SUMMARY_ENABLED:
        return last_sent_date

    now = datetime.now(settings.LOCAL_TZ)
    today = now.date()

    if last_sent_date == today or now.time() < summary_time:
        return last_sent_date

    offline = db.offline_now(conn)
    total = db.present_count(conn)

    log.info("Gui tong hop dau ngay: %d thiet bi offline", len(offline))
    notifier.notify_daily_summary(offline, total)
    return today


def decide_resync(conn, now=None):
    """
    Lan fetch dau tien sau khi khoi dong co phai la DONG BO LAI khong?

    Thiet bi rot trong luc monitor khong chay thi khong phai "vua offline",
    nen neu co khoang trong quan sat thi khong bao rieng le tung thiet bi.

    Tra ve (resync, gap_minutes). gap_minutes la None khi chua tung fetch.
    """
    now = now or datetime.now(settings.LOCAL_TZ)
    last_ok = db.last_successful_fetch(conn)
    gap_minutes = None
    if last_ok is not None:
        gap_minutes = (now - last_ok).total_seconds() / 60

    if db.is_empty(conn):
        log.info("DB dang rong - lan chay dau tien, se dong bo lai")
        return True, gap_minutes

    if gap_minutes is None:
        log.info("Chua co lan fetch thanh cong nao - se dong bo lai")
        return True, None

    if gap_minutes > settings.RESYNC_GAP_MINUTES:
        log.info("Lan fetch thanh cong cuoi cach day %.0f phut (nguong %d) - "
                 "se dong bo lai, khong bao rieng le tung thiet bi",
                 gap_minutes, settings.RESYNC_GAP_MINUTES)
        return True, gap_minutes

    log.info("Lan fetch thanh cong cuoi cach day %.0f phut - chay tiep binh thuong",
             gap_minutes)
    return False, gap_minutes


def wait_for_db(max_wait=60):
    """Postgres trong docker co the chua san sang luc container nay khoi dong."""
    deadline = time.monotonic() + max_wait
    while True:
        try:
            return db.connect()
        except Exception as exc:
            if time.monotonic() >= deadline:
                raise
            log.info("Cho Postgres... (%s)", exc.__class__.__name__)
            time.sleep(2)


def main():
    setup_logging()
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    log.info("=" * 70)
    log.info("DMB DEVICE MONITOR")
    log.info("API       : %s", settings.API_URL)
    log.info("Region    : %s", ", ".join(settings.REGIONS) or "ALL")
    log.info("Chu ky    : %ds", settings.INTERVAL)
    log.info("Gui tin   : %s - %s (%s)%s", settings.NOTIFY_FROM, settings.NOTIFY_TO,
             settings.LOCAL_TZ.key,
             " [24/7]" if settings.NOTIFY_FROM == settings.NOTIFY_TO else "")
    log.info("Tong hop  : %s", settings.DAILY_SUMMARY_AT
             if settings.DAILY_SUMMARY_ENABLED else "tat")
    log.info("Bitrix    : %s", "bat (dialog {})".format(settings.BITRIX_DIALOG_ID or "CHUA DAT")
             if settings.BITRIX_ENABLED else "tat")
    log.info("=" * 70)

    conn = wait_for_db()
    db.init_schema(conn)
    db.ensure_readonly_role(conn)

    resync, gap_minutes = decide_resync(conn)

    summary_time = _parse_hhmm(settings.DAILY_SUMMARY_AT)
    last_summary_date = None
    if summary_time and datetime.now(settings.LOCAL_TZ).time() >= summary_time:
        last_summary_date = datetime.now(settings.LOCAL_TZ).date()

    failure_streak = 0
    alerted_failure = False

    while not _stop:
        cycle_start = time.monotonic()

        try:
            result = run_cycle(conn, load_exception_list(), resync, gap_minutes)

            if failure_streak and alerted_failure:
                log.info("Fetch da hoat dong lai sau %d lan loi", failure_streak)
            failure_streak = 0
            alerted_failure = False

            handle_notifications(conn, result)
            last_summary_date = maybe_daily_summary(conn, last_summary_date, summary_time)
            resync = False
            gap_minutes = None

        except Exception as exc:
            failure_streak += 1
            log.error("Chu trinh that bai (lan %d lien tiep): %s", failure_streak, exc)

            if conn.closed:
                log.warning("Connection da dong - ket noi lai")
                try:
                    conn = wait_for_db()
                except Exception as db_exc:
                    log.error("Khong ket noi lai duoc DB: %s", db_exc)
            else:
                try:
                    conn.rollback()
                except Exception:
                    pass

            if failure_streak >= settings.ALERT_AFTER_FAILURES and not alerted_failure:
                notifier.notify_fetch_failure(failure_streak, str(exc))
                alerted_failure = True

        elapsed = time.monotonic() - cycle_start
        remaining = max(0.0, settings.INTERVAL - elapsed)
        log.debug("Chu trinh mat %.1fs - nghi %.0fs", elapsed, remaining)
        while remaining > 0 and not _stop:
            nap = min(1.0, remaining)
            time.sleep(nap)
            remaining -= nap

    log.info("Dung monitor")
    try:
        conn.close()
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
