from datetime import datetime, timezone
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.policy_index import build_policy_index, search_policy

manifest = build_policy_index()
print("PASS: Persistent policy vector index created.")
print(json.dumps(manifest, indent=2))
query = "Can the agent refund more than one hundred dollars in a single transaction?"
results = search_policy(query)
assert results and any("100.00" in r["text"] for r in results), "Relevant transaction policy was not retrieved"
print("PASS: Semantic query retrieved the transaction authority policy.")
output = ROOT / "redteam/results/retrieval-smoke.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(dict(executed_at=datetime.now(timezone.utc).isoformat(), test="semantic-policy-retrieval", query=query,
                                 manifest=manifest, matches=results, passed=True), indent=2)+"\n", encoding="utf-8")
print("Evidence:", output.relative_to(ROOT))
