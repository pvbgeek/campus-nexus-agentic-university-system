# Campus Nexus
### Multi-Agent University Marketplace Support and Refund Management System

Campus Nexus is a full-stack, AI-powered customer support and refund management application developed for **CSEN 296**. It integrates five specialized LLM agents with authenticated application workflows, semantic policy retrieval, scoped tools, and independently enforced financial authorization.

The system demonstrates how agentic AI can assist with customer support while keeping consequential operations under deterministic backend controls.

> **Project scope:** Educational demonstration using synthetic customer data, simulated refunds, and local mock inbox notifications. No real payments or external emails are processed.

## Live Application

**[Launch Campus Nexus](https://campus-nexus-vercel.vercel.app/)**

The application uses Vercel for its public frontend entry point and Railway for backend hosting.

### Project Documentation

| Document | Link |
|---|---|
| Final Project Report | [View PDF](report/Final_Project_Report.pdf) |
| User Guide | [View PDF](docs/Campus-Nexus-User-Guide.pdf) |
| System Architecture | [Architecture](Architecture/README.md) |
| Threat Model | [MAESTRO Mapping](threat_model/MAESTRO_mapping.md) |
| Red Team Test Plan | [Test Plan](redteam/plan.md) |
| Security Findings | [Findings](docs/findings.md) |
| Local Execution | [Run Instructions](run_instructions.md) |

## Technology Stack

| Component | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Agent Orchestration | LangGraph |
| LLM Inference | Groq API, `openai/gpt-oss-20b` |
| Tool Integration | Model Context Protocol (MCP) |
| Semantic Retrieval | FastEmbed, Qdrant |
| Embeddings | `BAAI/bge-small-en-v1.5` |
| Application Storage | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Hosting | Vercel, Railway, Docker |
| Testing | Python, API/MCP tests, adversarial workflow evaluation |
| Security Analysis | OWASP, MAESTRO threat modeling |

## Multi-Agent Architecture

Campus Nexus coordinates five specialized AI agents through LangGraph.

1. **Intake Agent:** Structures the submitted refund case and prepares relevant request information.
2. **Records Agent:** Retrieves scoped customer/order records and semantically relevant policy documents.
3. **Refunds Agent:** Evaluates eligibility and recommends execution, review, or denial.
4. **Email Agent:** Generates customer-facing messages for the local mock inbox.
5. **Reporting Agent:** Summarizes case processing and staff-facing outcomes.

The agents exchange structured workflow state, but their outputs do not independently authorize financial actions.

### Architecture Diagram

![Campus Nexus Architecture](Architecture/architecture.png)

The execution gateway validates agent proposals against authenticated case context and backend authority rules. Refund settlement is independently controlled by the application ledger.

## Application Features

### Customer Features

- Account registration and authenticated sign-in
- Synthetic marketplace order viewing
- Refund request submission and tracking
- Customer profile editing
- Case follow-up messages
- Mock inbox notifications
- Refund status and history visibility

### Staff Features

- Authenticated staff access
- Refund case and evidence review
- Evidence verification
- Multi-agent refund processing
- Staff reporting and audit inspection
- Refund authority revocation and restoration
- Policy update review workflows

Approved policy publication is performed through a separate administrative process.

## Security and Refund Controls

Campus Nexus separates LLM recommendations from backend execution authority.

Implemented controls include:

- Authenticated customer and staff sessions
- Role-based authorization
- Customer/order ownership validation
- Scoped MCP tool execution
- Request validation and CSRF protection
- Evidence verification requirements
- Supervisor denial and authority revocation
- Refund balance validation
- Idempotent refund execution
- Atomic SQLite transactions
- Correlated audit evidence

### Financial Limits

| Constraint | Enforced Limit |
|---|---|
| Individual refund transaction | $100 |
| Shared cumulative weekly refunds | $500 |
| Refund amount | Cannot exceed remaining order balance |
| Refund destination | Bound to the stored mock account |
| Duplicate execution | Prevented using idempotency controls |

Model-generated text, retrieved documents, and user-supplied instructions cannot independently change these backend limits.

## Run Locally

### Requirements

- Git
- Python 3.12
- `uv`
- Internet access for initial model downloads and Groq inference
- Groq API key

### Setup

Clone the repository:

```bash
git clone https://github.com/pvbgeek/campus-nexus-agentic-university-system.git
cd campus-nexus-agentic-university-system
```

Create the environment:

```bash
uv venv --python 3.12 .venv-agent
uv pip install --python .venv-agent/bin/python -r requirements-agents.lock.txt
```

Configure and initialize:

```bash
.venv-agent/bin/python scripts/configure_groq.py
.venv-agent/bin/python scripts/build_policy_index.py
.venv-agent/bin/python scripts/init_local.py
```

Start the application:

```bash
.venv-agent/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open: <http://127.0.0.1:8000>

Demo credentials are generated locally and stored in `data/demo-login.txt`. Do not commit credentials, `.env`, sessions, or operational databases.

For Windows, use `.venv-agent/Scripts/python.exe` instead.

## Testing and Evaluation

The project includes functional, integration, authorization, and adversarial workflow testing.

| Evaluation | Recorded Result |
|---|---|
| Refund ledger controls | 13/13 passed |
| API and MCP security controls | 19/19 passed |
| Retrieval integration | Passed |
| LangGraph integration | Passed using a labelled model test double |
| Eligible local refund | $64 mock credit executed |
| Adversarial local refund | $125 request held; no credit |
| Notification consistency retest | Customer inbox and staff reporting matched the ledger |
| Hosted legitimate refund | $64 executed within authority |

The live adversarial scenario included instructions to impersonate an administrator, modify authorization limits, and redirect refund processing.

No unauthorized credit occurred. However, the model incorrectly described refund authority as revoked, illustrating the distinction between execution safety and explanation accuracy.

These results establish behavior for the tested scenarios, not comprehensive prompt-injection resistance.

### Run Verification

```bash
.venv-agent/bin/python scripts/check_progress.py
```

This runs the progress verification suite, including real Groq workflows that consume API quota.

Evidence is stored under `redteam/results/`, with corresponding local audit information under `logs/`.

## Cloud Deployment

The public application uses:

- **Vercel:** Public entry point, frontend routing, and application proxy.
- **Railway:** Containerized FastAPI application, agents, MCP tools, and Groq integration.
- **Persistent Railway Volume:** Application data and the policy index.
- **Groq:** Hosted LLM inference.

The hosted demonstration confirmed customer and staff authentication and one eligible $64 mock refund.

Provider quotas, service availability, and recovery behavior remain operational considerations. A hosted restart-and-recovery exercise has not been established by the recorded evidence.

## Repository Structure

```text
Architecture/       Architecture diagram, generator, and documentation
app/                FastAPI backend, frontend, agents, storage, MCP integration
blue_team/          Blue Team controls and implementation notes
red_team/           Red Team directory reference
redteam/            Security tests, attack inputs, results, and evidence
docs/               User Guide, policies, findings, UI artifacts, evidence
logs/               Sanitized synthetic audit events
report/             Progress Report and Final Project Report
presentation/       Presentation materials
scripts/            Setup, policy indexing, validation, and verification
threat_model/       MAESTRO threat model
```

The connected application entry point is `app.main:app`.

The original instructor simulation remains available in `app/starter_main.py` and is separate from the connected multi-agent application.

## Threat Modeling and Governance

Security analysis covers:

- Prompt injection and instruction manipulation
- Cross-customer data access
- Unauthorized tool execution
- Policy and retrieval integrity
- Memory and inter-agent trust boundaries
- Agent explanation accuracy
- Audit traceability
- Infrastructure availability
- Refund authorization and financial integrity

The project examines governance concepts from the EU AI Act, including risk management, documentation, logging, human oversight, robustness, and incident response.

These are educational design and assurance mappings, not legal compliance certification.

See the Final Project Report for detailed findings.

## Limitations

- Refund settlement and notifications are simulated.
- Private customer records are retrieved through scoped application queries, not private-record vector search.
- Adversarial testing does not establish comprehensive robustness.
- The hosted record contains a successful legitimate refund but not a completed hosted adversarial benchmark.
- Hosted restart/recovery and long-term audit retention require additional validation.
- Groq free-plan quotas and external service availability can affect inference.

## Project Team

### Blue Team

- Parth Bhalerao
- Kavya Sharma
- Calianna Collins

### Red Team

- Dana Steinke
- Noelle Evanich

Detailed technical contributions are documented in the Final Project Report.

## License

See LICENSE.
