#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import findall


def test(device):
    """Not important or not necessary recommendations"""

    settings = device.settings
    result = []

    if settings['ARQ'] == 'Disabled':
        result.append('* Please enable ARQ. '
                      'It is a very useful feature.')

    if settings['Max DL MCS'] != '256-QAM-7/8' or settings['Max UL MCS'] != '256-QAM-7/8':
        result.append('* Maximum MCS is limited. '
                      'Please note the highest modulations cannot be reached.')

    pattern = findall(r'(\d{2}):(\d{2}):(\d{2})', device.uptime)
    if int(pattern[0][0]) <= 0 and int(pattern[0][1]) < 15:
        result.append('* Uptime is too short ({}). '
                      'It is recommended to wait more in order to collect more precise statistics.'
                      .format(device.uptime))

    if len(result) > 0:
        return '\nRecommendations: \n' + '\n'.join(result)
    else:
        pass