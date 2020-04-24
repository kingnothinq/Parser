#!/usr/bin/python
# -*- coding: utf-8 -*-

from ftplib import FTP
from re import findall, search


def test(device):
    """Not important or not necessary recommendations."""

    result = []

    if device.settings['Traffic prioritization'] == 'Enabled':
        result.append('* Traffic prioritization is not an exact QoS feature. '
                      'It is recommended to disable it due the bug (XG-1164).')

    if search(r'Antenna Gain not found in license', device.dc_string) is not None:
        result.append('* Antenna Gain not found in the license. '
                      'Please set this parameter via CLI (xg -antenna-gain <gain_dBm>).')

    pattern = findall(r'(\d{2}):(\d{2}):(\d{2})', device.uptime)
    if int(pattern[0][0]) <= 0 and int(pattern[0][1]) < 15:
        result.append('* Uptime is too short ({}). '
                      'It is recommended to wait more in order to collect more precise statistics.'.format(
            device.uptime))

    ftp = FTP('ftp.infinet.ru')
    ftp.login()
    fw_current = search(r'v((\d+\.){2}(\d+))', device.firmware).group(1)
    fw_release = ftp.nlst('/pub/Firmware/XG/H12/')
    fw_beta = ftp.nlst('/pub/Firmware/beta/XG/')
    fw_old = ftp.nlst('/pub/Firmware/old/XG/')
    firmwares = filter(lambda x: '.bin' in x, fw_release + fw_beta + fw_old)
    firmwares = [search(r'v(\d+\.\d+\.\d+)\.bin', fw).group(1) for fw in firmwares]
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