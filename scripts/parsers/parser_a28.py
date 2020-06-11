# -*- coding: utf-8 -*-

import logging
from time import time


def timer(function):
    def wrapper(dc_string, dc_list):
        time_start = time()
        created_class = function(dc_string, dc_list)
        time_end = time()
        logger.info(f'Diagnostic card parsed, Elapsed Time: {time_end - time_start}')
        return created_class
    return wrapper


@timer
def parse(dc_string, dc_list):

    pass


logger = logging.getLogger('logger.parser_a28')