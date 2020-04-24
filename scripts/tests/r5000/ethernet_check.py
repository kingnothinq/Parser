#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search


def test(device):
    """Check Ethernet interfaces."""

    result = []

    for interface in device.ethernet_status.keys():

        #Check CRC errors
        if int(device.ethernet_status[interface]['Rx CRC']) > 0 or int(device.ethernet_status[interface]['Tx CRC']) > 0:
            result.append('* CRC Errors detected on the {} interface. '
                          'Please check patch-cords, cables, crimps, '
                          'IDU, grounding, Ethernet ports.'.format(interface))

        #Check Ethernet statuses
        if device.ethernet_status[interface]['Status'] == 'UP' and device.ethernet_status[interface][
            'Duplex'] != 'Full-duplex' and device.ethernet_status[interface]['Negotiation'] == 'Auto':
            result.append('* The {} interface works in the {} mode. '
                          'Please check it.'.format(interface, device.ethernet_status[interface]['Duplex']))

    #Check flaps
    flap_counter = 0
    ld_previous = False
    ld_index = 0
    for index, line in enumerate(device.dc_list):
        pattern = search(r'(eth0|eth1) link down', line)
        if pattern is not None:
            ld_index = index + 1
            flap_interface = pattern.group(1)
            ld_text = '{} media changed'.format(flap_interface)
            ld_previous = True
            continue
        if ld_previous:
            pattern = search(ld_text, line)
            if pattern is not None and index == ld_index:
                flap_counter += 1
        else:
            ld_previous = False
        if flap_counter > 4:
            result.append('* The {} interface is flapping. '
                          'Please check it.'.format(flap_interface))

    result = list(set(result))
    if result:
        return '\nEthernet issues: \n' + '\n'.join(result)
    else:
        pass
