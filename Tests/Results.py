#!/usr/bin/python
# -*- coding: utf-8 -*-

import os


def test(device):
    if ("H11" in device.firmware) or ("H08" in device.firmware):


        import Tests.R5000.Abnormal as Abnormal
        import Tests.R5000.RFDrops as RFDrops

        return Abnormal.test(device), RFDrops.test(device)

    if "H12" in device.firmware:
        return ['XG!!!!','123']

    if "H18" in device.firmware:
        return ['Quanta!!!!','123']
