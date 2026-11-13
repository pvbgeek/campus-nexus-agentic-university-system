# Synthetic test inputs

`example-refund-request.json` matches the current authenticated case API format. Replace the request key for each new case. Identity and evidence verification are resolved by the server and must not be supplied in the body.

`prompt-injection-over-limit.json` documents the adversarial live fixture. Only submit it to this authorized local synthetic application. The executable live suite creates unique request keys, verifies synthetic evidence as staff and checks both model outcome and actual ledger/account effects.

Test code creates isolated fixtures for ownership, caps, concurrency, revocation and supervisor denial. Do not point tests at real accounts or put keys/passwords in input files.
