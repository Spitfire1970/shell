class WrongFlagsError(Exception):
    def __init__(self, message="Wrong Flags Given"):
        self.message = message
        super().__init__(self.message)
