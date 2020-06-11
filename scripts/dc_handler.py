# -*- coding: utf-8 -*-

import logging

from scripts.parsers.dc_parser import get_result
from scripts.tests.dc_tester import run_tests
from scripts.reports.dc_reporter import create_report, create_report_error


def analyze(dc_name, dc_file, dc_source):
    """Handle a diagnostic card."""

    try:
        if dc_source[0] == 'jira':
            dc_string = dc_file.read().decode('utf-8')
            dc_list = list(map(lambda x: x + '\n', dc_string.split('\n')))
        else:
            with open(dc_file) as text:
                dc_string = text.read()
            dc_list = list(map(lambda x: x + '\n', dc_string.split('\n')))
    except:
        logger.critical('Wrong file format or encoding')

    # Create a class instance
    device = get_result(dc_string, dc_list, dc_name, dc_source)

    # Perform tests and create report
    if device is None:
        report = create_report_error(dc_source)
    else:
        tests = run_tests(device)
        report = create_report(device, tests, dc_source)

    return report


logger = logging.getLogger('logger.dc_handler')