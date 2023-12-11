import sys
import os
import unittest
import tempfile
from collections import deque
from applications import head
from exceptions.WrongNumberOfArgsError import WrongNumberOfArgsError
from exceptions.NoFileFoundError import NoFileFoundError
from exceptions.WrongFlagsError import WrongFlagsError

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestHead(unittest.TestCase):
    def setUp(self):
        self.head = head([])

    def create_temp_file_with_content(self, content):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'w') as f:
            f.write(content)
        return temp_file

    def test_head_default_n_lines(self):
        temp_file = self.create_temp_file_with_content(
            "Line1\nLine2\nLine3\nLine4\nLine5\n")
        self.head.args = [temp_file.name]
        out = deque()
        self.head.exec(out)
        expected_output = [
            'Line1\n', 'Line2\n', 'Line3\n', 'Line4\n', 'Line5\n']
        actual_output = list(out)
        if actual_output and not actual_output[-1].endswith('\n'):
            expected_output = [
                line.strip('\n') for line in expected_output[:10]]
        self.assertEqual(actual_output, expected_output[:10])
        os.unlink(temp_file.name)

    def test_head_specific_n_lines(self):
        temp_file = self.create_temp_file_with_content(
            "Line1\nLine2\nLine3\nLine4\nLine5\n")
        self.head.args = ["-n", "3", temp_file.name]
        out = deque()
        self.head.exec(out)
        expected_output = ['Line1\n', 'Line2\n', 'Line3\n']
        actual_output = list(out)
        if actual_output and not actual_output[-1].endswith('\n'):
            expected_output = [line.strip('\n') for line in expected_output]
        self.assertEqual(actual_output, expected_output)
        os.unlink(temp_file.name)

    def test_head_file_not_found(self):
        self.head.args = ["nonexistent.txt"]
        out = deque()
        with self.assertRaises(NoFileFoundError):
            self.head.exec(out)

    def test_head_with_empty_file(self):
        temp_file = self.create_temp_file_with_content("")
        self.head.args = [temp_file.name]
        out = deque()
        self.head.exec(out)
        self.assertEqual(list(out), [])
        os.unlink(temp_file.name)

    def test_head_wrong_flag(self):
        temp_file = self.create_temp_file_with_content("Line1\nLine2\n")
        self.head.args = ["-x", "3", temp_file.name]
        out = deque()
        with self.assertRaises(WrongFlagsError):
            self.head.exec(out)
        os.unlink(temp_file.name)

    def test_head_no_args(self):
        out = deque()
        with self.assertRaises(WrongNumberOfArgsError):
            self.head.exec(out)
