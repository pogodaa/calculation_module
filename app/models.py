from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Indicator:
    """Единичный показатель для анализа"""
    id: str
    value: float
    weight: Optional[float] = 1.0
    unit: Optional[str] = ""

    def __post_init__(self):
        if self.weight is None:
            self.weight = 1.0


@dataclass
class CalculationInput:
    """Входные данные для расчёта"""
    indicators: List[Indicator]
    coefficients: Dict[str, float] = field(default_factory=dict)


@dataclass
class CalculationResult:
    """Результаты расчёта"""
    success: bool
    data: Dict[str, float]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())