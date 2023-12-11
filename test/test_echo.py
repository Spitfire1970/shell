import sys
import os
import unittest
from applications import echo
from collections import deque

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestEcho(unittest.TestCase):
    def setUp(self):
        self.echo = echo([])

    def test_echo_no_args(self):
        out = deque()
        self.echo.exec(out)
        self.assertEqual(''.join(out), "")

    def test_echo_single_arg(self):
        self.echo.args = ["hello"]
        out = deque()
        self.echo.exec(out)
        self.assertEqual(''.join(out), "hello")

    def test_echo_multiple_args(self):
        self.echo.args = ["hello", "world"]
        out = deque()
        self.echo.exec(out)
        self.assertEqual(''.join(out), "hello world")

    def test_echo_special_chars(self):
        self.echo.args = ["hello", "world,", "user!"]
        out = deque()
        self.echo.exec(out)
        self.assertEqual(''.join(out), "hello world, user!")

    def test_echo_with_quotes(self):
        self.echo.args = ["'hello'", "world"]
        out = deque()
        self.echo.exec(out)
        self.assertEqual(''.join(out), "'hello' world")

    def test_echo_escaped_characters(self):
        self.echo.args = ["hello\\nworld"]
        out = deque()
        self.echo.exec(out)
        self.assertEqual(''.join(out), "hello\\nworld")

    def test_echo_long_string(self):
        long_string = "a" * 1000
        self.echo.args = [long_string]
        out = deque()
        self.echo.exec(out)
        self.assertEqual(''.join(out), long_string)

    def test_echo_boundary_case(self):
        self.echo.args = [""] * 1000
        out = deque()
        self.echo.exec(out)
        self.assertEqual(''.join(out), " " * 999)

    def test_echo_unicode(self):
        self.echo.args = ["عربي", "انا"]
        out = deque()
        self.echo.exec(out)
        self.assertEqual(''.join(out), "عربي انا")

    def test_echo_mixed_quoted_unquoted(self):
        self.echo.args = ["'hello'", "unquoted", "\"world\""]
        out = deque()
        self.echo.exec(out)
        self.assertEqual(''.join(out), "'hello' unquoted \"world\"")

    def test_echo_error_handling(self):
        self.echo.args = ["-e", "unsupported", "flag"]
        out = deque()
        self.echo.exec(out)
        self.assertIn("unsupported flag", ''.join(out))
