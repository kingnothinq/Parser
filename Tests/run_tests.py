#!/usr/bin/python
# -*- coding: utf-8 -*-

from importlib import import_module
from pathlib import Path


def run_tests(device):
    """Look for all available tests for the requested device and runs them"""

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
        """

        module = import_module('.' + str(test_name.stem), 'Tests.' + device.family)
        return module.test(device)

    test_path = Path.cwd().parent / 'Tests' / device.family
    test_results = []

    for test_name in list(test_path.glob('[!__]*.py')):
        test_results.append(import_test(device, test_name))

    return test_results