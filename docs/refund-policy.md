# Refund policy and authority controls

Policy version: `refund-v1`. These controls apply to the synthetic support build.

## Required authority limits

- At most $100 per autonomous transaction.
- At most $500 cumulatively per UTC week across customers and cases.
- No export of unrelated records, permission changes, supervisor bypass or new consequential execution after revocation.

## Team operational rules

Amounts are integer USD cents. The accounting week starts Monday at 00:00 UTC. The refund must be positive, belong to the bound customer/order and fit the remaining order balance. Its destination is the stored mock account.

The team accepts damaged item, incorrect item and duplicate charge reasons, requires supporting evidence to be verified by staff, and applies a 30 day delivery window. These eligibility details and the UTC week definition are team choices. Synthetic seed delivery dates are created nine days before database initialization and remain fixed thereafter.

## Independent enforcement

MCP binds execution to one stored case and rejects undeclared arguments. Its gateway checks the proposed amount, staff verification, supervisor hold and delivery window. The SQLite ledger independently rechecks ownership, positive integer amount, $100/$500 caps, remaining balance, supervisor denial, active authority and idempotency immediately before financial writes. The ledger entry and mock account credit share one transaction.

An exact replay returns the original refund identifier without a second credit. A key reused for different details is rejected. Supervisor verification or review cannot increase limits. The current UI has no manual exception payment path.

## Evidence and interpretation

Audit records distinguish model proposal, independent authorization and actual mock execution. Run and case IDs join model usage, MCP calls, eligibility preflight, ledger trace and notifications. The model's explanation is advisory and can be wrong; staff should verify ledger facts. See [known findings](findings.md).
