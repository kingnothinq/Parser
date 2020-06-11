# -*- coding: utf-8 -*-

import logging
from re import search


def test(device):
    """Check a built-in switch."""

    result = []

    # MAC-table Overflow
    pattern = int(search(r'DB Records: \d+\/\d+ \(\d+%\), max: \d+, overflows: (\d+)', device.dc_string).group(1))
    if pattern:
        result.append('* Overflow of MAC-table detected. '
                      'The default number of records in the MAC table is 5000.')

    # Loop
    sw_status = device.switch_status
    for id in sw_status.keys():
        if sw_status[id]['Bcast'] > 9999990 or sw_status[id]['LOOP'] > 10000:
            result.append(f'* Perhaps there is a loop in the switch group {id}. '
                          f'Please check it.')

    result = list(set(result))
    if result:
        logger.info('Recommendations test failed')
        return '\nEthernet issues: \n' + '\n'.join(result)
    else:
        logger.info('Recommendations test passed')
        pass


logger = logging.getLogger('logger.r5000_switch')
