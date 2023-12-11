from abc import ABC, abstractmethod
import os
from exceptions.WrongNumberOfArgsError import WrongNumberOfArgsError
from exceptions.NoDirectoryFoundError import NoDirectoryFoundError
from exceptions.NoFileFoundError import NoFileFoundError
from exceptions.InvalidRangeError import InvalidRangeError
from exceptions.WrongFlagsError import WrongFlagsError
from helpers import head_tail_check, pipe_check
import re
from pathlib import Path


class Application(ABC):
    '''
    Functionality
    -------------
    Generic applciation class for applciations to inherit from

    Constructor
    -----
    List: Initializes subclasses with arguments

    Methods
    ------
    Empty exec method to be overriden by subclasses
    '''
    @abstractmethod
    def __init__(self, args):
        self.args = args

    @abstractmethod
    def exec(self, out):
        pass


class pwd(Application):
    '''
    Functionality
    -------------
    Appends the current working directory (cwd) to the output list

    Input
    -----
    List: Empty args list

    Output
    ------
    List with cwd appended to its end as a string
    '''
    def __init__(self, args):
        self.app = "pwd"
        super().__init__(args)

    def exec(self, out):
        len_args = len(self.args)
        if len_args != 0:
            raise WrongNumberOfArgsError(self.app, "0", "0", str(len_args))
        out.append(os.getcwd())


class cd(Application):
    '''
    Functionality
    -------------
    Changes the current working directory to the given child directory

    Input
    -----
    List with one string: Directory to change to

    Output
    ------
    Enters into given directory
    '''
    def __init__(self, args):
        self.app = "cd"
        super().__init__(args)

    def exec(self, out):
        len_args = len(self.args)
        if len_args != 1:
            raise WrongNumberOfArgsError(self.app, "1", "1", str(len_args))
        try:
            os.chdir(self.args[0])
        except FileNotFoundError:
            raise NoDirectoryFoundError(self.app, self.args[0])


class ls(Application):
    '''
    Functionality
    -------------
    Appends each directory or file in given directory to the output list

    Input
    -----
    List with one or zero string: Directory of which elements are to be listed.
    Pwd if empty list given.

    Output
    ------
    List with each directory/file in given directory appended as strings
    '''
    def __init__(self, args):
        self.app = "ls"
        super().__init__(args)

    def exec(self, out):
        len_args = len(self.args)
        if len_args == 0:
            ls_dir = os.getcwd()
        elif len_args > 1:
            len_args = str(len_args)
            raise WrongNumberOfArgsError(self.app, "0", "1", len_args)
        else:
            ls_dir = self.args[0]
            if not os.path.exists(ls_dir):
                raise NoDirectoryFoundError(self.app, ls_dir)
        for f in os.listdir(ls_dir):
            if not f.startswith("."):
                out.append(f)


class cat(Application):
    '''
    Functionality
    -------------
    Appends all lines in files given (contents of file)
    to output list as one string

    Input
    -----
    List with strings of file names

    Output
    ------
    List with one string (contents of all files) appended at its end
    '''
    def __init__(self, args):
        self.app = "cat"
        super().__init__(args)

    def printFile(self, file):
        with open(file, "r") as f:
            x = f.read()
            y = x.strip()
            final = y + "\n"
            return final

    def exec(self, out):
        len_args = len(self.args)
        if len_args == 0:
            len_args = str(len_args)
            raise WrongNumberOfArgsError(self.app, "1", "inf", len_args)
        s = ""
        for i in self.args:
            if os.path.exists(i):
                s += self.printFile(i)
            else:
                raise NoFileFoundError(self.app, i)
        s = s[:-1] if s[-1] == "\n" else s
        out.append(s)


class echo(Application):
    '''
    Functionality
    -------------
    Appends to output list each argument given to it separated by spaces

    Input
    -----
    List with any number of strings

    Output
    ------
    List with one string (args joined by space) appended at its end
    '''
    def __init__(self, args):
        self.app = "echo"
        super().__init__(args)

    def exec(self, out):
        if not self.args:
            out.append("")
        else:
            out.append(" ".join(self.args))


class head(Application):
    '''
    Functionality
    -------------
    Appends first n (first 10 if n not given) lines in given file
    to output list

    Input
    -----
    List of strings: "-n" flag followed by number of lines
    followed by file name or just file name

    Output
    ------
    List appended with n strings
    (file lines without the newline character at end)
    '''
    def __init__(self, args):
        self.app = "head"
        super().__init__(args)

    def exec(self, out):
        num_lines, file = head_tail_check(self.app, self.args)
        with open(file, "r") as f:
            lines = f.readlines()
            i = 0
            for val in lines:
                if i == num_lines:
                    break
                val = val[:-1] if val[-1] == "\n" else val
                out.append(val)
                i += 1


class tail(Application):
    '''
    Functionality
    -------------
    Appends last n (last 10 if n not given) lines in given file
    to output list

    Input
    -----
    List of strings: "-n" flag followed by number of lines
    followed by file name or just file name

    Output
    ------
    List appended with n strings
    (file lines without the newline character at end)
    '''
    def __init__(self, args):
        self.app = "tail"
        super().__init__(args)

    def exec(self, out):
        num_lines, file = head_tail_check(self.app, self.args)

        with open(file, "r") as f:
            lines = f.readlines()
            display_length = min(len(lines), num_lines)
            j = 0
            for i in range(display_length):
                if j == num_lines:
                    break
                val = lines[len(lines) - display_length + i]
                val = val[:-1] if val[-1] == "\n" else val
                out.append(val)
                j += 1


class grep(Application):
    '''
    Functionality
    -------------
    Appends all lines in given files matching a given pattern
    to output list prefixed with filepath and colon if multiple files

    Input
    -----
    List of strings: pattern string followed by any number of file names

    Output
    ------
    List appended with some number of strings
    (file lines without the newline characters at end)
    '''
    def __init__(self, args):
        self.app = "grep"
        super().__init__(args)

    def checkFile(self, num_files, f, pattern, out, bool, fileName=False):
        currentFile = f
        for ln in currentFile:
            if re.match(pattern, ln):
                ln = ln[:-1] if ln[-1] == "\n" else ln
                if num_files > 1 and fileName:
                    out.append(f"{fileName}:{ln}")
                else:
                    out.append(ln)
        if not bool:
            currentFile.close()

    def checkFiles(self, files, pattern, out):
        for f in files:
            try:
                currentFile = open(f, "r")
                self.checkFile(len(files), currentFile, pattern, out, False, f)
            except FileNotFoundError:
                raise NoFileFoundError(self.app, f)

    def fromPipe(self, file, pattern, out):
        file = file.split("\n")
        self.checkFile(1, file, pattern, out, True)

    def exec(self, out):
        self.args, pipe = pipe_check(self.args)
        len_args = len(self.args)
        if not pipe and len_args < 2:
            raise WrongNumberOfArgsError(self.app, "2", "inf", str(len_args))
        pattern = self.args[0]
        files = self.args[1:]
        if pipe:
            self.fromPipe(files[0], pattern, out)
        else:
            self.checkFiles(files, pattern, out)


class cut(Application):
    '''
    Functionality
    -------------
    Appends all lines in the given file but only those bytes
    of each line that match the bytes given in flag

    Input
    -----
    List of strings: "-b" flag followed by comma separated values
    of bytes to be cut (or range of bytes) followed by a file name

    Output
    ------
    List appended with one string that consists of all cut file lines
    separated by newlines (newline character removed at end of this string)
    '''
    def __init__(self, args):
        self.app = "cut"
        super().__init__(args)

    def cut_operation(self, delim, out, line):
        string = ""
        for d in delim:
            if "-" in d:
                interval = d.split("-")
                if interval[1] == "":
                    string += line[int(interval[0]) - 1:]
            else:
                try:
                    string += line[int(d) - 1]
                except IndexError:
                    string += ""
        if string:
            string = string[:-1] if string[-1] == "\n" else string
        out.append(string)

    def clean_delim(self, delim):
        # remove any duplicate single bytes and partial sort
        delim = sorted(list(set(delim)), key=lambda x: int(x.replace("-", "")))
        temp_list = []
        delim2 = delim.copy()
        for de in delim:
            if "-" not in de:
                continue
            if len(de) == 3:
                if int(de[0]) > int(de[2]):
                    raise InvalidRangeError
                else:
                    for i in range(int(de[0]), int(de[2]) + 1):
                        delim2.append(str(i))
            if de[0] == "-":
                for i in range(1, int(de[1:]) + 1):
                    delim2.append(str(i))
                delim2.remove(de)
            if de[-1] == "-":
                temp_list.append(int(de[:-1]))
                delim2.remove(de)
        delim = delim2
        temp_list = sorted(temp_list)
        if temp_list:
            min = temp_list[0]
            for j in delim:
                if int(j) > min:
                    delim.remove(j)
            delim.append(str(min) + "-")
        delim = list(set(sorted(delim, key=lambda x: int(x.replace("-", "")))))
        return sorted(delim)

    def exec(self, out):
        self.args, pipe = pipe_check(self.args)
        len_args = len(self.args)
        if len_args != 3:
            raise WrongNumberOfArgsError(self.app, "3", "3", str(len_args))
        if self.args[0] != "-b":
            raise WrongFlagsError

        delim = self.args[1].split(",")
        regexD = re.compile(r"^[0-9]*-*[0-9]*$")
        for d in delim:
            if not bool(re.match(regexD, d)):
                raise InvalidRangeError("Invalid Bytes/Range Given")
        delim = self.clean_delim(delim)
        file = self.args[-1]
        if pipe:
            if "\n" in file:
                file = file.split("\n")
                new_file = []
                for line in file:
                    new_file.append(line + "\n")
                lines = new_file
            else:
                lines = [file]
            for line in lines:
                self.cut_operation(delim, out, line)
        else:
            try:
                with open(file, encoding="UTF-8") as f:
                    lines = f.readlines()
                    for line in lines:
                        self.cut_operation(delim, out, line)
            except FileNotFoundError:
                raise NoFileFoundError(self.app, file)


class find(Application):
    '''
    Functionality
    -------------
    Appends all file names found in given root directory
    (or current working directory) that match the given pattern

    Input
    -----
    List of strings: Compulsory "-name" flag followed by a pattern
    (with zero or more *).
    Optionally can take a string of root directory name at the start of list

    Output
    ------
    List appended with some number of strings (file paths that match pattern)
    '''
    def __init__(self, args):
        self.app = "find"
        super().__init__(args)

    def exec(self, out):
        len_args = len(self.args)
        if len_args == 3:
            if self.args[1] != "-name":
                raise WrongFlagsError
            root = self.args[0]
            if not root[-1] == os.sep:
                root += os.sep
            pattern = self.args[2]
            add_parent = False
        elif len_args == 2:
            if self.args[0] != "-name":
                raise WrongFlagsError
            root = "."
            pattern = self.args[1]
            add_parent = True
        else:
            raise WrongNumberOfArgsError(self.app, "2", "3", str(len_args))
        root_path = Path(root)
        matches = root_path.rglob(pattern)
        file_paths = [
            str(file) for file in matches if not str(file.name).startswith(".")
        ]
        for file in file_paths:
            if add_parent:
                out.append("." + os.sep + file)
            else:
                out.append(file)


class uniq(Application):
    '''
    Functionality
    -------------
    Appends unique file lines in given file (a line that is not the same
    as any of its adjacent lines) to output list. Case insensitive if
    flag given.

    Input
    -----
    List of strings: Optional "-i" flag followed by a file name

    Output
    ------
    List appended with one string that consists of all unique file lines
    separated by newlines
    (newline character removed at end of this string)
    '''
    def __init__(self, args):
        self.app = "uniq"
        super().__init__(args)

    def match(self, line1, line2, case_sensitive):
        if line1 and line1[-1] == "\n":
            line1 = line1[:-1]
        if line2 and line2[-1] == "\n":
            line2 = line2[:-1]
        if len(line1) != len(line2):
            return False
        if case_sensitive:
            for i in range(len(line1)):
                if line1[i] != line2[i]:
                    return False
        if not case_sensitive:
            for i in range(len(line1)):
                if line1[i].lower() != line2[i].lower():
                    return False
        return True

    def exec(self, out):
        self.args, pipe = pipe_check(self.args)
        case_sensitive = True
        len_args = len(self.args)
        if len_args == 2:
            if self.args[0] != "-i":
                raise WrongFlagsError
            case_sensitive = False
            file = self.args[1]
        elif len_args == 1:
            file = self.args[0]
        else:
            raise WrongNumberOfArgsError(self.app, "1", "2", str(len_args))
        if pipe:
            lines = file.split("\n")
            prevline = ""
            s = ""
            for line in lines:
                if not self.match(prevline, line, case_sensitive):
                    s += line + "\n"
                prevline = line
            s = s[:-1] if s[-1] == "\n" else s
            out.append(s)
        else:
            try:
                with open(file, "r") as file:
                    lines = file.readlines()
                    prevline = ""
                    s = ""
                    for line in lines:
                        if not self.match(prevline, line, case_sensitive):
                            s += line
                        prevline = line
                    s = s[:-1] if s[-1] == "\n" else s
                    out.append(s)
            except FileNotFoundError:
                raise NoFileFoundError(self.app, file)


class sort(Application):
    '''
    Functionality
    -------------
    Appends all lines in given file in sorted order to output list.
    Sorted in reverse order if flag given.

    Input
    -----
    List of strings: Optional "-r" flag followed by a file name

    Output
    ------
    List appended with one string that consists of sorted file lines
    separated by newlines (newline character removed at end of this string)
    '''
    def __init__(self, args):
        self.app = "sort"
        super().__init__(args)

    def sortt(self, contents, reverse):
        if reverse:
            contents = sorted(contents, reverse=True)
        else:
            contents = sorted(contents)
        return contents

    def exec(self, out):
        self.args, pipe = pipe_check(self.args)
        reverse = False
        len_args = len(self.args)
        if len_args == 2:
            if self.args[0] != "-r":
                raise WrongFlagsError
            reverse = True
            file = self.args[1]
        elif len_args == 1:
            file = self.args[0]
        else:
            raise WrongNumberOfArgsError(self.app, "1", "2", str(len_args))
        if pipe:
            lines = file.split("\n")
            new_content = self.sortt(lines, reverse)
            val = ""
            for s in new_content:
                val += s + "\n"
            val = val[:-1] if val[-1] == "\n" else val
            out.append(val)
        else:
            try:
                with open(file, "r") as file:
                    lines = file.readlines()
                    new_content = self.sortt(lines, reverse)
                    val = ""
                    for s in new_content:
                        val += s
                    val = val[:-1] if val[-1] == "\n" else val
                    out.append(val)
            except FileNotFoundError:
                raise NoFileFoundError(self.app, file)
