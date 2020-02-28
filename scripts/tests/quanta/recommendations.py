#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search, findall

from ftplib import FTP


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

    ftp = FTP('ftp.infinet.ru')
    ftp.login()
    firmwares = ftp.nlst('pub/Firmware/octopus/h18/')
    current_version = search(r'PTPv((\d+\.){2}(\d+))', device.firmware).group(1)
    latest_version = []
    for version in firmwares:
        ftp_firmware = search(r'h18_(\d+\.\d+\.\d+)\.bin', version)
        latest_version.append(ftp_firmware.group(1))
    latest_version.sort()
    ftp_path = 'ftp://ftp.infinet.ru/pub/Firmware/octopus/h18/_{}.bin'.format(latest_version[-1])
    if current_version != latest_version[-1]:
        result.append('* The current firmware version ({}) is old. '
                      'Please update it. '
                      'The latest version ({}) can be downloaded '
                      'from our FTP server ({}).'
                      .format(current_version, latest_version[-1], ftp_path))

    if len(result) > 0:
        return '\nRecommendations: \n' + '\n'.join(result)
    else:
        pass