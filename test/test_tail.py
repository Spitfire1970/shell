import sys
import os
import tempfile
import unittest
from collections import deque
from applications import tail
from exceptions.WrongNumberOfArgsError import WrongNumberOfArgsError
from exceptions.NoFileFoundError import NoFileFoundError
from exceptions.WrongFlagsError import WrongFlagsError

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestTail(unittest.TestCase):
    def setUp(self):
        self.tail = tail([])

    def create_temp_file_with_content(self, content):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'w') as f:
            f.write(content)
        return temp_file

    def test_tail_default_n_lines(self):
        temp_file = self.create_temp_file_with_content(
            "Line1\nLine2\nLine3\nLine4\nLine5\n")
        self.tail.args = [temp_file.name]
        out = deque()
        self.tail.exec(out)
        expected_output = [
            'Line1\n', 'Line2\n', 'Line3\n', 'Line4\n', 'Line5\n']
        actual_output = [line.strip('\n') for line in list(out)]
        self.assertEqual(
            actual_output, [
                line.strip('\n') for line in expected_output[-10:]])
        os.unlink(temp_file.name)

    def test_tail_specific_n_lines(self):
        temp_file = self.create_temp_file_with_content(
            "Line1\nLine2\nLine3\nLine4\nLine5\n")
        self.tail.args = ["-n", "3", temp_file.name]
        out = deque()
        self.tail.exec(out)
        expected_output = ['Line3\n', 'Line4\n', 'Line5\n']
        actual_output = [line.strip('\n') for line in list(out)]
        self.assertEqual(actual_output, [
            line.strip('\n') for line in expected_output])
        os.unlink(temp_file.name)

    def test_tail_more_lines_than_exist(self):
        temp_file = self.create_temp_file_with_content(
            "Line1\nLine2\nLine3\nLine4\nLine5\n")
        self.tail.args = ["-n", "6", temp_file.name]
        out = deque()
        self.tail.exec(out)
        expected_output = [
            'Line1\n', 'Line2\n', 'Line3\n', 'Line4\n', 'Line5\n']
        actual_output = [line.strip('\n') for line in list(out)]
        self.assertEqual(
            actual_output, [line.strip('\n') for line in expected_output])
        os.unlink(temp_file.name)

    def test_tail_file_not_found(self):
        self.tail.args = ["nonexistent.txt"]
        out = deque()
        with self.assertRaises(NoFileFoundError):
            self.tail.exec(out)

    def test_tail_with_empty_file(self):
        temp_file = self.create_temp_file_with_content("")
        self.tail.args = [temp_file.name]
        out = deque()
        self.tail.exec(out)
        self.assertEqual(list(out), [])
        os.unlink(temp_file.name)

    def test_tail_wrong_flag(self):
        temp_file = self.create_temp_file_with_content("Line1\nLine2\n")
        self.tail.args = ["-x", "3", temp_file.name]
        out = deque()
        with self.assertRaises(WrongFlagsError):
            self.tail.exec(out)
        os.unlink(temp_file.name)

    def test_tail_no_args(self):
        out = deque()
        with self.assertRaises(WrongNumberOfArgsError):
            self.tail.exec(out)
