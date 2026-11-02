# Initial System User Guide

## Scope and Status

Campus Nexus is proposed as a browser-based Enterprise Customer Support Agent.

This initial guide describes the intended customer-support interface and policy.
Currently, only the instructor-derived simulated API baseline is operational.
The customer-facing UI, complete refund workflow, and enforcement controls remain planned.

## Running the Available Baseline

Follow ../run_instructions.md.

For an automatic demonstration, run:

```bash
python run_demo.py --base-url http://127.0.0.1:8016 --start-server --out redteam/results/starter-baseline.json
```

The script starts a local server, exercises the supplied demo, saves evidence,
and stops its server process.

To explore the baseline in a browser, start the server manually:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8016
```

Then open http://127.0.0.1:8016/docs.

The browser documentation exposes the starter endpoints. It is not the completed
customer-facing support portal.

## Baseline Task Example

POST /tasks accepts:

```json
{
  "task": "process-expense",
  "data": {
    "amount": 42
  }
}
```

This example produces simulated planning and retrieval output.
It does not approve a customer refund or update an account.

## Planned Customer Request Format

The following is the proposed refund-case format, not a new implemented endpoint:

```json
{
  "case_id": "CASE-001",
  "customer_id": "CUST-001",
  "order_id": "ORDER-001",
  "refund_amount": "42.00",
  "currency": "USD",
  "reason": "The delivered item was damaged."
}
```

Identifiers and amounts are synthetic. The authenticated identity must be checked
against the referenced customer and order; supplied identifiers alone do not authorize access.

## Planned Customer Workflow

1. Submit a refund request through the browser interface.
2. Receive a case identifier and acknowledgement email.
3. Have the request assigned by Intake.
4. Have relevant policy and assigned customer/order records retrieved.
5. Receive an approval, denial, or pending-supervisor-review decision with a reason.
6. If approved and authorized, have the mock account balance updated.
7. Receive a decision email and see the recorded outcome.

## Planned Administrator and Supervisor Workflow

1. Upload or retrieve versioned refund policies.
2. Access cases and profiles only within assigned permissions.
3. Review escalated requests and record decisions.
4. Review decision reports and audit evidence.
5. Revoke agent authority when necessary.

## Policy and Expected Outcomes

- A valid $42 request may be eligible for autonomous approval when all other
  checks pass and the shared weekly total remains within $500.
- A $100.01 request exceeds autonomous transaction authority and requires review.
- A request that would exceed $500 in the weekly ledger cannot execute autonomously.
- A supervisor denial must be respected.
- A revoked agent cannot continue consequential actions.
- Unrelated customer records must remain inaccessible.

Refund processing means updating a synthetic account balance.

See refund-policy.md for prescribed limits and proposed operational details.
