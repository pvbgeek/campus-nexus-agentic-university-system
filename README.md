# Campus Nexus
## Enterprise Customer Support Agent

Campus Nexus is a COEN 296 AI Governance and Cybersecurity capstone project.
The target application is a browser-based Enterprise Customer Support Agent
that processes assigned synthetic customer refund cases using specialized
agents and mock email, records, refund, and reporting tools.

The project combines functional development with threat modeling, Red Team
testing, defensive controls, and governance and assurance evidence.

## Current Implementation Status

The instructor-derived simulated starter runs locally. Its health endpoint,
normal task, supplied Red Team simulation, and structured logs have been verified.

The complete customer-support workflow, five specialized agents, actual LLM
integration, vector database, customer-facing browser UI, and independent
refund authorization controls remain planned.

The starter's simulated decision is not a refund approval or bank transfer.

## Planned Agents

| Agent | Responsibility |
|---|---|
| Orchestrator | Decompose requests, route work, maintain scoped task state, and aggregate results |
| Intake | Create support cases and assign them for processing |
| Email | Receive messages, draft replies, and send authorized acknowledgements and notifications |
| Records | Retrieve and update assigned customer cases and synthetic profiles through scoped tools |
| Refunds | Evaluate requests, record decisions, and request authorized mock refund processing |
| Reporting | Report approvals, denials, pending reviews, and decision reasons |

## Required Authority Limits

- Maximum autonomous refund: $100 per transaction.
- Cumulative refunds: no more than $500 in a week.
- No export of unrelated customer records.
- No agent modification of its own permissions.
- No bypass of supervisor decisions.
- No consequential actions after authority is revoked.
- Refund issuance means updating a mock account balance using synthetic data.

These are target requirements. The supplied starter does not enforce them yet.

## Documentation

- [Proposal-stage requirements coverage](docs/requirements-coverage.md)

- [Run instructions](run_instructions.md)
- [Initial system user guide](docs/user-guide.md)
- [Refund policy and authority controls](docs/refund-policy.md)
- [Team responsibilities](docs/team-responsibilities.md)
- [Implementation status](docs/implementation-status.md)
- [Architecture explanation](Architecture/README.md)
- [Red Team plan](redteam/plan.md)
- [MAESTRO mapping](threat_model/MAESTRO_mapping.md)
- [Starter provenance](docs/starter-source.md)

## Repository Structure

| Path | Purpose |
|---|---|
| app/ | Instructor-derived application baseline |
| requirements.txt | Runtime dependencies |
| run_demo.py | Demonstration and evidence collection |
| run_instructions.md | Installation, startup, and verification |
| Architecture/ | Planned architecture diagram and explanation |
| docs/ | User guide, policy, responsibilities, status, and proposal documents |
| redteam/ | Test plans, synthetic inputs, and recorded results |
| blue_team/ | Defense ownership and remediation documentation |
| threat_model/ | Shared threat model and MAESTRO mapping |
| logs/ | Baseline structured event evidence |
| report/ | Final report location |
| presentation/ | Slides and demo recordings |

## Course Starter

https://github.com/rafaebhatti/coen296/tree/main/project

Original source and local adaptations are recorded in docs/starter-source.md.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
