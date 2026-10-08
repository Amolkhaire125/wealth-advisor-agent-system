from typing import Any

from app.agents.base import Agent
from app.schemas import AdvisoryResult, AnalysisResult
from app.tools.base import HumanApprovalTool


class AdvisorAgent(Agent):
    name = "advisor"

    def __init__(self, approval_tool: HumanApprovalTool):
        self.approval_tool = approval_tool

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        data = context["financial_data"]
        analysis: AnalysisResult = context["analysis"]
        crm = context.get("crm_context")

        recommendations: list[str] = []

        if analysis.monthly_surplus < 0:
            recommendations.append(
                "Review monthly spending because expenses currently exceed income."
            )
        elif analysis.savings_rate < 0.20:
            recommendations.append(
                "Consider increasing the monthly savings buffer before increasing investment exposure."
            )

        if analysis.portfolio_concentration >= 0.60:
            recommendations.append(
                "Review portfolio diversification because the largest holding has high concentration."
            )

        for anomaly in analysis.anomalies:
            recommendations.append(
                f"Review transaction {anomaly.transaction_id}: {anomaly.reason}."
            )

        if not recommendations:
            recommendations.append(
                "No major risk signal was detected; continue periodic portfolio and cash-flow review."
            )

        if crm and crm.advisor_notes:
            recommendations.append(
                f"Consider the existing advisor note: {crm.advisor_notes[0]}"
            )

        approval_required = analysis.risk_level == "high"
        approved = True

        if approval_required:
            approved = self.approval_tool.request_approval(
                data.client_id,
                analysis.risk_level,
                recommendations,
            )

        if approval_required and not approved:
            status = "escalated"
            approval_status = "rejected"
        elif approval_required:
            status = "completed"
            approval_status = "approved"
        else:
            status = "completed"
            approval_status = "not_required"

        result = AdvisoryResult(
            client_id=data.client_id,
            status=status,
            risk_level=analysis.risk_level,
            summary={
                "monthly_surplus": analysis.monthly_surplus,
                "savings_rate": analysis.savings_rate,
                "portfolio_concentration": analysis.portfolio_concentration,
                "total_portfolio_value": analysis.total_portfolio_value,
                "risk_signals": analysis.risk_signals,
                "warnings": analysis.warnings,
            },
            anomalies=[
                {
                    "transaction_id": item.transaction_id,
                    "reason": item.reason,
                    "severity": item.severity,
                    "score": item.score,
                }
                for item in analysis.anomalies
            ],
            recommendations=recommendations,
            human_approval={
                "required": approval_required,
                "status": approval_status,
            },
            errors=[context["crm_error"]] if context.get("crm_error") else [],
        )

        return {"advisory": result}
