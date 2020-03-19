#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import findall, search


def test(device):
    """Check ethernet interfaces."""

    ethernet = device.ethernet_status['ge0']
    result = []

    #Check CRC errors
    if int(ethernet['CRC']) > 0:
        result.append('* CRC Errors detected on the ge0 interface. '
                      'Please check patch-cords, cables, crimps, '
                      'IDU, grounding, Ethernet ports.')

    #Check Ethernet statuses
    if ethernet['Status'] == 'UP' and ethernet['Duplex'] != 'Full-duplex' and ethernet['Negotiation'] == 'Auto':
        result.append('* The ge0 interface works in the {} mode. '
                      'Please check it.'.format(ethernet['Duplex']))

    #Check flaps
    flap_counter = 0
    ld_previous = False
    for line in device.dc_list:
        pattern = search(r'(ge0): link down', line)
        if pattern is not None:
            ld_previous = True
        pattern = search(r'(ge0): media changed', line)
        if pattern is not None and ld_previous == True:
            flap_counter += 1
        if flap_counter > 3:
            result.append('* The {} interface is flapping. '
                          'Please check it.'.format(pattern.group(1)))
            break

    #Runt bug
    pattern = findall(r'(Runt len errors|Frame length errors)\s+(\d+)', device.dc_string)
    if ethernet['Duplex'] == 'Full-duplex' and int(pattern[1][1]) > 0:
        result.append('* Runt len errors detected on the ge0 interface. '
                      'A runt frame is an Ethernet frame that is less '
                      'than the IEEE 802.3\'s minimum length of 64 octets. '
                      'Runt frames are most commonly caused by collisions; '
                      'other possible causes are a malfunctioning network card, '
                      'buffer underrun, duplex mismatch or software issues. '
                      'If everything is ok with the cables and interfaces, '
                      'it may be a bug (IOCT-XXX).')

    if result:
        return '\nEthernet issues: \n' + '\n'.join(result)
    else:
        pass
