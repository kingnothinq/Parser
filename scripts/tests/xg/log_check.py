# -*- coding: utf-8 -*-

import logging
from re import search


def test(device):
    """Check log and other service messages."""

    results = []

    # Power problems
    if device.reboot_reason == 'hardware reset':
        results.append('The last reboot reason is unexpected restart (hardware reset). '
                      'It may mean power problems. '
                      'Please check power source, PoE-injector and other stuff related to power.')

    # Check switch_smi_phy_busy timeout (it's rare)
    if search(r'switch_smi_phy_busy timeout', device.dc_string) is not None:
        results.append('The "switch_smi_phy_busy timeout" message detected. '
                      'Please ignore it if it does not cause problems.')

    # CPU
    pattern = search(r'CPU Load\s+(\d+)%\s+(\d+)%\(10s\)', device.dc_string)
    if int(pattern.group(1)) > 90 and int(pattern.group(2)) > 80:
        results.append(f'CPU utilization is {pattern.group(1)}%. '
                      f'Please pay attention.')

    # Temperature
    pattern = search(r'BOARD: ([\+\-\d\.]+) degrees Celsius', device.dc_string).group(1)
    if float(pattern) < -55 or float(pattern) > 60:
        results.append(f'Motherboard temperature is {pattern}°. '
                      f'Please pay attention.')

    results = list(set(results))
    if results:
        logger.info('Log issues test failed')
        return ('Log and other service messages issues', results)
    else:
        logger.info('Log issues test passed')
        pass


logger = logging.getLogger('logger.xg_log_check')