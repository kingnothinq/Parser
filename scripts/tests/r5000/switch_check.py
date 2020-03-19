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

    sw_status = device.switch_status
    for id in sw_status.keys():
        if sw_status[id]['Bcast'] > 9999990 or sw_status[id]['LOOP'] > 10000:
            result.append('* Perhaps there is a loop in the switch group {}. '
                          'Please check it.'.format(id))

    if result:
        return '\nEthernet issues: \n' + '\n'.join(result)
    else:
        pass
