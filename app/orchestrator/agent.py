import logging
from typing import Any

from app.agents.advisor import AdvisorAgent
from app.agents.analyzer import AnalyzerAgent
from app.agents.data_fetcher import DataFetcherAgent
from app.memory.store import JsonLongTermMemory, SessionMemory
from app.schemas import AdvisoryResult

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Coordinates the deterministic agent workflow."""

    def __init__(
        self,
        data_fetcher: DataFetcherAgent,
        analyzer: AnalyzerAgent,
        advisor: AdvisorAgent,
        long_term_memory: JsonLongTermMemory,
    ):
        self.data_fetcher = data_fetcher
        self.analyzer = analyzer
        self.advisor = advisor
        self.long_term_memory = long_term_memory

    def run(self, raw_client: dict[str, Any]) -> AdvisoryResult:
        client_id = str(raw_client.get("client_id", "unknown"))
        session = SessionMemory()
        session.set("client_id", client_id)
        logger.info("Workflow started for client %s", client_id)

        try:
            logger.info("Running DataFetcherAgent")
            fetched = self.data_fetcher.run({"raw_client": raw_client})
            session.set("data_fetcher", fetched)
            logger.info("DataFetcherAgent completed")

            logger.info("Running AnalyzerAgent")
            analyzed = self.analyzer.run({**session.snapshot(), **fetched})
            session.set("analysis", analyzed["analysis"])
            logger.info(
                "AnalyzerAgent completed: risk=%s anomalies=%d",
                analyzed["analysis"].risk_level,
                len(analyzed["analysis"].anomalies),
            )

            logger.info("Running AdvisorAgent")
            advised = self.advisor.run({**session.snapshot(), **fetched, **analyzed})
            result: AdvisoryResult = advised["advisory"]

            self.long_term_memory.save_insight(
                client_id=result.client_id,
                risk_level=result.risk_level,
                summary=result.summary,
            )

            logger.info(
                "Workflow completed for client %s with status=%s",
                client_id,
                result.status,
            )
            return result

        except Exception as exc:
            logger.exception("Workflow failed for client %s", client_id)
            return AdvisoryResult(
                client_id=client_id,
                status="failed",
                risk_level="unknown",
                summary={},
                anomalies=[],
                recommendations=[],
                human_approval={"required": False, "status": "not_applicable"},
                errors=[str(exc)],
            )
