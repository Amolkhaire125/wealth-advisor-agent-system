from app.schemas import CRMContext
from app.tools.base import CRMTool


class MockCRMTool(CRMTool):
    """Simulates a CRM API. Replace this class with an HTTP client in production."""

    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    def get_client_context(self, client_id: str) -> CRMContext:
        if self.should_fail:
            raise ConnectionError("Mock CRM API is unavailable")

        records = {
            "C001": CRMContext(
                client_id="C001",
                relationship_tier="premium",
                advisor_notes=["Client prefers diversified long-term investments."],
                last_review_date="2026-09-15",
            ),
            "C002": CRMContext(
                client_id="C002",
                relationship_tier="standard",
                advisor_notes=["Client requested conservative allocation."],
                last_review_date="2026-08-20",
            ),
        }
        return records.get(client_id, CRMContext(client_id=client_id))
