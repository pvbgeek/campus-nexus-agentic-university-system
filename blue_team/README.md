# Blue Team

This folder will organize defense documentation, monitoring plans, remediation notes, and retest evidence for Campus Nexus.

**Status:** Team assignments and defensive controls are pending.

## Responsibilities

- Define allowed agent actions, permissions, and trust boundaries.
- Implement controls that enforce permissions and refund policies.
- Monitor activity and investigate security findings.
- Remediate weaknesses and verify fixes through retesting.
- Contribute to the shared threat model, risk report, and governance documentation.

## Planned Defense Areas

- Access controls for synthetic student records
- Refund limits and supervisor approval requirements
- Restricted agent permissions and tool access
- Protection against prompt injection and poisoned retrieval content
- Audit logging and suspicious activity detection
- Revocation of agent authority and emergency stopping
- Incident containment and recovery

## Defense Documentation

Each control should record:

- Purpose and the threat it addresses
- Expected permitted and denied actions
- Enforcement point and responsible owner
- Test outcomes and supporting logs
- Remediation, retest results, and remaining risks

Control testing should verify both that unauthorized actions are blocked and that legitimate requests still work.
