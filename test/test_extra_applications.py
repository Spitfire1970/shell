import unittest
import os
import shutil
import sys
from pathlib import Path
from exceptions.WrongNumberOfArgsError import \
    WrongNumberOfArgsError
from extra_applications import mkdir, touch

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
)


class TestMkdir(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'test_dir_converter'
        self.original_dir = os.getcwd()
        os.makedirs(self.test_dir)
        os.chdir(self.test_dir)

        self.mkdir = mkdir([])

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_mkdir_create_directory(self):
        test_dir_name = 'new_test_directory'
        self.mkdir.args = [test_dir_name]
        self.mkdir.exec([])
        self.assertTrue(Path(test_dir_name).is_dir(),
                        f"Directory '{test_dir_name}' was not created")

    def test_mkdir_no_arguments(self):
        with self.assertRaises(WrongNumberOfArgsError):
            self.mkdir.exec([])

    def test_mkdir_existing_directory(self):
        test_dir_name = 'existing_directory'
        os.makedirs(test_dir_name)
        self.mkdir.args = [test_dir_name]

        self.mkdir.exec([])
        self.assertTrue(os.path.isdir(test_dir_name),
                        f"Directory '{test_dir_name}' does not exist after \
                            executing mkdir command")


class TestTouch(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'test_dir_converter'
        self.original_dir = os.getcwd()
        os.makedirs(self.test_dir)
        os.chdir(self.test_dir)

        self.touch = touch([])

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_touch_create_file(self):
        test_file_name = 'new_test_file.txt'
        self.touch.args = [test_file_name]
        self.touch.exec([])
        self.assertTrue(Path(test_file_name).is_file(),
                        f"File '{test_file_name}' was not created")

    def test_touch_no_arguments(self):
        with self.assertRaises(WrongNumberOfArgsError):
            self.touch.exec([])
