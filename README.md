# Wealth Advisor Assistant — Multi-Agent System

A lightweight, production-oriented multi-agent system for a **Wealth Advisor Assistant**.

The system ingests client financial data, fetches additional CRM context, analyzes transactions and risk signals, detects anomalies, and produces a structured advisory decision. It also includes short-term/long-term memory, logging, graceful error handling, and a human-in-the-loop checkpoint for high-risk cases.

> **Assignment alignment:** The implementation directly covers the required orchestrator, two or more specialized agents, tool abstraction, error handling, logging, and the optional memory + human approval features.

---

## 1. What the system does

Given a client ID and financial data, the system:

1. Loads and validates the client financial data.
2. Fetches CRM context through an abstracted CRM tool.
3. Runs financial analysis and anomaly detection.
4. Generates a structured advisory recommendation.
5. Stores useful session and historical insight information.
6. Requests human approval when the risk level requires it.
7. Returns a structured final result and records the complete execution flow.

### Example flow

```text
                    ┌──────────────────────┐
                    │   Orchestrator Agent │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
        ┌────────────────┐ ┌────────────┐ ┌────────────────┐
        │ Data Fetcher   │ │ Analyzer   │ │ Advisor Agent  │
        │ Agent          │ │ Agent      │ │                │
        └───────┬────────┘ └─────┬──────┘ └───────┬────────┘
                │                │                │
                ▼                ▼                ▼
        ┌──────────────┐ ┌───────────────┐ ┌───────────────┐
        │ Client Data  │ │ Anomaly Tool  │ │ Decision      │
        │ + CRM Tool   │ │ + Risk Rules  │ │ / HITL Check  │
        └──────────────┘ └───────────────┘ └───────────────┘
                │                │                │
                └────────────────┼────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ Memory + Structured     │
                    │ Advisory Output         │
                    └─────────────────────────┘
```

---

## 2. Architecture

### Agents

#### 1. Orchestrator Agent
Central coordinator.

Responsibilities:
- Starts and manages the workflow.
- Routes information between specialized agents.
- Controls execution order.
- Handles agent/tool failures.
- Decides when the workflow needs human approval.
- Produces the final structured response.

#### 2. Data Fetcher Agent
Responsible for gathering the input context.

Responsibilities:
- Validates client financial data.
- Fetches CRM information through the CRM tool abstraction.
- Normalizes the data into a common internal representation.
- Uses graceful fallback when CRM is unavailable.

#### 3. Analyzer Agent
Responsible for deterministic financial analysis.

Responsibilities:
- Calculates income/expense/savings metrics.
- Calculates portfolio concentration.
- Detects unusual transactions.
- Detects spending and risk signals.
- Produces a normalized risk assessment.

#### 4. Advisor Agent
Turns analysis into an actionable but non-executing advisory decision.

Responsibilities:
- Produces structured recommendations.
- Explains the main reasons for the recommendation.
- Adds warnings/disclaimers.
- Requests human validation for high-risk recommendations.

The separation is intentional: the analyzer calculates facts, while the advisor interprets those facts. This makes the system easier to test and reduces hidden coupling.

---

## 3. Tool abstraction

Agents never directly instantiate or depend on raw API implementations.

The project defines tool protocols/interfaces:

```text
CRMTool
 └── MockCRMTool

AnomalyDetectionTool
 └── StatisticalAnomalyTool

HumanApprovalTool
 └── ConsoleHumanApprovalTool
```

This means a real CRM client, cloud service, or UI-based approval mechanism can replace the mock implementation without changing the agents.

---

## 4. End-to-end execution

```text
Input JSON
   │
   ▼
Orchestrator
   │
   ├── DataFetcherAgent
   │      ├── Validate client data
   │      └── CRMTool.get_client_context()
   │
   ├── AnalyzerAgent
   │      ├── Financial metrics
   │      ├── Concentration analysis
   │      └── AnomalyDetectionTool
   │
   ├── AdvisorAgent
   │      ├── Risk-based recommendation
   │      └── Human approval if required
   │
   └── Memory
          ├── Session memory
          └── Historical insight memory
   │
   ▼
Structured JSON output
```

---

## 5. Project structure

```text
wealth_advisor_agent/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── data_fetcher.py
│   │   ├── analyzer.py
│   │   └── advisor.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── crm.py
│   │   ├── anomaly.py
│   │   └── human_approval.py
│   └── memory/
│       ├── __init__.py
│       └── store.py
├── data/
│   ├── clients.json
│   └── sample_output.json
├── tests/
│   ├── test_anomaly.py
│   ├── test_agents.py
│   └── test_orchestrator.py
├── logs/
│   └── .gitkeep
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 6. Setup

### Requirements

- Python 3.10+
- No external database
- No API key
- No LLM key required for the default implementation

### Create environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## 7. Run the application

From the project root:

```bash
python -m app.main
```

The application reads:

```text
data/clients.json
```

and writes/prints a structured advisory result.

To run with a specific client:

```bash
python -m app.main --client-id C001
```

To simulate CRM failure and verify fallback behavior:

```bash
python -m app.main --client-id C001 --crm-failure
```

To bypass interactive human approval during automated execution:

```bash
python -m app.main --client-id C001 --auto-approve
```

---

## 8. Run tests

```bash
pytest -q
```

The tests cover:
- anomaly detection,
- data-fetcher behavior,
- analyzer calculations,
- CRM failure fallback,
- orchestrator execution,
- high-risk human approval flow.

---

## 9. Sample input

`data/clients.json` contains mock data with:
- client profile,
- monthly income,
- monthly expenses,
- investment holdings,
- recent transactions,
- financial goals.

Example:

```json
{
  "client_id": "C001",
  "monthly_income": 180000,
  "monthly_expenses": 85000,
  "risk_profile": "moderate",
  "holdings": [
    {"asset": "Equity Fund A", "value": 650000},
    {"asset": "Equity Fund B", "value": 150000},
    {"asset": "Debt Fund A", "value": 200000}
  ]
}
```

---

## 10. Sample output

The output is intentionally structured rather than a block of generated text:

```json
{
  "client_id": "C001",
  "status": "completed",
  "risk_level": "medium",
  "summary": {
    "monthly_surplus": 95000,
    "savings_rate": 0.528,
    "portfolio_concentration": 0.65,
    "anomaly_count": 2
  },
  "anomalies": [
    {
      "transaction_id": "T007",
      "reason": "Transaction amount is unusually high"
    }
  ],
  "recommendations": [
    "Review the unusually large transaction.",
    "Consider reducing concentration in the largest equity holding.",
    "Maintain an emergency reserve before increasing investment exposure."
  ],
  "human_approval": {
    "required": false,
    "status": "not_required"
  }
}
```

---

## 11. Anomaly detection approach

The assignment asks for unusual transactions, trends, or risk signals.

This implementation uses a simple and explainable statistical approach:

- For a sufficiently large transaction history, calculate the mean and standard deviation.
- Flag unusually large deviations using a configurable z-score threshold.
- Also apply deterministic business rules for:
  - negative/invalid amounts,
  - unusually large transactions relative to monthly income,
  - repeated high-value transactions,
  - concentration risk.

Why not use a complex ML model?

For this assignment, explainability and reliability are more valuable than model complexity. A financial reviewer should be able to understand why a transaction was flagged.

The anomaly detector is isolated behind a tool interface, so an ML-based detector can be introduced later.

---

## 12. Risk assessment

Risk is derived from transparent signals rather than an opaque score.

Example signals:

```text
High:
- severe transaction anomalies
- very high portfolio concentration
- suspicious data quality
- conflicting client/CRM information

Medium:
- moderate concentration
- unusual spending
- multiple anomaly signals

Low:
- no major anomalies
- healthy savings behavior
- diversified holdings
```

The risk engine is deliberately deterministic. This avoids making financial decisions dependent on an LLM's probabilistic behavior.

---

## 13. Memory layer

The optional memory requirement is implemented using two lightweight stores.

### Short-term memory

Stores information for the current execution:
- client ID,
- current workflow state,
- intermediate agent outputs,
- execution status.

This is useful for passing context between agents without relying on global variables.

### Long-term memory

Stores historical advisory summaries in:

```text
data/memory.json
```

The stored information is intentionally limited to useful summaries rather than raw sensitive financial data.

In a production system, this could be replaced by:
- PostgreSQL,
- Redis,
- a secure document store,
- or a vector database for semantic historical retrieval.

---

## 14. Human-in-the-loop checkpoint

For high-risk cases, the advisor agent does not silently finalize the recommendation.

Instead:

```text
Analysis
   │
   ▼
High Risk?
 ┌─┴─────┐
No       Yes
│         │
▼         ▼
Finalize  Human Approval
          │
      ┌───┴───┐
    Approve  Reject
      │         │
      ▼         ▼
   Finalize   Escalated
```

This is especially important for a financial-advisory workflow because the system is designed to assist a human advisor, not independently execute financial transactions.

For CI/test environments, `--auto-approve` can be used.

---

## 15. Error handling

The system handles failures at the boundaries where they are expected:

### CRM failure
The Data Fetcher records the error and continues with a clearly marked fallback context.

### Missing financial fields
Input validation reports the missing field rather than producing a misleading recommendation.

### Empty transaction history
Analysis still runs, but anomaly detection is skipped with an explicit reason.

### Tool failure
Tool errors are captured in the workflow result and logs.

### Human approval failure
The workflow is marked as `escalated` rather than treating an unavailable approval channel as approval.

The guiding principle is:

> **Fail safely, not silently.**

---

## 16. Logging and observability

Logs are written to:

```text
logs/app.log
```

Each major operation records:
- workflow start/end,
- agent execution,
- tool calls,
- decisions,
- warnings,
- errors,
- human approval state.

Example:

```text
INFO  Workflow started for client C001
INFO  DataFetcherAgent completed
INFO  AnalyzerAgent completed: risk=medium anomalies=2
INFO  AdvisorAgent generated 3 recommendations
INFO  Workflow completed
```

For production, these structured events could be sent to Cloud Logging, ELK, Datadog, OpenTelemetry, or another observability platform.

---

## 17. Key design decisions and trade-offs

### Deterministic analysis vs LLM-first analysis

**Decision:** deterministic Python analysis for financial calculations.

**Reason:** numerical calculations, thresholds, and anomaly detection should be reproducible and auditable.

An LLM can later be added for natural-language explanation, but it should not be responsible for core numerical calculations.

### Sequential orchestration vs autonomous agents

**Decision:** controlled sequential workflow.

**Reason:** this problem has a clear dependency chain:

```text
Data → Analysis → Advisory
```

An autonomous agent loop would add complexity without improving the assignment's core objective.

### Tool interfaces vs direct implementations

**Decision:** agents depend on interfaces/protocols.

**Reason:** easier testing and replacement of mock services with real APIs.

### Local JSON memory vs database

**Decision:** JSON for the assignment.

**Reason:** zero setup and easy reproducibility. The memory implementation is isolated so a production database can replace it later.

### Human approval

**Decision:** mandatory checkpoint for high-risk outcomes.

**Reason:** the assistant should support the advisor rather than autonomously execute consequential financial actions.

---

## 18. Assumptions

1. Client data is mock/synthetic data.
2. The CRM API is simulated.
3. Currency is assumed to be INR.
4. The system is advisory and does not execute trades or transfer money.
5. Anomaly thresholds are configurable and illustrative, not financial-regulatory thresholds.
6. The default implementation does not require an external LLM.
7. Long-term memory stores summaries rather than complete raw financial histories.
8. A real production deployment would require authentication, encryption, secrets management, audit controls, and compliance review.

---

## 19. Production extension

The current design can be extended without changing the agent contracts:

```text
MockCRMTool
     ↓
RealCRMTool

StatisticalAnomalyTool
     ↓
MLAnomalyDetectionTool

JSONMemory
     ↓
PostgreSQL / Redis / Vector DB

ConsoleHumanApproval
     ↓
Advisor UI / Workflow System

Deterministic Advisor
     ↓
LLM explanation layer
```

A possible production stack would be:

- FastAPI for service exposure
- PostgreSQL for durable state
- Redis for session state
- OpenTelemetry for tracing
- Vault/Secret Manager for credentials
- OAuth2/OIDC for authentication
- LLM only for explanation/reasoning where appropriate
- deterministic Python services for financial calculations and policy rules

---

## 20. Assignment requirement checklist

| Requirement | Implementation |
|---|---|
| Orchestrator Agent | `app/orchestrator/agent.py` |
| Minimum 2 specialized agents | Data Fetcher, Analyzer, Advisor |
| Client financial data ingestion | `DataFetcherAgent` |
| CRM/API context | `CRMTool` + mock implementation |
| Financial analysis | `AnalyzerAgent` |
| Anomaly detection | `AnomalyDetectionTool` |
| Tool abstraction | `app/tools/base.py` |
| Error handling | Agent/orchestrator boundary handling |
| Logging | `logging` + `logs/app.log` |
| Short-term memory | `SessionMemory` |
| Long-term memory | `JsonLongTermMemory` |
| Human-in-the-loop | `HumanApprovalTool` |
| Structured output | `AdvisoryResult` |
| Sample input/output | `data/` |
| Tests | `tests/` |
| Run instructions | This README |

---

## 21. Important note

This is a **technical assignment demonstration**, not a financial advisory product. The recommendations are generated from synthetic data and simplified rules and should not be used for real investment decisions.
