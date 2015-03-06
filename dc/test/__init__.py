#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
unit tests for DC reloaded
"""
import glob
import importlib
import os
import unittest

TEST_FILE_PATTERN = "test*"


def get_tests():
    """
    Return a test suite filled with all available test cases.
    """
    test_directory = os.path.dirname(__file__)
    current_dir = os.getcwd()
    os.chdir(test_directory)

    test_files = glob.glob(TEST_FILE_PATTERN)
    test_modules = [name for name, ext in map(os.path.splitext, test_files)]

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for module_name in test_modules:
        module_path = "{}.{}".format(__name__, module_name)
        module = importlib.import_module(module_path, __name__)
        suite.addTest(loader.loadTestsFromModule(module))

    os.chdir(current_dir)
    return suite
