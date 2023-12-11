import sys
import os
import unittest
from collections import deque
from applications import pwd
from exceptions.WrongNumberOfArgsError import WrongNumberOfArgsError

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestPwd(unittest.TestCase):
    def setUp(self):
        self.pwd = pwd([])

    def test_pwd_no_args(self):
        """Test pwd with no arguments."""
        out = deque()
        self.pwd.exec(out)
        self.assertEqual(''.join(out), os.getcwd())

    def test_pwd_with_args(self):
        """Test pwd with unexpected arguments."""
        self.pwd.args = ["unexpected_arg"]
        out = deque()
        with self.assertRaises(WrongNumberOfArgsError):
            self.pwd.exec(out)
