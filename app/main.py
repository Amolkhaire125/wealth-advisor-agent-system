import argparse
import json
import logging
from pathlib import Path

from app.agents.advisor import AdvisorAgent
from app.agents.analyzer import AnalyzerAgent
from app.agents.data_fetcher import DataFetcherAgent
from app.config import Settings
from app.memory.store import JsonLongTermMemory
from app.orchestrator.agent import OrchestratorAgent
from app.tools.anomaly import StatisticalAnomalyTool
from app.tools.crm import MockCRMTool
from app.tools.human_approval import ConsoleHumanApprovalTool


def configure_logging() -> None:
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def load_clients(path: str) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_orchestrator(crm_failure: bool = False, auto_approve: bool = False) -> OrchestratorAgent:
    settings = Settings()
    crm_tool = MockCRMTool(should_fail=crm_failure)
    anomaly_tool = StatisticalAnomalyTool(settings)
    approval_tool = ConsoleHumanApprovalTool(auto_approve=auto_approve)

    return OrchestratorAgent(
        data_fetcher=DataFetcherAgent(crm_tool),
        analyzer=AnalyzerAgent(anomaly_tool, settings),
        advisor=AdvisorAgent(approval_tool),
        long_term_memory=JsonLongTermMemory(settings.memory_path),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Wealth Advisor Assistant")
    parser.add_argument("--client-id", default=None)
    parser.add_argument("--data", default="data/clients.json")
    parser.add_argument("--crm-failure", action="store_true")
    parser.add_argument("--auto-approve", action="store_true")
    args = parser.parse_args()

    configure_logging()

    clients = load_clients(args.data)
    if args.client_id:
        clients = [c for c in clients if c.get("client_id") == args.client_id]

    if not clients:
        raise SystemExit("No matching client found.")

    orchestrator = build_orchestrator(
        crm_failure=args.crm_failure,
        auto_approve=args.auto_approve,
    )

    for client in clients:
        result = orchestrator.run(client)
        print(json.dumps(result, default=lambda obj: obj.__dict__, indent=2))


if __name__ == "__main__":
    main()
