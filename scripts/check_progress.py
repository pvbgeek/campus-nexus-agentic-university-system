"""One batch: control tests, real MCP/graph integration, live model tests and evidence export."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
stages=[
    ("Refund boundary controls", "redteam/test_refund_controls.py"),
    ("API and real MCP security controls", "redteam/test_api_controls.py"),
    ("Real MCP policy retrieval", "scripts/verify_retrieval_mcp.py"),
    ("Graph and tool integration with a labelled model test double", "redteam/test_graph_integration.py"),
    ("Live Groq workflows and prompt injection", "scripts/verify_live_workflow.py"),
]
output=ROOT/"redteam/results/progress-check.json"
summary=dict(executed_at=datetime.now(timezone.utc).isoformat(),stages=[],passed=False)
if "--resume-live" in sys.argv:
    if not output.is_file():
        raise SystemExit("No earlier progress-check results found. Run without --resume-live.")
    previous=json.loads(output.read_text(encoding="utf-8"))
    prior=previous.get("stages",[])
    required=[script for _,script in stages[:3]]
    if len(prior)<3 or any(row.get("script")!=script or row.get("exit_code")!=0 for row,script in zip(prior[:3],required)):
        raise SystemExit("The earlier control and retrieval stages did not all pass. Run the full batch.")
    summary["stages"]=prior[:3]
    summary["reused_control_results_from"]=previous.get("executed_at")
    stages=stages[3:]
    print("Reusing passed control suites. Rerunning affected graph integration and the live scenarios.",flush=True)
output.parent.mkdir(parents=True,exist_ok=True)
for title,script in stages:
    print("\n=== "+title+" ===",flush=True)
    completed=subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT)
    summary["stages"].append(dict(name=title,script=script,exit_code=completed.returncode))
    output.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    if completed.returncode:
        print("STOPPED: Fix this stage before committing or claiming the full build passed.",flush=True)
        sys.exit(completed.returncode)
# Export correlated synthetic audit evidence from the isolated live test, not from private user files.
live=json.loads((ROOT/"redteam/results/live-agent-workflow.json").read_text(encoding="utf-8"))
logs=ROOT/"logs/progress-live-audit.jsonl"
logs.parent.mkdir(exist_ok=True)
with logs.open("w",encoding="utf-8") as stream:
    for row in live["audit"]:
        row=dict(row)
        if isinstance(row.get("details"),str):row["details"]=json.loads(row["details"])
        stream.write(json.dumps(row)+"\n")
summary.update(passed=True,live_evidence="redteam/results/live-agent-workflow.json",audit_jsonl="logs/progress-live-audit.jsonl")
output.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
print("\nALL PROGRESS CHECKS PASSED",flush=True)
print("Evidence:",output.relative_to(ROOT))
print("Live audit:",logs.relative_to(ROOT))
print("Next: review the browser, update the architecture and progress report, then commit and push.")
