# -*- coding: utf-8 -*-

import logging
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

    # New firmware
    ftp = FTP('ftp.infinet.ru')
    ftp.set_debuglevel(0)  # Print FTP log in console
    ftp.login()
    pattern = search(r'((H\d{2})S\d{2})-(MINT|TDMA)v((\d+\.){2}(\d+))', device.firmware)
    platform = pattern.group(2)
    fw_type = pattern.group(3)
    path_release = f'/pub/Firmware/{fw_type}/{platform}/'
    path_beta = f'/pub/Firmware/beta/{fw_type}/'
    path_old = f'/pub/Firmware/old/{fw_type}/{platform}/'
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
                path_latest = f'ftp://ftp.infinet.ru{pattern[0]}'
                result.append(f'* The current firmware version ({fw_current_own}) is old. '
                              f'Please update it. '
                              f'The latest version ({fw_latest}) can be downloaded '
                              f'from our FTP server ({path_latest}).')

    # Link flags
    links = device.radio_status['Links']
    links_old_fw = []
    for link in links:
        pattern = search(r'(H\d{2})v((\d+\.){2}(\d+))', links[link]['Firmware']).group(2)
        if fw_type == 'TDMA':
            fw_current_link = pattern.replace('2.1', '201')
        else:
            fw_current_link = pattern.replace('1.7', '17')
            fw_current_link = pattern.replace('1.8', '18')
            fw_current_link = pattern.replace('1.9', '19')
        if fw_current_link != fw_latest:
            for fw in [fw_release, fw_beta, fw_old]:
                pattern = list(filter(lambda x: fw_latest in x, fw))
                if pattern:
                    path_latest = f'ftp://ftp.infinet.ru{pattern[0]}'
            links_old_fw.append(links[link]["Name"])
    result.append(f'* The current installed firmware versions on the remote devices ({", ".join(links_old_fw)})'
                  f' are old. Please update them. '
                  f'The latest version ({fw_latest}) can be downloaded '
                  f'from our FTP server ({path_latest}).')


    result = list(set(result))
    if result:
        logger.info('Recommendations test failed')
        return '\nRecommendations: \n' + '\n'.join(result)
    else:
        logger.info('Recommendations test passed')
        pass


logger = logging.getLogger('logger.r5000_recommendations')