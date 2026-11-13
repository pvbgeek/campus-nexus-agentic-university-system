"""Prompt locally for a Groq key and verify a real, bounded model request."""
from datetime import datetime, timezone
from pathlib import Path
from getpass import getpass
import json
import os
import sys

from dotenv import load_dotenv, set_key
from groq import Groq

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / ".env"
load_dotenv(path)
key = os.environ.get("GROQ_API_KEY", "").strip()
if not key:
    key = getpass("Paste your FREE-tier Groq API key (hidden): ").strip()
if not key:
    raise SystemExit("No API key entered. Nothing was configured.")
model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
try:
    client = Groq(api_key=key, timeout=45, max_retries=0)
    available = {item.id for item in client.models.list().data}
    if model not in available:
        raise SystemExit("Configured model is unavailable to this account. Set GROQ_MODEL to an available model before retrying.")
    result = client.chat.completions.create(model=model, temperature=0, max_completion_tokens=512,
        reasoning_effort="low" if model.startswith("openai/gpt-oss") else None,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": "Return a JSON object with exactly one field: status equal to ok."},
                  {"role": "user", "content": "Verify the connection."}])
    parsed = json.loads(result.choices[0].message.content or "")
    if parsed != {"status": "ok"}:
        raise ValueError("Unexpected verification response")
except Exception as exc:
    # Provider exceptions can contain request bodies. Print only the exception type and HTTP status.
    print("Groq verification failed:", type(exc).__name__, "HTTP", getattr(exc, "status_code", "n/a"))
    print("Check the key, model access, network and free-tier limits. The key was not printed.")
    sys.exit(1)
set_key(str(path), "GROQ_API_KEY", key)
set_key(str(path), "GROQ_MODEL", model)
path.chmod(0o600)
output = ROOT / "redteam/results/groq-connection.json"
output.parent.mkdir(parents=True, exist_ok=True)
usage = result.usage.model_dump() if result.usage else {}
output.write_text(json.dumps(dict(executed_at=datetime.now(timezone.utc).isoformat(), test="live-groq-connection", passed=True,
    provider="Groq", model=model, request_id=result.id, usage=usage,
    verified_response=parsed), indent=2)+"\n", encoding="utf-8")
print("PASS: Real Groq model request returned the verified response.")
print("Key saved to ignored .env; it was not included in evidence.")
print("Model:", model)
print("Evidence:", output.relative_to(ROOT))
