# Run instructions

The primary entry point is now `app.main:app`, serving the connected application.

Follow [the User Guide](docs/user-guide.md) for complete setup and workflows. Linux and macOS commands:

```bash
uv venv --python 3.12 .venv-agent
uv pip install --python .venv-agent/bin/python -r requirements-agents.lock.txt
.venv-agent/bin/python scripts/configure_groq.py
.venv-agent/bin/python scripts/build_policy_index.py
.venv-agent/bin/python scripts/init_local.py
.venv-agent/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 and use the generated local demo credentials in ignored `data/demo-login.txt`. Keep the server terminal open. Stop it with Ctrl+C. On Windows use `.venv-agent/Scripts/python.exe` instead of `.venv-agent/bin/python`.

Run current verification separately from the repository root:

```bash
.venv-agent/bin/python scripts/check_progress.py
```

The test suite uses isolated synthetic databases. It does not populate the browser's operational database. Test results and live audit exports are saved in `redteam/results/` and `logs/progress-live-audit.jsonl`.

The legacy `run_demo.py` walkthrough targets the preserved instructor simulation, not the connected application. Historical starter results are baseline evidence only. Do not use that walkthrough as the current application verification command.

Keys, credentials, sessions, local databases, model caches and source backups are ignored. Keep the development listener on loopback. No Vercel or other hosted deployment is required for this local progress demonstration.
