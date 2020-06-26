# -*- coding: utf-8 -*-

import logging
from re import search


def test(device):
    """Check QoS."""

    result = []

    pattern_1 = search(r'qm ch201 max=(\d+)\s+cur \d+ \(max \d+\), '
                       r'pps \d+ \(max \d+\) \(curQL=\d+ maxQL=\d+\)\s+packets'
                       r' \d+ \(dropped (\d+)\)', device.dc_string)
    pattern_2 = search(r'qm ch202 max=(\d+)\s+cur \d+ \(max \d+\), '
                       r'pps \d+ \(max \d+\) \(curQL=\d+ maxQL=\d+\)\s+packets'
                       r' \d+ \(dropped (\d+)\)', device.dc_string)
    if pattern_1 is not None or pattern_2 is not None:
        qos_lic_rx = [int(pattern_1.group(1)), int(pattern_1.group(2))]
        qos_lic_tx = [int(pattern_2.group(1)), int(pattern_2.group(2))]
        qos_lic = [qos_lic_rx[0] + qos_lic_tx[0], qos_lic_rx[1] + qos_lic_tx[1]]
        if qos_lic[1]:
            result.append(f'* Packet drops ({qos_lic[1]}) caused by the license restriction detected. '
                          f'Please upgrade the license to unlock full capacity. '
                          f'The current limitation is {qos_lic[0]} kbps.')

    channel_drops = []
    for channel, status in device.qos_status.items():
        if int(status['Drops']):
            if status['Prio']:
                channel = f'{channel} ({status["Prio"]})'
            channel_drops.append(channel)
    result.append(f'* Packet drops detected in the queues {", ".join(channel_drops)} of the radio module. '
                  f'Please check the QoS settings.')

    result = list(set(result))
    if result:
        logger.info('QoS test failed')
        return ('QoS issues', result)
    else:
        logger.info('QoS test passed')
        pass

logger = logging.getLogger('logger.r5000_qos_check')