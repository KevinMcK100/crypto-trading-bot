from dataclasses import dataclass


@dataclass
class Position:
    positionAmt: float
    entryPrice: float
    side: str = None
