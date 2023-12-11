from exceptions.WrongNumberOfArgsError import WrongNumberOfArgsError
from exceptions.WrongFlagsError import WrongFlagsError
from exceptions.NoFileFoundError import NoFileFoundError
import os
import glob


def globber_with_dot(arg: str) -> list:
    if isinstance(arg, dict):
        return [arg]
    starts_with_sq = arg[0] == "'" and arg[-1] == "'"
    starts_with_dq = arg[0] == '"' and arg[-1] == '"'
    if starts_with_sq or starts_with_dq:
        if arg == "''":
            return [arg]
        else:
            return [arg[1:-1]]
    if "*" not in arg:
        return [arg]
    paths = glob.glob(arg)
    return paths


def glob_all(args: list) -> list:
    new_args = []
    for arg in args:
        arg = globber_with_dot(arg)
        new_args += arg
    return new_args


def head_tail_check(app, args):
    if len(args) not in [1, 3]:
        raise WrongNumberOfArgsError(app, 1, 3, len(args))

    if len(args) == 1:
        num_lines = 10
        file = args[0]

    if len(args) == 3:
        if args[0] != "-n":
            raise WrongFlagsError
        else:
            try:
                num_lines = int(args[1])
            except ValueError:
                raise WrongFlagsError
            file = args[2]
    if not os.path.isfile(file):
        raise NoFileFoundError(app, file)
    return num_lines, file


def pipe_check(args: list):
    pipe = False
    key = {"passed_code": 100200100}
    if args:
        if args[-1] == key:
            pipe = True
            del args[-1]
    return args, pipe
