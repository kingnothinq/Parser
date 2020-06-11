# -*- coding: utf-8 -*-

import logging
from importlib import import_module
from time import time
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
    """
    #Fix for Apache (httpd.service)
    httpd_location = '/var/www/html/parser/www/'
    test_path = Path.cwd() / httpd_location / 'scripts' / 'tests' / str.lower(device.family)
    """
    test_results = []

    time_all_start = time()
    for test_name in list(test_path.glob('[!__]*.py')):
        time_start = time()
        test_results.append(import_test(device, test_name))
        time_end = time()
        logger.debug(f'Test "*/{device.family}/{test_name.stem}", Elapsed Time: {time_end - time_start}')
    time_all_stop = time()
    logger.info(f'Tests finished, Elapsed Time: {time_all_stop - time_all_start}')

    return test_results


logger = logging.getLogger('logger.dc_tester')