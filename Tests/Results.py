#!/usr/bin/python
# -*- coding: utf-8 -*-

import importlib
from pathlib import Path


def tests(device):

    if ("H11" in device.firmware) or ("H08" in device.firmware):
        pass



    if "H12" in device.firmware:

        return ['XG!!!!','123']

    if "H18" in device.firmware:

        return ['Quanta!!!!','123']

def dynamic_import():
    return importlib.import_module('blabla')
dynamic_import().bla()


"""

        import Tests.R5000.abnormal as Abnormal
        import Tests.R5000.rfdrops as RFDrops

        Abnormal.test(device), RFDrops.test(device)

        return Abnormal.test(device), RFDrops.test(device)
"""