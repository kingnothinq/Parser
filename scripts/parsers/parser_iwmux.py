# -*- coding: utf-8 -*-

import logging
from time import time


def timer(function):
    """Estimate time"""
    def wrapper(dc_string, dc_list):
        time_start = time()
        function_result = function(dc_string, dc_list)
        time_end = time()
        logger.info(f'Diagnostic card parsed, Elapsed Time: {time_end - time_start}')
        return function_result
    return wrapper


@timer
def parse(dc_string, dc_list):
    pass


logger = logging.getLogger('logger.parser_iwmux')