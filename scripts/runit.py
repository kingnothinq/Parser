#!/usr/bin/python
# -*- coding: utf-8 -*-

from pathlib import Path
from re import search, split
import io

from werkzeug.datastructures import FileStorage

import scripts.dcard_parser as dparser
import scripts.dcard_reporter as dreporter
import scripts.tests.run_tests as dtester


def analyze(file):
    dc_string = file.read().decode("utf-8")
    dc_list = split(r'(.*\n)', dc_string)
    # dc_list = dc_string.splitline()

    print(dc_list)

    if True:
        # pass
        # try:
        # Open a diagnostic card and handle it following the model

        # InfiMux
        if search(r'#\sR5000\sWANFleX\sH09', dc_string) is not None:
            iwmux = dparser.parse_iwmux(dc_string, dc_list)
            report = dreporter.create_report(iwmux, dtester.run_tests(iwmux),
                                             dc_path)  # dreporter.write_report(report, iwmux.serial_number)  # dreporter.debug_report(report)

        # R5000 series
        elif search(r'#\sR5000\sWANFleX\sH(01|02|03|04|05|06|07|08|11)', dc_string) is not None:
            r5000 = dparser.parse_r5000(dc_string, dc_list)
            report = dreporter.create_report(r5000, dtester.run_tests(r5000), dc_path)
            # dreporter.write_report(report, r5000.serial_number)
            dreporter.debug_report(report)

        # XG series
        elif search(r'#\sXG\sWANFleX\sH12', dc_string) is not None:
            xg = dparser.parse_xg(dc_string, dc_list)
            report = dreporter.create_report(xg, dtester.run_tests(xg), dc_path)
            # dreporter.write_report(report, xg.serial_number)
            dreporter.debug_report(report)

        # Quanta series
        elif search(r'#\sOCTOPUS-PTP\sWANFleX\sH18', dc_string) is not None:
            quanta = dparser.parse_quanta(dc_string, dc_list)
            report = dreporter.create_report(quanta, dtester.run_tests(quanta), dc_path)
            # dreporter.write_report(report, quanta.serial_number)
            dreporter.debug_report(report)
        else:
            raise

    """
    except:
        report = dreporter.error_report(dc_path)
        dreporter.debug_report(report)

    finally:
        dreporter.jira_report(report)
    """