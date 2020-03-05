#!/usr/bin/python
# -*- coding: utf-8 -*-

from pathlib import Path
from re import search

import dcard_parser as dparser
import dcard_reporter as dreporter
import tests.run_tests as dtester


def get_dc_string(dc_path):
    """Open a diagnostic card as a list of strings."""

    with open(dc_path, encoding='utf-8', errors='ignore') as dcard:
        return dcard.read()


def get_dc_list(dc_path):
    """Open a diagnostic card as a list of strings."""

    with open(dc_path, encoding='utf-8', errors='ignore') as dcard:
        return dcard.readlines()

if __name__ == "__main__":

    list_of_dcards = list((Path.cwd() / 'dcards').glob('*.txt'))

    counter = 0

    for dc_path in list_of_dcards:

        #print(dc_path)

        if True:
            # pass
            # try:
            # Open a diagnostic card and handle it following the model
            dc_string = get_dc_string(dc_path)
            dc_list = get_dc_list(dc_path)

            # InfiMux
            if search(r'#\sR5000\sWANFleX\sH09', dc_string) is not None:
                iwmux = dparser.parse_iwmux(dc_string, dc_list)
                report = dreporter.create_report(iwmux, dtester.run_tests(iwmux), dc_path)
                # dreporter.write_report(report, iwmux.serial_number)
                # dreporter.debug_report(report)
                counter += 1

            # R5000 series
            elif search(r'#\sR5000\sWANFleX\sH(01|02|03|04|05|06|07|08|11)', dc_string) is not None:
                r5000 = dparser.parse_r5000(dc_string, dc_list)
                report = dreporter.create_report(r5000, dtester.run_tests(r5000), dc_path)
                #dreporter.write_report(report, r5000.serial_number)
                dreporter.debug_report(report)
                counter += 1

            # XG series
            elif search(r'#\sXG\sWANFleX\sH12', dc_string) is not None:
                xg = dparser.parse_xg(dc_string, dc_list)
                report = dreporter.create_report(xg, dtester.run_tests(xg), dc_path)
                #dreporter.write_report(report, xg.serial_number)
                dreporter.debug_report(report)
                counter += 1

            # Quanta series
            elif search(r'#\sOCTOPUS-PTP\sWANFleX\sH18', dc_string) is not None:
                quanta = dparser.parse_quanta(dc_string, dc_list)
                report = dreporter.create_report(quanta, dtester.run_tests(quanta), dc_path)
                #dreporter.write_report(report, quanta.serial_number)
                dreporter.debug_report(report)
                counter += 1
            else:
                raise

        """
        except:
            report = dreporter.error_report(dc_path)
            dreporter.debug_report(report)

        finally:
            dreporter.jira_report(report)
        """


    print('\nCounter ', counter)