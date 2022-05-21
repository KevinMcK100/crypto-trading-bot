from dataclasses import dataclass


@dataclass
class OpenOrder:
    orderId: int
    clientOrderId: str
    type: str = None
