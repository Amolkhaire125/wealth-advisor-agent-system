import json
from pathlib import Path
from typing import Any


class SessionMemory:
    """In-memory context for one workflow execution."""

    def __init__(self):
        self._data: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def snapshot(self) -> dict[str, Any]:
        return dict(self._data)


class JsonLongTermMemory:
    """Small persistent summary store used for the assignment."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, list[dict[str, Any]]]:
        if not self.path.exists():
            return {"insights": []}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"insights": []}

    def save_insight(self, client_id: str, risk_level: str, summary: dict[str, Any]) -> None:
        data = self._load()
        data.setdefault("insights", []).append(
            {
                "client_id": client_id,
                "risk_level": risk_level,
                "summary": summary,
            }
        )
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_client_history(self, client_id: str) -> list[dict[str, Any]]:
        return [
            item for item in self._load().get("insights", [])
            if item.get("client_id") == client_id
        ]
