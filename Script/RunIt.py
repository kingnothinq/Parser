#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from pathlib import Path
import dcard_parser as dparser
import Tests.results as results

if __name__ == "__main__":

    def get_dcard_raw(dcard_path):
        """Open a diagnostic card as a list of strings"""
        with open(dcard_path) as dcard:
            return (dcard.read().split('\n'))


    def create_txt_report(serial_number, model, dcard_report, dcard_name):
        """Save report as a file"""
        with open(("F:\Parser\Report\{}_result from the card {}.txt".format(serial_number, dcard_name)), 'w') as report:
            report.write("Serial Number is {}\nModel is {}\n".format(serial_number, model))
            report.write("Test results:\n")
            for problem in dcard_report:
                report.write(problem + "\n")

    #Find all diagnostic cards in the folder
    list_of_dcards = os.listdir("F:\Parser\DiagnosticCard")
    for dcard_name in list_of_dcards:
        print("----------------------------------------------------------------------------"
              "\nParsing diagnostic card: F:\Parser\DiagnosticCard\\{}"
              "\n----------------------------------------------------------------------------"
              .format(dcard_name))

        #Open a diagnostic card and handle it following the model
        dcard_raw = get_dcard_raw("F:\Parser\DiagnosticCard\\" + dcard_name)
        for line in dcard_raw:
            if ("WANFleX H08" in line) or ("WANFleX H11" in line):
                #R5000 series
                r5000 = dparser.parse_r5000(dcard_raw)
                print("Serial Number is {}\nModel is {}\n".format(r5000.serial_number, r5000.model))
                print("Test results:")
                create_txt_report(r5000.serial_number, r5000.model, results.tests(r5000), dcard_name)
                for problem in results.tests(r5000):
                    print(problem)
                break

            elif "WANFleX H12" in line:
                #XG and XG1000 series
                xg = dparser.parse_xg(dcard_raw)
                print("Serial Number is {}\nModel is {}\n".format(xg.serial_number, xg.model))
                print("Test results:")
                create_txt_report(xg.serial_number, xg.model, results.tests(xg), dcard_name)
                for problem in results.tests(xg):
                    print(problem)
                break

            elif "WANFleX H18" in line:
                #Quanta 5 series
                quanta = dparser.parse_quanta(dcard_raw)
                print("Serial Number is {}\nModel is {}\n".format(quanta.serial_number, quanta.model))
                print("Test results:")
                create_txt_report(quanta.serial_number, quanta.model, results.tests(quanta), dcard_name)
                for problem in results.tests(quanta):
                    print(problem)
                break


