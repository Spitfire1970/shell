import sys
import os
import unittest
import shutil
from applications import find
from collections import deque
from exceptions.WrongNumberOfArgsError import WrongNumberOfArgsError
from exceptions.WrongFlagsError import WrongFlagsError

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestFind(unittest.TestCase):

    def setUp(self):
        self.original_dir = os.getcwd()
        self.find = find([])
        self.test_dir = 'test_directory'
        os.makedirs(self.test_dir)
        os.chdir(self.test_dir)
        with open('random.txt', 'w') as file:
            file.write('the\nquick\nbrown\nfox\nkumped\nover')
        with open('cool.txt', 'w') as file:
            file.write('twentyonepilots\nis\ncool\nlol')
        os.chdir(self.original_dir)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_find_no_match(self):
        self.find.args = ["-name", "invalid_filename"]
        output = deque()
        self.find.exec(output)
        output_str = ''.join(list(output))
        self.assertEqual(output_str, '')

    def test_find_with_specified_path(self):
        self.find.args = ["test_directory", "-name", "*.txt"]
        out = []
        self.find.exec(out)
        self.assertEqual(
            set(out), set(
                ["test_directory/cool.txt", "test_directory/random.txt"]))

    def test_find_with_no_path_provided(self):
        os.chdir("test_directory")
        self.find.args = ["-name", "*.txt"]
        out = []
        self.find.exec(out)
        self.assertEqual(set(out), set(["./cool.txt", "./random.txt"]))

    def test_find_wrong_num_args(self):
        self.find.args = ["-name"]
        out = []
        with self.assertRaises(WrongNumberOfArgsError):
            self.find.exec(out)

    def test_find_with_no_path_provided_wrong_flag(self):
        os.chdir("test_directory")
        self.find.args = ["-namey", "*.txt"]
        out = []
        with self.assertRaises(WrongFlagsError):
            self.find.exec(out)
            self.assertNotEquals(out, ["./cool.txt", "./random.txt"])

    def test_find_with_specified_path_wrong_flag(self):
        self.find.args = ["test_directory", "-namey", "*.txt"]
        out = []
        with self.assertRaises(WrongFlagsError):
            self.find.exec(out)
            self.assertNotEquals(
                out, ["test_directory/cool.txt", "test_directory/random.txt"])
