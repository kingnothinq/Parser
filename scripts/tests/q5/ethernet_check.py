# -*- coding: utf-8 -*-

import logging
from re import findall, search


def test(device):
    """Check ethernet interfaces."""

    ethernet = device.ethernet_status['ge0']
    result = []

    # CRC errors
    if int(ethernet['CRC']) > 0:
        result.append('CRC Errors detected on the ge0 interface. '
                      'Please check patch-cords, cables, crimps, '
                      'IDU, grounding, Ethernet ports.')

    # Ethernet statuses
    if ethernet['Status'] == 'up' \
            and ethernet['Duplex'] != 'Full' \
            and ethernet['Negotiation'] == 'Auto':
        result.append(f'The ge0 interface works in the {ethernet["Duplex"]}-duplex mode. '
                      f'Please check it.')

    # Wire link flapping
    flap_counter = 0
    ld_previous = False
    ld_index = 0
    for index, line in enumerate(device.dc_list):
        pattern = search(r'(ge0) link down', line)
        if pattern is not None:
            ld_index = index + 1
            flap_interface = pattern.group(1)
            ld_text = f'{flap_interface} media changed'
            ld_previous = True
            continue
        if ld_previous:
            pattern = search(ld_text, line)
            if pattern is not None and index == ld_index:
                flap_counter += 1
        else:
            ld_previous = False
        if flap_counter > 4:
            result.append(f'The {flap_interface} interface is flapping. '
                          f'Please check it.')

    # Runt bug
    pattern = findall(r'(Runt len errors|Frame length errors)\s+(\d+)', device.dc_string)
    if ethernet['Duplex'] == 'Full-duplex' and int(pattern[1][1]) > 0:
        result.append('Runt len errors detected on the ge0 interface. '
                      'A runt frame is an Ethernet frame that is less '
                      'than the IEEE 802.3\'s minimum length of 64 octets. '
                      'Runt frames are most commonly caused by collisions; '
                      'other possible causes are a malfunctioning network card, '
                      'buffer underrun, duplex mismatch or software issues. '
                      'If everything is ok with the cables and interfaces, '
                      'it may be a bug (IOCT-XXX).')

    result = list(set(result))
    if result:
        logger.info('Ethernet test failed')
        return ('Ethernet issues', result)
    else:
        logger.info('Ethernet test passed')
        pass


logger = logging.getLogger('logger.quanta_ethernet_check')