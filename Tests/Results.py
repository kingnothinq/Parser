#!/usr/bin/python
# -*- coding: utf-8 -*-

import os


def test(device):
    if ("H11" in device.firmware) or ("H08" in device.firmware):
        # R5000_tests = os.listdir("F:\Parser\Tests\R5000")

        import Tests.R5000.Abnormal as Abnormal
        import Tests.R5000.RFDrops as RFDrops

        return Abnormal.abnormal(device), RFDrops.drops(device)

    if "H12" in device.firmware:
        return ['XG!!!!','123']

    if "H18" in device.firmware:
        return ['Quanta!!!!','123']
