#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search


def test(device):
    for line in device.dcard_raw_text_list:
        if search(r"\|\sq\d+\s(\(?P(\d+)\))?\s+(\d+)\s\/\s(\d+)", line) is not None:
            if (int(search(r"\|\sq\d+\s(\(?P(\d+)\))?\s+(\d+)\s\/\s(\d+)", line).group(4)) is not 0):
                return '* Packet drops detected in the amount of {} in the queue {} of the radio channel. Please check QoS settings or channel capacity.\n' \
                    .format(
                    search(r"\|\sq\d+\s(\(?P(\d+)\))?\s+(\d+)\s\/\s(\d+)", line).group(4),
                    search(r"\|\sq\d+\s(\(?P(\d+)\))?\s+(\d+)\s\/\s(\d+)", line).group(2)
                )
