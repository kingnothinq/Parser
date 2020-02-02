#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

def list_of_tests():

    series = []
    for folder in os.listdir("F:\Parser\Tests"):
        if (".py" not in folder) and ("__" not in folder):
            series.append(folder)

    new_tests = dict.fromkeys(series,[])

    for model in series:
        temp = []
        for test in os.listdir("F:\Parser\Tests\\" + model):
            if (".py" in test) and ("__" not in test):
                temp.append(test)
        new_tests[model] = temp

    return new_tests

def actualize():

    print(list(list_of_tests().keys()))

    with open("F:\Parser\Tests\Results.py", 'r') as file:
        file = file.readlines()

    newfile = []
    for line in file:
        if "if (\"H11\" in device.firmware) or (\"H08\" in device.firmware):" in line:
            newfile.append(line + "\n\n        123\n")
        if "if \"H12\" in device.firmware:" in line:
            newfile.append(line + "\n\n        123\n")
        if "if \"H18\" in device.firmware:" in line:
            newfile.append(line + "\n\n        123\n")
        else:
            newfile.append(line)

    with open("F:\Parser\Tests\Results.py", 'w') as file:
        file.writelines(newfile)

actualize()



"""
открыть файл
найти строку
внести изменения
перезаписать файл

new.file(append)
else!!
def result_export(serial_number, model, results):
    with open(("F:\Parser\Report\{}_result.txt".format(serial_number)), 'w') as result:
        result.write("Serial Number is {}\nModel is {}\n".format(serial_number, model))
        result.write("Test results:\n")
        for problem in results:
            result.write(problem + "\n")
            
    def get_rawd_card(dcardpath):
        with open(dcardpath) as dcard:
            return (dcard.read().split('\n'))
"""