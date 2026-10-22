# Red Team

This folder will organize security testing plans, findings, and evidence for Campus Nexus.

**Status:** Team assignments and test cases are pending.

## Responsibilities

- Identify attacker objectives and possible attack paths.
- Develop and execute authorized tests within the project sandbox.
- Preserve reproducible evidence of test outcomes.
- Evaluate proposed defenses and retest fixes.
- Contribute findings to the shared threat model and risk report.

## Planned Testing Areas

- Prompt injection and agent goal manipulation
- Unauthorized access to synthetic student records
- Refund policy and authorization bypasses
- Tool misuse and privilege abuse
- RAG and memory poisoning
- Insecure communication between agents

## Test Documentation

Each test should record:

- Objective, setup, and test inputs
- Expected and observed behavior
- Whether the agent attempted an unauthorized action
- Whether a control blocked it and whether the action executed
- Relevant logs, evidence, and retest results

Testing will use synthetic data and mock services within the authorized project environment.
