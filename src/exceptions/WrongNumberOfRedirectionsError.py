class WrongNumberOfRedirectionsError(Exception):
    def __init__(self, message="Wrong Number Of Redirections Given"):
        self.message = message
        super().__init__(self.message)
