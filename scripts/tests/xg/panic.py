#!/usr/bin/python
# -*- coding: utf-8 -*-

def test(device):
    """Find panic and suggest a solution."""

    def find_panic(panic):
        """Return a workaround."""

        if 'LINKDOWN' in panic:
            result.append('* Watchdog activation detected: XG_TIMEOUT. '
                          'No connection during the watchdog timer. '
                          'The watchdog timer can be changed:'
                          '\"wd -downlink-timer X\", where X is time in minutes.')

        elif 'XG_TIMEOUT' in panic:
            result.append('* Watchdog activation detected: XG_TIMEOUT. '
                          'The last boot was incorrect and the device was rebooted. '
                          'If this watchdog works too often, then contact the developers.')

        elif 'RLM_FG_TIMEOUT' in panic:
            result.append('* Watchdog activation detected: RLM_FG_TIMEOUT. '
                          'The foreground spectrum scanner stucked and the device was rebooted. '
                          'If this watchdog works too often, then contact the developers.')

        elif 'MCHL_ADM_TIMEOUT' in panic:
            result.append('* Watchdog activation detected: MCHL_ADM_TIMEOUT. '
                          'There was a failure in the frequency changing mechanism and the device was rebooted. '
                          'If this watchdog works too often, then contact the developers.')

        elif 'TXPWR' in panic:
            result.append('* Watchdog activation detected: TXPWR. '
                          'There was a failure in the radio modem and the device was rebooted. '
                          'If this watchdog works too often, then contact the developers.')

        elif 'HTA' in panic:
            result.append('* Watchdog activation detected: HTA. '
                          'Performance dropdown was found. '
                          'If this watchdog works too often, then contact the developers.')

        elif 'PP' in panic or 'UPDOWN' in panic:
            result.append('* Watchdog activation detected: PP. '
                          'There is no service p2p between the master and the slave and the device was rebooted. '
                          'This watchdog must be enabled on both devices. '
                          'If this watchdog works too often, then contact the developers.')
        elif 'UD' in panic:
            result.append('* Watchdog activation detected: UD. '
                          'There was a failure in the radio modem and the device was rebooted. '
                          'If this watchdog works too often, then contact the developers.')

        elif 'SIN' in panic:
            result.append('* Watchdog activation detected: SIN. '
                          'There was a failure in the radio modem and the device was rebooted. '
                          'If this watchdog works too often, then contact the developers.')

        elif 'ASSERT' in panic:
            result.append('* Assert was detected. '
                          'If this assert works too often, then contact the developers.')

        else:
            result.append('* An unknown panic message was found. '
                          'Please look for it in Jira or contact the developers. '
                          'The message: {}'.format(panic))

    result = []

    if len(device.panic) > 0:
        for panic in device.panic:
            find_panic(panic)

    if len(result) > 0:
        return '\nPanic and asserts: \n' + '\n'.join(result)
    else:
        pass