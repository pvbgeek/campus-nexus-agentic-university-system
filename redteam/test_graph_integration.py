"""LangGraph/MCP integration with a clearly labelled model test double; not live-model evidence."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import asyncio
import json
import os
import shutil
import sys
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
with TemporaryDirectory() as folder:
    target=Path(folder)
    shutil.copytree(ROOT/"data/vectors",target/"vectors")
    shutil.copy2(ROOT/"data/policy-index.json",target/"policy-index.json")
    os.environ["CAMPUS_NEXUS_DATA"]=folder
    os.environ["GROQ_API_KEY"]="test-double-no-network"
    from app.storage import database,now
    from app.workflow import run_workflow
    case="TEST-"+uuid.uuid4().hex
    with database(write=True) as db:
        db.execute("INSERT INTO cases VALUES (?,?,?,?,?,?,?,?,?,?,?)",(case,"CUST-001","NX-2048",6400,"damaged","Synthetic verified damage","submitted","verified","test-key",now(),1))

    class Completions:
        async def create(self,**options):
            role=options["response_format"]["json_schema"]["name"]
            payload=json.loads(options["messages"][1]["content"])
            values={
                "intake":dict(summary="Synthetic refund request",retrieval_query="refund transaction ownership authority",injection_suspected=False),
                "records":dict(evidence_summary="Verified synthetic order",policy_chunk_ids=[p["point_id"] for p in payload.get("policy",[])],missing_evidence=False),
                "refunds":dict(action="execute",proposed_amount_cents=6400,reason="Within authority"),
                "email":dict(subject="Refund result",body="The mock refund execution is recorded."),
                "reporting":dict(summary="Synthetic case processed",risks=["Model provider mocked in this test"]),
            }
            return SimpleNamespace(id="TEST-DOUBLE-"+role,choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(values[role])))],
                usage=SimpleNamespace(total_tokens=100,model_dump=lambda:dict(total_tokens=100)))

    class Provider:
        def __init__(self,**kwargs):self.chat=SimpleNamespace(completions=Completions())
        async def close(self):pass

    with patch("app.workflow.AsyncGroq",Provider):
        result=asyncio.run(run_workflow(case,"TEST-STAFF"))
    assert result["completed_nodes"]==["Intake","Records","Refunds","Email","Reporting"]
    assert result["execution"]["status"]=="executed"
    with database() as db:
        assert db.execute("SELECT balance FROM accounts WHERE customer='CUST-001'").fetchone()[0]==6400
        assert db.execute("SELECT status FROM agent_runs").fetchone()[0]=="completed"
    output=ROOT/"redteam/results/graph-integration.json"
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(dict(passed=True,real_model_calls=False,model_provider="test_double",mcp_transport="real_stdio",vector_retrieval="real_qdrant_fastembed",result=result),indent=2)+"\n",encoding="utf-8")
    print("PASS: Five-node graph, actual MCP tools, real vector retrieval and persisted mock credit.")
    print("Model provider was a test double. Live model behavior is verified separately.")
