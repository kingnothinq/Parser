#!/usr/bin/python
# -*- coding: utf-8 -*-

from pathlib import Path
from re import search

import dcard_parser as dparser
import Tests.run_tests as dtester


if __name__ == "__main__":

    def get_dcard_raw_text_as_string(dcard_path):
        """Open a diagnostic card as a list of strings"""
        with open(dcard_path) as dcard:
            return dcard.read()

    def get_dcard_raw_text_as_list(dcard_path):
        """Open a diagnostic card as a list of strings"""
        with open(dcard_path) as dcard:
            return dcard.readlines()


    def create_report(serial_number, model, tests_report, dcard_path):
        """Create report and save it"""
        report_name = "diagcard_{}_report.txt".format(serial_number)
        report_path = Path.joinpath(Path.cwd().parent / 'Report', report_name)

        report_name_counter = 0
        while Path.exists(report_path):
            report_name_counter += 1
            report_name = "diagcard_{}_report_{}.txt".format(serial_number, report_name_counter)
            report_path = Path.joinpath(Path.cwd().parent / 'Report', report_name)

        message_1 = "\nParsing diagnostic card: {}".format(dcard_path)
        message_1_complete = "{}{}\n{}\n".format("-" * len(message_1), message_1, "-" * len(message_1))
        message_2 = str("Serial Number is {}\nModel is {}\n".format(serial_number, model))
        message_3 = "Test results:\n"
        message_4 = 'Device {} is fine'.format(serial_number)

        if not list(filter(None, tests_report)):
            report_text = [message_1_complete, message_2, message_3] + [message_4]
        else:
            report_text = [message_1_complete, message_2, message_3] + tests_report


        with open(report_path, "w") as report:
            for line in report_text:
                print(line)
                report.write(line)


    # Find all diagnostic cards in the folder
    list_of_dcards = list((Path.cwd().parent / 'DiagnosticCard').glob('*.txt'))

    for dcard_path in list_of_dcards:


        # Open a diagnostic card and handle it following the model
        dcard_raw_text_string = get_dcard_raw_text_as_string(dcard_path)
        dcard_raw_text_list = get_dcard_raw_text_as_list(dcard_path)

        # R5000 series

        if search(r"WANFleX\WH(08|11)S\d+", dcard_raw_text_string) is not None:
            R5000 = dparser.parse_R5000(dcard_raw_text_string, dcard_raw_text_list)
            create_report(R5000.serial_number, R5000.model, dtester.run_tests(R5000), dcard_path)

        # XG series

        elif search(r"WANFleX\WH12S\d+", dcard_raw_text_string) is not None:
            XG = dparser.parse_XG(dcard_raw_text_string, dcard_raw_text_list)
            create_report(XG.serial_number, XG.model, dtester.run_tests(XG), dcard_path)

        # Quanta series

        elif search(r"WANFleX\WH18S\d+", dcard_raw_text_string) is not None:
            Quanta = dparser.parse_Quanta(dcard_raw_text_string, dcard_raw_text_list)
            create_report(Quanta.serial_number, Quanta.model, dtester.run_tests(Quanta), dcard_path)


        """
        for line in dcard_raw_text:

            # R5000 series
            
            if search(r"WANFleX\WH(08|11)S\d+", line) is not None:
                R5000 = dparser.parse_R5000(dcard_raw_text)
                create_report(R5000.serial_number, R5000.model, dtester.run_tests(R5000), dcard_path)
                break


            # XG series
            if search(r"WANFleX\WH12S\d+", line) is not None:
                XG = dparser.parse_XG(dcard_raw_text)
                #print(XG.subfamily, XG.model, XG.serial_number, XG.firmware, XG.uptime, XG.rebootreason)
                #print(XG.settings)
                #print(XG.radio_status['Link status'])

                #print(XG.radio_status['Measured Distance'])

                #print(XG.radio_status['Master']['Role'])
                print(XG.radio_status['Master']['Carrier 0'])
                print(XG.radio_status['Master']['Carrier 1'])

                #print(XG.radio_status['Slave']['Role'])
                print(XG.radio_status['Slave']['Carrier 0'])
                print(XG.radio_status['Slave']['Carrier 1'])

                #print(dtester.run_tests(XG))
                #create_report(XG.serial_number, XG.model, dtester.run_tests(XG), dcard_path)
                break

            # Quanta series

            elif search(r"WANFleX\WH18S\d+", line) is not None:
                Quanta = dparser.parse_Quanta(dcard_raw_text)
                create_report(Quanta.serial_number, Quanta.model, dtester.run_tests(Quanta), dcard_path)
                break
            """

