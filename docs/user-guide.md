# Campus Nexus User Guide

This guide describes the working progress build. Campus Nexus handles synthetic customer support cases and refund requests. The five agents use real Groq inference and real policy retrieval. Payments and email use local mock tools.

## 1. Install and start

You need Git, uv, internet for Groq and the first embedding model download, and a Groq Free plan key. Clone the repository, then run these commands in its root on Linux or macOS:

```bash
git clone https://github.com/pvbgeek/campus-nexus-agentic-university-system.git
cd campus-nexus-agentic-university-system
uv venv --python 3.12 .venv-agent
uv pip install --python .venv-agent/bin/python -r requirements-agents.lock.txt
.venv-agent/bin/python scripts/configure_groq.py
.venv-agent/bin/python scripts/build_policy_index.py
.venv-agent/bin/python scripts/init_local.py
.venv-agent/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

If the repository and environment already exist, do not recreate them to start the server. Run the final command. On Windows replace `.venv-agent/bin/python` with `.venv-agent/Scripts/python.exe` and use the equivalent paths in your shell.

Open http://127.0.0.1:8000. Read `data/demo-login.txt` privately in a second terminal. The setup generates unique passwords for `avery`, `jordan` and `supervisor`. Avery and Jordan are separate synthetic customers. Supervisor is the authorized support staff user. These names do not refer to project team members.

The Groq key is saved in ignored `.env`. Model vectors and operational data are stored locally under ignored cache/data directories. Do not upload these private files. The Free plan has usage limits; the app does not upgrade the account or use a paid provider fallback.

## 2. Customer workflow

1. Sign in as Avery or Jordan.
2. Open My orders and choose Request a refund for an owned order.
3. Enter a positive USD amount with at most two decimal places, select a reason and describe the issue. Do not enter bank details.
4. Submit. The server saves a case and a mock inbox acknowledgement. Submission is not approval or execution.
5. Open My cases and choose View case and messages to inspect the current status, inbox and saved agent runs.
6. Ask agents to review can start a live review of the customer's own case. It cannot bypass staff evidence verification. Review may take several minutes because provider usage is bounded.
7. Sign out before changing identities, or use a separate browser profile for staff.

The local demo begins with fictional orders and account balances. The isolated automated test results do not appear in this operational database. New browser cases get new identifiers.

## 3. Staff workflow

1. Sign in as supervisor and open Staff workspace.
2. Read the request and supporting evidence. Record an assessment and choose Verify evidence only when the supporting facts have actually been checked. In a demonstration, use clearly identified synthetic evidence.
3. Select Process refund to invoke Intake, Records, Refunds, Email and Reporting. The model can recommend an action; the execution gateway makes the authorization decision.
4. Inspect the case status, saved run and inbox. A successful mock credit has an actual ledger identifier; a completed workflow can also produce a hold.
5. Use Deny request or Escalate with a reason where appropriate. Denial is final in this build and also blocks refunds for the referenced order. Escalation holds the case; this UI does not provide a manual exception payment path.
6. Open Reports to view SQL ledger totals, case outcomes and audit records. Enter a reason before revoking or restoring refund authority. The model cannot use these staff controls.

The demo has one authorized staff queue. It does not yet implement a configurable multi-staff assignment system. Staff verification never increases monetary limits.

## 4. Request format

The browser converts USD to integer cents and sends an authenticated JSON request. Identity is taken from the server session, not from a customer ID supplied in the body.

```json
{
  "order_id": "NX-2048",
  "amount_cents": 6400,
  "reason": "damaged",
  "details": "The hoodie arrived with a torn seam.",
  "request_key": "unique-request-id"
}
```

Accepted reason codes are `damaged`, `wrong_item` and `duplicate_charge`. The description is required and limited to 2,000 characters. The amount must be a positive integer number of cents. Unsupported identity or verification fields are rejected. A repeated submission key with different details is rejected; consequential processing uses a stable case-specific execution key.

## 5. Policy and outcomes

- Autonomous refunds are limited to $100 per transaction and $500 cumulatively per UTC week across customers and cases. The team week begins Monday at 00:00 UTC.
- The refund cannot exceed the owned order's remaining refundable amount. Its destination is the stored synthetic account; customer text cannot redirect it.
- Supporting eligibility evidence requires staff verification. The team policy includes a 30 day delivery window. Seeded dates are fictional fixtures; missing or unsuitable evidence is held for review.
- Supervisor denial and revocation block new consequential actions. A review or staff verification cannot override the configured caps.
- An executed mock refund writes the ledger and credits the synthetic account atomically. An identical repeated request returns the original identifier without another credit.
- `submitted` means a saved request. `review_required`, `blocked`, `denied` and `escalated` do not represent an executed refund. `executed` requires a ledger record. `replayed` returns an existing execution.
- Workflow completion means all agents finished; it does not mean the refund was approved. Read the separate execution outcome.

## 6. Evidence and troubleshooting

```bash
.venv-agent/bin/python scripts/check_progress.py
```

The suite writes JSON evidence under `redteam/results/` and successful live audit events to `logs/progress-live-audit.jsonl`. Control tests do not call the model. The graph integration check labels its provider test double. The live suite uses real Groq calls for a valid refund and an injected over-limit request. It uses temporary databases rather than the browser's operational records.

If a run pauses, inspect the case, saved agent state and staff audit view before retrying. A late provider failure can happen after a refund executed; the ledger is the authority. Retrying uses the same refund key. Provider failures do not trigger a simulated success response or a paid fallback. A busy workflow or local usage ceiling can require waiting before another run.

Initial unauthenticated session checks may return HTTP 401 before sign in. That is expected. Stop the server with Ctrl+C when finished. Keep credentials and API keys private.

## 7. Current limits

Policy updates currently use `docs/policies/current-policy.md` and the indexing script. Admin upload/review UI is pending. Private cases/profiles use scoped SQL; private vector retrieval and richer profile editing remain pending. Email send/receive is a case mock inbox, not a real mail server. Broader memory poisoning, inter-agent, accessibility and production deployment work remain open. Agent explanations can contain factual errors even when the execution boundary correctly blocks an action; verified ledger facts take precedence.
