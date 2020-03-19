#!/usr/bin/python
# -*- coding: utf-8 -*-

from importlib import import_module
from pathlib import Path


def run_tests(device):
    """Look for all available tests for the requested device and runs them.
    Return a list of strings with results or an empty list if all tests have passed successfully.
    """

    def import_test(device, test_name):
        """Dynamic modules (tests) import

        A module must follow the next template:
        def test(device):
            #check problem
            if something_happens:
                #rerurn results
                return string_with_problem
            else:
                #return None
                pass

        Use __ (double underscore) before file name if you need to hide a test from the importer.
        """

        module = import_module('.' + str(test_name.stem), 'scripts.tests.' + str.lower(device.family))
        return module.test(device)

    test_path = Path.cwd() / 'scripts' / 'tests' / str.lower(device.family)
    test_results = []

    for test_name in list(test_path.glob('[!__]*.py')):
        test_results.append(import_test(device, test_name))

    return test_results
