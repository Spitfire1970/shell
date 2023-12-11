class NoFileFoundError(Exception):
    def __init__(self, app, filename) -> None:
        self._app = app
        self._filename = filename

    def __str__(self) -> str:
        return (
            f"File cannot be found, {self._app} "
            f'cannot locate "{self._filename}"'
            )
