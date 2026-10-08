from app.tools.base import HumanApprovalTool


class ConsoleHumanApprovalTool(HumanApprovalTool):
    """Simple CLI approval mechanism for the assignment."""

    def __init__(self, auto_approve: bool = False):
        self.auto_approve = auto_approve

    def request_approval(self, client_id: str, risk_level: str, recommendations: list[str]) -> bool:
        if self.auto_approve:
            return True

        print("\n--- HUMAN APPROVAL REQUIRED ---")
        print(f"Client: {client_id}")
        print(f"Risk level: {risk_level}")
        print("Recommendations:")
        for item in recommendations:
            print(f"  - {item}")

        answer = input("Approve recommendation? [y/N]: ").strip().lower()
        return answer in {"y", "yes"}
