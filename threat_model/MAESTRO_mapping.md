# Initial MAESTRO Mapping

Status: initial planning outline, not a completed threat model or verified control assessment.
Both Red and Blue subteams contribute.

| Layer | Initial threats to examine | Planned controls and evidence |
|---|---|---|
| 1. Foundation Models | Prompt injection and incorrect refund reasoning | Trusted instruction handling, independent execution checks, recorded outputs |
| 2. Data Operations | Policy poisoning and cross-customer disclosure | Provenance, scoped retrieval, case isolation, controlled updates |
| 3. Agent Frameworks | Unsafe routing and tool misuse | Explicit tool permissions, validated messages, bounded delegation |
| 4. Deployment and Infrastructure | Exposed services and credential leakage | Local development isolation, controlled configuration, dependency review |
| 5. Evaluation and Observability | Missing logs and misleading test success | Decision/execution records, reproducible inputs, explicit result checks |
| 6. Security and Compliance | Limit bypasses and ignored revocation | Independent authorization, atomic weekly ledger, supervisor decisions, revocation |
| 7. Agent Ecosystem / Use Case | Forged authority and cascading failures | Identity-bound calls, bounded permissions, containment and recovery plans |

## Development Process

1. Identify assets and trust boundaries.
2. Develop plausible attacks and attack chains.
3. Assess implemented controls and detection gaps.
4. Execute authorized tests and preserve evidence.
5. Assign remediation owners and retest.
6. Update threats, controls, and residual-risk assessments.

The instructor's file refers to a MAESTRO template. Use the class-provided template
when available; this outline is not presented as that official template.
