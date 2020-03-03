#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search


def test(device):
    """Check log and other service messages."""

    result = []

    # Check power problems
    if device.reboot_reason == 'hardware reset':
        result.append('* The last reboot reason is unexpected restart (hardware reset). '
                      'It may mean power problems. '
                      'Please check power source, PoE-injector and other stuff related to power.')

    pattern = search(r'CPU Load\s+(\d+)%\s+(\d+)%\(10s\)', device.dc_string)
    print(pattern)
    if int(pattern.group(1)) > 98 and int(pattern.group(2)) > 95:
        result.append('* CPU utilization is {}%. '
                      'Please pay attention.'
                      .format(pattern.group(1)))

    pattern = search(r'Temperature is ([\+\-\d\.]+) degrees Celsius', device.dc_string)
    if pattern is not None:
        if float(pattern.group(1)) < -55 or float(pattern.group(1)) > 60:
            result.append('* Motherboard temperature is {}°. '
                          'Please pay attention.'
                          .format(pattern.group(1)))

    if len(result) > 0:
        return '\nLog and other service messages issues: \n' + '\n'.join(result)
    else:
        pass