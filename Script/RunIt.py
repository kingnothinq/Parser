#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import Parser
import Tests.Results as Results

if __name__ == "__main__":

    def get_rawd_card(dcardpath):
        with open(dcardpath) as dcard:
            return (dcard.read().split('\n'))


    def result_export(serial_number, model, results, card):
        with open(("F:\Parser\Report\{}_result from the card {}.txt".format(serial_number, card)), 'w') as result:
            result.write("Serial Number is {}\nModel is {}\n".format(serial_number, model))
            result.write("Test results:\n")
            for problem in results:
                result.write(problem + "\n")


    list_of_cards = os.listdir("F:\Parser\DiagnosticCard")
    for card in list_of_cards:
        print("----------------------------------------------------------------------------"
              "\nParsing diagnostic card: F:\Parser\DiagnosticCard\\{}"
              "\n----------------------------------------------------------------------------"
              .format(card))

        rawdcard = get_rawd_card("F:\Parser\DiagnosticCard\\" + card)
        for line in rawdcard:
            if ("WANFleX H08" in line) or ("WANFleX H11" in line):
                R5000 = Parser.parse_R5000(rawdcard)
                print("Serial Number is {}\nModel is {}\n".format(R5000.serial_number, R5000.model))
                print("Test results:")
                result_export(R5000.serial_number, R5000.model, Results.tests(R5000), card)
                for problem in Results.tests(R5000):
                    print(problem)
                break

            elif "WANFleX H12" in line:
                XG = Parser.parse_XG(rawdcard)
                print("Serial Number is {}\nModel is {}\n".format(XG.serial_number, XG.model))
                print("Test results:")
                result_export(XG.serial_number, XG.model, Results.tests(XG), card)
                for problem in Results.tests(XG):
                    print(problem)
                break

            elif "WANFleX H18" in line:
                Quanta = Parser.parse_Quanta(rawdcard)
                print("Serial Number is {}\nModel is {}\n".format(Quanta.serial_number, Quanta.model))
                print("Test results:")
                result_export(Quanta.serial_number, Quanta.model, Results.tests(Quanta), card)
                for problem in Results.tests(Quanta):
                    print(problem)
                break