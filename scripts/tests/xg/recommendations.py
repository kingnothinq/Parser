#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search


def test(device):
    """Not important or not necessary recommendations"""

    result = []

    # Check TP feature (It should be disabled due to a bug)
    if device.settings['Traffic prioritization'] == 'Enabled':
        result.append('* This is not an exact QoS feature. '
                      'It is recommended to disable it due the bug (XG-1164).')

    # Check Antenna Gain
    if search(r'Antenna Gain not found in license', device.dc_string) is not None:
        result.append('* Antenna Gain not found in the license. '
                      'Please set this parameter via CLI (xg -antenna-gain <gain_dBm>).')

    if len(device.panic) > 0:
        return '\nRecommendations: \n' + '\n'.join(result)
    else:
        pass