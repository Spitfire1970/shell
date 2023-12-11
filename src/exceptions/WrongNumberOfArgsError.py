class WrongNumberOfArgsError(Exception):
    def __init__(
        self, application: str, correct_min: str,
        correct_max: str, entered: str
    ):
        self.application = application
        self.correct_min = correct_min
        self.correct_max = correct_max
        self.entered = entered

    def __str__(self) -> str:
        if self.correct_max == self.correct_min:
            return (
                f"Wrong number of arguments given, "
                f"{self.application} requires "
                f"{self.correct_min} argument(s)"
                f", but {self.entered} argument(s) was entered"
            )
        return (
            f"Wrong number of arguments given, "
            f"{self.application} requires {self.correct_min}"
            f" to {self.correct_max} arguments"
            f", but {self.entered} argument(s) was entered"
        )
