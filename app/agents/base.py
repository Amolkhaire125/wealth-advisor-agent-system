from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    name: str = "agent"

    @abstractmethod
    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
