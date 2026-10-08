from dataclasses import dataclass, field
from typing import Any


@dataclass
class Transaction:
    transaction_id: str
    category: str
    amount: float
    transaction_type: str = "expense"
    description: str = ""


@dataclass
class Holding:
    asset: str
    value: float


@dataclass
class ClientFinancialData:
    client_id: str
    monthly_income: float
    monthly_expenses: float
    risk_profile: str
    holdings: list[Holding]
    transactions: list[Transaction]
    goals: list[str] = field(default_factory=list)


@dataclass
class CRMContext:
    client_id: str
    relationship_tier: str = "standard"
    advisor_notes: list[str] = field(default_factory=list)
    last_review_date: str | None = None
    source: str = "crm"


@dataclass
class Anomaly:
    transaction_id: str
    reason: str
    severity: str
    score: float | None = None


@dataclass
class AnalysisResult:
    monthly_surplus: float
    savings_rate: float
    portfolio_concentration: float
    total_portfolio_value: float
    anomalies: list[Anomaly]
    risk_level: str
    risk_signals: list[str]
    warnings: list[str] = field(default_factory=list)


@dataclass
class AdvisoryResult:
    client_id: str
    status: str
    risk_level: str
    summary: dict[str, Any]
    anomalies: list[dict[str, Any]]
    recommendations: list[str]
    human_approval: dict[str, Any]
    errors: list[str] = field(default_factory=list)
