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

    with open("F:\Parser\Tests\Results.py", 'ar') as file:
        for line in file:
            if "if (\"H11\" in device.firmware) or (\"H08\" in device.firmware):" in line:
                print(line)
            #print(line)
            pass

actualize()



"""
открыть файл
найти строку
внести изменения
перезаписать файл
def result_export(serial_number, model, results):
    with open(("F:\Parser\Report\{}_result.txt".format(serial_number)), 'w') as result:
        result.write("Serial Number is {}\nModel is {}\n".format(serial_number, model))
        result.write("Test results:\n")
        for problem in results:
            result.write(problem + "\n")
"""