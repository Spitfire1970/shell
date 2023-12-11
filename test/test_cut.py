import sys
import os
import unittest
import tempfile
from applications import cut
from exceptions.WrongFlagsError import WrongFlagsError
from exceptions.InvalidRangeError import InvalidRangeError
from exceptions.WrongNumberOfArgsError import WrongNumberOfArgsError

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestCut(unittest.TestCase):

    def setUp(self):
        self.cut = cut([])
        self.file1 = tempfile.NamedTemporaryFile(delete=False)
        with open(self.file1.name, 'w') as f:
            f.write('abc\ndef\nxyz\n')

        self.file2 = tempfile.NamedTemporaryFile(delete=False)
        with open(self.file2.name, 'w') as f:
            f.write('AAABBBCCC\nDDDEEEFFF\nGGGHHHIII\n')

        self.cut = cut([])

    def tearDown(self):
        os.remove(self.file1.name)
        os.remove(self.file2.name)

    def test_cut_no_flag(self):
        with self.assertRaises(WrongNumberOfArgsError):
            self.cut.args = [self.file1.name]
            out = []
            self.cut.exec(out)

    def test_cut_multiple_range(self):
        fname = self.file2.name
        self.cut.args = ['-b', '-3,6,9-', fname]
        out = []
        self.cut.exec(out)
        exp_res = ['AAABC', 'DDDEF', 'GGGHI']
        self.assertEqual(out, exp_res)

    def test_cut_simple_range(self):
        fname = self.file2.name
        self.cut.args = ['-b', '2-5', fname]
        out = []
        self.cut.exec(out)
        exp_res = ['AABB', 'DDEE', 'GGHH']
        self.assertEqual(out, exp_res)

    def test_cut_wrong_flag(self):
        fname = self.file2.name
        self.cut.args = ['-r', '-3,6,9-', fname]
        out = []
        with self.assertRaises(WrongFlagsError):
            self.cut.exec(out)

    def test_cut_wrong_range(self):
        fname = self.file2.name
        self.cut.args = ['-b', '_9--', fname]
        out = []
        with self.assertRaises(InvalidRangeError):
            self.cut.exec(out)

    def test_cut_(self):
        fname = self.file1.name
        self.cut.args = ['-b', '1-', fname]
        out = []
        self.cut.exec(out)
        exp_res = ['abc', 'def', 'xyz']
        self.assertEqual(out, exp_res)

    def test_cut_no_end(self):
        fname = self.file1.name
        self.cut.args = ['-b', '1-', fname]
        out = []
        self.cut.exec(out)
        exp_res = ['abc', 'def', 'xyz']
        self.assertEqual(out, exp_res)

    def test_cut_no_start(self):
        fname = self.file1.name
        self.cut.args = ['-b', '-3', fname]
        out = []
        self.cut.exec(out)
        exp_res = ['abc', 'def', 'xyz']
        self.assertEqual(out, exp_res)

    def test_cut_opp_range(self):
        fname = self.file1.name
        self.cut.args = ['-b', '3-2', fname]
        out = []
        with self.assertRaises(InvalidRangeError):
            self.cut.exec(out)

    def test_cut_redundant_range(self):
        fname = self.file1.name
        self.cut.args = ['-b', '5,3-', fname]
        out = []
        self.cut.exec(out)
        exp_res = ['c', 'f', 'z']
        self.assertEqual(out, exp_res)

    def test_cut_pipe_content(self):
        self.cut.args = ['-b', '2,5', "abcde\nfghij",
                         {"passed_code": 100200100}]
        out = []
        self.cut.exec(out)
        exp_res = ['be', 'gj']
        self.assertEqual(out, exp_res)
