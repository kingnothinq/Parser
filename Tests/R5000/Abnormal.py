#!/usr/bin/python
# -*- coding: utf-8 -*-

def abnormal(device):
    for line in device.rawdcard:
        if "Warning: Abnormal transmit power disbalance!" in line:
            return '* Abnormal transmit power disbalance is detected. The radio module of the device {} is faulty. Please approve RMA.'.format(
                device.serial_number)
            break
