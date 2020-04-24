#!/usr/bin/python
# -*- coding: utf-8 -*-

from ftplib import FTP
from re import findall, search


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
                      'It is recommended to wait more in order to collect more precise statistics.'.format(
                device.uptime))

    ftp = FTP('ftp.infinet.ru')
    ftp.login()
    fw_current = search(r'PTPv((\d+\.){2}(\d+))', device.firmware).group(1)
    fw_release = ftp.nlst('/pub/Firmware/octopus/h18/')
    fw_beta = []  # ftp.nlst('/pub/Firmware/beta/octopus/')
    fw_old = ftp.nlst('/pub/Firmware/old/octopus/h18/')
    firmwares = filter(lambda x: '.bin' in x, fw_release + fw_beta + fw_old)
    firmwares = [search(r'h18_(\d+\.\d+\.\d+)\.bin', fw).group(1) for fw in firmwares]
    fw_latest = sorted(firmwares, key=lambda x: [int(num) for num in x.split('.')])[-1]
    if fw_current != fw_latest:
        for fw in [fw_release, fw_beta, fw_old]:
            pattern = list(filter(lambda x: fw_latest in x, fw))
            if len(pattern) > 0:
                path_latest = 'ftp://ftp.infinet.ru{}'.format(pattern[0])
        result.append('* The current firmware version ({}) is old. '
                      'Please update it. '
                      'The latest version ({}) can be downloaded '
                      'from our FTP server ({}).'.format(fw_current, fw_latest, path_latest))

    result = list(set(result))
    if result:
        return '\nRecommendations: \n' + '\n'.join(result)
    else:
        pass
