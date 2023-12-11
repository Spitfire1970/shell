import sys
import os
import unittest
import tempfile
from collections import deque
from applications import grep
from exceptions.WrongNumberOfArgsError import WrongNumberOfArgsError
from exceptions.NoFileFoundError import NoFileFoundError

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestGrep(unittest.TestCase):
    def setUp(self):
        self.temp_file1 = tempfile.NamedTemporaryFile(delete=False)
        with open(self.temp_file1.name, 'w') as f:
            f.write('AAA\nBBB\nCCC\n')

        self.temp_file2 = tempfile.NamedTemporaryFile(delete=False)
        with open(self.temp_file2.name, 'w') as f:
            f.write('AAA\nDDD\nEEE\n')

        self.grep = grep([])

    def tearDown(self):
        os.remove(self.temp_file1.name)
        os.remove(self.temp_file2.name)

    def test_grep_no_match(self):
        self.grep.args = ["DDD", self.temp_file1.name]
        out = deque()
        self.grep.exec(out)
        self.assertEqual(list(out), [])

    def test_grep_single_match(self):
        self.grep.args = ["BBB", self.temp_file1.name]
        out = deque()
        self.grep.exec(out)
        self.assertEqual(list(out), ["BBB"])

    def test_grep_multiple_matches(self):
        with open(self.temp_file1.name, 'a') as f:
            f.write('AAA\nBBB\nCCC\n')
        with open(self.temp_file1.name, 'r') as f:
            f"Content of file {self.temp_file1.name}: {f.read()}"

        self.grep.args = ["AAA", self.temp_file1.name]
        out = deque()
        self.grep.exec(out)

        expected_output = ["AAA", "AAA"]
        self.assertEqual(list(out), expected_output)

    def test_grep_multiple_files(self):
        self.grep.args = ["AAA", self.temp_file1.name, self.temp_file2.name]
        out = []
        self.grep.exec(out)
        expected_output = [f"{self.temp_file1.name}:AAA",
                           f"{self.temp_file2.name}:AAA"]
        self.assertEqual(out, expected_output)

    def test_grep_file_not_found(self):
        self.grep.args = ["AAA", "nonexistent.txt"]
        out = deque()
        with self.assertRaises(NoFileFoundError):
            self.grep.exec(out)

    def test_grep_wrong_number_of_arguments(self):
        self.grep.args = []
        out = deque()
        with self.assertRaises(WrongNumberOfArgsError):
            self.grep.exec(out)
