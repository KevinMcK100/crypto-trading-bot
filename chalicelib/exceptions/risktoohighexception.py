class RiskTooHighException(Exception):
    """Raised when the maximum calculated risk for a position is exceeded"""

    def __init__(self, risk, max_risk, message="Maximum risk exceeded for position."):
        self.risk = risk
        self.max_risk = max_risk
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} Risk: {self.risk} Max Risk: {self.max_risk}"
