# -*- coding: utf-8 -*-

import logging
from time import time


def timer(function):
    """Estimate time"""
    def wrapper():
        time_start = time()
        created_report = function()
        time_end = time()
        logger.info(f'Report prepared, Elapsed Time: {time_end - time_start}')
        return created_report
    return wrapper


@timer
def jira():
    """Create an error report. Return 5 values in accordance with create_report()."""

    message = 'This is not a valid diagnostic card. Please analyze it manually.'
    return None, None, None, None, None, message


@timer
def web():
    pass


@timer
def cli():
    pass


logger = logging.getLogger('logger.report_error')