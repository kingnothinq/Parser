#!/usr/bin/python
# -*- coding: utf-8 -*-

from pathlib import Path
from re import search

import dcard_parser as dparser
import tests.run_tests as dtester


def get_dc_string(*args):
    """Open a diagnostic card as a list of strings"""
    with open(dc_path) as dcard:
        return dcard.read()


def get_dc_list(*args):
    """Open a diagnostic card as a list of strings"""
    with open(dc_path) as dcard:
        return dcard.readlines()


def write_report(report_text, serial_number):
    """Save report"""
    report_name = 'diagcard_{}_report.txt'.format(serial_number)
    report_path = Path.joinpath(Path.cwd() / 'reports', report_name)

    if Path.is_dir(report_path.parent) is False:
        Path.mkdir(report_path.parent)

    report_name_counter = 0
    while Path.exists(report_path):
        report_name_counter += 1
        report_name = 'diagcard_{}_report_{}.txt'.format(
            serial_number, report_name_counter)
        report_path = Path.joinpath(Path.cwd() / 'reports', report_name)

    with open(report_path, 'w') as report:
        for line in report_text:
            report.write(line)


def debug_report(report_text):
    """Print report in console"""
    for line in report_text:
        print(line)


def create_report(serial_number, model, tests_report, *args):
    """Create report"""
    message_1 = '\nParsing diagnostic card: {}'.format(dc_path)
    message_1_complete = '{}{}\n{}\n'.format('-' * len(message_1), message_1,
                                             '-' * len(message_1))
    message_2 = 'Serial Number is {}\nModel is {}\n'.format(serial_number, model)
    message_3 = 'Test results:\n'
    message_4 = 'The {} device is fine'.format(serial_number)

    if not list(filter(None, tests_report)):
        report_text = [message_1_complete, message_2, message_3] + [message_4]
    else:
        report_text = [message_1_complete, message_2, message_3] + list(
            filter(None, tests_report))

    return report_text


if __name__ == '__main__':

    # Find all diagnostic cards in the folder
    list_of_dcards = list((Path.cwd() / 'dcards').glob('*.txt'))

    for dc_path in list_of_dcards:

        # Open a diagnostic card and handle it following the model
        dc_string = get_dc_string(dc_path)
        dc_list = get_dc_list(dc_path)

        # R5000 series
        if search(r'#\sR5000\sWANFleX\sH(08|11)', dc_string) is not None:
            r5000 = dparser.parse_r5000(dc_string, dc_list)
            report = create_report(r5000.serial_number, r5000.model, dtester.run_tests(r5000), dc_path)
            # write_report(report, r5000.serial_number)
            debug_report(report)

        # XG series
        elif search(r'#\sXG\sWANFleX\sH12', dc_string) is not None:
            xg = dparser.parse_xg(dc_string, dc_list)
            report = create_report(xg.serial_number, xg.model, dtester.run_tests(xg), dc_path)
            write_report(report, xg.serial_number)
            debug_report(report)

        # Quanta series
        elif search(r'#\sOCTOPUS-PTP\sWANFleX\sH18', dc_string) is not None:
            quanta = dparser.parse_quanta(dc_string, dc_list)
            report = create_report(quanta.serial_number, quanta.model, dtester.run_tests(quanta), dc_path)
            # write_report(report, quanta.serial_number)
            debug_report(report)
