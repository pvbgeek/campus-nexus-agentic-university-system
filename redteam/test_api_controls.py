"""Real API and stdio MCP boundary tests. No model calls are made by this suite."""
from pathlib import Path
from tempfile import TemporaryDirectory
import asyncio
import hashlib
import json
import os
import secrets
import sys
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TEMP = TemporaryDirectory()
os.environ["CAMPUS_NEXUS_DATA"] = TEMP.name
from fastapi.testclient import TestClient
from app.web import app
from app.storage import database, now
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

passwords = {name: secrets.token_urlsafe(20) for name in ("avery", "jordan", "supervisor")}
users = {}
for username, actor, role in [("avery", "CUST-001", "customer"), ("jordan", "CUST-002", "customer"), ("supervisor", "STAFF-001", "staff")]:
    salt = secrets.token_hex(16)
    users[username] = dict(actor=actor,role=role,salt=salt,
        digest=hashlib.pbkdf2_hmac("sha256",passwords[username].encode(),bytes.fromhex(salt),310000).hex())
(Path(TEMP.name)/"identities.json").write_text(json.dumps(users),encoding="utf-8")
EVIDENCE = []


class Controls(unittest.TestCase):
    def setUp(self):
        with database(write=True) as db:
            for table in ("sessions", "cases", "refunds", "messages", "audit", "agent_runs", "login_failures"):
                db.execute("DELETE FROM "+table)
            db.execute("UPDATE orders SET supervisor_denied=0")
            db.execute("UPDATE accounts SET balance=0")
            db.execute("UPDATE control SET active=1 WHERE id=1")
        self.clients = {}
        self.observed = []

    def tearDown(self):
        with database() as db:
            logs = [dict(r) for r in db.execute("SELECT * FROM audit ORDER BY sequence")]
            ledger = [dict(r) for r in db.execute("SELECT * FROM refunds")]
            accounts = [dict(r) for r in db.execute("SELECT customer,balance FROM accounts")]
        EVIDENCE.append(dict(test_id=self.id(),observed=self.observed,audit=logs,ledger=ledger,accounts=accounts))
        for client in self.clients.values():
            client.close()

    def client(self, name="avery"):
        if name not in self.clients:
            client=TestClient(app)
            response=client.post("/api/login",json=dict(username=name,password=passwords[name]))
            self.assertEqual(response.status_code,200)
            client.headers["X-CSRF-Token"]=response.json()["csrf"]
            self.clients[name]=client
        return self.clients[name]

    def create(self, amount=6400, **extra):
        data=dict(order_id="NX-2048",amount_cents=amount,reason="damaged",
                  details="Synthetic damaged seam evidence.",request_key=str(uuid.uuid4()))
        data.update(extra)
        response=self.client().post("/api/cases",json=data)
        self.observed.append(dict(action="create_case",http=response.status_code,response=response.json()))
        return response

    def test_authentication_required(self):
        with TestClient(app) as client:
            for path in ("/api/orders", "/api/cases", "/api/reports", "/api/audit"):
                response=client.get(path)
                self.assertEqual(response.status_code,401)
                self.observed.append(dict(path=path,http=response.status_code))

    def test_customer_cannot_change_authority(self):
        response=self.client().post("/api/authority",json=dict(active=False,note="Attempt customer privilege escalation"))
        self.assertEqual(response.status_code,403)
        with database() as db:self.assertEqual(db.execute("SELECT active FROM control").fetchone()[0],1)
        self.observed.append(dict(http=response.status_code,action="customer_authority_change"))

    def test_customer_cannot_process_as_staff(self):
        case=self.create().json()["case_id"]
        response=self.client().post("/api/cases/"+case+"/process",json={})
        self.assertEqual(response.status_code,403)
        self.observed.append(dict(http=response.status_code,action="customer_staff_route"))

    def test_cross_case_read(self):
        case=self.create().json()["case_id"]
        response=self.client("jordan").get("/api/cases/"+case)
        self.assertEqual(response.status_code,404)
        self.assertEqual(self.client("jordan").get("/api/cases").json(),[])
        self.observed.append(dict(http=response.status_code,action="cross_customer_case_read"))

    def test_cross_order_submission(self):
        self.assertEqual(self.create(order_id="NX-2050").status_code,404)

    def test_forged_identity_field(self):
        self.assertEqual(self.create(customer="CUST-002",evidence_verified=1).status_code,422)

    def test_csrf_required(self):
        client=self.client()
        del client.headers["X-CSRF-Token"]
        response=client.post("/api/cases",json={})
        self.assertEqual(response.status_code,403)
        self.observed.append(dict(http=response.status_code,action="missing_csrf"))

    def test_foreign_origin_blocked(self):
        response=self.client().post("/api/logout",json={},headers={"Origin":"https://attacker.invalid"})
        self.assertEqual(response.status_code,403)
        self.observed.append(dict(http=response.status_code,action="foreign_origin"))

    def test_strict_integer_money(self):
        for value in (True,6400.5,"6400",0,-1):
            self.assertEqual(self.create(amount=value).status_code,422)

    def test_submission_does_not_pay(self):
        case=self.create().json()["case_id"]
        detail=self.client().get("/api/cases/"+case).json()
        self.assertEqual(detail["case"]["status"],"submitted")
        self.assertEqual(len(detail["messages"]),1)
        self.assertEqual(detail["messages"][0]["kind"],"acknowledgement")
        with database() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM refunds").fetchone()[0],0)
            self.assertEqual(db.execute("SELECT SUM(balance) FROM accounts").fetchone()[0],0)

    def test_customer_cannot_read_reports(self):
        for path in ("/api/reports","/api/audit"):
            response=self.client().get(path)
            self.assertEqual(response.status_code,403)
            self.observed.append(dict(path=path,http=response.status_code))

    def test_dynamic_ui_is_served(self):
        with TestClient(app) as client:
            for path in ("/ui/index.html","/ui/orders.html","/ui/refund.html","/ui/cases.html","/ui/staff.html","/ui/reports.html","/ui/connected.js"):
                self.assertEqual(client.get(path).status_code,200)
            text=client.get("/ui/refund.html").text
            self.assertIn("connected.js",text)
            self.assertNotIn("NX-1042",text)
        self.observed.append(dict(check="Dynamic UI assets served; not a browser interaction test"))

    async def tool(self,case,name,args):
        run=str(uuid.uuid4())
        with database(write=True) as db:
            db.execute("INSERT INTO agent_runs VALUES (?,?,?,?,?,?)",(run,case,"running",now(),now(),"{}"))
        env=dict(os.environ,CAMPUS_MCP_CASE=case,CAMPUS_MCP_RUN=run)
        params=StdioServerParameters(command=sys.executable,args=["-m","app.support_mcp"],cwd=str(ROOT),env=env)
        async with stdio_client(params) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize()
                result=await session.call_tool(name,args)
                payload=[b.text for b in result.content if b.type=="text"]
                self.observed.append(dict(transport="real_stdio_mcp",tool=name,arguments=args,is_error=result.isError,result=payload))
                return result,json.loads(payload[0]) if payload and not result.isError else None

    def verified(self,case):
        response=self.client("supervisor").post("/api/cases/"+case+"/decision",json=dict(decision="verify",note="Staff verified synthetic damage and delivery evidence."))
        self.assertEqual(response.status_code,200)

    def test_mcp_requires_verified_evidence(self):
        case=self.create().json()["case_id"]
        result,data=asyncio.run(self.tool(case,"execute_refund",dict(proposed_amount_cents=6400,recommendation="execute")))
        self.assertFalse(result.isError)
        self.assertEqual(data["reason"],"staff_evidence_verification_required")

    def test_mcp_amount_tampering(self):
        case=self.create().json()["case_id"]
        self.verified(case)
        result,data=asyncio.run(self.tool(case,"execute_refund",dict(proposed_amount_cents=99999,recommendation="execute")))
        self.assertFalse(result.isError)
        self.assertEqual(data["reason"],"proposal_amount_mismatch")

    def test_mcp_cannot_select_another_case(self):
        case=self.create().json()["case_id"]
        result,_=asyncio.run(self.tool(case,"read_case",dict(case_id="OTHER-CUSTOMER-CASE")))
        self.assertTrue(result.isError)

    def test_mcp_cannot_change_permissions(self):
        case=self.create().json()["case_id"]
        result,_=asyncio.run(self.tool(case,"restore_authority",dict(active=True)))
        self.assertTrue(result.isError)

    def test_mcp_executes_mock_credit_once(self):
        case=self.create().json()["case_id"]
        self.verified(case)
        for expected in ("executed","replayed"):
            _,data=asyncio.run(self.tool(case,"execute_refund",dict(proposed_amount_cents=6400,recommendation="execute")))
            self.assertEqual(data["status"],expected)
        with database() as db:
            self.assertEqual(db.execute("SELECT balance FROM accounts WHERE customer='CUST-001'").fetchone()[0],6400)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM refunds").fetchone()[0],1)

    def test_mcp_honors_revocation(self):
        case=self.create().json()["case_id"]
        self.verified(case)
        self.client("supervisor").post("/api/authority",json=dict(active=False,note="Red Team revocation test"))
        _,data=asyncio.run(self.tool(case,"execute_refund",dict(proposed_amount_cents=6400,recommendation="execute")))
        self.assertEqual(data["reason"],"authority_revoked")

    def test_mcp_honors_supervisor_denial(self):
        case=self.create().json()["case_id"]
        self.verified(case)
        self.client("supervisor").post("/api/cases/"+case+"/decision",json=dict(decision="deny",note="Red Team test: supervisor explicitly denied"))
        _,data=asyncio.run(self.tool(case,"execute_refund",dict(proposed_amount_cents=6400,recommendation="execute")))
        self.assertEqual(data["reason"],"supervisor_decision")


if __name__=="__main__":
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
    output=ROOT/"redteam/results/api-mcp-controls.json"
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(dict(suite="api-mcp-boundaries-v1",passed=result.wasSuccessful(),tests_run=result.testsRun,
        model_calls=False,scenarios=EVIDENCE,failures=[dict(test=str(t),traceback=trace) for t,trace in result.failures+result.errors]),indent=2)+"\n",encoding="utf-8")
    print("Evidence:",output.relative_to(ROOT))
    TEMP.cleanup()
    sys.exit(0 if result.wasSuccessful() else 1)
