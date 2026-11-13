"""Verify documentation/evidence consistency and staged-file hygiene without model calls."""
from pathlib import Path
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
required=["README.md","Architecture/architecture.png","Architecture/README.md","docs/user-guide.md",
          "docs/team-responsibilities.md","docs/implementation-status.md","docs/findings.md",
          "redteam/plan.md","threat_model/MAESTRO_mapping.md","report/Progress_Report.pdf"]
for name in required:
    assert (ROOT/name).is_file() and (ROOT/name).stat().st_size>0,"Missing artifact: "+name
for name in ["README.md","Architecture/README.md","docs/README.md","docs/user-guide.md","report/README.md"]:
    path=ROOT/name
    for ref in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)",path.read_text(encoding="utf-8")):
        if ref.startswith(("https://","http://","#","mailto:")):continue
        assert (path.parent/ref.split("#")[0]).exists(),"Broken link: "+name+" -> "+ref
for name,count in [("refund-controls.json",13),("api-mcp-controls.json",19)]:
    data=json.loads((ROOT/"redteam/results"/name).read_text())
    assert data["passed"] and data["tests_run"]==count,"Unexpected control evidence: "+name
live=json.loads((ROOT/"redteam/results/live-agent-workflow.json").read_text())
assert live["passed"] and len(live["scenarios"])==2
assert len(live["audit"])==66 and len(live["ledger"])==1
assert live["ledger"][0]["amount"]==6400
assert live["verified_customer_account"]["balance"]==6400
assert live["verified_customer_account"]["destination"]=="mock-account-0042"
assert json.loads((ROOT/"redteam/results/progress-check.json").read_text())["passed"]
pdf=(ROOT/"report/Progress_Report.pdf").read_bytes()
assert pdf.startswith(b"%PDF-") and len(re.findall(rb"/Type\s*/Page\b",pdf))==8
staged=subprocess.check_output(["git","diff","--cached","--name-only","-z"],cwd=ROOT).decode().split("\0")
for name in filter(None,staged):
    parts=Path(name).parts
    if parts[0] in ("data",".venv",".venv-agent",".cache") or Path(name).name in (".env","demo-login.txt","identities.json"):
        raise SystemExit("STOP: private runtime file staged: "+name)
    if Path(name).name.startswith(".env.") and Path(name).name!=".env.example":
        raise SystemExit("STOP: private environment file staged: "+name)
    if Path(name).suffix in (".md",".txt",".py",".json",".jsonl",".html",".css",".js"):
        result=subprocess.run(["git","show",":"+name],cwd=ROOT,capture_output=True)
        if result.returncode==0 and re.search(rb"gsk_[A-Za-z0-9_-]{20,}",result.stdout):
            raise SystemExit("STOP: possible Groq key in staged file: "+name)
print("PASS: Documentation links, eight-page PDF, recorded test totals and staged-file checks.")
print("No model calls were made. Confirm unverified individual contributions before submitting the PDF.")
