"""
Tang truy cap Postgres.

Mo hinh hybrid:
  - devices: UPSERT moi lan fetch (1 dong / thiet bi)
  - status_events: trigger trong DB tu ghi khi status doi
  - fetch_runs: 1 dong moi lan fetch

Viec phat hien chuyen trang thai lam bang trigger o DB chu khong o Python,
nen khong the bo sot event ngay ca khi process chet giua chu trinh.
"""

import logging
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from . import settings

log = logging.getLogger(__name__)

SCHEMA_FILE = Path(__file__).resolve().parent.parent / "sql" / "001_schema.sql"

_UPSERT = """
INSERT INTO devices (device_id, name, status, device_type, fw_version, health,
                     last_seen, brand, region, model, menu,
                     is_present, last_fetch_id)
VALUES (%(device_id)s, %(name)s, %(status)s, %(device_type)s, %(fw_version)s,
        %(health)s, %(last_seen)s, %(brand)s, %(region)s, %(model)s, %(menu)s,
        TRUE, %(fetch_id)s)
ON CONFLICT (device_id) DO UPDATE SET
    name          = EXCLUDED.name,
    status        = EXCLUDED.status,
    device_type   = EXCLUDED.device_type,
    fw_version    = EXCLUDED.fw_version,
    health        = EXCLUDED.health,
    last_seen     = EXCLUDED.last_seen,
    brand         = EXCLUDED.brand,
    region        = EXCLUDED.region,
    model         = EXCLUDED.model,
    menu          = EXCLUDED.menu,
    is_present    = TRUE,
    last_fetch_id = EXCLUDED.last_fetch_id
"""


def connect():
    """Mo connection moi. autocommit=False de moi fetch la 1 transaction."""
    return psycopg.connect(settings.DB_DSN, row_factory=dict_row)


def init_schema(conn) -> None:
    """Chay schema (idempotent - toan bo dung IF NOT EXISTS / OR REPLACE)."""
    sql = SCHEMA_FILE.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    log.info("Schema da san sang")


def is_empty(conn) -> bool:
    """DB chua co thiet bi nao -> day la lan chay dau tien."""
    with conn.cursor() as cur:
        cur.execute("SELECT NOT EXISTS (SELECT 1 FROM devices) AS empty")
        return bool(cur.fetchone()["empty"])


def start_run(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("INSERT INTO fetch_runs (started_at) VALUES (now()) RETURNING id")
        run_id = cur.fetchone()["id"]
    conn.commit()
    return run_id


def finish_run(conn, run_id: int, *, ok: bool, total_records=None,
               stored_count=None, online_count=None, offline_count=None,
               excluded_count=None, error_msg=None) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE fetch_runs SET
                finished_at    = now(),
                duration_ms    = EXTRACT(EPOCH FROM (now() - started_at)) * 1000,
                ok             = %s,
                total_records  = %s,
                stored_count   = %s,
                online_count   = %s,
                offline_count  = %s,
                excluded_count = %s,
                error_msg      = %s
            WHERE id = %s
            """,
            (ok, total_records, stored_count, online_count, offline_count,
             excluded_count, error_msg, run_id),
        )
    conn.commit()


def sync_devices(conn, run_id: int, devices: list) -> int:
    """
    UPSERT toan bo thiet bi cua lan fetch nay, roi danh dau nhung thiet bi
    khong con xuat hien trong feed la is_present = FALSE.

    Tra ve so thiet bi vua bien mat khoi feed.
    """
    rows = [dict(d, fetch_id=run_id) for d in devices]

    with conn.cursor() as cur:
        if rows:
            cur.executemany(_UPSERT, rows)

        # Thiet bi ton tai trong DB nhung khong co trong lan fetch nay.
        # Khong doi status (khong biet thuc te the nao) - chi ha co is_present.
        cur.execute(
            """
            UPDATE devices SET is_present = FALSE
            WHERE is_present
              AND (last_fetch_id IS DISTINCT FROM %s)
            """,
            (run_id,),
        )
        vanished = cur.rowcount

    conn.commit()
    return vanished


def pending_offline_events(conn, max_age_hours: int) -> list:
    """
    Cac event can gui notification: thiet bi chuyen sang Off (tu On, hoac lan
    dau thay no da Off) ma chua gui duoc.

    KHONG gioi han theo fetch_id cua run hien tai: neu lan truoc gui Bitrix
    that bai thi event van con notified=FALSE va se duoc thu lai o chu trinh sau.
    Gioi han theo tuoi de khong gui lai nhung event qua cu (vi du monitor tat
    may ngay roi bat lai).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT e.id, e.device_id, e.old_status, e.new_status, e.changed_at,
                   e.last_seen, d.name, d.region, d.model, d.menu
            FROM status_events e
            JOIN devices d USING (device_id)
            WHERE e.new_status = 'Off'
              AND NOT e.notified
              AND e.changed_at > now() - make_interval(hours => %s)
            ORDER BY e.changed_at, d.name
            """,
            (max_age_hours,),
        )
        return cur.fetchall()


def discard_stale_events(conn, max_age_hours: int) -> int:
    """
    Danh dau cac event Off qua cu (vuot max_age_hours) la da xu ly, de chung
    khong nam mai trong danh sach cho. Tra ve so event bi bo qua.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE status_events SET notified = TRUE, notified_at = now()
            WHERE new_status = 'Off'
              AND NOT notified
              AND changed_at <= now() - make_interval(hours => %s)
            """,
            (max_age_hours,),
        )
        discarded = cur.rowcount
    conn.commit()
    return discarded


def mark_notified(conn, event_ids: list) -> None:
    if not event_ids:
        return
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE status_events SET notified = TRUE, notified_at = now() WHERE id = ANY(%s)",
            (list(event_ids),),
        )
    conn.commit()


def offline_now(conn) -> list:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT device_id, name, region, model, menu, last_seen, status_changed_at,
                   -- Thoi gian offline thuc te tinh tu last_seen cua thiet bi.
                   -- status_changed_at chi la luc monitor GHI NHAN, nen voi thiet
                   -- bi da Off truoc khi monitor chay thi no khong phan anh dung.
                   COALESCE(now() - last_seen, now() - status_changed_at) AS offline_duration
            FROM devices
            WHERE status = 'Off' AND is_present
            ORDER BY COALESCE(last_seen, status_changed_at)
            """
        )
        return cur.fetchall()


def last_successful_fetch(conn):
    """
    Thoi diem lan fetch thanh cong gan nhat, hoac None neu chua co lan nao.
    Dung de do khoang trong quan sat khi monitor vua chay lai.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT max(finished_at) AS at FROM fetch_runs WHERE ok")
        return cur.fetchone()["at"]


def present_count(conn) -> int:
    """So thiet bi dang co trong feed."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM devices WHERE is_present")
        return int(cur.fetchone()["n"])


def recent_failures(conn, limit: int) -> int:
    """Dem so lan fetch that bai lien tiep gan nhat."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT ok FROM fetch_runs
            WHERE finished_at IS NOT NULL
            ORDER BY id DESC LIMIT %s
            """,
            (limit,),
        )
        streak = 0
        for row in cur.fetchall():
            if row["ok"]:
                break
            streak += 1
        return streak
