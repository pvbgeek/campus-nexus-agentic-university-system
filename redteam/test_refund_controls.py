"""Independent refund boundary tests using isolated synthetic SQLite fixtures."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.refund_store import RefundStore, week_start

EVIDENCE = []


class RefundControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = RefundStore(Path(self.temp.name) / "refunds.sqlite3")
        self.observed = []

    def tearDown(self):
        with self.store.connect() as db:
            audit = [dict(row) for row in db.execute("SELECT * FROM audit ORDER BY sequence")]
            ledger = [dict(row) for row in db.execute("SELECT * FROM refunds ORDER BY id")]
        EVIDENCE.append(dict(test_id=self.id(), observed=self.observed,
                             audit=audit, ledger=ledger))
        self.temp.cleanup()

    def attempt(self, amount=6400, key="request-1", customer="CUST-001", order="NX-2048"):
        result = self.store.execute(customer, order, amount, key)
        self.observed.append(result)
        return result

    def test_valid_refund(self):
        result = self.attempt()
        self.assertEqual(result["status"], "executed")
        self.assertEqual(result["order_remaining_cents"], 1200)

    def test_cross_customer_access(self):
        self.assertEqual(self.attempt(customer="CUST-002")["reason"], "order_not_accessible")

    def test_transaction_limit(self):
        self.assertEqual(self.attempt(amount=10001, order="NX-2049")["reason"], "transaction_limit")

    def test_exact_transaction_limit(self):
        self.assertEqual(self.attempt(amount=10000, order="NX-2049")["status"], "executed")

    def test_duplicate_replay(self):
        first = self.attempt()
        second = self.attempt()
        self.assertEqual(second["status"], "replayed")
        self.assertEqual(first["refund_id"], second["refund_id"])
        with self.store.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM refunds").fetchone()[0], 1)

    def test_duplicate_conflict(self):
        self.attempt()
        self.assertEqual(self.attempt(amount=1200)["reason"], "idempotency_conflict")

    def test_remaining_balance(self):
        self.attempt()
        self.assertEqual(self.attempt(amount=1201, key="second")["reason"], "order_balance_exceeded")

    def test_revoked_authority(self):
        with self.store.connect() as db:
            db.execute("UPDATE control SET active=0 WHERE id=1")
        self.assertEqual(self.attempt()["reason"], "authority_revoked")

    def test_supervisor_denial(self):
        with self.store.connect() as db:
            db.execute("UPDATE orders SET supervisor_denied=1 WHERE id=?", ("NX-2048",))
        self.assertEqual(self.attempt()["reason"], "supervisor_denied")

    def test_invalid_amounts(self):
        for i, value in enumerate([0, -1, 1.5, True, "6400"]):
            self.assertEqual(self.attempt(amount=value, key=str(i))["reason"], "invalid_amount")

    def seed_week(self, amount):
        # Explicit historical synthetic fixture, not an action through the public API.
        with self.store.connect() as db:
            db.execute("INSERT INTO refunds VALUES (?,?,?,?,?,?)",
                       ("fixture", "FIXTURE", "HISTORICAL", amount, week_start(), "fixture"))

    def test_weekly_limit(self):
        self.seed_week(49000)
        self.assertEqual(self.attempt(amount=1001)["reason"], "weekly_limit")
        self.assertEqual(self.attempt(amount=1000, key="exact")["status"], "executed")

    def test_concurrent_weekly_limit(self):
        self.seed_week(45000)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda key: self.store.execute("CUST-001", "NX-2049", 4000, key), ["race-a", "race-b"]))
        self.observed.extend(results)
        self.assertEqual(sorted(r["status"] for r in results), ["executed", "review_required"])
        with self.store.connect() as db:
            self.assertEqual(db.execute("SELECT SUM(amount) FROM refunds WHERE week=?", (week_start(),)).fetchone()[0], 49000)

    def test_concurrent_duplicate(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.store.execute("CUST-001", "NX-2048", 6400, "same-key"), range(2)))
        self.observed.extend(results)
        self.assertEqual(sorted(r["status"] for r in results), ["executed", "replayed"])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RefundControls)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    output = ROOT / "redteam/results/refund-controls.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(dict(
        suite="refund-controls-v1", scope="Local deterministic ledger controls; no LLM or browser tests",
        tests_run=result.testsRun, passed=result.wasSuccessful(),
        failures=[dict(test=str(test), traceback=trace) for test, trace in result.failures + result.errors],
        scenarios=EVIDENCE,
    ), indent=2) + "\n", encoding="utf-8")
    print(f"Evidence: {output}")
    sys.exit(0 if result.wasSuccessful() else 1)
