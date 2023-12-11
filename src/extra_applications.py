from abc import ABC, abstractmethod
import os
from exceptions.WrongNumberOfArgsError import WrongNumberOfArgsError
import pathlib


class ExtraApplication(ABC):
    @abstractmethod
    def __init__(self, args):
        self.args = args

    @abstractmethod
    def exec(self, out):
        pass


class touch(ExtraApplication):
    def __init__(self, args):
        self.app = "touch"
        super().__init__(args)

    def exec(self, out):
        len_args = len(self.args)
        if len_args == 0:
            raise WrongNumberOfArgsError(self.app, "1", "inf", str(len_args))
        for file_name in self.args:
            pathlib.Path(file_name).touch()


class mkdir(ExtraApplication):
    def __init__(self, args):
        self.app = "mkdir"
        super().__init__(args)

    def exec(self, out):
        len_args = len(self.args)
        if len_args == 0:
            raise WrongNumberOfArgsError(self.app, "1", "inf", str(len_args))
        for dir_name in self.args:
            try:
                os.makedirs(dir_name)
            except FileExistsError:
                pass
