"""Authenticated UI and API for the live Groq/LangGraph/MCP support workflow."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
from contextlib import contextmanager
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time
import uuid

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, StrictInt
from app.refund_store import POLICY_VERSION, RefundStore, week_start

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
from app.storage import ROOT, DATA, store, database, now, audit, notify

app = FastAPI(title="Campus Nexus Support", docs_url=None, redoc_url=None, openapi_url=None)
COOKIE = "campus_session"
REASONS = {"damaged", "wrong_item", "duplicate_charge"}


def get_case(db, case_id, user):
    row = db.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
    if not row or (user["role"] != "staff" and row["customer"] != user["actor"]):
        audit(db, str(uuid.uuid4()), "case_access", actor=user["actor"], case_id=case_id, outcome="blocked")
        db.commit()
        raise HTTPException(404, "Case not found")
    return row


@app.middleware("http")
async def browser_boundary(request, call_next):
    origin = request.headers.get("origin")
    if request.method not in ("GET", "HEAD", "OPTIONS") and origin:
        expected = f"{request.url.scheme}://{request.url.netloc}"
        if origin != expected:
            return Response("Cross-origin mutation blocked", status_code=403)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["X-Frame-Options"] = "DENY"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


class Body(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Login(Body):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=200)


class Signup(Body):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=12, max_length=200)


with database() as db:
    db.executescript("""
        CREATE TABLE IF NOT EXISTS customer_identities (
            username TEXT PRIMARY KEY,
            actor TEXT NOT NULL UNIQUE,
            salt TEXT NOT NULL,
            digest TEXT NOT NULL
        );
    """)


def demo_identities():
    path = DATA / "identities.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def enforce_signup_limit(request: Request):
    # Count attempts before password hashing. The global budget also
    # protects the service when requests arrive from multiple peers.
    peer = request.client.host if request.client else "unknown"
    window = int(time.time()) // 600
    with database(write=True) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS signup_limits (
            bucket TEXT PRIMARY KEY, window INTEGER NOT NULL, attempts INTEGER NOT NULL
        )""")
        db.execute("DELETE FROM signup_limits WHERE window < ?", (window,))
        for bucket, limit in (("global", 60), ("peer:" + peer, 6)):
            row = db.execute("SELECT attempts FROM signup_limits WHERE bucket=?", (bucket,)).fetchone()
            if row and row["attempts"] >= limit:
                retry = str(max(1, (window + 1) * 600 - int(time.time())))
                raise HTTPException(429, "Too many signup attempts. Try again later.",
                                    headers={"Retry-After": retry})
        for bucket in ("global", "peer:" + peer):
            db.execute("""INSERT INTO signup_limits VALUES (?,?,1)
                ON CONFLICT(bucket) DO UPDATE SET attempts=attempts+1""", (bucket, window))


@app.post("/api/signup", status_code=201)
def signup(body: Signup, request: Request):
    enforce_signup_limit(request)
    username = body.username.strip().lower()
    if not re.fullmatch(r"[a-z0-9_]{3,32}", username):
        raise HTTPException(422, "Use 3 to 32 letters, digits or underscores")
    if username in {"avery", "jordan", "supervisor"} or username in demo_identities():
        raise HTTPException(409, "Username unavailable")
    actor = "CUST-" + uuid.uuid4().hex
    order_id = "NX-" + uuid.uuid4().hex
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", body.password.encode(), salt, 310000).hex()
    delivered = (datetime.now(timezone.utc) - timedelta(days=3)).date().isoformat()
    with database(write=True) as db:
        if db.execute("SELECT 1 FROM customer_identities WHERE username=?", (username,)).fetchone():
            raise HTTPException(409, "Username unavailable")
        db.execute("INSERT INTO customer_identities VALUES (?,?,?,?)",
                   (username, actor, salt.hex(), digest))
        db.execute("INSERT INTO accounts(customer,destination,balance) VALUES (?,?,0)",
                   (actor, "mock-" + actor))
        db.execute("INSERT INTO orders(id,customer,total) VALUES (?,?,7600)", (order_id, actor))
        db.execute("INSERT INTO order_evidence VALUES (?,?,?)",
                   (order_id, delivered, "synthetic_signup_fixture"))
        audit(db, str(uuid.uuid4()), "customer_signup", actor=actor, outcome="created")
    return {"username": username}


class CaseRequest(Body):
    order_id: str = Field(min_length=1, max_length=80)
    amount_cents: StrictInt = Field(gt=0, le=1000000)
    reason: str = Field(min_length=1, max_length=40)
    details: str = Field(min_length=1, max_length=2000)
    request_key: str = Field(min_length=1, max_length=128)


class Decision(Body):
    decision: str
    note: str = Field(min_length=1, max_length=1000)


class Authority(Body):
    active: bool
    note: str = Field(min_length=1, max_length=1000)


@app.post("/api/login")
def login(body: Login, request: Request, response: Response):
    username = body.username.strip().lower()
    user = demo_identities().get(username)
    if user is None:
        with database() as db:
            row = db.execute("SELECT actor,salt,digest FROM customer_identities WHERE username=?",
                             (username,)).fetchone()
        if row is not None:
            user = dict(row, role="customer")
    peer = request.client.host if request.client else "local"
    with database(write=True) as db:
        failure = db.execute("SELECT * FROM login_failures WHERE peer=?", (peer,)).fetchone()
        if failure and failure["first_seen"] > time.time() - 300 and failure["attempts"] >= 10:
            raise HTTPException(429, "Too many login attempts. Wait five minutes.")
    # Unknown identities still perform a password hash calculation.
    salt = bytes.fromhex(user["salt"] if user else "00" * 16)
    digest = hashlib.pbkdf2_hmac("sha256", body.password.encode(), salt, 310000).hex()
    if not user or not hmac.compare_digest(digest, user["digest"]):
        with database(write=True) as db:
            db.execute("""INSERT INTO login_failures VALUES (?,1,?)
                ON CONFLICT(peer) DO UPDATE SET
                attempts=CASE WHEN first_seen < ? THEN 1 ELSE attempts+1 END,
                first_seen=CASE WHEN first_seen < ? THEN excluded.first_seen ELSE first_seen END""",
                (peer, time.time(), time.time()-300, time.time()-300))
            audit(db, str(uuid.uuid4()), "login", outcome="blocked")
        raise HTTPException(401, "Invalid login")
    token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    with database(write=True) as db:
        db.execute("DELETE FROM sessions WHERE expires<?", (time.time(),))
        db.execute("DELETE FROM login_failures WHERE peer=?", (peer,))
        db.execute("INSERT INTO sessions VALUES (?,?,?,?,?)", (
            hashlib.sha256(token.encode()).hexdigest(), user["actor"], user["role"], csrf, time.time()+3600))
        audit(db, str(uuid.uuid4()), "login", actor=user["actor"], outcome="allowed")
    response.set_cookie(COOKIE, token, httponly=True, samesite="strict", max_age=3600,
                        secure=request.url.scheme == "https")
    return dict(actor=user["actor"], role=user["role"], csrf=csrf)


def identity(request: Request):
    token = request.cookies.get(COOKIE, "")
    digest = hashlib.sha256(token.encode()).hexdigest()
    with database() as db:
        row = db.execute("SELECT * FROM sessions WHERE digest=? AND expires>?", (digest, time.time())).fetchone()
    if not row:
        raise HTTPException(401, "Sign in first")
    if request.method not in ("GET", "HEAD"):
        if not hmac.compare_digest(request.headers.get("X-CSRF-Token", ""), row["csrf"]):
            raise HTTPException(403, "Missing or invalid request protection token")
    return dict(row)


def staff(user=Depends(identity)):
    if user["role"] != "staff":
        with database(write=True) as db:
            audit(db, str(uuid.uuid4()), "staff_access", actor=user["actor"], outcome="blocked")
        raise HTTPException(403, "Staff access required")
    return user


def customer(user=Depends(identity)):
    if user["role"] != "customer":
        raise HTTPException(403, "Use a customer login for this action")
    return user


def get_case(db, case_id, user):
    row = db.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
    if not row or (user["role"] != "staff" and row["customer"] != user["actor"]):
        audit(db, str(uuid.uuid4()), "case_access", actor=user["actor"], case_id=case_id, outcome="blocked")
        # Commit the failed-access audit without disclosing whether the case exists.
        db.commit()
        raise HTTPException(404, "Case not found")
    return row


@app.get("/health")
def health():
    return dict(status="ok", mode="groq-langgraph-mcp", model=os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b"), groq_configured=bool(os.environ.get("GROQ_API_KEY")), mock_payments=True)


@app.get("/api/me")
def me(user=Depends(identity)):
    return dict(actor=user["actor"], role=user["role"], csrf=user["csrf"])


@app.post("/api/logout")
def logout(response: Response, user=Depends(identity)):
    with database(write=True) as db:
        db.execute("DELETE FROM sessions WHERE digest=?", (user["digest"],))
    response.delete_cookie(COOKIE)
    return dict(status="signed_out")


@app.get("/api/orders")
def orders(user=Depends(customer)):
    with database() as db:
        rows = db.execute("""SELECT o.*, o.total-COALESCE((SELECT SUM(amount) FROM refunds r
                    WHERE r.order_id=o.id),0) remaining_cents FROM orders o WHERE customer=?""", (user["actor"],))
        account = db.execute("SELECT destination,balance FROM accounts WHERE customer=?", (user["actor"],)).fetchone()
        return dict(orders=[dict(r) for r in rows], account=dict(account))


@app.get("/api/policy")
def policy(user=Depends(identity)):
    return dict(version=POLICY_VERSION, transaction_limit_cents=10000, weekly_limit_cents=50000,
                week_start_utc=week_start(), accepted_reasons=sorted(REASONS),
                eligibility="Reason category and order balance only in this build; delivery dates and duplicate-charge evidence need staff verification.",
                model=os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b"))


@app.post("/api/cases")
def create_case(body: CaseRequest, user=Depends(customer)):
    if body.reason not in REASONS or not body.details.strip():
        raise HTTPException(422, "Choose an accepted reason and provide details")
    case_id = "NX-" + uuid.uuid4().hex[:12].upper()
    with database(write=True) as db:
        order = db.execute("SELECT * FROM orders WHERE id=? AND customer=?", (body.order_id, user["actor"])).fetchone()
        if not order:
            audit(db, str(uuid.uuid4()), "order_access", actor=user["actor"], order_id=body.order_id, outcome="blocked")
            db.commit()
            raise HTTPException(404, "Order not found")
        existing = db.execute("SELECT * FROM cases WHERE customer=? AND request_key=?", (user["actor"], body.request_key)).fetchone()
        if existing:
            expected = (body.order_id, body.amount_cents, body.reason, body.details)
            if tuple(existing[k] for k in ("order_id", "amount", "reason", "details")) != expected:
                raise HTTPException(409, "Request key already used for different details")
            return dict(case_id=existing["id"], status=existing["status"], replayed=True)
        db.execute("INSERT INTO cases(id,customer,order_id,amount,reason,details,status,decision_reason,request_key,created) VALUES (?,?,?,?,?,?,?,?,?,?)", (
            case_id, user["actor"], body.order_id, body.amount_cents, body.reason, body.details,
            "submitted", "awaiting_review", body.request_key, now()))
        case = db.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
        audit(db, str(uuid.uuid4()), "intake", actor=user["actor"], case_id=case_id,
              amount_cents=body.amount_cents, outcome="submitted")
        notify(db, case, "acknowledgement", "Request received. Submission is not approval or payment.")
    return dict(case_id=case_id, status="submitted")


@app.get("/api/cases")
def cases(user=Depends(identity)):
    with database() as db:
        rows = db.execute("SELECT * FROM cases ORDER BY created DESC") if user["role"] == "staff" else db.execute(
            "SELECT * FROM cases WHERE customer=? ORDER BY created DESC", (user["actor"],))
        return [dict(r) for r in rows]


@app.get("/api/cases/{case_id}")
def case_detail(case_id: str, user=Depends(identity)):
    with database(write=True) as db:
        row = get_case(db, case_id, user)
        messages = db.execute("SELECT kind,body,created FROM messages WHERE case_id=? ORDER BY created", (case_id,))
        return dict(case=dict(row), messages=[dict(r) for r in messages], runs=[
            dict(id=r["id"], status=r["status"], started=r["started"], updated=r["updated"], state=json.loads(r["state_json"]))
            for r in db.execute("SELECT * FROM agent_runs WHERE case_id=? ORDER BY started", (case_id,))])


class CaseMessage(Body):
    text: str = Field(min_length=1, max_length=2000)


@app.post("/api/cases/{case_id}/messages", status_code=201)
def add_case_message(case_id: str, body: CaseMessage, user=Depends(customer)):
    content = body.text.strip()
    if not content:
        raise HTTPException(422, "Enter a message")
    with database(write=True) as db:
        case = get_case(db, case_id, user)
        count = db.execute(
            "SELECT COUNT(*) FROM messages WHERE case_id=? AND kind=?",
            (case_id, "customer_followup"),
        ).fetchone()[0]
        if count >= 30:
            raise HTTPException(409, "This demo case has reached its follow-up limit")
        message_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO messages(id,case_id,customer,kind,body,created) VALUES (?,?,?,?,?,?)",
            (message_id, case_id, case["customer"], "customer_followup", content, now()),
        )
        audit(db, str(uuid.uuid4()), "customer_followup", actor=user["actor"],
              case_id=case_id, message_id=message_id)
    return {"message_id": message_id}


@app.post("/api/cases/{case_id}/review")
def customer_review(case_id: str, user=Depends(customer)):
    with database(write=True) as db:
        get_case(db, case_id, user)
    # Same controlled graph as staff processing; it cannot bypass required evidence verification.
    return process(case_id, {"actor": user["actor"], "role": "customer"})


@app.post("/api/cases/{case_id}/process")
def process(case_id: str, user=Depends(staff)):
    from app.workflow import run_workflow, WorkflowBusy, WorkflowFailure
    import asyncio
    with database(write=True) as db:
        get_case(db, case_id, user)
    if not os.environ.get("GROQ_API_KEY"):
        raise HTTPException(503, "Configure the local Groq key first")
    try:
        return asyncio.run(run_workflow(case_id, user["actor"]))
    except WorkflowBusy:
        raise HTTPException(409, "Another workflow is running. Retry after it completes.")
    except WorkflowFailure as exc:
        raise HTTPException(502, exc.public_result)


@app.post("/api/cases/{case_id}/decision")
def decision(case_id: str, body: Decision, user=Depends(staff)):
    if body.decision not in ("deny", "escalate", "verify") or not body.note.strip():
        raise HTTPException(422, "Choose verify, deny or escalate and provide a reason")
    with database(write=True) as db:
        case = get_case(db, case_id, user)
        if db.execute("SELECT 1 FROM refunds WHERE customer=? AND request_key=?", (case["customer"], "case:"+case_id)).fetchone():
            raise HTTPException(409, "An executed refund cannot be denied or undone here")
        if case["status"] == "denied":
            raise HTTPException(409, "Supervisor denial is final in this build")
        if body.decision == "verify":
            if case["status"] in ("denied", "escalated"):
                raise HTTPException(409, "A supervisor hold cannot be cleared by this action")
            db.execute("UPDATE cases SET evidence_verified=1,decision_reason=? WHERE id=?", (body.note, case_id))
            audit(db, str(uuid.uuid4()), "evidence_verified", actor=user["actor"], case_id=case_id, reason=body.note, note_recorded=True)
            return dict(status="evidence_verified", case_id=case_id)
        status = "denied" if body.decision == "deny" else "escalated"
        if status == "denied":
            db.execute("UPDATE orders SET supervisor_denied=1 WHERE id=?", (case["order_id"],))
        db.execute("UPDATE cases SET status=?,decision_reason=? WHERE id=?", (status, body.note, case_id))
        audit(db, str(uuid.uuid4()), "supervisor_decision", actor=user["actor"], case_id=case_id,
              decision=status, reason=body.note, note_recorded=True)
        notify(db, case, "decision", f"Staff decision: {status}. {body.note}")
    return dict(status=status, case_id=case_id)


@app.post("/api/authority")
def authority(body: Authority, user=Depends(staff)):
    if not body.note.strip():
        raise HTTPException(422, "Record a reason")
    with database(write=True) as db:
        db.execute("UPDATE control SET active=? WHERE id=1", (int(body.active),))
        audit(db, str(uuid.uuid4()), "authority_change", actor=user["actor"], active=body.active, reason=body.note, note_recorded=True)
    return dict(active=body.active)


@app.get("/api/reports")
def reports(user=Depends(staff)):
    with database() as db:
        used = db.execute("SELECT COALESCE(SUM(amount),0) FROM refunds WHERE week=?", (week_start(),)).fetchone()[0]
        # Actual ledger execution takes precedence over an interrupted case-status update.
        rows = db.execute("""SELECT c.id,c.amount,c.reason,c.status,c.decision_reason,
            r.id refund_id,r.amount executed_cents FROM cases c LEFT JOIN refunds r
            ON r.customer=c.customer AND r.request_key=('case:' || c.id) ORDER BY c.created DESC""")
        ledger = [dict(r) for r in rows]
        active = bool(db.execute("SELECT active FROM control WHERE id=1").fetchone()[0])
        audit(db, str(uuid.uuid4()), "report_read", actor=user["actor"], scope="staff_case_summary")
        db.commit()
        return dict(weekly_used_cents=used, weekly_remaining_cents=50000-used,
                    week_start_utc=week_start(), active=active, cases=ledger)


@app.get("/api/audit")
def audit_records(user=Depends(staff)):
    with database() as db:
        rows = [dict(r) for r in db.execute("SELECT * FROM audit ORDER BY sequence DESC LIMIT 300")]
        for row in rows:
            row["details"] = json.loads(row["details"])
        return rows


@app.get("/")
def root():
    return RedirectResponse("/ui/index.html")


app.mount("/ui", StaticFiles(directory=str(ROOT / "app/static"), html=True), name="ui")
