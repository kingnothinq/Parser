#!/usr/bin/python
# -*- coding: utf-8 -*-

from ftplib import FTP
from re import search, findall


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
    latest_firmware = []
    for version in firmwares:
        ftp_firmware = findall(r'h18_((\d+)\.(\d+)\.(\d+))\.bin', version)[0]
        ftp_firmware = [ftp_firmware[1], ftp_firmware[2], ftp_firmware[3]]
        latest_firmware.append(ftp_firmware)
    latest_firmware.sort()
    latest_firmware = '.'.join(latest_firmware[-1])
    ftp_path = 'ftp://ftp.infinet.ru/pub/Firmware/octopus/h18/_{}.bin'.format(latest_firmware)
    if current_version != latest_firmware:
        result.append('* The current firmware version ({}) is too old. '
                      'Please update it. '
                      'The latest version {} can be downloaded '
                      'from our FTP server ({}).'
                      .format(current_version, latest_firmware, ftp_path))

    if len(result) > 0:
        return '\nRecommendations: \n' + '\n'.join(result)
    else:
        pass