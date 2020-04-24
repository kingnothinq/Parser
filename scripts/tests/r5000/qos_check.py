#!/usr/bin/python
# -*- coding: utf-8 -*-

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
            result.append('* Packet drops ({}) caused by the license restriction detected. '
                          'Please upgrade the license to unlock full capacity. '
                          'The current limitation is {} kbps.'.format(qos_lic[1], qos_lic[0]))

    for channel, status in device.qos_status.items():
        if int(channel.replace('q', '')) > 16 and int(status['Drops']):
            result.append('* Packet drops ({}) in the channel {} of the radio module. '
                          'Please check the QoS settings.'.format(status['Drops'], channel))

    result = list(set(result))
    if result:
        return '\nQoS issues: \n' + '\n'.join(result)
    else:
        pass
