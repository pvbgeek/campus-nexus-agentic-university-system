# Refund Policy and Authority Controls

Status: initial policy for the proposed application.
The current starter does not implement these controls.

## Limits Prescribed by the Project Specification

1. Autonomous refunds must not exceed $100 per transaction.
2. Cumulative refunds must not exceed $500 in a single week.
3. The agent must not export unrelated customer records.
4. The agent must not change its own permissions.
5. The agent must not bypass supervisor decisions.
6. Consequential actions must stop after authority is revoked.

## Proposed Operational Rules

These details are team design choices for implementing the prescribed limits:

- Use USD and integer cents for monetary calculations.
- Define the weekly accounting window as Monday 00:00 UTC through the next Monday.
- Use one shared weekly ledger across cases and customers.
- Verify customer identity and ownership of the referenced order.
- Require a positive amount no greater than the order's remaining refundable amount.
- Record a reason for every approval, denial, or pending review.
- Use a unique refund identifier to prevent duplicate processing.
- Retrieve the refund destination from the authorized synthetic customer profile,
  rather than trusting account instructions in a customer message.

## Supervisor Review

Requests outside autonomous authority are held for supervisor review.
A supervisor decision must be recorded and must not be overridden by the agent.
Review does not allow the agent to bypass the configured refund limits.
Any separately authorized manual process is outside autonomous agent processing.

## Independent Enforcement

The planned execution gateway checks identity, assigned case, tool permissions,
refund amount, weekly total, supervisor decision, revocation, and duplicate
processing immediately before execution.

Monetary checks and ledger updates must be atomic to prevent concurrent requests
from exceeding the weekly limit.

LLM output and retrieved text cannot grant authority or change these checks.

## Mock Refund Processing

An approved and authorized refund updates a synthetic account balance.
No real bank transfer or external payment is made.

## Audit Evidence

Record case and decision identifiers, actor, requested action, authorization
outcome, execution outcome, policy version, amount, timestamp, and reason.
Keep unrelated profile information and credentials out of evidence exports.
