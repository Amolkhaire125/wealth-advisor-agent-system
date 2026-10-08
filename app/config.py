from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    anomaly_z_score: float = 2.0
    large_transaction_income_ratio: float = 0.50
    concentration_threshold: float = 0.60
    high_risk_anomaly_count: int = 3
    memory_path: str = "data/memory.json"
