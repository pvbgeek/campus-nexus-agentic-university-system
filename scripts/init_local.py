"""Create ignored, local-only demo identities. Never commit or share generated credentials."""
from pathlib import Path
import hashlib
import json
import secrets

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
config = DATA / "identities.json"
if config.exists():
    print("Local demo identities already exist. Credentials were not changed.")
else:
    users = {}
    lines = ["Campus Nexus LOCAL SYNTHETIC DEMO ONLY", "Do not commit, share, or paste these credentials.", ""]
    for username, actor, role in [("avery", "CUST-001", "customer"), ("jordan", "CUST-002", "customer"), ("supervisor", "STAFF-001", "staff")]:
        password = secrets.token_urlsafe(18)
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 310000).hex()
        users[username] = dict(actor=actor, role=role, salt=salt, digest=digest)
        lines.append(f"{username}: {password}")
    config.write_text(json.dumps(users, indent=2) + "\n", encoding="utf-8")
    config.chmod(0o600)
    credentials = DATA / "demo-login.txt"
    credentials.write_text("\n".join(lines) + "\n", encoding="utf-8")
    credentials.chmod(0o600)
    print("Created local identities. Read data/demo-login.txt privately to sign in.")
print("Start: .venv-agent/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
