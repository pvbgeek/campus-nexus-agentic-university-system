# Implementation status

Verified on November 12, 2026. Evidence timestamps use UTC; the successful live run started on November 13 UTC, which was November 12 in California.

| Component | Current behavior |
|---|---|
| Browser UI | Customer/staff sign in, orders, refund submission, case messages/traces, staff verification and decisions, authority controls and reports |
| Intake | Persistent case submission, ownership check and common authorized staff queue |
| Five agents | Real Groq calls for Intake, Records, Refunds, Email and Reporting in a LangGraph graph |
| MCP | Real local stdio discovery/calls; one bound case; declared tools and strict argument validation |
| Policy retrieval | FastEmbed BAAI/bge-small-en-v1.5 vectors; persistent local Qdrant; source hashes and chunk IDs |
| Private records | Scoped SQL order/case/account reads; no vector index of private profiles/cases yet |
| Memory | Short term graph state and persisted case-specific prior summaries; history remains untrusted |
| Authorization | Independent proposal/evidence checks plus atomic ledger checks for ownership, caps, balance, denial, revocation and duplicates |
| Mock payment | Refund ledger entry and synthetic account credit in one SQLite transaction |
| Mock email | Saved acknowledgement and agent decision in case inbox; no external email transport |
| Reporting | Actual SQL totals and outcomes; model summaries labelled separately |
| Logs | Timestamp, case/run IDs, source evidence, provider IDs/usage, proposal, authorization and execution can be correlated |
| Deployment | Local loopback application only; hosting and durable hosted storage remain pending |

## Verified results

- 13/13 ledger checks passed.
- 19/19 API/MCP checks passed.
- Real MCP policy retrieval passed.
- Five-node graph integration passed with a labelled provider test double and real MCP/vector tools.
- Two live model workflows passed: one $64 mock credit; injected $125 request held; destination unchanged.
- Successful live batch: 10 Groq calls, 9,601 tokens, 66 audit events, one ledger entry.
- Browser HTTP logs supplied by Parth show successful sign in, orders, case submission, agent review, case detail and sign out. A complete manual staff UI walkthrough and accessibility assessment have not been independently confirmed.

The control results were reused from the earlier passed stages when rerunning the affected graph and live checks. They were not all rerun after every prompt/diagnostic edit.

## Remaining findings and scope

See [findings](findings.md). The injected request was contained, but the Refunds agent incorrectly described authority as revoked while the server reported it active. Explanation grounding remains open. Earlier valid-request refusal and provider HTTP 400 runs are preserved in history. A later valid request executed successfully; the HTTP 400 cause was not conclusively identified.

Admin policy upload/review UI, private case/profile vector retrieval, profile editing, richer inbound messages, broader memory poisoning and inter-agent attacks, final benchmarks and governance/assurance deliverables remain pending. The graph has a fixed five-stage decomposition; it is not a general dynamically replanning system. Persisted stage snapshots support inspection, not complete checkpoint resume.
