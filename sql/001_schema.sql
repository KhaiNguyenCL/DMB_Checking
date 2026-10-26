-- ============================================================
-- DMB Device Monitor - Schema (mo hinh hybrid)
--   devices       : trang thai hien tai, UPSERT moi lan fetch
--   status_events : chi ghi khi co chuyen trang thai On <-> Off
--   fetch_runs    : metadata moi lan fetch (dung cho Grafana + debug)
-- ============================================================

CREATE TABLE IF NOT EXISTS fetch_runs (
    id             BIGSERIAL PRIMARY KEY,
    started_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at    TIMESTAMPTZ,
    duration_ms    INTEGER,
    total_records  INTEGER,   -- recordsTotal tu API (tat ca region)
    stored_count   INTEGER,   -- so device da ghi vao DB (sau khi loc region)
    online_count   INTEGER,
    offline_count  INTEGER,
    excluded_count INTEGER,   -- so device bi loai boi Exception_list
    ok             BOOLEAN NOT NULL DEFAULT FALSE,
    error_msg      TEXT
);

COMMENT ON TABLE fetch_runs IS 'Mot dong moi lan monitor goi API';

CREATE TABLE IF NOT EXISTS devices (
    device_id         TEXT PRIMARY KEY,          -- idx 12 cua API (KHONG dung idx 13)
    name              TEXT,                      -- idx 1
    status            TEXT NOT NULL,             -- idx 2  On / Off
    device_type       TEXT,                      -- idx 3  'Unknown 57', 'AIO 353'...
    fw_version        TEXT,                      -- idx 4
    health            TEXT,                      -- idx 5  Normal / Unknown
    last_seen         TIMESTAMPTZ,               -- idx 6  (gio local thiet bi -> da convert)
    brand             TEXT,                      -- idx 7
    region            TEXT,                      -- idx 8
    model             TEXT,                      -- idx 9
    menu              TEXT,                      -- idx 10
    is_present        BOOLEAN NOT NULL DEFAULT TRUE,  -- FALSE = bien mat khoi API feed
    first_seen_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    status_changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_fetch_id     BIGINT REFERENCES fetch_runs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS devices_status_idx      ON devices (status);
CREATE INDEX IF NOT EXISTS devices_region_idx      ON devices (region);
CREATE INDEX IF NOT EXISTS devices_offline_idx     ON devices (status_changed_at DESC) WHERE status = 'Off';
CREATE INDEX IF NOT EXISTS devices_not_present_idx ON devices (updated_at DESC) WHERE NOT is_present;

CREATE TABLE IF NOT EXISTS status_events (
    id          BIGSERIAL PRIMARY KEY,
    device_id   TEXT NOT NULL REFERENCES devices (device_id) ON DELETE CASCADE,
    old_status  TEXT,                       -- NULL = lan dau thay thiet bi nay
    new_status  TEXT NOT NULL,
    changed_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen   TIMESTAMPTZ,
    fetch_id    BIGINT REFERENCES fetch_runs (id) ON DELETE SET NULL,
    notified    BOOLEAN NOT NULL DEFAULT FALSE,
    notified_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS status_events_device_idx   ON status_events (device_id, changed_at DESC);
CREATE INDEX IF NOT EXISTS status_events_time_idx     ON status_events (changed_at DESC);
CREATE INDEX IF NOT EXISTS status_events_fetch_idx    ON status_events (fetch_id);
CREATE INDEX IF NOT EXISTS status_events_pending_idx  ON status_events (changed_at) WHERE NOT notified;

-- ------------------------------------------------------------
-- Trigger: tu dong ghi status_events khi status doi
-- Lam o DB thay vi o Python de dam bao atomic va khong bo sot
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION devices_touch() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := now();
    IF NEW.status IS DISTINCT FROM OLD.status THEN
        NEW.status_changed_at := now();
    ELSE
        NEW.status_changed_at := OLD.status_changed_at;
    END IF;
    NEW.first_seen_at := OLD.first_seen_at;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION devices_log_status() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO status_events (device_id, old_status, new_status, changed_at, last_seen, fetch_id)
        VALUES (NEW.device_id, NULL, NEW.status, NEW.status_changed_at, NEW.last_seen, NEW.last_fetch_id);
    ELSIF NEW.status IS DISTINCT FROM OLD.status THEN
        INSERT INTO status_events (device_id, old_status, new_status, changed_at, last_seen, fetch_id)
        VALUES (NEW.device_id, OLD.status, NEW.status, NEW.status_changed_at, NEW.last_seen, NEW.last_fetch_id);
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devices_touch_trg ON devices;
CREATE TRIGGER devices_touch_trg
    BEFORE UPDATE ON devices
    FOR EACH ROW EXECUTE FUNCTION devices_touch();

DROP TRIGGER IF EXISTS devices_log_status_trg ON devices;
CREATE TRIGGER devices_log_status_trg
    AFTER INSERT OR UPDATE ON devices
    FOR EACH ROW EXECUTE FUNCTION devices_log_status();

-- ------------------------------------------------------------
-- View tien dung cho Grafana / query tay
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_offline_now AS
SELECT device_id, name, region, model, menu, fw_version,
       last_seen, status_changed_at,
       -- Tinh tu last_seen: status_changed_at chi la luc monitor ghi nhan
       COALESCE(now() - last_seen, now() - status_changed_at) AS offline_duration
FROM devices
WHERE status = 'Off' AND is_present
ORDER BY COALESCE(last_seen, status_changed_at);

CREATE OR REPLACE VIEW v_flapping_7d AS
SELECT d.device_id, d.name, d.region, count(*) AS "so_lan_doi_trang_thai"
FROM status_events e
JOIN devices d USING (device_id)
WHERE e.changed_at > now() - INTERVAL '7 days'
  AND e.old_status IS NOT NULL
GROUP BY d.device_id, d.name, d.region
ORDER BY so_lan_doi_trang_thai DESC;
