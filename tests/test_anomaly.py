from app.config import Settings
from app.schemas import Transaction
from app.tools.anomaly import StatisticalAnomalyTool


def test_large_transaction_is_detected():
    tool = StatisticalAnomalyTool(Settings())
    transactions = [
        Transaction("T1", "food", 1000),
        Transaction("T2", "food", 1200),
        Transaction("T3", "shopping", 50000),
    ]

    anomalies = tool.detect(transactions, monthly_income=100000)

    assert any(item.transaction_id == "T3" for item in anomalies)
