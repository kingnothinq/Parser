# -*- coding: utf-8 -*-

import logging
from re import search


def test(device):
    """Check Ethernet interfaces."""

    results = []

    for interface in device.ethernet_status.keys():

        # CRC errors
        if int(device.ethernet_status[interface]['Rx CRC']) > 0 \
                or int(device.ethernet_status[interface]['Tx CRC']) > 0:
            results.append(f'CRC Errors detected on the {interface} interface. '
                          f'Please check patch-cords, cables, crimps, '
                          f'IDU, grounding, Ethernet ports.')

        # Ethernet statuses
        if device.ethernet_status[interface]['Status'] == 'UP' \
                and device.ethernet_status[interface]['Duplex'] != 'Full-duplex' \
                and device.ethernet_status[interface]['Negotiation'] == 'Auto':
            results.append(f'The {interface} interface works in '
                          f'the {device.ethernet_status[interface]["Duplex"]} mode. '
                          f'Please check it.')

    # Wire link flapping
    flap_counter = 0
    ld_previous = False
    ld_index = 0
    for index, line in enumerate(device.dc_list):
        pattern = search(r'(ge0|ge1|sfp) link down', line)
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
            results.append(f'The {flap_interface} interface is flapping. Please check it.')

    result = list(set(result))
    if results:
        logger.info('Ethernet test failed')
        return ('Ethernet issues', results)
    else:
        logger.info('Ethernet test passed')
        pass


logger = logging.getLogger('logger.xg_ethernet_check')