# -*- coding: utf-8 -*-

import logging
from time import time


def timer(function):
    """Estimate time"""
    def wrapper(dc_string, dc_list):
        time_start = time()
        created_report = function(dc_string, dc_list)
        time_end = time()
        logger.info(f'Report prepared, Elapsed Time: {time_end - time_start}')
        return created_report
    return wrapper


@timer
def jira():
    pass

def web():
    pass

def cli():
    pass


logger = logging.getLogger('logger.report_q70')