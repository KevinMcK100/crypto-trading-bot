class PositionOfSameSideAlreadyExists(Exception):
    """
    Raised when attempt to place order when an existing position of same side is already in place.
    """

    def __init__(self, position_side, message="Position of same side already exists."):
        self.position_side = position_side
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} Existing position side: {self.position_side}"
