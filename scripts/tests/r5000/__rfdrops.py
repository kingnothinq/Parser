#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search


def test(device):
    for line in device.dc_list:
        pattern = search(r"\|\sq\d+\s(\(?P(\d+)\))?\s+(\d+)\s\/\s(\d+)", line)
        if pattern is not None:
            if (int(pattern.group(4)) is not 0):
                return '* Packet drops detected in the amount of {} in the queue {} of the radio channel.' \
                       ' Please check QoS settings or channel capacity.\n' \
                    .format(pattern.group(4), pattern.group(2))