#!/usr/bin/python
# -*- coding: utf-8 -*-

from ftplib import FTP
from re import findall, search


def test(device):
    """Not important or not necessary recommendations."""

    result = []

    pattern = findall(r'(\d{2}):(\d{2}):(\d{2})', device.uptime)
    if int(pattern[0][0]) <= 0 and int(pattern[0][1]) < 15:
        result.append('* Uptime is too short ({}). '
                      'It is recommended to wait more in order to collect more precise statistics.'.format(
            device.uptime))

    ftp = FTP('ftp.infinet.ru')
    ftp.login()
    pattern = search(r'((H\d{2})S\d{2})-(MINT|TDMA)v((\d+\.){2}(\d+))', device.firmware)
    platform = pattern.group(2)
    fw_type = pattern.group(3)
    path_release = '/pub/Firmware/{}/{}/'.format(fw_type, platform)
    path_beta = '/pub/Firmware/beta/{}/'.format(fw_type)
    path_old = '/pub/Firmware/old/{}/{}/'.format(fw_type, platform)
    fw_release = ftp.nlst(path_release)
    fw_beta = ftp.nlst(path_beta)
    fw_old = ftp.nlst(path_old)
    if fw_type == 'TDMA':
        fw_current_own = pattern.group(4).replace('2.1', '201')
    else:
        fw_current_own = pattern.group(4).replace('1.7', '17')
        fw_current_own = pattern.group(4).replace('1.8', '18')
        fw_current_own = pattern.group(4).replace('1.9', '19')
    firmwares = filter(lambda x: '.bin' in x, fw_release + fw_beta + fw_old)
    firmwares = [search(r'v(\d+\.\d+)\.bin', fw).group(1) for fw in firmwares]
    fw_latest = sorted(firmwares, key=lambda x: [int(num) for num in x.split('.')])[-1]
    if fw_current_own != fw_latest:
        for fw in [fw_release, fw_beta, fw_old]:
            pattern = list(filter(lambda x: fw_latest in x, fw))
            if pattern:
                path_latest = 'ftp://ftp.infinet.ru{}'.format(pattern[0])
                result.append('* The current firmware version ({}) is old. '
                              'Please update it. '
                              'The latest version ({}) can be downloaded '
                              'from our FTP server ({}).'.format(fw_current_own, fw_latest, path_latest))

    links = device.radio_status['Links']
    for link in links:
        flags = findall(r'(\w+)', links[link]['Flags'])
        pattern = search(r'(H\d{2})v((\d+\.){2}(\d+))', links[link]['Firmware']).group(2)
        if fw_type == 'TDMA':
            fw_current_link = pattern.replace('2.1', '201')
        else:
            fw_current_link = pattern.replace('1.7', '17')
            fw_current_link = pattern.replace('1.8', '18')
            fw_current_link = pattern.replace('1.9', '19')
        if 'F' in flags:
            result.append('* The current installed firmware version ({}) '
                          'on the slave device ({}) differs from the firmware installed on '
                          'the master device ({}). It is recommended to install the same version.'.format(
                    fw_current_link, links[link]['Name'], fw_current_own))

    if result:
        return '\nRecommendations: \n' + '\n'.join(result)
    else:
        pass