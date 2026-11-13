# MAESTRO threat model outline

## Scope, assets and actors

The target is a local browser based Enterprise Customer Support Agent with synthetic customers, refund cases, policy vectors, mock accounts and inboxes. Assets include customer/case confidentiality, refund integrity, stored destination, authority settings, model key, policy provenance, memory, audit evidence and availability.

Actors are two synthetic customer identities, one authorized staff identity, the five Groq agents, trusted application/MCP processes and the authorized Red Team. A customer can place hostile instructions in a request. Model output, retrieved text and prior case summaries are untrusted even when they appear well formatted.

## Trust boundaries

1. Browser to API: server-resolved identity, role checks, case ownership and request protection.
2. Application to Groq: only case-scoped context; key remains server side; schema validation does not establish factual truth.
3. Graph to MCP: local stdio capability bound to one case/run, declared tool allowlist and strict arguments.
4. Proposal to financial execution: server evidence/case checks, followed by atomic ledger checks independent of model text.
5. Retrieval/memory to reasoning: approved policy vectors and scoped case memory remain reference data rather than authority.
6. Stored evidence to reporting: actual SQL ledger totals take precedence over a generated explanation.

## Seven layer outline

| MAESTRO layer | Threat and entry point | Current controls/evidence | Remaining work |
|---|---|---|---|
| 1. Foundation Models | Prompt injection, false refusal and misleading explanation in model output | Real live adversarial fixture; validated response schemas; independent gateway | In-limit attack variants, explanation grounding, utility/security comparison |
| 2. Data Operations | Policy poisoning, unrelated record disclosure, altered memory | Source hashes, approved policy collection, scoped SQL and case-specific prior memory; cross-case tests | Admin ingestion/review, private vector records, poisoning tests and memory integrity checks |
| 3. Agent Frameworks | Forged arguments, unauthorized tool selection, confused deputy | Fixed LangGraph roles, real scoped MCP tools, strict tool/argument validation; direct MCP tests | Broader forged inter-agent messages and dependency review |
| 4. Deployment & Infrastructure | Secret exposure, unauthorized listener, lost or tampered storage | Loopback development service, ignored private files, generated credentials, dependency lock | Hosted storage, hardened transport/secrets, backups and deployment controls |
| 5. Evaluation & Observability | Missing traces, misleading model claims, log poisoning | Correlated case/run/ledger IDs, usage, 66 live audit events, JSON and JSONL exports; test-double labels | Tamper evidence, retention/redaction policy and broader coverage metrics |
| 6. Security & Compliance | Scope/permission escalation, supervisor bypass, over-limit or revoked execution | Authentication/roles/CSRF, bound case, staff verification, atomic caps/ledger, denial/revocation/idempotency checks | More race tests, governance mapping and final assurance evidence |
| 7. Agent Ecosystem / Use Case | Cascading wrong decisions, inappropriate reliance on generated summaries | Authoritative SQL totals, separate proposal/authorization/execution, mock financial boundary | End-to-end risk analysis, human oversight evaluation and Appendix I context |

## Initial findings and risk treatment

The successful live attack was contained, but the agent incorrectly claimed authority was revoked. Treat this as an explanation integrity risk, not a financial escape. The earlier valid refusal is a utility failure; the provider HTTP 400 is an availability/reliability issue with an unconfirmed original cause. See `docs/findings.md` and the preserved evidence history.

MCP's unexpected-argument behavior was tightened and the final boundary suite passed. The uploaded record does not contain a separate complete before/after attack trace for that development observation.

The current coverage is an outline and interim evidence, not the final threat model or complete assurance audit. Final work will assess residual risks, functional/security benchmarks and the public benefits scenario added in Appendix I of the supplied specification. No legal classification or final compliance conclusion is asserted here.
