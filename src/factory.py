from applications import pwd, cd, ls, cat, echo, head
from applications import tail, grep, cut, find, uniq, sort
import sys
from helpers import glob_all
from exceptions.UnsupportedApplicationError import UnsupportedApplicationError
from extra_applications import mkdir, touch


class UnsafeDecorator:
    def __init__(self, app):
        self.app = app

    def exec(self, out):
        try:
            self.app.exec(out)
        except Exception:
            err = sys.exc_info()[1]
            out.append(str(err) + "\n")


class Singleton(type):
    instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance


class Factory(metaclass=Singleton):
    def __init__(self) -> None:
        pass

    def factory(self, app, args, out):
        if len(args) != 0 and all(isinstance(elem, list) for elem in args):
            # return the first inner list if arg is a list of list
            args = args[0]
        args = glob_all(args)
        applications = {
            "pwd": pwd(args),
            "cd": cd(args),
            "ls": ls(args),
            "cat": cat(args),
            "echo": echo(args),
            "head": head(args),
            "tail": tail(args),
            "grep": grep(args),
            "cut": cut(args),
            "find": find(args),
            "uniq": uniq(args),
            "sort": sort(args),
            "mkdir": mkdir(args),
            "touch": touch(args)
        }
        unsafe = False
        if app[0] == "_":
            unsafe = True
            app_exec = app[1:]
        else:
            app_exec = app
        if app_exec in applications:
            if unsafe:
                return UnsafeDecorator(applications[app_exec]).exec(out)
            else:
                return applications[app_exec].exec(out)
        else:
            raise UnsupportedApplicationError(app)
