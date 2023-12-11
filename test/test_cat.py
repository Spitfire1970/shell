import sys
import os
import tempfile
import unittest
from collections import deque
from exceptions.WrongNumberOfArgsError import WrongNumberOfArgsError
from exceptions.NoFileFoundError import NoFileFoundError
from applications import cat

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestCat(unittest.TestCase):
    def setUp(self):
        self.cat = cat([])

    def create_temp_file(self, content):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'w') as f:
            f.write(content)
        return temp_file

    def test_cat_single_file(self):
        temp_file = self.create_temp_file("Hello\nWorld\n")
        self.cat.args = [temp_file.name]
        out = deque()
        self.cat.exec(out)
        out_str = ''.join(list(out))
        self.assertEqual(out_str, "Hello\nWorld")
        os.unlink(temp_file.name)

    def test_cat_multiple_files(self):
        temp_file1 = self.create_temp_file("File1\nContent\n")
        temp_file2 = self.create_temp_file("File2\nContent\n")
        self.cat.args = [temp_file1.name, temp_file2.name]
        out = deque()
        self.cat.exec(out)
        out_str = ''.join(list(out))
        self.assertEqual(out_str, "File1\nContent\nFile2\nContent")
        os.unlink(temp_file1.name)
        os.unlink(temp_file2.name)

    def test_cat_nonexistent_file(self):
        self.cat.args = ["nonexistent.txt"]
        out = deque()
        with self.assertRaises(NoFileFoundError):
            self.cat.exec(out)

    def test_cat_no_args(self):
        out = deque()
        with self.assertRaises(WrongNumberOfArgsError):
            self.cat.exec(out)

    def test_cat_empty_file(self):
        temp_file = self.create_temp_file("")
        self.cat.args = [temp_file.name]
        out = deque()
        self.cat.exec(out)
        if out:
            out_str = ''.join(list(out))
            self.assertEqual(out_str, "")
        else:
            self.fail("Output deque is empty")
        os.unlink(temp_file.name)
