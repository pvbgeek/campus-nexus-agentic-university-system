# Current progress build

The connected application runs with:

```bash
.venv-agent/bin/python scripts/init_local.py
.venv-agent/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. Read ignored `data/demo-login.txt` privately for the generated local passwords. Customer identities are `avery` and `jordan`; the authorized staff identity is `supervisor`. These are synthetic demonstration users, not team members. Sessions expire after one hour. Sign out before switching identities, or use separate browser profiles.

## Working customer flow

Sign in as a customer, open an order, submit a positive USD refund request, and view the saved case and mock inbox acknowledgement. Submission does not execute a refund. A customer can request agent review of their own case; unverified evidence remains held for staff review.

## Working staff flow

Sign in as supervisor, open the case and read the supporting evidence. For the synthetic demonstration, record a specific assessment and select Verify evidence. This step does not authorize an exception to any monetary limit. Select Process refund to run the five live Groq agents through LangGraph. Wait for completion; throttling may make a run take several minutes. Inspect the agent trace and inbox messages, then open Reports to compare the actual ledger and authority state. Reports supports revoking and restoring authority with a recorded reason.

The seeded delivery dates are fictional fixtures created nine days before database initialization. Verified supporting evidence is an explicit staff action. The 30 day return window is a team policy, not an additional instructor requirement.

## Agents and retrieval

Intake summarizes the request and formulates the query. Records retrieves the bound customer's order and approved policy vectors, checks evidence and supplies source identifiers. Refunds proposes an action and amount. The independent MCP execution gateway validates the proposal and ledger rules. Email drafts a message for the bound case's mock inbox. Reporting summarizes that case while authoritative totals remain SQL computations.

Each stage makes a real Groq request with a validated output schema. There is no automatic simulated-model fallback. Missing credentials, invalid model responses or provider failures pause the workflow. Completed stages are saved in the case's agent run record. A retry rechecks current state and uses the same refund key, preventing a second credit if an earlier run executed before a later stage failed. This is persisted workflow evidence, not a claim of full LangGraph checkpoint resume.

Case-specific prior summaries provide persistent memory. Current graph state provides short term memory. Both prior summaries and retrieved passages remain untrusted inputs; neither can change server-side authority.

## Guardrails

Customer identity comes from the server session. Customer and staff routes enforce separate permissions. Mutating authenticated requests require a session-bound CSRF token; foreign origins are blocked. MCP receives one case capability and accepts only declared tool names and arguments. The model receives no shell, file reader, permissions editor or arbitrary SQL tool.

The gateway binds amount, customer, order and destination to stored case data. It requires staff evidence verification and a delivery date within the team return window. The ledger independently enforces ownership, a positive integer amount, the $100 transaction cap, the shared $500 UTC-week cap, remaining order balance, supervisor denial, revocation and idempotency. The ledger entry and synthetic account credit share one SQLite transaction.

Agent approval and actual execution are separate audit events. Model output cannot grant permissions, increase limits, restore authority or redirect a payment. API keys and passwords are stored only in ignored local files and are never returned by the API.

The application serializes workflows locally, caps per-case runs, bounds output tokens and applies local daily request/token budgets below the advertised Groq Free plan totals. The provider may still impose earlier organization limits. There is no paid-provider fallback.

## Verification

```bash
.venv-agent/bin/python scripts/check_progress.py
```

The ledger suite has 13 checks. The API/MCP suite has 19 checks, including unauthorized staff access, cross-customer reads, forged identity fields, CSRF, unexpected MCP arguments, amount tampering, revocation and supervisor denial. These make no model requests. The graph integration check uses real MCP and vector retrieval with an explicitly labelled model test double. The separate live check uses real Groq requests for a valid refund and a prompt-injection attempt requesting an over-limit refund and account redirection.

All security scenarios use isolated temporary synthetic databases. The live test expects one $64 mock credit, no injected $125 credit and no destination change. Its audit records are exported to `logs/progress-live-audit.jsonl`. Provider identifiers, usage, retrieved sources, case IDs, run IDs, proposals, independent authorization and actual ledger execution can be correlated from the JSON evidence.

## Remaining work

The current UI supports the documented refund flow. Original storefront, catalog, design-system and state reference pages remain design material; they are not a functioning commerce platform. The project target remains customer support.

Policy source changes can be indexed using the existing script. A staff policy upload/review interface, broader memory poisoning and inter-agent attack coverage, richer notification handling, deployment, final benchmarks and final governance analysis remain future work. The app uses local SQLite and local Qdrant; hosted deployment needs an explicit persistent-storage plan.

Do not claim successful live model tests until `scripts/check_progress.py` completes on the machine with the configured free-tier key. The User Guide, architecture and progress PDF should report verified results and remaining work honestly.

The original course simulation is preserved in `app/starter_main.py`. The primary `app.main:app` entry point now serves the connected application. Historical starter evidence remains labelled as baseline evidence; use `scripts/check_progress.py` for the current build.
