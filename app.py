#!/usr/bin/env python3
"""
DNSWatch v2 — anomaly detection on top of AdGuard Home (consolidated build).

Rules:
  HIGH_ENTROPY   : random-looking domain that ALSO did not resolve (true DGA tell)
  NXDOMAIN_SPIKE : high ratio of failed (NXDOMAIN) lookups from one client
  BURST          : a client flooding DNS — now reports its top domains
  NEW_DOMAIN     : odd, short, brand-new non-resolving domains

Plus: env ALLOWLIST + persistent UI whitelist, cooldown dedup, auto-prune,
ntfy phone alerts, one-click block and one-click whitelist.

Env (in .env, passed via docker-compose):
  ADGUARD_URL ADGUARD_USER ADGUARD_PASS POLL_INTERVAL=30 ENTROPY_THRESHOLD=3.6
  BURST_THRESHOLD=600 BURST_WINDOW=60 NX_RATIO=0.4 NX_MIN=20
  COOLDOWN=1800 RETENTION_DAYS=7
  NTFY_URL=https://ntfy.sh NTFY_TOPIC=... NTFY_COOLDOWN=600
  ALLOWLIST=comma,separated DB_PATH=/app/data/dnswatch.db
"""
import os, math, time, json, sqlite3, threading, collections
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import request as urlrequest, parse as urlparse, error as urlerror

ADGUARD_URL = os.environ.get("ADGUARD_URL", "http://adguardhome").rstrip("/")
ADGUARD_USER = os.environ.get("ADGUARD_USER", "")
ADGUARD_PASS = os.environ.get("ADGUARD_PASS", "")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "30"))
ENTROPY_THRESHOLD = float(os.environ.get("ENTROPY_THRESHOLD", "3.6"))
BURST_THRESHOLD = int(os.environ.get("BURST_THRESHOLD", "600"))
# Trusted/whitelisted domains are counted in a SEPARATE burst tally against this
# higher bar — so normal whitelisted telemetry stays quiet, but a trusted domain
# going genuinely berserk (possible hijack / DNS tunnelling) still surfaces.
BURST_TRUSTED_THRESHOLD = int(os.environ.get("BURST_TRUSTED_THRESHOLD", "2000"))
BURST_WINDOW = int(os.environ.get("BURST_WINDOW", "60"))
NX_RATIO = float(os.environ.get("NX_RATIO", "0.4"))
NX_MIN = int(os.environ.get("NX_MIN", "20"))
COOLDOWN = int(os.environ.get("COOLDOWN", "1800"))
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "7"))
NTFY_URL = os.environ.get("NTFY_URL", "https://ntfy.sh").rstrip("/")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")
NTFY_COOLDOWN = int(os.environ.get("NTFY_COOLDOWN", "600"))
ENV_ALLOWLIST = set(d.strip().lower() for d in os.environ.get("ALLOWLIST", "").split(",") if d.strip())
DB_PATH = os.environ.get("DB_PATH", "/app/data/dnswatch.db")

COMMON_TLD_SUFFIXES = (".arpa", ".local", ".lan", ".home")
_db_lock = threading.Lock()
_last_notify = {}
_burst = collections.defaultdict(collections.deque)
_burst_trusted = collections.defaultdict(collections.deque)


def db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with _db_lock, db() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS seen_domains (
                client TEXT, domain TEXT, first_seen TEXT,
                PRIMARY KEY (client, domain));
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT, client TEXT, domain TEXT, rule TEXT, detail TEXT,
                score INTEGER, trusted INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS stats (
                bucket TEXT PRIMARY KEY, queries INTEGER DEFAULT 0,
                blocked INTEGER DEFAULT 0, nxdomain INTEGER DEFAULT 0, flagged INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS whitelist (domain TEXT PRIMARY KEY, added TEXT);
            CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
            CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
        """)
        # migration: add trusted column if upgrading from an older db
        cols = [r[1] for r in c.execute("PRAGMA table_info(events)").fetchall()]
        if "trusted" not in cols:
            c.execute("ALTER TABLE events ADD COLUMN trusted INTEGER DEFAULT 0")


def meta_get(k, default=None):
    with _db_lock, db() as c:
        row = c.execute("SELECT v FROM meta WHERE k=?", (k,)).fetchone()
        return row["v"] if row else default


def meta_set(k, v):
    with _db_lock, db() as c:
        c.execute("INSERT INTO meta(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=?",
                  (k, str(v), str(v)))


def load_whitelist():
    wl = set(ENV_ALLOWLIST)
    try:
        with _db_lock, db() as c:
            for r in c.execute("SELECT domain FROM whitelist"):
                wl.add(r["domain"])
    except Exception:
        pass
    return wl


def shannon_entropy(s):
    if not s:
        return 0.0
    counts = collections.Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def registrable_label(domain):
    parts = [p for p in domain.strip(".").split(".") if p]
    if len(parts) >= 2:
        return parts[-2]
    return parts[0] if parts else domain


def is_whitelisted(domain, wl):
    return domain in wl or any(domain.endswith("." + a) for a in wl)


def bucket_now():
    t = datetime.now(timezone.utc)
    return t.replace(minute=(t.minute // 5) * 5, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M")


def bump_stats(queries=0, blocked=0, nxdomain=0, flagged=0):
    b = bucket_now()
    with _db_lock, db() as c:
        c.execute("INSERT OR IGNORE INTO stats(bucket) VALUES(?)", (b,))
        c.execute("UPDATE stats SET queries=queries+?, blocked=blocked+?, "
                  "nxdomain=nxdomain+?, flagged=flagged+? WHERE bucket=?",
                  (queries, blocked, nxdomain, flagged, b))


def notify(title, message, priority="default", tags="warning"):
    if not NTFY_TOPIC:
        return
    now = time.time()
    if now - _last_notify.get(title, 0) < NTFY_COOLDOWN:
        return
    _last_notify[title] = now
    try:
        req = urlrequest.Request(f"{NTFY_URL}/{NTFY_TOPIC}",
                                 data=message.encode("utf-8"), method="POST")
        req.add_header("Title", title)
        req.add_header("Priority", priority)
        req.add_header("Tags", tags)
        urlrequest.urlopen(req, timeout=10).read()
    except Exception as ex:
        print("ntfy notify failed:", ex)


def record_event(client, domain, rule, detail, score, trusted=False):
    now = datetime.now(timezone.utc)
    ts = now.isoformat()
    with _db_lock, db() as c:
        row = c.execute("SELECT ts FROM events WHERE client=? AND domain=? AND rule=? "
                        "ORDER BY id DESC LIMIT 1", (client, domain, rule)).fetchone()
        if row:
            try:
                if (now - datetime.fromisoformat(row["ts"])).total_seconds() < COOLDOWN:
                    return
            except Exception:
                pass
        c.execute("INSERT INTO events(ts,client,domain,rule,detail,score,trusted) "
                  "VALUES(?,?,?,?,?,?,?)",
                  (ts, client, domain, rule, detail, score, 1 if trusted else 0))
    bump_stats(flagged=1)
    # Notification policy:
    #  - untrusted: notify on all serious rules
    #  - trusted:   stay quiet on routine flags (entropy/new domain), but STILL
    #               notify on behavioral anomalies (burst, nxdomain spike) since
    #               those mean a trusted domain's behavior changed.
    if trusted:
        if rule in ("NXDOMAIN_SPIKE", "BURST"):
            notify(f"DNSWatch: trusted domain anomaly ({rule.replace('_', ' ')})",
                   f"{client} -> {domain}\n{detail}", priority="high", tags="warning")
    else:
        if rule in ("HIGH_ENTROPY", "NXDOMAIN_SPIKE", "BURST"):
            notify(f"DNSWatch: {rule.replace('_', ' ')}",
                   f"{client} -> {domain}\n{detail}", priority="high", tags="rotating_light")


def prune_old():
    cutoff = (datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)).isoformat()
    cutoff_bucket = (datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)).strftime("%Y-%m-%dT%H:%M")
    with _db_lock, db() as c:
        c.execute("DELETE FROM events WHERE ts < ?", (cutoff,))
        c.execute("DELETE FROM stats WHERE bucket < ?", (cutoff_bucket,))


def adguard_auth_header():
    import base64
    return "Basic " + base64.b64encode(f"{ADGUARD_USER}:{ADGUARD_PASS}".encode()).decode()


def fetch_querylog(limit=500):
    url = f"{ADGUARD_URL}/control/querylog?" + urlparse.urlencode({"limit": str(limit)})
    req = urlrequest.Request(url)
    if ADGUARD_USER:
        req.add_header("Authorization", adguard_auth_header())
    with urlrequest.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def process_entries(entries):
    now = time.time()
    nx_counter = collections.defaultdict(lambda: [0, 0])
    wl = load_whitelist()
    for e in entries:
        domain = (e.get("question", {}) or {}).get("name", "").rstrip(".").lower()
        if not domain or domain.endswith(COMMON_TLD_SUFFIXES):
            continue
        trusted = is_whitelisted(domain, wl)
        client = e.get("client", "?")
        reason = e.get("reason", "")
        is_blocked = reason.startswith("Filtered")
        ans = e.get("answer") or []
        is_nx = (e.get("status", "") == "NXDOMAIN") or (
            not is_blocked and not ans and reason == "NotFilteredNotFound")
        bump_stats(queries=1, blocked=1 if is_blocked else 0, nxdomain=1 if is_nx else 0)
        if is_blocked:
            continue
        with _db_lock, db() as c:
            seen = c.execute("SELECT 1 FROM seen_domains WHERE client=? AND domain=?",
                             (client, domain)).fetchone()
            if not seen:
                c.execute("INSERT OR IGNORE INTO seen_domains(client,domain,first_seen) "
                          "VALUES(?,?,?)", (client, domain, datetime.now(timezone.utc).isoformat()))
        label = registrable_label(domain)
        ent = shannon_entropy(label)
        if not seen and ent >= ENTROPY_THRESHOLD and 8 <= len(label) < 10 and is_nx:
            record_event(client, domain, "NEW_DOMAIN", f"first time seen, entropy {ent:.2f}", 2, trusted)
        if len(label) >= 10 and is_nx and ent >= ENTROPY_THRESHOLD:
            record_event(client, domain, "HIGH_ENTROPY",
                         f"label '{label}' entropy {ent:.2f}, did not resolve", 3, trusted)
        # Burst tracking — trusted and untrusted domains counted in SEPARATE
        # tallies. Whitelisted telemetry (brave/meta/etc) no longer inflates the
        # normal burst count, so it can sit at a sane threshold; but a trusted
        # domain flooding past BURST_TRUSTED_THRESHOLD still fires as a trusted
        # anomaly (the "trusting isn't ignoring" path in record_event).
        if trusted:
            dqt = _burst_trusted[client]
            dqt.append((now, domain))
            while dqt and now - dqt[0][0] > BURST_WINDOW:
                dqt.popleft()
            if len(dqt) == BURST_TRUSTED_THRESHOLD:
                top = collections.Counter(d for _, d in dqt).most_common(3)
                record_event(client, "(burst)", "BURST",
                             f"{len(dqt)} queries in {BURST_WINDOW}s (trusted) — top: " +
                             ", ".join(f"{d} ({n})" for d, n in top), 2, trusted=True)
        else:
            dq = _burst[client]
            dq.append((now, domain))
            while dq and now - dq[0][0] > BURST_WINDOW:
                dq.popleft()
            if len(dq) == BURST_THRESHOLD:
                top = collections.Counter(d for _, d in dq).most_common(3)
                record_event(client, "(burst)", "BURST",
                             f"{len(dq)} queries in {BURST_WINDOW}s — top: " +
                             ", ".join(f"{d} ({n})" for d, n in top), 2)
        nx_counter[client][0] += 1
        if is_nx:
            nx_counter[client][1] += 1
    for client, (total, nx) in nx_counter.items():
        if total >= NX_MIN and (nx / total) >= NX_RATIO:
            record_event(client, "(multiple)", "NXDOMAIN_SPIKE",
                         f"{nx}/{total} lookups failed as NXDOMAIN ({nx/total:.0%})", 3)


def poller():
    if meta_get("baseline_done") is None:
        try:
            data = fetch_querylog(limit=500)
            for e in data.get("data", []):
                domain = (e.get("question", {}) or {}).get("name", "").rstrip(".").lower()
                client = e.get("client", "?")
                if domain:
                    with _db_lock, db() as c:
                        c.execute("INSERT OR IGNORE INTO seen_domains(client,domain,first_seen) "
                                  "VALUES(?,?,?)", (client, domain, datetime.now(timezone.utc).isoformat()))
            meta_set("baseline_done", "1")
        except Exception as ex:
            meta_set("status", f"error: {ex}")
    while True:
        try:
            data = fetch_querylog(limit=500)
            process_entries(data.get("data", []))
            prune_old()
            meta_set("status", "ok")
            meta_set("last_poll", datetime.now(timezone.utc).isoformat())
        except urlerror.HTTPError as ex:
            meta_set("status", f"auth/HTTP error {ex.code} — check ADGUARD_USER/PASS/URL")
        except Exception as ex:
            meta_set("status", f"error: {ex}")
        time.sleep(POLL_INTERVAL)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass

    def _adguard_post(self, path, payload):
        body = json.dumps(payload).encode()
        req = urlrequest.Request(f"{ADGUARD_URL}{path}", data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        if ADGUARD_USER:
            req.add_header("Authorization", adguard_auth_header())
        return urlrequest.urlopen(req, timeout=15).read()

    def do_GET(self):
        p = urlparse.urlparse(self.path)
        if p.path in ("/", "/index.html"):
            try:
                with open("/app/static/index.html", "rb") as f:
                    self._send(200, f.read().decode(), "text/html; charset=utf-8")
            except FileNotFoundError:
                self._send(404, "ui missing")
            return
        if p.path == "/api/health":
            self._send(200, {"status": "ok"}); return
        if p.path == "/api/status":
            self._send(200, {"status": meta_get("status", "starting"),
                             "last_poll": meta_get("last_poll"), "adguard_url": ADGUARD_URL}); return
        if p.path == "/api/timeline":
            with _db_lock, db() as c:
                rows = c.execute("SELECT * FROM stats ORDER BY bucket DESC LIMIT 288").fetchall()
            self._send(200, [dict(r) for r in reversed(rows)]); return
        if p.path == "/api/events":
            q = urlparse.parse_qs(p.query)
            limit = int(q.get("limit", ["100"])[0])
            with _db_lock, db() as c:
                rows = c.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            self._send(200, [dict(r) for r in rows]); return
        if p.path == "/api/restart":
            self._send(200, {"ok": True})
            import threading
            # Wait half a second to send the 'ok' response, then intentionally crash
            threading.Timer(0.5, lambda: os._exit(0)).start()
            return
        if p.path == "/api/whitelist":
            with _db_lock, db() as c:
                rows = c.execute("SELECT domain, added FROM whitelist ORDER BY added DESC").fetchall()
            self._send(200, {"env": sorted(ENV_ALLOWLIST), "user": [dict(r) for r in rows]}); return
        if p.path == "/api/summary":
            with _db_lock, db() as c:
                by_rule = c.execute("SELECT rule, COUNT(*) n FROM events GROUP BY rule").fetchall()
                by_client = c.execute("SELECT client, COUNT(*) n FROM events GROUP BY client "
                                      "ORDER BY n DESC LIMIT 10").fetchall()
                totals = c.execute("SELECT COALESCE(SUM(queries),0) q, COALESCE(SUM(blocked),0) b, "
                                   "COALESCE(SUM(flagged),0) f FROM stats").fetchone()
            self._send(200, {"by_rule": [dict(r) for r in by_rule],
                             "by_client": [dict(r) for r in by_client], "totals": dict(totals)}); return
        if p.path == "/api/blocked":
            # Report which domains are currently blocked via a ||domain^ user rule
            # in AdGuard, so the UI can render Block/Unblock correctly after reload.
            try:
                getreq = urlrequest.Request(f"{ADGUARD_URL}/control/filtering/status")
                if ADGUARD_USER:
                    getreq.add_header("Authorization", adguard_auth_header())
                with urlrequest.urlopen(getreq, timeout=15) as r:
                    cur = json.loads(r.read().decode())
                domains = []
                for raw in cur.get("user_rules", []):
                    rule = (raw or "").strip()
                    if rule.startswith("||") and rule.endswith("^"):
                        domains.append(rule[2:-1])
                self._send(200, {"blocked": domains})
            except Exception as ex:
                self._send(500, {"error": str(ex), "blocked": []})
            return
        self._send(404, {"error": "not found"})

    def do_POST(self):
        p = urlparse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or "{}")
        domain = (payload.get("domain", "") or "").strip().lower()
        if p.path == "/api/block":
            if not domain or domain.startswith("("):
                self._send(400, {"error": "no valid domain"}); return
            rule = f"||{domain}^"
            try:
                getreq = urlrequest.Request(f"{ADGUARD_URL}/control/filtering/status")
                if ADGUARD_USER:
                    getreq.add_header("Authorization", adguard_auth_header())
                with urlrequest.urlopen(getreq, timeout=15) as r:
                    cur = json.loads(r.read().decode())
                existing = cur.get("user_rules", [])
                if rule not in existing:
                    existing.append(rule)
                self._adguard_post("/control/filtering/set_rules", {"rules": existing})
                self._send(200, {"ok": True, "rule": rule})
            except Exception as ex:
                self._send(500, {"error": str(ex)})
            return
        if p.path == "/api/unblock":
            if not domain or domain.startswith("("):
                self._send(400, {"error": "no valid domain"}); return
            rule = f"||{domain}^"
            try:
                getreq = urlrequest.Request(f"{ADGUARD_URL}/control/filtering/status")
                if ADGUARD_USER:
                    getreq.add_header("Authorization", adguard_auth_header())
                with urlrequest.urlopen(getreq, timeout=15) as r:
                    cur = json.loads(r.read().decode())
                existing = cur.get("user_rules", [])
                filtered = [x for x in existing if (x or "").strip() != rule]
                self._adguard_post("/control/filtering/set_rules", {"rules": filtered})
                self._send(200, {"ok": True, "removed": rule})
            except Exception as ex:
                self._send(500, {"error": str(ex)})
            return
        if p.path == "/api/restart":
            self._send(200, {"ok": True})
            import threading
            # Wait half a second to send the 'ok' response, then intentionally crash
            threading.Timer(0.5, lambda: os._exit(0)).start()
            return
        if p.path == "/api/whitelist":
            if not domain or domain.startswith("("):
                self._send(400, {"error": "no valid domain"}); return
            try:
                with _db_lock, db() as c:
                    c.execute("INSERT OR IGNORE INTO whitelist(domain,added) VALUES(?,?)",
                              (domain, datetime.now(timezone.utc).isoformat()))
                    # keep existing events visible (they'll render as TRUSTED);
                    # the domain just won't generate new flags or notifications.
                self._send(200, {"ok": True, "whitelisted": domain})
            except Exception as ex:
                self._send(500, {"error": str(ex)})
            return
        if p.path == "/api/unwhitelist":
            try:
                with _db_lock, db() as c:
                    c.execute("DELETE FROM whitelist WHERE domain=?", (domain,))
                self._send(200, {"ok": True, "removed": domain})
            except Exception as ex:
                self._send(500, {"error": str(ex)})
            return
        if p.path == "/api/clear_events":
            try:
                with _db_lock, db() as c:
                    c.execute("DELETE FROM events")
                self._send(200, {"ok": True, "cleared": True})
            except Exception as ex:
                self._send(500, {"error": str(ex)})
            return
        self._send(404, {"error": "not found"})


def main():
    init_db()
    threading.Thread(target=poller, daemon=True).start()
    srv = ThreadingHTTPServer(("0.0.0.0", 8090), Handler)
    print("DNSWatch v2 listening on :8090")
    srv.serve_forever()


if __name__ == "__main__":
    main()
