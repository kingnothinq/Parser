#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search


def test(device):
    """Check Ethernet interfaces."""

    result = []

    for interface in device.ethernet_status.keys():

        # Check CRC errors
        if int(device.ethernet_status[interface]['Rx CRC']) > 0 \
                or int(device.ethernet_status[interface]['Tx CRC']) > 0:
            result.append('* CRC Errors detected on the {} interface. '
                          'Please check patch-cords, cables, crimps, '
                          'IDU, grounding, Ethernet ports.'
                          .format(interface))

        # Check Ethernet statuses
        if device.ethernet_status[interface]['Status'] == 'UP' \
                and device.ethernet_status[interface]['Duplex'] != 'Full-duplex' \
                and device.ethernet_status[interface]['Negotiation'] == 'Auto':
            result.append('* The {} interface works in the {} mode. '
                          'Please check it.'
                          .format(interface, device.ethernet_status[interface]['Duplex']))

    # Check flaps
    flap_counter = 0
    ld_previous = False
    for line in device.dc_list:
        pattern = search(r'(eth0|eth1) link down', line)
        if pattern is not None:
            ld_previous = True
            ld_port = pattern.group(1)
        pattern = search(r'(eth0|eth1) media changed', line)
        if pattern is not None and ld_previous and ld_port == pattern.group(1):
            flap_counter += 1
        if flap_counter > 3:
            result.append('* The {} interface is flapping. '
                          'Please check it.'.format(pattern.group(1)))
            break

    if result:
        return '\nEthernet issues: \n' + '\n'.join(result)
    else:
        pass