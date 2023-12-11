import sys
import os
import tempfile
import unittest
from collections import deque
from applications import uniq
from exceptions.WrongNumberOfArgsError import WrongNumberOfArgsError
from exceptions.NoFileFoundError import NoFileFoundError
from exceptions.WrongFlagsError import WrongFlagsError

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestUniq(unittest.TestCase):
    def setUp(self):
        self.uniq = uniq([])

    def create_temp_file_with_content(self, content):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'w') as f:
            f.write(content)
        return temp_file

    def test_uniq_basic(self):
        temp_file = self.create_temp_file_with_content("a\na\na\nb\nb\n")
        self.uniq.args = [temp_file.name]
        out = deque()
        self.uniq.exec(out)
        self.assertEqual(''.join(out), 'a\nb')
        os.unlink(temp_file.name)

    def test_uniq_case_insensitive(self):
        temp_file = self.create_temp_file_with_content("A\na\nB\nb\n")
        self.uniq.args = ["-i", temp_file.name]
        out = deque()
        self.uniq.exec(out)
        self.assertEqual(''.join(out), 'A\nB')
        os.unlink(temp_file.name)

    def test_uniq_file_not_found(self):
        self.uniq.args = ["nonexistent.txt"]
        out = deque()
        with self.assertRaises(NoFileFoundError):
            self.uniq.exec(out)

    def test_uniq_no_args(self):
        out = deque()
        with self.assertRaises(WrongNumberOfArgsError):
            self.uniq.exec(out)

    def test_uniq_wrong_flag(self):
        temp_file = self.create_temp_file_with_content("a\na\nb\nb\n")
        self.uniq.args = ["-x", temp_file.name]
        out = deque()
        with self.assertRaises(WrongFlagsError):
            self.uniq.exec(out)
        os.unlink(temp_file.name)
