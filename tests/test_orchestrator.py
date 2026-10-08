from app.agents.advisor import AdvisorAgent
from app.agents.analyzer import AnalyzerAgent
from app.agents.data_fetcher import DataFetcherAgent
from app.config import Settings
from app.memory.store import JsonLongTermMemory
from app.orchestrator.agent import OrchestratorAgent
from app.tools.anomaly import StatisticalAnomalyTool
from app.tools.crm import MockCRMTool
from app.tools.human_approval import ConsoleHumanApprovalTool


def build_orchestrator(tmp_path, crm_failure=False):
    settings = Settings(memory_path=str(tmp_path / "memory.json"))
    return OrchestratorAgent(
        DataFetcherAgent(MockCRMTool(should_fail=crm_failure)),
        AnalyzerAgent(StatisticalAnomalyTool(settings), settings),
        AdvisorAgent(ConsoleHumanApprovalTool(auto_approve=True)),
        JsonLongTermMemory(settings.memory_path),
    )


def test_crm_failure_uses_fallback(tmp_path):
    client = {
        "client_id": "C001",
        "monthly_income": 100000,
        "monthly_expenses": 40000,
        "risk_profile": "moderate",
        "holdings": [{"asset": "A", "value": 100000}],
        "transactions": [{"transaction_id": "T1", "category": "food", "amount": 5000}],
    }

    result = build_orchestrator(tmp_path, crm_failure=True).run(client)

    assert result.status == "completed"
    assert any("CRM context was unavailable" in warning for warning in result.summary["warnings"])


def test_workflow_persists_memory(tmp_path):
    client = {
        "client_id": "C001",
        "monthly_income": 100000,
        "monthly_expenses": 40000,
        "risk_profile": "moderate",
        "holdings": [{"asset": "A", "value": 50000}, {"asset": "B", "value": 50000}],
        "transactions": [{"transaction_id": "T1", "category": "food", "amount": 5000}],
    }

    orchestrator = build_orchestrator(tmp_path)
    result = orchestrator.run(client)

    assert result.status == "completed"
    assert len(orchestrator.long_term_memory.get_client_history("C001")) == 1
