#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search


def test(device):
    """Check log and other service messages."""

    result = []

    if device.reboot_reason == 'hardware reset':
        result.append('* The last reboot reason is unexpected restart (hardware reset). '
                      'It may mean power problems. '
                      'Please check power source, PoE-injector and other stuff related to power.')
    elif device.reboot_reason == 'unexpected restart':
        result.append('* The last reboot reason is unexpected restart (hardware reset). '
                      'It may mean power problems. '
                      'Please check power source, PoE-injector and other stuff related to power.')
    elif device.reboot_reason == 'RF Stuck':
        result.append('* The last reboot reason is RF stuck. '
                      'It means that the radio module was paused and rebooted by system. '
                      'This is a built-in protection mechanism, '
                      'designed to prevent the device from becoming unmanageable. '
                      'Most likely it was triggered by external interference.')
    elif device.reboot_reason == 'software fault':
        result.append('* The last reboot reason is software fault. '
                      'Please upgrade firmware or contact developers.')

    pattern = search(r'CPU Load\s+(\d+)%\s+(\d+)%\(10s\)', device.dc_string)
    if int(pattern.group(1)) > 98 and int(pattern.group(2)) > 95:
        result.append('* CPU utilization is {}%. '
                      'Please pay attention.'.format(pattern.group(1)))

    pattern = search(r'Temperature is ([\+\-\d\.]+) degrees Celsius', device.dc_string)
    if pattern is not None:
        if float(pattern.group(1)) < -55 or float(pattern.group(1)) > 60:
            result.append('* Motherboard temperature is {}°. '
                          'Please pay attention.'.format(pattern.group(1)))

    pattern = search(r'RECOVERY MODE ACTIVE', device.dc_string)
    if pattern is not None:
        result.append('* The device has been reset. '
                      'Please save config (CLI: "config save") '
                      'and reboot the device.'.format(pattern.group(1)))

    pattern = search(r'EMERGENCY!!!', device.dc_string)
    if pattern is not None:
        result.append('* Please check the installed license or '
                      'hardware components.'.format(pattern.group(1)))

    pattern = search(r'license: license not found', device.dc_string)
    if pattern is not None:
        result.append('* No license. '
                      'Please check the installed license.'.format(pattern.group(1)))

    pattern = search(r'DFFS: Can`t erase sector', device.dc_string)
    if pattern is not None:
        result.append('* Flash memory failure detected.'.format(pattern.group(1)))

    pattern = search(r'RTC not waking up', device.dc_string)
    if pattern is not None:
        result.append('* Real-Time Clock failure detected.'.format(pattern.group(1)))

    pattern = search(r'Scrambling engine overflow', device.dc_string)
    if pattern is not None:
        result.append('* Hardware encryption module overflow. '
                      'Maximum number of connected CPEs is 62. '
                      'Please disable scrambling (CLI: "mint rf5.0 -scrambling").'.format(pattern.group(1)))

    if result:
        return '\nLog and other service messages issues: \n' + '\n'.join(result)
    else:
        pass