from grammar.ShellGrammarVisitor import ShellGrammarVisitor
from evaluator import Evaluation_Single_Call
from evaluator import Evaluation_Non_Single_Call
from antlr4 import InputStream, CommonTokenStream
from grammar.ShellGrammarLexer import ShellGrammarLexer
from grammar.ShellGrammarParser import ShellGrammarParser
import re

"""
- Overview:

* The Converter class in the ANTLR-based parsing system plays a crucial role
in interpreting and structuring shell commands into a format that can be
easily processed by the Evaluator class. This class does not fully separate
commands and arguments but breaks down the script into manageable chunks.

- Core Functionality:

* At its core, the Converter class generates a "list" that encapsulates
commands, arguments, redirections, and separators ("|" and ";").
This list is then utilized by the Evaluator class for further recognition and
execution of the commands.

- List Structure:

* The structure of the list created by the Converter class adheres to
specific nesting rules to represent different components of the shell command:

- Call Command Structure:

* The first element of the list represents the command itself.

* If the list contains another nested list, this nested list comprises the
arguments of the command.

* If the list contains a tuple, it indicates a redirection operation. The
tuple format is:
(redirection symbol, target), e.g., ('>', 'filename.txt').

* The command is stored directly in the list, while arguments are in a nested
list, and redirections are in nested tuples.

- Pipe (|) / Sequence (;) Command Structure:

* The list still starts with the actual command as the first element.

* Following the command, nested lists and tuples represent arguments and
redirections, respectively.

* Additionally, if the list contains a set, it signifies the presence of
a pipe (|) or sequence (;) operator, linking multiple commands.

* Each pipe or sequence command is essentially a collection of call
commands, each represented as a complete list within the main list.
This creates three levels of nesting:

1) The first level iterates over the all the commands.
2) The second level allows access to a specific command and its components
(arguments, redirections, separators).
3) The third level delves into the details of each component, such as
individual arguments, redirection details, or separator types.

main_list =
[
    ["command_1", ["arg1", "arg2"], (">", "output.txt"), ("|")],
    ["command_2", ["arg3"], ("<", "input.txt"), (";")]
    ["command_3", ["arg4"]]
]

"""


class Converter(ShellGrammarVisitor):
    def __init__(self):
        super().__init__()

    def visitCommand(self, ctx):
        """
        Visits and processes a 'command' node in the parse tree.

        Depending on the type of command (Pipe, Seq, or Call), the method
        delegates processing to specific visit methods and passes
        the processed data to the corresponding evaluation class for execution.

        Args:
            ctx (ParserRuleContext): The context of the command node in the
            parse tree.

        Returns:
            result (list): The processed command data passed from the
            evaluation class.
        """
        data = None
        result = None

        if ctx.call():
            data = self.visitCall(ctx.call())
            eval_instance = Evaluation_Single_Call()
            result = eval_instance.single_call(data)

        else:
            if ctx.pipe():
                data = self.visitPipe(ctx.pipe())

            if ctx.seq():
                data = self.visitSeq(ctx.seq())

            eval_instance = Evaluation_Non_Single_Call()
            result = eval_instance.call_seperate(
                data
            )

        return result

    def visitCall(self, ctx):
        """
        Visits and processes a 'call' node in the parse tree.

        This method interprets the command, its arguments, and any associated
        redirections, organizing them into the structured format as mentioned
        before.

        Args:
            ctx (ParserRuleContext): The context of the call node in the parse
            tree.

        Returns:
            main_list (list): A structured representation of the call
            command, including command, arguments, and redirections.
        """
        extracted_command = ""
        main_list = []
        arg_list = []
        redirections = []

        # Edge case when no command at the beginning [for example:
        # "< dir1/file2.txt cat"]
        if (ctx.argument()) and (ctx.redirection()) and (ctx.atom() == []):
            redir_result = self.visitRedirection(ctx.redirection())
            redirections.append(redir_result)
            arg_result = self.visitArgument(ctx.argument())
            main_list.append(arg_result)

        else:
            # Process the main command (call->argument then its a command)
            extracted_command = self.visitArgument(ctx.argument())
            main_list.append(extracted_command)

            # Process atoms (arguments and redirections)
            if ctx.atom():
                for atom in ctx.atom():
                    atom_result = self.visitAtom(atom)
                    if isinstance(atom_result, tuple):
                        # If it's a tuple, it's a redirection
                        redirections.append(atom_result)
                    else:
                        arg_list.append(atom_result)

        # Append arguments and redirections separately to the main list
        if arg_list:
            main_list.append(arg_list)
        else:
            main_list.append([])
        main_list.extend(redirections)

        return main_list

    def visitArgument(self, ctx):
        """
        Visits and processes an 'argument' node in the parse tree.

        This method appropriately processes different types of
        quotes (single, double, backquotes)

        Args:
            ctx (ParserRuleContext): The context of the argument node in the
            parse tree.

        Returns:
            result_string (str): The processed argument as a string,
            with quotes handled appropriately
        """
        quote_list = ["`", '"', "'"]
        get_text = ctx.getText()
        first_char = get_text[0]

        if (
            first_char not in quote_list and ctx.quoted() == []
        ):
            return get_text
        elif first_char[0] == "'":
            return self.visitSingle_quoted(get_text)
        elif first_char[0] == '"':
            return self.visitDouble_quoted(get_text)
        elif first_char[0] == "`":
            return self.visitBack_quoted(get_text)
        else:  # Quotations exist but not at the beginning
            list_str = self.split_string_with_quotes(ctx.getText())
            for i in range(len(list_str)):
                if list_str[i][0] == "'":
                    get_text = self.visitSingle_quoted(list_str[i])
                    list_str[i] = get_text
                elif list_str[i][0] == '"':
                    get_text = self.visitDouble_quoted(list_str[i])
                    list_str[i] = get_text[1:-1]
                elif list_str[i][0] == "`":
                    get_text = self.visitBack_quoted(list_str[i])
                    get_text = get_text[0]
                    list_str[i] = get_text

            result_string = "".join(list_str)
            return result_string

    def split_string_with_quotes(self, s):
        """
        Splits a string into segments based on the presence of quotes.

        Args:
            s (str): The string to be split.

        Returns:
            result (list): A list of string segments, each possibly
            including quotes.
        """
        result = []
        temp = ""
        quote_char = None

        for char in s:
            if char in ['"', "'", "`"]:
                if quote_char is None:
                    quote_char = char
                    result.append(temp)
                    temp = ""
                else:
                    temp += char
                    result.append(temp)
                    temp = ""
                    quote_char = None
                    continue
                temp += char
            else:
                temp += char

        if temp:
            result.append(temp)

        return result

    def visitAtom(self, ctx):
        """
        Visits and processes an 'atom' node in the parse tree.

        An atom can be an argument or a redirection. The method determines the
        type of atom and processes it accordingly. For an argument, it returns
        the processed argument. For a redirection, it delegates to the
        visitRedirection method.

        Args:
            ctx (ParserRuleContext): The context of the atom node in the parse
            tree.

        Returns:
            The processed atom, either as an argument string or a redirection
            tuple.
        """
        if ctx.argument():
            argument = ctx.argument()
            extracted_argument = self.visitArgument(argument)

            if isinstance(extracted_argument, list) \
                    and len(extracted_argument) == 1:
                return extracted_argument[0]

            return extracted_argument

        else:
            return self.visitRedirection(ctx.redirection())

    def visitSingle_quoted(self, ctx_str):
        """
        Processes a string representing a single-quoted segment.

        This method removes single quotes from the input string and handles
        any escaped characters within the quotes.

        Args:
            ctx (str): The string segment enclosed in single quotes.

        Returns:
            cleaned_data (str): The cleaned and processed string without
            its enclosing single quotes.
        """
        # Single quotes cannot have single quotes within
        string_returned = ctx_str.replace("'", "")
        string_returned = string_returned.replace('\\"', "")
        cleaned_data = "'" + string_returned + "'"

        return cleaned_data

    def visitBack_quoted(self, ctx_str):
        """
        Processes a string representing a backquoted segment.

        This method handles backquoted segments by parsing the content within
        the backquotes as a new command, using a fresh instance of the
        Converter. It strips the backquotes and parses the contained string
        because commands cannot begin with backquotes.

        Args:
            ctx (str): The string segment enclosed in backquotes.

        Returns:
            result (list): The list containing the result of the processed
            command contained within the backquotes.
        """
        get_text = ctx_str

        # Commands cannot begin with "`"
        get_text = get_text.replace("`", "")
        get_text = get_text.strip()

        input_stream = InputStream(get_text)
        lexer = ShellGrammarLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = ShellGrammarParser(token_stream)
        tree = parser.command()

        new_converter = Converter()
        result = new_converter.visit(tree)

        return result

    def visitDouble_quoted(self, ctx):
        """
        Processes a string representing a double-quoted segment.

        This method handles double-quoted segments as well as backquotes if
        they are within double quotes.

        Args:
            ctx (str): The string segment enclosed in double quotes.

        Returns:
            str: The processed string with double quotes and
            any inner backquoted sections appropriately handled.
        """
        if "`" in ctx:
            count = 0
            for char in ctx:
                if char == "`":
                    count += 1

            string_passed = ctx
            string_list = self.split_preserving_backquotes(string_passed)

            for i in range(len(string_list)):
                if string_list[i][0] == "`":
                    get_bquote_data = self.visitBack_quoted(string_list[i])
                    string_list[
                        i
                    ] = get_bquote_data
                    string_list = (
                        string_list[:i] + string_list[i] +
                        string_list[i + 1:]
                    )

            result_string = "".join(string_list)
            return result_string

        else:
            # Double quotes cannot have double quotes within
            string_passed = ctx.replace('"', "")
            cleaned_data = '"' + string_passed + '"'

            return cleaned_data

    def split_preserving_backquotes(self, string):
        """
        Splits a string while preserving backquoted sections.

        This function splits the string around backquoted sections without
        breaking the backquoted parts. It uses a regular expression to identify
        and preserve backquoted segments.

        Args:
            string (str): The string to be split.

        Returns:
            result (list): A list of string segments, with backquoted sections
            intact.
        """
        pattern = r"(`[^`]*`)"  # Pattern to identify backquoted sections
        parts = re.split(pattern, string)  # Split string based on pattern
        result = []
        buffer = ""

        for part in parts:
            if part.startswith("`") and part.endswith("`"):
                # If it's a backquoted section, append the buffer
                # and the backquoted section separately
                result.append(buffer)
                buffer = ""
                result.append(part)
            else:
                # If it's not a backquoted section, accumulate it in buffer
                buffer += part

        # Append remaining buffer
        result.append(buffer)

        return result

    def visitRedirection(self, ctx):
        """
        Visits and processes a 'redirection' node in the parse tree.

        This method handles redirections. It supports both
        input (<) and output (>) redirections.

        Args:
            ctx (ParserRuleContext): The context of the redirection node in
            the parse tree.

        Returns:
            tuple_main (tuple): A tuple representing the redirection,
            including its type (input or output)and the target (file name).
        """
        if isinstance(ctx, list):
            obj = ctx
            extracted_stuff = obj[0].getText()
            extracted_redir = extracted_stuff[0]
            extraced_arg = extracted_stuff[1:].strip()

            tuple_main = (extracted_redir, extraced_arg)
            return tuple_main

        else:
            extracted_text = ctx.getText()
            extracted_argument = self.visitArgument(ctx.argument())
            tuple_main = (extracted_text[0], extracted_argument)

            return tuple_main

    def visitPipe(self, ctx, results=None, contextType="pipe",
                  followedBySeq=False):
        """
        Visits and processes a 'pipe' node in the parse tree.

        This method interprets a series of piped commands (connected by '|').
        It recursively processes each command and appends the appropriate
        separator based on the command's position and context.

        Args:
            1) ctx (ParserRuleContext): The context of the pipe node in the
            parse tree.
            2) results (list, optional): A list to accumulate the processed
            command results.
            3) contextType (str): Indicates the type of context, default
            is "pipe". followedBySeq (bool): Flag to indicate if the pipe is
            followed by a sequence.

        Returns:
            results (list): A list containing processed commands
            with appropriate separators ('|' or ';').
        """
        if results is None:
            results = []

        children = list(ctx.getChildren())
        num_children = len(children)

        for i, child in enumerate(children):
            if isinstance(child, ShellGrammarParser.CallContext):
                command_result = self.visitCall(child)
                # Append "|" for all but the last command, or ";" if it's
                # followed by a sequence
                if i < num_children - 1:
                    command_result.append(set("|"))
                elif followedBySeq:
                    command_result.append(set(";"))
                results.append(command_result)
            elif isinstance(child, ShellGrammarParser.PipeContext):
                self.visitPipe(
                    child, results, contextType="pipe",
                    followedBySeq=followedBySeq
                )

        return results

    def visitSeq(self, ctx, results=None):
        """
        Visits and processes a 'seq' (sequence) node in the parse tree.

        This method interprets a series of sequenced commands (connected
        by ';').

        Args:
            1) ctx (ParserRuleContext): The context of the seq node in the
            parse tree.
            2) results (list, optional): A list to accumulate the
            processed command results.

        Returns:
            results (list): A list containing processed commands with
            semicolons as separators.
        """
        if results is None:
            results = []

        children = list(ctx.getChildren())
        num_children = len(children)

        for i, child in enumerate(children):
            if isinstance(child, ShellGrammarParser.CallContext):
                command_result = self.visitCall(child)
                if i < num_children - 1:
                    command_result.append(set(";"))
                results.append(command_result)
            elif isinstance(child, ShellGrammarParser.SeqContext):
                self.visitSeq(child, results)
            elif isinstance(child, ShellGrammarParser.PipeContext):
                # Pass an indicator that the pipe is followed by a sequence
                self.visitPipe(
                    child,
                    results,
                    contextType="seq",
                    followedBySeq=(i < num_children - 1),
                )

        return results
