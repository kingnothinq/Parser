# -*- coding: utf-8 -*-

import logging
from ftplib import FTP
from re import findall, search


def test(device):
    """Not important or not necessary recommendations."""

    result = []

    # Traffic prioritization enabled
    if device.settings['Traffic prioritization'] == 'Enabled':
        result.append('Traffic prioritization is not an exact QoS feature. '
                      'It is recommended to disable it due the bug (XG-1164).')

    # Antenna gain
    if search(r'Antenna Gain not found in license', device.dc_string) is not None:
        result.append('Antenna Gain not found in the license. '
                      'Please set this parameter via CLI (xg -antenna-gain <gain_dBm>).')

    # Uptime
    pattern = findall(r'(\d{2}):(\d{2}):(\d{2})', device.uptime)
    if 'day' not in device.uptime:
        if int(pattern[0][0]) <= 0 and int(pattern[0][1]) < 15:
            result.append(f'Uptime is too short ({device.uptime}). '
                          'It is recommended to wait for more in order to collect more precise statistics.')

    # New firmware
    try:
        ftp = FTP('ftp.infinet.ru', timeout=2)
        ftp.set_debuglevel(0)  # Print FTP log in console
        ftp.login()
        logger.info(f'FTP - Connected to {ftp.host}')
        fw_current = search(r'v((\d+\.){2}(\d+))', device.firmware).group(1)
        fw_release = ftp.nlst('/pub/Firmware/XG/H12/')
        fw_beta = ftp.nlst('/pub/Firmware/beta/XG/')
        fw_old = ftp.nlst('/pub/Firmware/old/XG/')
        logger.debug(f'FTP - NLST from {ftp.host}')
        ftp.quit()
        logger.info(f'FTP - Disconnected from {ftp.host}')
        firmwares = filter(lambda x: '.bin' in x, fw_release + fw_beta + fw_old)
        firmwares = [search(r'v(\d+\.\d+\.\d+)\.bin', fw).group(1) for fw in firmwares]
        fw_latest = sorted(firmwares, key=lambda x: [int(num) for num in x.split('.')])[-1]
        if fw_current != fw_latest:
            for fw in [fw_release, fw_beta, fw_old]:
                pattern = list(filter(lambda x: fw_latest in x, fw))
                if len(pattern) > 0:
                    path_latest = f'ftp://ftp.infinet.ru{pattern[0]}'
            result.append(f'The current firmware version ({fw_current}) is old. '
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


logger = logging.getLogger('logger.xg_recommendations')