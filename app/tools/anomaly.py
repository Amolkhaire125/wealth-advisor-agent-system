import math
import statistics

from app.config import Settings
from app.schemas import Anomaly, Transaction
from app.tools.base import AnomalyDetectionTool


class StatisticalAnomalyTool(AnomalyDetectionTool):
    def __init__(self, settings: Settings):
        self.settings = settings

    def detect(
        self,
        transactions: list[Transaction],
        monthly_income: float,
    ) -> list[Anomaly]:
        if not transactions:
            return []

        amounts = [abs(t.amount) for t in transactions if t.amount is not None]
        if not amounts:
            return []

        mean = statistics.mean(amounts)
        std = statistics.stdev(amounts) if len(amounts) >= 2 else 0.0
        anomalies: list[Anomaly] = []

        for tx in transactions:
            amount = abs(tx.amount)

            if amount <= 0:
                anomalies.append(
                    Anomaly(
                        transaction_id=tx.transaction_id,
                        reason="Transaction amount is zero or negative",
                        severity="high",
                    )
                )
                continue

            z_score = (amount - mean) / std if std > 0 else 0.0
            large_vs_income = monthly_income > 0 and amount / monthly_income >= self.settings.large_transaction_income_ratio

            if z_score >= self.settings.anomaly_z_score:
                anomalies.append(
                    Anomaly(
                        transaction_id=tx.transaction_id,
                        reason="Transaction amount is statistically unusual",
                        severity="medium",
                        score=round(z_score, 2),
                    )
                )
            elif large_vs_income:
                anomalies.append(
                    Anomaly(
                        transaction_id=tx.transaction_id,
                        reason="Transaction is unusually large relative to monthly income",
                        severity="medium",
                        score=round(amount / monthly_income, 2),
                    )
                )

        return anomalies
