#!/usr/bin/python
# -*- coding: utf-8 -*-

from pathlib import Path
from re import search

from jira import JIRA

import dcard_parser as dparser
import dcard_reporter as dreporter
import tests.run_tests as dtester


def get_dc_string(*args):
    """Open a diagnostic card as a list of strings."""

    with open(dc_path) as dcard:
        return dcard.read()


def get_dc_list(*args):
    """Open a diagnostic card as a list of strings."""

    with open(dc_path) as dcard:
        return dcard.readlines()


if __name__ == "__main__":

    # Find all diagnostic cards in the folder
    list_of_dcards = list((Path.cwd() / 'dcards').glob('*.txt'))

    for dc_path in list_of_dcards:

        # Open a diagnostic card and handle it following the model
        dc_string = get_dc_string(dc_path)
        dc_list = get_dc_list(dc_path)

        try:
            # R5000 series
            if search(r'#\sR5000\sWANFleX\sH(08|11)', dc_string) is not None:
                r5000 = dparser.parse_r5000(dc_string, dc_list)
                report = dreporter.create_report(r5000, dtester.run_tests(r5000), dc_path)
                #dreporter.write_report(report, r5000.serial_number)
                dreporter.debug_report(report)

            # XG series
            elif search(r'#\sXG\sWANFleX\sH12', dc_string) is not None:
                xg = dparser.parse_xg(dc_string, dc_list)
                report = dreporter.create_report(xg, dtester.run_tests(xg), dc_path)
                #dreporter.write_report(report, xg.serial_number)
                dreporter.debug_report(report)

            # Quanta series
            elif search(r'#\sOCTOPUS-PTP\sWANFleX\sH18', dc_string) is not None:
                quanta = dparser.parse_quanta(dc_string, dc_list)
                report = dreporter.create_report(quanta, dtester.run_tests(quanta), dc_path)
                #dreporter.write_report(report, quanta.serial_number)
                dreporter.debug_report(report)
            else:
                raise

        except:
            report = dreporter.error_report(dc_path)
            dreporter.debug_report(report)

        finally:
            """
            jira_options = {'server': 'https://jira.infinet.ru/'}

            login = input('Login: ')
            password = input('Password: ')

            jira = JIRA(options=jira_options, basic_auth=(login, password))

            comment = jira.add_comment('DESK-53647', '\n'.join(report))
            """