import sys
import os
import unittest
import tempfile
from applications import cd
from collections import deque
from exceptions.WrongNumberOfArgsError import WrongNumberOfArgsError
from exceptions.NoDirectoryFoundError import NoDirectoryFoundError

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestCd(unittest.TestCase):
    def setUp(self):
        self.original_dir = os.getcwd()
        self.cd = cd([])

    def tearDown(self):
        os.chdir(self.original_dir)

    def test_cd_no_args(self):
        self.cd.args = []
        out = deque()
        with self.assertRaises(WrongNumberOfArgsError):
            self.cd.exec(out)

    def test_cd_too_many_args(self):
        self.cd.args = ["arg1", "arg2"]
        out = deque()
        with self.assertRaises(WrongNumberOfArgsError):
            self.cd.exec(out)

    def test_cd_invalid_path(self):
        self.cd.args = ["invalid_dir"]
        out = deque()
        with self.assertRaises(NoDirectoryFoundError):
            self.cd.exec(out)

    def test_cd_valid_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.cd.args = [temp_dir]
            out = deque()
            self.cd.exec(out)
            self.assertEqual(
                os.path.realpath(os.getcwd()), os.path.realpath(temp_dir))

    def test_cd_parent_directory(self):
        parent_dir = os.path.dirname(os.getcwd())
        self.cd.args = [".."]
        out = deque()
        self.cd.exec(out)
        self.assertEqual(os.getcwd(), parent_dir)

    def test_cd_current_directory(self):
        current_dir = os.getcwd()
        self.cd.args = ["."]
        out = deque()
        self.cd.exec(out)
        self.assertEqual(os.getcwd(), current_dir)

    def test_cd_home_directory(self):
        home_dir = os.path.expanduser('~')
        self.cd.args = [home_dir]
        out = deque()
        self.cd.exec(out)
        self.assertEqual(
            os.path.realpath(os.getcwd()), os.path.realpath(home_dir))

    def test_cd_subdirectory_and_back(self):
        subdir = os.path.join(self.original_dir, 'subdir')
        os.mkdir(subdir)
        self.cd.args = ["subdir"]
        out = deque()
        self.cd.exec(out)
        self.assertNotEqual(os.getcwd(), self.original_dir)
        self.cd.args = [".."]
        out = deque()
        self.cd.exec(out)
        self.assertEqual(os.getcwd(), self.original_dir)
        os.rmdir(subdir)  # Clean up after test

    def test_cd_directory_with_spaces(self):
        dir_with_spaces = os.path.join(self.original_dir, 'dir with spaces')
        os.mkdir(dir_with_spaces)
        self.cd.args = ["dir with spaces"]
        out = deque()
        self.cd.exec(out)
        self.assertEqual(os.path.realpath(os.getcwd()),
                         os.path.realpath(dir_with_spaces))
        os.rmdir(dir_with_spaces)  # Clean up after test

    def test_cd_recursive_parent_navigation(self):
        self.cd.args = ["../../"]
        out = deque()
        self.cd.exec(out)
        expected_dir = os.path.abspath(
            os.path.join(self.original_dir, "../../"))
        self.assertEqual(os.getcwd(), expected_dir)
