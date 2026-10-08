from typing import Any

from app.agents.base import Agent
from app.schemas import ClientFinancialData, Holding, Transaction
from app.tools.base import CRMTool


class DataFetcherAgent(Agent):
    name = "data_fetcher"

    def __init__(self, crm_tool: CRMTool):
        self.crm_tool = crm_tool

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        raw = context["raw_client"]

        required = ["client_id", "monthly_income", "monthly_expenses", "risk_profile", "holdings", "transactions"]
        missing = [field for field in required if field not in raw]
        if missing:
            raise ValueError(f"Missing required client fields: {', '.join(missing)}")

        financial_data = ClientFinancialData(
            client_id=str(raw["client_id"]),
            monthly_income=float(raw["monthly_income"]),
            monthly_expenses=float(raw["monthly_expenses"]),
            risk_profile=str(raw["risk_profile"]).lower(),
            holdings=[
                Holding(asset=str(h["asset"]), value=float(h["value"]))
                for h in raw["holdings"]
            ],
            transactions=[
                Transaction(
                    transaction_id=str(t["transaction_id"]),
                    category=str(t.get("category", "unknown")),
                    amount=float(t["amount"]),
                    transaction_type=str(t.get("transaction_type", "expense")),
                    description=str(t.get("description", "")),
                )
                for t in raw["transactions"]
            ],
            goals=[str(goal) for goal in raw.get("goals", [])],
        )

        crm_error = None
        try:
            crm_context = self.crm_tool.get_client_context(financial_data.client_id)
        except Exception as exc:
            crm_context = None
            crm_error = str(exc)

        return {
            "financial_data": financial_data,
            "crm_context": crm_context,
            "crm_error": crm_error,
        }
