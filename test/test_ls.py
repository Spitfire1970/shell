import sys
import os
import tempfile
import unittest
from applications import ls
from collections import deque
from exceptions.WrongNumberOfArgsError import WrongNumberOfArgsError
from exceptions.NoDirectoryFoundError import NoDirectoryFoundError

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestLs(unittest.TestCase):
    def setUp(self):
        self.ls = ls([])
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file1 = tempfile.NamedTemporaryFile(
            dir=self.test_dir.name, delete=False)
        self.test_file2 = tempfile.NamedTemporaryFile(
            dir=self.test_dir.name, delete=False)

    def tearDown(self):
        os.remove(self.test_file1.name)
        os.remove(self.test_file2.name)
        self.test_dir.cleanup()

    def test_ls_no_args(self):
        self.ls.args = []
        out = deque()
        self.ls.exec(out)
        expected_files = [
            f for f in os.listdir(os.getcwd()) if not f.startswith('.')]
        self.assertEqual(sorted(list(out)), sorted(expected_files))

    def test_ls_with_valid_directory(self):
        self.ls.args = [self.test_dir.name]
        out = deque()
        self.ls.exec(out)
        expected_files = [os.path.basename(
            self.test_file1.name), os.path.basename(self.test_file2.name)]
        self.assertEqual(sorted(list(out)), sorted(expected_files))

    def test_ls_with_invalid_directory(self):
        self.ls.args = ["non_existing_directory"]
        out = deque()
        with self.assertRaises(NoDirectoryFoundError):
            self.ls.exec(out)

    def test_ls_too_many_args(self):
        self.ls.args = ["arg1", "arg2"]
        out = deque()
        with self.assertRaises(WrongNumberOfArgsError):
            self.ls.exec(out)

    def test_ls_hidden_files(self):
        # Create a hidden file in the test directory
        hidden_file = tempfile.NamedTemporaryFile(
            dir=self.test_dir.name, prefix='.', delete=False)
        self.ls.args = [self.test_dir.name]
        out = deque()
        self.ls.exec(out)
        self.assertNotIn(os.path.basename(hidden_file.name), list(out))
        os.remove(hidden_file.name)

    def test_ls_empty_directory(self):
        empty_dir = tempfile.TemporaryDirectory()
        self.ls.args = [empty_dir.name]
        out = deque()
        self.ls.exec(out)
        self.assertEqual(list(out), [])
        empty_dir.cleanup()
