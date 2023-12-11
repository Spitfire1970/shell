class NoDirectoryFoundError(Exception):
    def __init__(self, app, directory) -> None:
        self._app = app
        self._directory = directory

    def __str__(self) -> str:
        return (
            f"Directory cannot be found, {self._app} "
            f'cannot locate "{self._directory}"'
        )
