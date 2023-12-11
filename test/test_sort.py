import sys
import os
import unittest
import tempfile
from collections import deque
from applications import sort
from exceptions.WrongNumberOfArgsError import WrongNumberOfArgsError
from exceptions.NoFileFoundError import NoFileFoundError
from exceptions.WrongFlagsError import WrongFlagsError

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestSort(unittest.TestCase):
    def setUp(self):
        self.sort = sort([])

    def create_temp_file_with_content(self, content):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'w') as f:
            f.write(content)
        return temp_file

    def test_sort_basic(self):
        temp_file = self.create_temp_file_with_content("c\na\nb\n")
        self.sort.args = [temp_file.name]
        out = deque()
        self.sort.exec(out)
        self.assertEqual(''.join(out), 'a\nb\nc')
        os.unlink(temp_file.name)

    def test_sort_reverse(self):
        temp_file = self.create_temp_file_with_content("c\na\nb\n")
        self.sort.args = ["-r", temp_file.name]
        out = deque()
        self.sort.exec(out)
        self.assertEqual(''.join(out), 'c\nb\na')
        os.unlink(temp_file.name)

    def test_sort_no_args(self):
        out = deque()
        with self.assertRaises(WrongNumberOfArgsError):
            self.sort.exec(out)

    def test_sort_file_not_found(self):
        self.sort.args = ["nonexistent.txt"]
        out = deque()
        with self.assertRaises(NoFileFoundError):
            self.sort.exec(out)

    def test_sort_wrong_flag(self):
        temp_file = self.create_temp_file_with_content("c\na\nb\n")
        self.sort.args = ["-x", temp_file.name]
        out = deque()
        with self.assertRaises(WrongFlagsError):
            self.sort.exec(out)
        os.unlink(temp_file.name)
