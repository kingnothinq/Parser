#!/usr/bin/python
# -*- coding: utf-8 -*-

def test(device):
    """Check ethernet interfaces"""

    result = []

    for interface in device.ethernet_status.keys():
        if int(device.ethernet_status[interface]['Rx CRC']) > 0 \
                or int(device.ethernet_status[interface]['Tx CRC']) > 0:
            result.append('* CRC Errors detected on the {} interface. '
                          'Please check patch-cords, cables, crimps, '
                          'IDU, grounding, Ethernet ports.\n'.format(interface))
        if device.ethernet_status[interface]['Status'] == 'UP' \
                and device.ethernet_status[interface]['Duplex'] != 'Full-duplex' \
                and device.ethernet_status[interface]['Negotiation'] == 'Auto':
            result.append('* The {} interface works in the {} mode. '
                          'Please check it.\n'.format(interface, device.ethernet_status[interface]['Duplex']))

    if len(result) > 0:
        return ' '.join(result)
    else:
        pass
