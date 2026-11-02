# Proposal-Stage Requirements Coverage

This document maps repository evidence to the project specification and Camino rubric.
It distinguishes verified starter functionality from the planned target application.

## Required Proposal Content

| Requirement | Repository evidence | Current status |
|---|---|---|
| Application name and correct target | README.md | Campus Nexus: Enterprise Customer Support Agent |
| Initial architecture diagram and explanation | Architecture/architecture.png and Architecture/README.md | Proposed complete target design documented |
| Initial system user guide | docs/user-guide.md | Initial guide and synthetic request examples provided |
| Starter and team repository references | README.md and docs/starter-source.md | Instructor source, upstream commit, and local adaptations documented |
| Individual responsibilities | docs/team-responsibilities.md | Existing subteams retained; individual work allocation proposed for team confirmation |

## Camino Rubric Coverage

| Criterion | Evidence | Qualification |
|---|---|---|
| Team details | docs/team-responsibilities.md | Includes full names, subteams, and proposed individual duties |
| Functioning sample repository | app/, requirements.txt, run_demo.py, run_instructions.md | Instructor-derived simulated baseline verified locally |
| Architecture and description | Architecture/ | Includes five specialized agents, orchestration, retrieval, mock tools, and authority boundaries |
| Structured write-up | README.md and docs/ | Repository documentation is organized; revised submission PDF is the next deliverable |

## Verified Baseline Evidence

- redteam/results/starter-baseline.json
- redteam/results/RT-01/rt-01-results.json
- logs/events.jsonl

The health endpoint, normal task, supplied Red Team simulation, and log retrieval
returned HTTP 200. The two supplied canned inputs were flagged and persisted
JSONL records were parsed successfully.

This evidence applies to the simulated starter only.

## Planned Application Requirements

The target design includes Intake, Email, Records, Refunds, and Reporting agents,
plus an orchestrator, browser UI, scoped memory, vector retrieval, synthetic
customer/account records, and mock tools.

The policy specifies a $100 autonomous transaction limit and a $500 cumulative
weekly limit. Unrelated-record export, permission changes, supervisor-decision
bypass, and consequential actions after revocation are prohibited.

These controls and the complete refund workflow remain planned, as stated in
docs/implementation-status.md.

## Remaining Submission Actions

- Confirm the proposed individual work allocation with the team.
- Prepare the corrected proposal PDF using the current repository documentation.
- Verify that the PDF includes every required section and a readable diagram.
- Update the GitHub About description to match the corrected application scope.

The original submission and original architecture are preserved under docs/archive/.
