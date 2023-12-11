class UnsupportedApplicationError(Exception):
    def __init__(self, application_name: str) -> None:
        self.application_name = application_name

    def __str__(self) -> str:
        return (
            f"Unsupported application given, "
            f'"{self.application_name}" is not supported'
        )
