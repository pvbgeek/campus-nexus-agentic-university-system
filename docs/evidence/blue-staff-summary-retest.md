# Blue Team retest: staff refund summary

Recorded (UTC): 2026-11-24T21:48:38Z

Base commit: dea89e5

## Change

The staff summary now uses the verified refund ledger entry. The model draft remains in the workflow checkpoint. The earlier inbox change and its retest are documented separately in `blue-inbox-notification-retest.md`.

## Observed result

PASS: Staff summary, credited amount and refund ID agree with the ledger.

The targeted check covered two synthetic outcomes: no credit (0 cents and no refund ID), and an executed 6400-cent credit with a matching refund ID. It exercised the report construction code without calling Groq or running the full workflow.

## Remaining verification

Confirm that a full case run saves the ledger-based inbox message and returns the matching staff summary. Retain the historical Red Team evidence separately.
