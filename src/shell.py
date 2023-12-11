import sys
import os
import readline
from grammar.ShellGrammarLexer import ShellGrammarLexer
from grammar.ShellGrammarParser import ShellGrammarParser
from converter import Converter
from antlr4 import InputStream, CommonTokenStream


class History():

    def __init__(self, command_history=[], history_index=0):
        self.command_history = command_history
        self.history_index = history_index

    def browse_command_history(self, direction):
        _ = readline.get_line_buffer()
        if direction == "up":
            if self.history_index > 0:
                self.history_index -= 1
        elif direction == "down":
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
        if self.command_history:
            return self.command_history[history_index]
        else:
            return ""


def eval(s):
    input_stream = InputStream(s)
    lexer = ShellGrammarLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ShellGrammarParser(stream)
    tree = parser.command()
    visitor = Converter()
    cmd = tree.accept(visitor)
    return cmd


if __name__ == "__main__":
    args_num = len(sys.argv) - 1
    if args_num > 0:
        if args_num != 2:
            raise ValueError("wrong number of command line arguments")
        if sys.argv[1] != "-c":
            raise ValueError(f"unexpected command line argument {sys.argv[1]}")

        out = eval(sys.argv[2])
        if out:
            for line in out:
                print(line, end="\n")
    else:
        while True:
            cmdline = input(os.getcwd() + "> ")

            # Handle command history navigation
            history = History()

            if cmdline == "\x1b[A":  # Up arrow key
                cmdline = history.browse_command_history("up")
            elif cmdline == "\x1b[B":  # Down arrow key
                cmdline = history.browse_command_history("down")

            history.command_history.append(cmdline)
            history_index = len(history.command_history)

            out = eval(cmdline)
            if out:
                for line in out:
                    print(line)
