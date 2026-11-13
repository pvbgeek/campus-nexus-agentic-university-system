"""Shared transactional storage for the UI, agent graph and scoped MCP tools."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import os
import uuid
from app.refund_store import RefundStore, POLICY_VERSION, week_start

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("CAMPUS_NEXUS_DATA", str(ROOT / "data"))).resolve()
store = RefundStore(DATA / "campus.sqlite3")


@contextmanager
def database(write=False):
    db = store.connect()
    try:
        if write:
            db.execute("BEGIN IMMEDIATE")
        yield db
        if write:
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


with database() as db:
    db.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            digest TEXT PRIMARY KEY, actor TEXT NOT NULL, role TEXT NOT NULL,
            csrf TEXT NOT NULL, expires REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY, customer TEXT NOT NULL, order_id TEXT NOT NULL,
            amount INTEGER NOT NULL, reason TEXT NOT NULL, details TEXT NOT NULL,
            status TEXT NOT NULL, decision_reason TEXT NOT NULL,
            request_key TEXT NOT NULL, created TEXT NOT NULL,
            evidence_verified INTEGER NOT NULL DEFAULT 0
        );
        CREATE UNIQUE INDEX IF NOT EXISTS unique_case_request ON cases(customer,request_key);
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY, case_id TEXT NOT NULL, customer TEXT NOT NULL,
            kind TEXT NOT NULL, body TEXT NOT NULL, created TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS login_failures (
            peer TEXT PRIMARY KEY, attempts INTEGER NOT NULL, first_seen REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS agent_runs (
            id TEXT PRIMARY KEY, case_id TEXT NOT NULL, status TEXT NOT NULL,
            started TEXT NOT NULL, updated TEXT NOT NULL, state_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS order_evidence (
            order_id TEXT PRIMARY KEY, delivered TEXT NOT NULL, source TEXT NOT NULL
        );
    """)
    delivered = (datetime.now(timezone.utc) - timedelta(days=9)).date().isoformat()
    db.executemany("INSERT OR IGNORE INTO order_evidence VALUES (?,?,?)", [
        (order_id, delivered, "synthetic_demo_fixture") for order_id in ("NX-2048", "NX-2049", "NX-2050")
    ])
    db.commit()


def now():
    return datetime.now(timezone.utc).isoformat()


def audit(db, trace, event, **details):
    db.execute("INSERT INTO audit(timestamp,trace_id,event,details) VALUES (?,?,?,?)", (
        now(), trace, event, json.dumps(dict(policy_version=POLICY_VERSION, **details))))


def notify(db, case, kind, body):
    db.execute("INSERT INTO messages VALUES (?,?,?,?,?,?)", (
        str(uuid.uuid4()), case["id"], case["customer"], kind, body, now()))
    audit(db, str(uuid.uuid4()), "mock_email", case_id=case["id"], kind=kind,
          transport="database_only", recipient=case["customer"])
