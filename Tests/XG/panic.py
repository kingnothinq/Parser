#!/usr/bin/python
# -*- coding: utf-8 -*-

from copy import deepcopy


def test(device):
    """Find panic and suggest a solution"""

    def find_panic(panic):
        """Return a workaround"""
        if 'LINKDOWN' in panic:
            return '* Watchdog activation detected: XG_TIMEOUT. ' \
                   'No connection during the watchdog timer.' \
                   'The watchdog timer can be changed:' \
                   '\"wd -downlink-timer X\", where X is time in minutes.\n'
        elif 'XG_TIMEOUT' in panic:
            return '* Watchdog activation detected: XG_TIMEOUT. ' \
                   'The last boot was incorrect and the device was rebooted.' \
                   ' If this watchdog works too often, then contact the developers.\n'
        elif 'RLM_FG_TIMEOUT' in panic:
            return '* Watchdog activation detected: RLM_FG_TIMEOUT. ' \
                   'The foreground spectrum scanner stucked and the device was rebooted.' \
                   ' If this watchdog works too often, then contact the developers.\n'
        elif 'MCHL_ADM_TIMEOUT' in panic:
            return '* Watchdog activation detected: MCHL_ADM_TIMEOUT. ' \
                   'There was a failure in the frequency changing mechanism and the device was rebooted. ' \
                   'If this watchdog works too often, then contact the developers.\n'
        elif 'TXPWR' in panic:
            return '* Watchdog activation detected: TXPWR. ' \
                   'There was a failure in the radio modem and the device was rebooted. ' \
                   'If this watchdog works too often, then contact the developers.\n'
        elif 'HTA' in panic:
            return '* Watchdog activation detected: HTA. ' \
                   'Performance dropdown was found. ' \
                   'If this watchdog works too often, then contact the developers.\n'
        elif 'PP' in panic or 'UPDOWN' in panic:
            return '* Watchdog activation detected: PP. ' \
                   'There is no service p2p between the master and the slave and the device was rebooted. ' \
                   'This watchdog must be enabled on both devices. ' \
                   'If this watchdog works too often, then contact the developers.\n'
        elif 'UD' in panic:
            return '* Watchdog activation detected: UD. ' \
                   'There was a failure in the radio modem and the device was rebooted. ' \
                   'If this watchdog works too often, then contact the developers.\n'
        elif 'SIN' in panic:
            return '* Watchdog activation detected: SIN. ' \
                   'There was a failure in the radio modem and the device was rebooted. ' \
                   'If this watchdog works too often, then contact the developers.\n'
        elif 'ASSERT' in panic:
            return '* Assert was detected. ' \
                   'If this assert works too often, then contact the developers.\n'
        else:
            return '* An unknown panic message was found. Please look for it in Jira or contact the developers.\n'

    result = []

    if len(device.panic) > 0:
        for panic in device.panic:
            result.append(find_panic(panic))
        return ' '.join(result)
    else:
        pass
