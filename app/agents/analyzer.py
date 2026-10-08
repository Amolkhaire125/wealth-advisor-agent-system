from typing import Any

from app.agents.base import Agent
from app.config import Settings
from app.schemas import AnalysisResult
from app.tools.base import AnomalyDetectionTool


class AnalyzerAgent(Agent):
    name = "analyzer"

    def __init__(self, anomaly_tool: AnomalyDetectionTool, settings: Settings):
        self.anomaly_tool = anomaly_tool
        self.settings = settings

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        data = context["financial_data"]

        if data.monthly_income <= 0:
            raise ValueError("Monthly income must be greater than zero")

        surplus = data.monthly_income - data.monthly_expenses
        savings_rate = surplus / data.monthly_income

        total_value = sum(max(0.0, holding.value) for holding in data.holdings)
        largest_holding = max((max(0.0, h.value) for h in data.holdings), default=0.0)
        concentration = largest_holding / total_value if total_value else 0.0

        anomalies = self.anomaly_tool.detect(data.transactions, data.monthly_income)

        signals: list[str] = []
        warnings: list[str] = []

        if savings_rate < 0:
            signals.append("Monthly expenses exceed income.")
        elif savings_rate < 0.20:
            signals.append("Savings rate is below 20%.")

        if concentration >= self.settings.concentration_threshold:
            signals.append(
                f"Largest holding represents {concentration:.0%} of the portfolio."
            )

        if anomalies:
            signals.append(f"{len(anomalies)} unusual transaction(s) detected.")

        if context.get("crm_error"):
            warnings.append("CRM context was unavailable; analysis used financial input only.")

        if data.risk_profile not in {"low", "moderate", "medium", "high", "conservative", "aggressive"}:
            warnings.append("Risk profile is not one of the recognized profiles.")

        if len(anomalies) >= self.settings.high_risk_anomaly_count or savings_rate < 0:
            risk_level = "high"
        elif concentration >= self.settings.concentration_threshold or anomalies:
            risk_level = "medium"
        else:
            risk_level = "low"

        result = AnalysisResult(
            monthly_surplus=round(surplus, 2),
            savings_rate=round(savings_rate, 4),
            portfolio_concentration=round(concentration, 4),
            total_portfolio_value=round(total_value, 2),
            anomalies=anomalies,
            risk_level=risk_level,
            risk_signals=signals,
            warnings=warnings,
        )

        return {"analysis": result}
