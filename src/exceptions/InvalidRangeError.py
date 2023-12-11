class InvalidRangeError(Exception):
    def __init__(self, message="Invalid Range Given"):
        self.message = message
        super().__init__(self.message)
