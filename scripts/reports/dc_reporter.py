# -*- coding: utf-8 -*-

from importlib import import_module
import logging


def create_report(device, tests, dc_source):
    """Look for all available report templates for the requested device and run them.
    Return a text report.
    """

    def import_report(device, tests, dc_source):
        """Dynamic modules (reports) import. Import only modules starts from "report_*"

                A module must follow the next template:
                def parse(dc_string, dc_list):
                    #parse settings
                    #parse radio
                    #parse ethernet
                    #etc...
                    return tuple of objects
        """

        module = import_module(f'.report_{str.lower(device.family)}', 'scripts.reports')

        #Filter empty test reports
        if not list(filter(None, tests)):
            tests = ['Everything is ok']
        else:
            tests = list(filter(None, tests))

        #Create a report in accordance with the source of the diagnostic card
        if dc_source[0] == 'jira':
            return module.jira(device, tests)
        elif dc_source[0] == 'web':
            return module.web(device, tests)
        elif dc_source[0] == 'cli':
            return module.cli(device, tests)

    return import_report(device, tests, dc_source)


def create_report_error(dc_source):
    """Look for all available parsers for the requested device and run them.
    Return a class with filled arguments or an error.
    """

    import scripts.reports.report_error as module

    # Create a report in accordance with the source of the diagnostic card
    if dc_source[0] == 'jira':
        return module.jira()
    elif dc_source[0] == 'web':
        return module.web()
    elif dc_source[0] == 'cli':
        return module.cli()


logger = logging.getLogger('logger.dc_reporter')