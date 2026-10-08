from app.agents.analyzer import AnalyzerAgent
from app.agents.data_fetcher import DataFetcherAgent
from app.config import Settings
from app.tools.anomaly import StatisticalAnomalyTool
from app.tools.crm import MockCRMTool


def sample_client():
    return {
        "client_id": "C001",
        "monthly_income": 100000,
        "monthly_expenses": 50000,
        "risk_profile": "moderate",
        "holdings": [
            {"asset": "A", "value": 70000},
            {"asset": "B", "value": 30000},
        ],
        "transactions": [
            {"transaction_id": "T1", "category": "food", "amount": 5000}
        ],
    }


def test_data_fetcher_returns_context():
    agent = DataFetcherAgent(MockCRMTool())
    result = agent.run({"raw_client": sample_client()})

    assert result["financial_data"].client_id == "C001"
    assert result["crm_context"].relationship_tier == "premium"


def test_analyzer_calculates_surplus():
    fetcher = DataFetcherAgent(MockCRMTool())
    fetched = fetcher.run({"raw_client": sample_client()})

    analyzer = AnalyzerAgent(StatisticalAnomalyTool(Settings()), Settings())
    result = analyzer.run(fetched)

    assert result["analysis"].monthly_surplus == 50000
    assert result["analysis"].savings_rate == 0.5
