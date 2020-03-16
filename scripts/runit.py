#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search, split

import scripts.dcard_parser as dc_parser
import scripts.dcard_reporter as dc_reporter
import scripts.tests.run_tests as dc_tester


def analyze(dc, dc_name):
    """Handle a diagnostic card."""

    dc_string = dc.read().decode("utf-8")
    dc_list = split(r'(.*\n)', dc_string)

    try:
        # InfiMux (not supported at this moment)
        if search(r'#\sR5000\sWANFleX\sH09', dc_string) is not None:
            iwmux = dc_parser.parse_iwmux(dc_string, dc_list)
            report = dc_reporter.create_report(iwmux, dc_tester.run_tests(iwmux),
                                               dc_name)  # dc_reporter.write_report(report, iwmux.serial_number)  # dc_reporter.debug_report(report)

        # R5000 series
        elif search(r'#\sR5000\sWANFleX\sH(01|02|03|04|05|06|07|08|11)', dc_string) is not None:
            r5000 = dc_parser.parse_r5000(dc_string, dc_list)
            report = dc_reporter.create_report(r5000, dc_tester.run_tests(r5000),
                                               dc_name)  # dc_reporter.write_report(report, r5000.serial_number)  # dc_reporter.debug_report(report)

        #XG series
        elif search(r'#\sXG\sWANFleX\sH12', dc_string) is not None:
            xg = dc_parser.parse_xg(dc_string, dc_list)
            report = dc_reporter.create_report(xg, dc_tester.run_tests(xg),
                                               dc_name)  # dc_reporter.write_report(report, xg.serial_number)  #dc_reporter.debug_report(report)

        #Quanta series
        elif search(r'#\sOCTOPUS-PTP\sWANFleX\sH18', dc_string) is not None:
            quanta = dc_parser.parse_quanta(dc_string, dc_list)
            report = dc_reporter.create_report(quanta, dc_tester.run_tests(quanta),
                                               dc_name)  # dc_reporter.write_report(report, quanta.serial_number)  # dc_reporter.debug_report(report)
        else:
            raise
    except:
        report = dc_reporter.error_report(dc_name)  # dc_reporter.debug_report(report)

    finally:
        return '\n'.join(report)