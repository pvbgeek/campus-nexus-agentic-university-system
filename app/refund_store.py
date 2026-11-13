"""Local synthetic refund ledger. All amounts are integer USD cents."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import sqlite3
import uuid

POLICY_VERSION = "refund-v1"


def week_start():
    now = datetime.now(timezone.utc)
    return (now - timedelta(days=now.weekday())).date().isoformat()


class RefundStore:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY, customer TEXT NOT NULL,
                    total INTEGER NOT NULL, supervisor_denied INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS control (
                    id INTEGER PRIMARY KEY CHECK(id=1), active INTEGER NOT NULL
                );
                INSERT OR IGNORE INTO control VALUES (1,1);
                CREATE TABLE IF NOT EXISTS refunds (
                    id TEXT PRIMARY KEY, customer TEXT NOT NULL, order_id TEXT NOT NULL,
                    amount INTEGER NOT NULL, week TEXT NOT NULL, request_key TEXT NOT NULL,
                    UNIQUE(customer,request_key)
                );
                CREATE TABLE IF NOT EXISTS accounts (
                    customer TEXT PRIMARY KEY, destination TEXT NOT NULL,
                    balance INTEGER NOT NULL DEFAULT 0
                );
                INSERT OR IGNORE INTO accounts VALUES ('CUST-001','mock-account-0042',0);
                INSERT OR IGNORE INTO accounts VALUES ('CUST-002','mock-account-0077',0);
                CREATE TABLE IF NOT EXISTS audit (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL, trace_id TEXT NOT NULL, event TEXT NOT NULL,
                    details TEXT NOT NULL
                );
            """)
            db.executemany("INSERT OR IGNORE INTO orders(id,customer,total) VALUES (?,?,?)", [
                ("NX-2048", "CUST-001", 7600),
                ("NX-2049", "CUST-001", 20000),
                ("NX-2050", "CUST-002", 9000),
            ])

    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        return db

    def execute(self, customer, order_id, amount_cents, request_key, case_id=None):
        """Customer identity must come from authenticated server context, never model text."""
        trace = str(uuid.uuid4())
        db = self.connect()
        try:
            db.execute("BEGIN IMMEDIATE")

            def event(name, **details):
                db.execute("INSERT INTO audit(timestamp,trace_id,event,details) VALUES (?,?,?,?)", (
                    datetime.now(timezone.utc).isoformat(), trace, name,
                    json.dumps(dict(policy_version=POLICY_VERSION, case_id=case_id, **details)),
                ))

            def finish(status, reason, **extra):
                event("authorization", status=status, reason=reason)
                db.commit()
                return dict(status=status, reason=reason, trace_id=trace, **extra)

            event("refund_attempt", actor=customer, order_id=order_id, amount_cents=amount_cents)
            if type(amount_cents) is not int or amount_cents <= 0:
                return finish("blocked", "invalid_amount")
            if not isinstance(request_key, str) or not 1 <= len(request_key) <= 128:
                return finish("blocked", "invalid_request_key")
            order = db.execute("SELECT * FROM orders WHERE id=? AND customer=?", (order_id, customer)).fetchone()
            if order is None:
                return finish("blocked", "order_not_accessible")
            previous = db.execute("SELECT * FROM refunds WHERE customer=? AND request_key=?", (customer, request_key)).fetchone()
            if previous:
                if previous["order_id"] != order_id or previous["amount"] != amount_cents:
                    return finish("blocked", "idempotency_conflict")
                return finish("replayed", "already_executed", refund_id=previous["id"])
            if not db.execute("SELECT active FROM control WHERE id=1").fetchone()[0]:
                return finish("blocked", "authority_revoked")
            if order["supervisor_denied"]:
                return finish("blocked", "supervisor_denied")
            if amount_cents > 10000:
                return finish("review_required", "transaction_limit")
            refunded = db.execute("SELECT COALESCE(SUM(amount),0) FROM refunds WHERE order_id=?", (order_id,)).fetchone()[0]
            if refunded + amount_cents > order["total"]:
                return finish("blocked", "order_balance_exceeded")
            week = week_start()
            used = db.execute("SELECT COALESCE(SUM(amount),0) FROM refunds WHERE week=?", (week,)).fetchone()[0]
            if used + amount_cents > 50000:
                return finish("review_required", "weekly_limit")
            refund_id = str(uuid.uuid4())
            event("authorization", status="allowed", reason="within_authority")
            db.execute("INSERT INTO refunds VALUES (?,?,?,?,?,?)", (refund_id, customer, order_id, amount_cents, week, request_key))
            account = db.execute("SELECT destination FROM accounts WHERE customer=?", (customer,)).fetchone()
            if account is None:
                raise RuntimeError("Synthetic account is missing; transaction rolled back.")
            db.execute("UPDATE accounts SET balance=balance+? WHERE customer=?", (amount_cents, customer))
            event("mock_refund_executed", refund_id=refund_id, amount_cents=amount_cents,
                  destination=account["destination"],
                  order_remaining_cents=order["total"] - refunded - amount_cents,
                  weekly_used_cents=used + amount_cents)
            db.commit()
            return dict(status="executed", reason="within_authority", trace_id=trace,
                        refund_id=refund_id, amount_cents=amount_cents,
                        order_remaining_cents=order["total"] - refunded - amount_cents)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
