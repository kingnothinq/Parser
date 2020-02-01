#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re

def names():

    new_tests = []
    series = []
    for folder in os.listdir("F:\Parser\Tests"):
        if (".py" not in folder) and ("__" not in folder):

            series.append(folder)
    #print(series)

    for model in series:
        for test in os.listdir("F:\Parser\Tests\\" + model):
            print(test)
            if (".py" in os.listdir("F:\Parser\Tests\\" + test)) and ("__" not in os.listdir("F:\Parser\Tests\\" + test)):
            """
        print(os.listdir("F:\Parser\Tests\\"+test))
        
            print(test)


def actualize_test():
    R5000_tests = os.listdir("F:\Parser\Tests\R5000")
    XG_tests = os.listdir("F:\Parser\Tests\XG")
    Quanta_tests = os.listdir("F:\Parser\Tests\Quanta")

    #print(R5000_tests)
    ##print(Quanta_tests)

    tests = os.listdir("F:\Parser\Tests")
    #print(tests)
"""
names()




#actualize_test()