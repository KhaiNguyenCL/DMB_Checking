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


def in_quiet_hours(now):
    """Quiet hours vat qua nua dem, vi du 22:00 -> 05:00."""
    start = time_cls(settings.QUIET_START, 0)
    end = time_cls(settings.QUIET_END, 0)
    t = now.time()
    if start <= end:
        return start <= t < end
    return t >= start or t < end


def _parse_hhmm(value):
    try:
        hh, mm = value.split(":")
        return time_cls(int(hh), int(mm))
    except (ValueError, AttributeError):
        log.warning("DMB_DAILY_SUMMARY_AT khong hop le: %r - tat tong hop dau ngay", value)
        return None


def run_cycle(conn, exception_ids, first_run):
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
        "first_run": first_run,
    }


def handle_notifications(conn, result):
    events = result["events"]
    if not events:
        return

    if result["first_run"] and not settings.NOTIFY_ON_FIRST_RUN:
        db.mark_notified(conn, [e["id"] for e in events])
        log.info("Lan chay dau tien: danh dau %d event la da xu ly, khong gui "
                 "(dat DMB_NOTIFY_ON_FIRST_RUN=true neu muon gui)", len(events))
        return

    if in_quiet_hours(datetime.now(settings.LOCAL_TZ)):
        # Danh dau da xu ly thay vi de ton lai, neu khong thi dung 05:00 se
        # ban ra mot loat tin don cua ca dem. Thiet bi nao con Off se xuat
        # hien trong tong hop dau ngay.
        db.mark_notified(conn, [e["id"] for e in events])
        log.info("Phat hien %d thiet bi vua offline nhung dang trong quiet hours "
                 "(%02d:00-%02d:00) - khong gui, se nam trong tong hop dau ngay",
                 len(events), settings.QUIET_START, settings.QUIET_END)
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
    log.info("Quiet     : %02d:00 - %02d:00 (%s)", settings.QUIET_START,
             settings.QUIET_END, settings.LOCAL_TZ.key)
    log.info("Tong hop  : %s", settings.DAILY_SUMMARY_AT
             if settings.DAILY_SUMMARY_ENABLED else "tat")
    log.info("Bitrix    : %s", "bat (dialog {})".format(settings.BITRIX_DIALOG_ID or "CHUA DAT")
             if settings.BITRIX_ENABLED else "tat")
    log.info("=" * 70)

    conn = wait_for_db()
    db.init_schema(conn)

    first_run = db.is_empty(conn)
    if first_run:
        log.info("DB dang rong - day la lan chay dau tien")

    summary_time = _parse_hhmm(settings.DAILY_SUMMARY_AT)
    last_summary_date = None
    if summary_time and datetime.now(settings.LOCAL_TZ).time() >= summary_time:
        last_summary_date = datetime.now(settings.LOCAL_TZ).date()

    failure_streak = 0
    alerted_failure = False

    while not _stop:
        cycle_start = time.monotonic()

        try:
            result = run_cycle(conn, load_exception_list(), first_run)

            if failure_streak and alerted_failure:
                log.info("Fetch da hoat dong lai sau %d lan loi", failure_streak)
            failure_streak = 0
            alerted_failure = False

            handle_notifications(conn, result)
            last_summary_date = maybe_daily_summary(conn, last_summary_date, summary_time)
            first_run = False

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
