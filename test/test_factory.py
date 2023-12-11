import sys
import os
import unittest
from factory import Factory
from exceptions.UnsupportedApplicationError import UnsupportedApplicationError

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestFactory(unittest.TestCase):

    def setUp(self):
        self.out = []
        self.factory = Factory()

    def tearDown(self):
        self.out = []
        self.factory = Factory()

    def test_edge_case_listoflist(self):
        self.factory.factory("echo", [["hello", "world"]], self.out)
        self.assertEqual(self.out, ["hello world"])

    def test_normal_app(self):
        self.factory.factory("echo", ["'hello'", "'world'"], self.out)
        self.assertEqual(self.out, ["hello world"])

    def test_non_existent_app(self):
        with self.assertRaises(UnsupportedApplicationError):
            self.factory.factory("hey", ["hello", "world"], self.out)


class TestSingleton(unittest.TestCase):
    def setUp(self):
        self.out = []
        self.factory1 = Factory()
        self.factory2 = Factory()

    def tearDown(self):
        self.out = []
        self.factory = Factory()

    def test_returns_same_factory(self):
        self.assertEqual(id(self.factory1), id(self.factory2))
        self.assertEqual([], self.out)


class TestUnsafeDecorator(unittest.TestCase):
    def test_unsafe(self):
        out = []
        factory = Factory()
        factory.factory("_pwd", ["some_arg"], out)
        self.assertNotEqual(out, [])


class TestGlob(unittest.TestCase):
    def setUp(self):
        self.out = []
        self.factory = Factory()

    def tearDown(self):
        self.out = []
        self.factory = Factory()

    def test_shell(self):
        self.factory.factory("echo", ["*/*.py"], self.out)
        self.assertTrue(len(self.out) > 0)
        self.assertTrue(all(ele[len(ele)-3:] == ".py" for ele in self.out))

    def test_removes_quotes_no_glob(self):
        self.factory.factory("echo", ["'shell'"], self.out)
        self.assertEqual(self.out, ["shell"])

    def test_edge_case_passed_dict_for_pipe(self):
        self.factory.factory(
            "cut", ["-b", "2-", "hey", {"passed_code": 100200100}], self.out)
        self.assertEqual(self.out, ["ey"])

    def test_edge_case_disabled_quotes(self):
        self.factory.factory("echo", ['\'\''], self.out)
        self.assertEqual(["\'\'"], self.out)
