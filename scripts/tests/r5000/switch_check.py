#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search


def test(device):
    """Check a built-in switch."""

    result = []

    pattern = int(search(r'DB Records: \d+\/\d+ \(\d+%\), max: \d+, overflows: (\d+)', device.dc_string).group(1))
    if pattern:
        result.append('* Overflow of MAC-table detected. '
                      'The default number of records in the MAC table is 5000.')

    pattern = search(r'==!\s+(?P<ID>\d+)\s+'
                     r'(?P<Unicast>\d+)\s+'
                     r'(?P<Bcast>\d+)\s+'
                     r'(?P<Flood>\d+)\s+'
                     r'(?P<STPL>\d+)\s+'
                     r'(?P<UNRD>\d+)\s+'
                     r'(?P<FRWL>\d+)\s+'
                     r'(?P<LOOP>\d+)\s+'
                     r'(?P<DISC>\d+)\s+'
                     r'(?P<BACK>\d+)', device.dc_string)
    print(pattern.group('Unicast'))

    if result:
        return '\nEthernet issues: \n' + '\n'.join(result)
    else:
        pass