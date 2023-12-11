import unittest
import os
import shutil
import sys
from hypothesis import settings
from hypothesis import given, strategies as st
from antlr4 import InputStream, CommonTokenStream
from grammar.ShellGrammarLexer import ShellGrammarLexer
from grammar.ShellGrammarParser import ShellGrammarParser
from converter import Converter

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestConverter(unittest.TestCase):
    def setUp(self):
        self.converter = Converter()

        self.test_dir = 'test_dir_converter'
        self.original_dir = os.getcwd()
        os.makedirs(self.test_dir)
        os.chdir(self.test_dir)

        with open('test_file.txt', 'w') as file:
            file.write('I am in the file')

    def parse_command(self, input_data):
        # Parses the input command and returns the parse tree
        input_stream = InputStream(input_data)
        lexer = ShellGrammarLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = ShellGrammarParser(stream)
        return parser.command()

    def test_visit_command_call_words(self):
        tree = self.parse_command("echo Hello World")
        result = self.converter.visitCommand(tree).pop()
        expected_result = "Hello World"
        self.assertEqual(result, expected_result)

    def test_visit_command_call_single_quotes_arg_begin(self):
        tree = self.parse_command("echo 'Hey'")
        result = self.converter.visitCommand(tree).pop()
        expected_result = "Hey"
        self.assertEqual(result, expected_result)

    def test_visit_command_call_double_quotes_arg_begin(self):
        tree = self.parse_command("echo \"Hey\"")
        result = self.converter.visitCommand(tree).pop()
        expected_result = "Hey"
        self.assertEqual(result, expected_result)

    def test_visit_command_call_backquotes_arg_begin(self):
        tree = self.parse_command("echo `echo Hey`")
        result = self.converter.visitCommand(tree).pop()
        expected_result = "Hey"
        self.assertEqual(result, expected_result)

    def test_visit_command_call_single_quotes_arg_non_begin(self):
        tree = self.parse_command("echo a'b'c")
        result = self.converter.visitCommand(tree).pop()
        expected_result = "a'b'c"
        self.assertEqual(result, expected_result)

    def test_visit_command_call_double_quotes_arg_non_begin(self):
        tree = self.parse_command("echo a\"b\"c")
        result = self.converter.visitCommand(tree).pop()
        expected_result = "abc"
        self.assertEqual(result, expected_result)

    def test_visit_command_call_backquotes_arg_non_begin(self):
        tree = self.parse_command("echo a`echo b`c")
        result = self.converter.visitCommand(tree).pop()
        expected_result = "abc"
        self.assertEqual(result, expected_result)

    def test_visit_command_call_single_and_double_quotes_arg_begin(self):
        tree = self.parse_command(
            "echo 'I am \"echo Shell and I am\" the best'"
            )
        result = self.converter.visitCommand(tree).pop()
        expected_result = 'I am "echo Shell and I am" the best'
        self.assertEqual(result, expected_result)

    def test_visit_command_call_double_and_single_quotes_arg_begin(self):
        tree = self.parse_command(
            "echo \"I am 'echo Shell and I am' the best\""
            )
        result = self.converter.visitCommand(tree).pop()
        expected_result = "I am 'echo Shell and I am' the best"
        self.assertEqual(result, expected_result)

    def test_visit_command_call_single_and_backquotes_arg_begin(self):
        tree = self.parse_command("echo 'I am `echo Shell and I am` the best'")
        result = self.converter.visitCommand(tree).pop()
        expected_result = 'I am `echo Shell and I am` the best'
        self.assertEqual(result, expected_result)

    def test_visit_command_call_double_and_backquotes_arg_begin(self):
        tree = self.parse_command(
            "echo \"I am `echo Shell and I am` the best\""
            )
        result = self.converter.visitCommand(tree).pop()
        expected_result = "I am Shell and I am the best"
        self.assertEqual(result, expected_result)

    def test_visit_command_call_nested_single_quotes_arg_begin(self):
        tree = self.parse_command("echo 'I am 'echo Shell and I am' the best'")
        result = self.converter.visitCommand(tree).pop()
        expected_result = 'I am echo Shell and I am\' the best\''
        self.assertEqual(result, expected_result)

    def test_visit_command_call_nested_double_quotes_arg_begin(self):
        tree = self.parse_command(
            'echo "I am \'echo shell and I am\' the best"'
            )
        result = self.converter.visitCommand(tree).pop()
        expected_result = "I am \'echo shell and I am\' the best"
        self.assertEqual(result, expected_result)

    def test_visit_command_call_backquotes_cmd_arg(self):
        tree = self.parse_command("`echo echo` `echo hey`")
        result = self.converter.visitCommand(tree).pop()
        expected_result = "hey"
        self.assertEqual(result, expected_result)

    def test_visit_command_call_backquotes_cmd(self):
        tree = self.parse_command("`echo echo` hey")
        result = self.converter.visitCommand(tree).pop()
        expected_result = "hey"
        self.assertEqual(result, expected_result)

    def test_visit_command_input_redir(self):
        tree = self.parse_command("head < test_file.txt")
        result = self.converter.visitCommand(tree).pop()
        expected_result = "I am in the file"
        self.assertEqual(result, expected_result)

    def test_visit_command_input_redir_2(self):
        tree = self.parse_command("< test_file.txt head")
        result = self.converter.visitCommand(tree).pop()
        expected_result = "I am in the file"
        self.assertEqual(result, expected_result)

    def test_visit_command_output_redir(self):
        tree = self.parse_command("echo hey > output.txt")
        result = self.converter.visitCommand(tree)
        expected_result = []
        self.assertEqual(result, expected_result)

    @given(input_data=st.lists(
        st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
            min_size=1
        ).map(lambda s: f"echo {s}"),
        min_size=1
    ).map("; ".join))  # Hypothesis Testing
    @settings(max_examples=500)  # Generates 500 test cases
    def test_visit_command_seq(self, input_data):
        tree = self.parse_command(input_data)
        result = self.converter.visitCommand(tree)
        num_semicolons = input_data.count(';')
        expected_length = num_semicolons + 1
        self.assertEqual(len(result), expected_length)

    def test_visit_command_pipe_multiple(self):
        tree = self.parse_command("ls | grep '^d' | sort 5")
        result = self.converter.visitCommand(tree)
        expected_result = ['5']
        self.assertEqual(result, expected_result)

    def test_visit_command_pipe_single_and_seq(self):
        tree = self.parse_command(
            "echo test_file.txt | grep GO; echo hey; echo hi; echo bye"
            )
        result = self.converter.visitCommand(tree)
        expected_result = ['hey', 'hi', 'bye']
        self.assertEqual(result, expected_result)

    def tearDown(self):
        del self.converter

        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
