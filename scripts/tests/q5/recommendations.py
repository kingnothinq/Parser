# -*- coding: utf-8 -*-

import logging
from ftplib import FTP
from re import findall, search


def test(device):
    """Not important or not necessary recommendations"""

    settings = device.settings
    result = []

    # Disabled ARQ
    if settings['ARQ'] == 'Disabled':
        result.append('* Please enable ARQ. '
                      'It is a very useful feature.')

    # Locked modulations
    if settings['Max DL MCS'] != '256-QAM-7/8' or settings['Max UL MCS'] != '256-QAM-7/8':
        result.append('* Maximum MCS is limited. '
                      'Please note the highest modulations cannot be reached.')

    # Uptime
    pattern = findall(r'(\d{2}):(\d{2}):(\d{2})', device.uptime)
    if 'day' not in device.uptime:
        if int(pattern[0][0]) <= 0 and int(pattern[0][1]) < 15:
            result.append(f'* Uptime is too short ({device.uptime}). '
                          'It is recommended to wait more in order to collect more precise statistics.')

    # New firmware
    try:
        ftp = FTP('ftp.infinet.ru', timeout=2)
        ftp.set_debuglevel(0)  # Print FTP log in console
        ftp.login()
        logger.info(f'FTP - Connected to {ftp.host}')
        fw_current = search(r'PTPv((\d+\.){2}(\d+))', device.firmware).group(1)
        fw_release = ftp.nlst('/pub/Firmware/octopus/h18/')
        fw_beta = []  # ftp.nlst('/pub/Firmware/beta/octopus/')
        fw_old = ftp.nlst('/pub/Firmware/old/octopus/h18/')
        logger.debug(f'FTP - NLST from {ftp.host}')
        ftp.quit()
        logger.info(f'FTP - Disconnected from {ftp.host}')
        firmwares = filter(lambda x: '.bin' in x, fw_release + fw_beta + fw_old)
        firmwares = [search(r'h18_(\d+\.\d+\.\d+)\.bin', fw).group(1) for fw in firmwares]
        fw_latest = sorted(firmwares, key=lambda x: [int(num) for num in x.split('.')])[-1]
        if fw_current != fw_latest:
            for fw in [fw_release, fw_beta, fw_old]:
                pattern = list(filter(lambda x: fw_latest in x, fw))
                if len(pattern) > 0:
                    path_latest = f'ftp://ftp.infinet.ru{pattern[0]}'
            result.append(f'* The current firmware version ({fw_current}) is old. '
                          f'Please update it. '
                          f'The latest version ({fw_latest}) can be downloaded '
                          f'from our FTP server ({path_latest}).')
    except TimeoutError:
        logger.exception(f'FTP - A connection to FTP server attempt failed '
                         f'because the connected party did not properly respond after '
                         f'a period of time, or established connection failed '
                         f'because connected host has failed to respond')
    except:
        logger.exception(f'FTP - A connection to FTP server attempt failed')
    finally:
        pass


    result = list(set(result))
    if result:
        logger.info('Recommendations test failed')
        return ('Recommendations', result)
    else:
        logger.info('Recommendations test passed')
        pass


logger = logging.getLogger('logger.quanta_recommendations')