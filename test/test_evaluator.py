import sys
import os
import unittest
import shutil
from evaluator import Evaluation_Single_Call
from evaluator import Evaluation_Non_Single_Call
from exceptions.WrongNumberOfRedirectionsError import \
    WrongNumberOfRedirectionsError
from exceptions.NoFileFoundError import NoFileFoundError

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
    )


class TestEvaluateSingleCall(unittest.TestCase):
    def setUp(self):
        self.evaluator = Evaluation_Single_Call()

        self.test_dir = 'test_dir_converter'
        self.original_dir = os.getcwd()
        os.makedirs(self.test_dir)
        os.chdir(self.test_dir)

        with open('test_file.txt', 'w') as file:
            file.write('I am in the file')

    def tearDown(self):
        del self.evaluator

        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_single_call(self):
        given_input = ['echo', ['hello', 'world']]
        result = self.evaluator.single_call(given_input).pop()
        expected_result = "hello world"
        self.assertEqual(result, expected_result)

    def test_single_call_nested_cmd(self):
        given_input = [['echo'], ['hello', 'world']]
        result = self.evaluator.single_call(given_input).pop()
        expected_result = "hello world"
        self.assertEqual(result, expected_result)

    def test_single_call_nested_args(self):
        given_input = ['echo', [['hello', 'world']]]
        result = self.evaluator.single_call(given_input).pop()
        expected_result = "hello world"
        self.assertEqual(result, expected_result)

    def test_single_call_output_redirection(self):
        given_input = ['echo', ['hello', 'world'], (">", "output.txt")]
        result = self.evaluator.single_call(given_input)
        expected_result = []
        self.assertEqual(result, expected_result)

    def test_single_call_input_redirection(self):
        given_input = ['cat', [], ("<", "test_file.txt")]
        result = self.evaluator.single_call(given_input).pop()
        expected_result = "I am in the file"
        self.assertEqual(result, expected_result)

    def test_file_not_found_exception(self):
        expr = ["cat", [], ("<", "non_existent_file.txt")]

        with self.assertRaises(NoFileFoundError):
            self.evaluator.single_call(expr)

    def test_wrong_number_of_redirections_exception(self):
        expr = ["echo", ["hello"], (">", "output.txt"), (">", "output2.txt")]
        with self.assertRaises(WrongNumberOfRedirectionsError):
            self.evaluator.single_call(expr)


class TestEvaluateNonSingleCall(unittest.TestCase):
    def setUp(self):
        self.evaluator = Evaluation_Non_Single_Call()

        self.test_dir = 'test_dir_converter'
        self.original_dir = os.getcwd()
        os.makedirs(self.test_dir)
        os.chdir(self.test_dir)

        with open('test_file.txt', 'w') as file:
            file.write('I am in the file')

    def tearDown(self):
        del self.evaluator

        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_multiple_call_seq(self):
        given_input = [['echo', ['hello', 'world'], {';'}],
                       ['echo', ['hi'], {';'}], ['echo', ['bye']]]
        result = self.evaluator.call_seperate(given_input)
        expected_result = ["hello world", "hi", "bye"]
        self.assertEqual(result, expected_result)

    def test_multiple_call_pipe(self):
        given_input = [['ls', [], {'|'}], ['grep', ["'^d'"], {'|'}],
                       ['sort', ['5']]]
        result = self.evaluator.call_seperate(given_input).pop()
        expected_result = "5"
        self.assertEqual(result, expected_result)

    def test_multiple_call_pipe_and_seq(self):
        given_input = [['echo', ['test_file.txt'], {'|'}],
                       ['grep', ['GO'], {';'}], ['echo', ['hey'], {';'}],
                       ['echo', ['hi'], {';'}], ['echo', ['bye']]]
        result = self.evaluator.call_seperate(given_input)
        expected_result = ["hey", "hi", "bye"]
        self.assertEqual(result, expected_result)

    def test_multiple_call_pipe_and_seq_2(self):
        given_input = [['echo', ['aaa'], ('>', 'test_file.txt'), {';'}],
                       ['cat', ['test_file.txt'], {'|'}], ['uniq', ['-i']]]
        result = self.evaluator.call_seperate(given_input)
        expected_result = ["aaa"]
        self.assertEqual(result, expected_result)
