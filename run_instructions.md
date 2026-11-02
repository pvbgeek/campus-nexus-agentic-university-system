# Run Instructions

## Prerequisites

- Python 3.10 or newer
- Git
- Windows Git Bash or a compatible shell

Run commands from the Campus Nexus repository root.

## Windows Git Bash Setup

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

On Linux/macOS, activate with source .venv/bin/activate instead.

## Automatic Baseline Demonstration

```bash
python run_demo.py --base-url http://127.0.0.1:8016 --start-server --out redteam/results/starter-baseline.json
```

The demo checks health, submits the instructor's sample task, runs its supplied
Red Team simulation, retrieves logs, saves evidence, and stops its server.

Use an unused local port. The automatic startup detects an occupied port.

## Manual Server and Browser Exploration

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8016
```

Open http://127.0.0.1:8016/docs in a browser.

From a second activated terminal, run:

```bash
python run_demo.py --base-url http://127.0.0.1:8016 --out redteam/results/starter-baseline.json
```

Stop a manually started server with Ctrl+C.

## Baseline Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /health | Identify the running simulated starter |
| POST | /tasks | Plan and simulate a supplied task |
| POST | /tests/rt-01 | Run the supplied canned-input simulation |
| GET | /logs | Retrieve structured baseline events |

## Evidence

- redteam/results/starter-baseline.json
- redteam/results/RT-01/rt-01-results.json
- logs/events.jsonl

The two supplied Red Team inputs should be flagged. Successful endpoint responses
are HTTP 200. Inspect response content as well as status codes.

## Limitations

The baseline is simulated. It does not implement the complete refund-support
application, actual LLM calls, a vector database, or independent refund authorization.

See docs/implementation-status.md and docs/starter-source.md.

## Rebuild the Architecture Diagram

Diagram-generation dependencies are separate from runtime requirements.

```bash
python -m pip install -r requirements-dev.txt
python Architecture/generate_diagram.py
```
