from exceptions.WrongNumberOfRedirectionsError \
    import WrongNumberOfRedirectionsError
from exceptions.NoFileFoundError import NoFileFoundError
from factory import Factory
import os


class Evaluation_Single_Call:
    """
    Class to handle the evaluation of a single command call

    Attributes:
        out (list): A list to store the output of the command execution.
    """

    def __init__(self):
        self.out = []

    def single_call(self, expr):
        """
        This method handles a single call command expression by parsing
        the expression and executing the command.

        Args:
            expr (list): The command expression to be evaluated. It can
            include the command, its arguments, and redirection operators.

        Returns:
            self.out (list): The output of the command execution.
        """

        cmd = expr[0]

        if isinstance(expr[0], list):
            cmd = expr[0][0]  # cmd can only be a single word

        args = []
        redirs = []
        arrow = None
        redirect_file = None

        if len(expr) == 2:
            args = expr[1]

        if len(expr) > 2:
            args = expr[1]
            redirs = expr[2]
            arrow, redirect_file = redirs

        if len(expr) > 3:
            raise WrongNumberOfRedirectionsError

        if arrow == "<":
            self.handle_input_redirection(cmd, args, redirect_file)

            return self.out
        """
        We need to do input redirection first and then create factory class to
        send it to application because if we have sth like echo < input.txt, we
        have to interpret input redirection first.
        """
        factory = Factory()
        factory.factory(cmd, args, self.out)

        if arrow == ">":
            self.handle_output_redirection(redirect_file)

        return self.out

    def handle_output_redirection(self, file_name):
        """
        This method handles output redirection

        Args:
            file_name (str): The name of the file where the output should be
            redirected.

        Side Effects:
            Writes to a file specified by file_name.
            Clears the last line of output after writing to the file.
        """
        with open(file_name, "w") as file:

            for line in self.out:
                file.write(line)
            self.out.pop()

    def handle_input_redirection(self, cmd, args, file_name):
        """
        This method handles input redirection

        Args:
            1) cmd (str): The command to be executed.
            2) args (list): The list of arguments for the command.
            3) file_name (str): The name of the file from which input is to be
            redirected.

        Side Effects:
            Modifies the args list by appending the file name for input
            redirection.
        """
        if not os.path.exists(file_name):
            raise NoFileFoundError("<", file_name)
        args.append(file_name)

        factory = Factory()
        factory.factory(cmd, args, self.out)


class Evaluation_Non_Single_Call:
    """
    Class to handle the evaluation of non-single command calls - command
    expressions separated by pipes or semicolons.

    Attributes:
        out (list): A list to store all the output of each command's
        execution.
    """
    def __init__(self):
        self.out = []

    def call_seperate(self, passed_list):
        """
        It seperates and executes each command expression as per the pipes
        and/or semicolons.

        Args:
            passed_list (list): A list of command expressions, each
            potentially ending with a pipe '|' or semicolon ';'.

        Returns:
            out (list) : A list to store all the output of each command's
            execution.

        Note:
            This method internally uses an instance of Evaluation_Single_Call
            to execute individual commands.
        """

        pipe_count = 0

        for expr_count in range(len(passed_list)):
            if (passed_list[expr_count][-1]) == {"|"}:
                pipe_count += 1

        if pipe_count == 0:  # Handling multiple sequences only, no pipes.
            for expr in passed_list:
                self.seq_call(expr)
            self.out = [
                item[0] for item in self.out if item
            ]  # Removing the sublists and ensuring a big list
            return self.out
        else:

            pointer_1 = 0
            eval_single_call = Evaluation_Single_Call()

            while pointer_1 < len(passed_list):
                current_command = passed_list[pointer_1]
                next_command = (
                    passed_list[pointer_1 + 1]
                    if pointer_1 + 1 < len(passed_list)
                    else None
                )
                # Remove pipe or semicolon symbol if it's the last element
                if current_command[-1] == {"|"} \
                        or current_command[-1] == {";"}:
                    command_to_execute = current_command[
                        :-1
                    ]  # Slice off the last element (pipe or semicolon symbol)
                else:

                    command_to_execute = current_command

                if next_command and current_command[-1] == {"|"}:
                    eval_single_call.single_call(command_to_execute)
                    output = eval_single_call.out

                    next_command[1].extend(
                        output
                    )
                    next_command[1].append(
                        {"passed_code": 100200100}
                    )  # Appends a flag if "|" is present
                    eval_single_call.out = []

                else:
                    eval_single_call.single_call(command_to_execute)
                    self.out.extend(eval_single_call.out)
                    eval_single_call.out = []

                pointer_1 += 1

            return self.out

    def seq_call(self, expr):
        """
        This method is responsible for handling individual command expressions
        within a sequence of command expressions.

        Args:
            expr (list): A single command expression, possibly ending with a
            semicolon ';'. [The last command expression in a list of
            command expressions do not have a pipe or semicolon]

        Side Effects:
            Appends the output of the executed command to the 'out'
            attribute of the class.
        """
        get_last = expr[-1]

        multiple_cmds_seperator = [{";"}]

        if get_last in multiple_cmds_seperator:
            sliced_list = expr[0: len(expr) - 1]
            eval_single_call_obj = Evaluation_Single_Call()
            self.out.append(eval_single_call_obj.single_call(sliced_list))
        else:
            eval_single_call_obj = Evaluation_Single_Call()
            self.out.append(eval_single_call_obj.single_call(expr))
