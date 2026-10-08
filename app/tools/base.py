from abc import ABC, abstractmethod
from app.schemas import Anomaly, CRMContext, Transaction


class CRMTool(ABC):
    @abstractmethod
    def get_client_context(self, client_id: str) -> CRMContext:
        raise NotImplementedError


class AnomalyDetectionTool(ABC):
    @abstractmethod
    def detect(
        self,
        transactions: list[Transaction],
        monthly_income: float,
    ) -> list[Anomaly]:
        raise NotImplementedError


class HumanApprovalTool(ABC):
    @abstractmethod
    def request_approval(self, client_id: str, risk_level: str, recommendations: list[str]) -> bool:
        raise NotImplementedError
