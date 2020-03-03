#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search, findall

from ftplib import FTP


def test(device):
    """Not important or not necessary recommendations."""

    def ftp_path():
        if 'H08' in platform or 'H11' in platform:
            release_path = '/pub/Firmware/{}/'.format(fw_type)
            beta_path = '/pub/Firmware/beta/{}/'.format(fw_type, platform)
            pass

    result = []

    pattern = findall(r'(\d{2}):(\d{2}):(\d{2})', device.uptime)
    if int(pattern[0][0]) <= 0 and int(pattern[0][1]) < 15:
        result.append('* Uptime is too short ({}). '
                      'It is recommended to wait more in order to collect more precise statistics.'
                      .format(device.uptime))

    ftp = FTP('ftp.infinet.ru')
    ftp.login()
    pattern = search(r'((H\d{2})S\d{2})-(MINT|TDMA)v((\d+\.){2}(\d+))', device.firmware)
    platform = pattern.group(2)
    fw_type = pattern.group(3)
    fw_current = pattern.group(4)
    path_release_ = '/pub/Firmware/{}/{}/'.format(fw_type, platform)
    path_beta = '/pub/Firmware/beta/{}/'.format(fw_type)
    path_old = '/pub/Firmware/old/{}/{}/'.format(fw_type, platform)
    fw_release = ftp.nlst(path_release_)
    fw_beta = ftp.nlst(path_beta)
    fw_old = ftp.nlst(path_old)
    firmwares = fw_release + fw_beta + fw_old
    fw_latest = []
    build_1 = 0
    build_2 = 0

    print(firmwares)

    def func(a):
        if a == 'bin':
            return a

    firmwares = [search(r'v(\d+)\.(\d+)\.bin', fw).group() for fw in firmwares]
    print(firmwares)

    a = ['1.19', '1.8']
    print(sorted(a, key=lambda x:[int(x1) for x1 in x.split('.')]))

    for fw in firmwares:
        fw_ftp = search(r'v(\d+)\.(\d+)\.bin', fw)
        if fw_ftp is not None:
            fw_ftp = fw_ftp.groups()
            if int(fw_ftp[0]) > build_1 and int(fw_ftp[1]) > build_2:
                build_1 = int(fw_ftp[0])
                build_2 = int(fw_ftp[1])
                fw_latest = '{}.{}'.format(build_1, build_2)

    print(fw_latest)

    fw_latest = []

    for fw in firmwares:
        fw_ftp = search(r'v(\d+)\.(\d+)\.bin', fw)
        if fw_ftp is not None:
            if len(fw_ftp.group(2)) < 2:
                fw_latest.append('{}.0{}'.format(fw_ftp.group(1), fw_ftp.group(2)))
            else:
                fw_latest.append('{}.{}'.format(fw_ftp.group(1), fw_ftp.group(2)))

    fw_latest.sort()
    print(fw_latest[-1])

    #fw_latest = 'R5000-{}-{}v{}.bin'.format(pattern.group(1), fw_type, fw_latest[-1])
    #print(fw_latest)

    if len(result) > 0:
        return '\nRecommendations: \n' + '\n'.join(result)
    else:
        pass