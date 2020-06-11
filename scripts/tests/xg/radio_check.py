# -*- coding: utf-8 -*-

import logging
from re import search


def test(device):
    """Check radio parameters and return conclusion."""

    def check_carrier(position, carrier_name, carrier_data):
        """Check important carrier parameters and return the conclusion."""

        if carrier_data['Frequency'] is None:
            return

        pattern = float(search(r'\(([\d\.]+)%\)', carrier_data['Rx Acc FER']).group(1))
        if pattern > 1.5:
            result.append(f'* Rx Acc FER errors ({pattern} %) detected '
                          f'in the {carrier_name} on the {position} side. '
                          f'Please check other radio link parameters '
                          f'and find better frequency.')

        check_gain(position, carrier_name,
                   carrier_data['Stream 0']['Tx Gain'], carrier_data['Stream 1']['Tx Gain'])

        for stream in ['Stream 0', 'Stream 1']:
            check_stream(position, carrier_name, str.lower(stream), carrier_data[stream])

    def check_stream(position, carrier_name, stream_name, stream_data):
        """Check important stream parameters and return the conclusion."""

        check_rssi(position, carrier_name, stream_name, stream_data['RSSI'])
        check_cinr(position, carrier_name, stream_name, stream_data['CINR'])
        check_crosstalk(position, carrier_name, stream_name, stream_data['Crosstalk'])
        check_errors_ratio(position, carrier_name, stream_name, stream_data['Errors Ratio'])

    def check_rssi(position, carrier_name, stream_name, rssi):
        """Check RSSI and return the conclusion."""

        try:
            rssi = int(search(r'(\d+)', rssi).group(1))
            if position == 'local' and rssi < 40:
                result.append(f'* RSSI is -{rssi} dBm in the {stream_name} of '
                              f'the {carrier_name} on the {position} side. '
                              f'Please decrease Tx power on the remote '
                              f'side in order to avoid damage to the radio module.')
            elif position == 'remote' and rssi < 40:
                result.append(f'* RSSI is -{rssi} dBm in the {stream_name} of '
                              f'the {carrier_name} on the {position} side. '
                              f'Please decrease Tx power on the local side '
                              f'in order to avoid damage to the radio module.'
                              f'The current Tx power set as {settings["Tx Power"]} dBm.')
            elif position == 'local' and rssi > 80:
                result.append(f'* RSSI is -{rssi} dBm in the {stream_name} of '
                              f'the {carrier_name} on the {position} side. '
                              f'Please increase Tx power or improve alignment '
                              f'on the remote side in order to reach better signal.')
            elif position == 'remote' and rssi > 80:
                result.append(f'* RSSI is -{rssi} dBm in the {stream_name} of '
                              f'the {carrier_name} on the {position} side. '
                              f'Please increase Tx power or improve alignment '
                              f'on the local side in order to reach better signal.'
                              f'The current Tx power set as {settings["Tx Power"]} dBm.')
        except TypeError:
            logger.exception('Radio RSSI TypeError')
        finally:
            pass

    def check_cinr(position, carrier_name, stream_name, cinr):
        """Check CINR and return the conclusion."""

        try:
            cinr = int(search(r'(\d+)', cinr).group(1))
            if position == 'local' and cinr < 10:
                result.append(f'* CINR is {cinr} dB in the {stream_name} of '
                              f'the {carrier_name} on the {position} side. '
                              f'The quality of the signal is very low. '
                              f'Only low-level modulations are available. '
                              f'Please improve the quality of the signal to reach better modulations. '
                              f'Possible solutions: '
                              f'1) Increase Tx power on the remote side; '
                              f'2) Find better frequency for the remote side '
                              f'(the spectrum analyzer can be used to do that); '
                              f'3) Reduce bandwidth on the master device '
                              f'in order to improve the sensitivity of the radio module. '
                              f'The current bandwidth is {settings["Bandwidth"]} MHz.')
            elif position == 'remote' and cinr < 10:
                result.append(f'* CINR is {cinr} dB in the {stream_name} of '
                              f'the {carrier_name} on the {position} side. '
                              f'The quality of the signal is very low. '
                              f'Only low-level modulations are available. '
                              f'Please improve the quality of the signal to reach better modulations. '
                              f'Possible solutions: '
                              f'1) Increase Tx power on the local side. '
                              f'The current Tx power set as {settings["Tx Power"]}; '
                              f'2) Find better frequency for the remote side '
                              f'(the spectrum analyzer can be used to do that); '
                              f'3) Reduce bandwidth on the master device '
                              f'in order to improve the sensitivity of the radio module. '
                              f'The current bandwidth is {settings["Bandwidth"]} MHz.')
            elif position == 'local' and cinr < 20:
                result.append(f'* CINR is {cinr} dB in the {stream_name} of '
                              f'the {carrier_name} on the {position} side. '
                              f'The quality of the signal is very low. '
                              f'Only middle-level modulations are available. '
                              f'Please improve the quality of the signal to reach better modulations. '
                              f'Possible solutions: '
                              f'1) Increase Tx power on the remote side; '
                              f'2) Find better frequency for the remote side '
                              f'(the spectrum analyzer can be used to do that); '
                              f'3) Reduce bandwidth on the master device '
                              f'in order to improve the sensitivity of the radio module. '
                              f'The current bandwidth is {settings["Bandwidth"]} MHz.')
            elif position == 'remote' and cinr < 20:
                result.append(f'* CINR is {cinr} dB in the {stream_name} of '
                              f'the {carrier_name} on the {position} side. '
                              f'The quality of the signal is very low. '
                              f'Only middle-level modulations are available. '
                              f'Please improve the quality of the signal to reach better modulations. '
                              f'Possible solutions: '
                              f'1) Increase Tx power on the local side. '
                              f'The current Tx power set as {settings["Tx Power"]}; '
                              f'2) Find better frequency for the remote side '
                              f'(the spectrum analyzer can be used to do that); '
                              f'3) Reduce bandwidth on the master device '
                              f'in order to improve the sensitivity of the radio module. '
                              f'The current bandwidth is {settings["Bandwidth"]} MHz.')
        except TypeError:
            logger.exception('Radio CINR TypeError')
        finally:
            pass

    def check_crosstalk(position, carrier_name, stream_name, crosstalk):
        """Check Crosstalk and return the conclusion."""

        try:
            crosstalk = int(search(r'(\d+)', crosstalk).group(1))
            if crosstalk < 20:
                result.append(f'* Crosstalk is -{crosstalk} dB in '
                              f'the {stream_name} of the {carrier_name} on the {position} side. '
                              f'Please check the installation of the antenna and LOS.')
        except TypeError:
            logger.exception('Radio Crosstalk TypeError')
        finally:
            pass

    def check_errors_ratio(position, carrier_name, stream_name, errors_ratio):
        """Check Errors Ratio in the stream and return the conclusion."""

        try:
            errors_ratio = float(search(r'([\d\.]+)', errors_ratio).group(1))
            if errors_ratio > 1.5:
                result.append(f'* TBER Errors ({errors_ratio} %) detected in '
                              f'the {stream_name} of the {carrier_name} on the {position} side. '
                              f'XG does not support ARQ. '
                              f'Therefore, some important data may be lost. '
                              f'Please check other radio link parameters and find better frequency.')
        except TypeError:
            logger.exception('Radio Errors Ratio TypeError')
        finally:
            pass

    def check_gain(position, carrier_name, gain_stream_0, gain_stream_1):
        """Check Gain and return the conclusion."""

        try:
            gain_stream_0 = float(search(r'([\d\.]+)', gain_stream_0).group(1))
            gain_stream_1 = float(search(r'([\d\.]+)', gain_stream_1).group(1))

            delta = abs(gain_stream_0 - gain_stream_1)

            if delta > 10:
                result.append(f'* Gain skew detected between '
                              f'the streams 0 and 1 of the {carrier_name} on the {position} side. '
                              f'Please check the radio module. It may be faulty.')
        except TypeError:
            logger.exception('Radio Gain TypeError')
        finally:
            pass


    master = device.radio_status['Master']
    slave = device.radio_status['Slave']
    settings = device.settings
    result = []

    # Check Link statuses
    if device.radio_status['Link status'] == 'DOWN':
        result.append('* The link is not established. '
                      'Please check alignment, '
                      'settings of the remote side, '
                      'LOS, the spectrum, etc.')

    elif device.radio_status['Link status'] == 'ERROR':
        # function_to_check_errors(args)
        result.append('* The link is not established and '
                      'stucked in the ERROR state. '
                      'Please find out the cause of the error.')

    elif device.radio_status['Link status'] == 'STARTING':
        result.append('* The link is establishing but this '
                      'status should not be displayed. '
                      'Please find out the cause of this status.')

    elif device.radio_status['Link status'] == 'STOPPED':
        result.append('* The link is not established because '
                      'of the radio interface is turned off. '
                      'Please enable the radio interface (CLI: \"ifc radio up\").')

    elif device.radio_status['Link status'] == 'PHY':
        result.append('* The link is not established. '
                      'Please find out the cause of the error.')
    else:
        # If Link Status is OK, check radio parameters
        if device.subfamily == 'XG 500':
            check_carrier(str.lower(master['Role']), str.lower('Carrier 0'), master['Carrier 0'])
            check_carrier(str.lower(slave['Role']), str.lower('Carrier 0'), slave['Carrier 0'])
        elif device.subfamily == 'XG 1000':
            for carrier in ['Carrier 0', 'Carrier 1']:
                check_carrier(str.lower(master['Role']), str.lower(carrier), master[carrier])
                check_carrier(str.lower(slave['Role']), str.lower(carrier), slave[carrier])

        if master['Carrier 0']['Frequency'] is None:
            result.append('* No statistic from the master device found.')
        elif slave['Carrier 0']['Frequency'] is None:
            result.append('* No statistic from the slave device found.')

    # Check RANGING_ST
    if search(r'RANGING_ST', device.dc_string) is not None and settings['Role'] == 'master':
        result.append('* The link stucked in the RANGING_ST state. '
                      'It may mean problems with alignment and LOS. '
                      'Also, there is a bug in the 1.7.9 and lower versions of the firmware. '
                      'A workaround is reboot.')

    result = list(set(result))
    if result:
        logger.info('Radio test failed')
        return '\nRadio issues: \n' + '\n'.join(result)
    else:
        logger.info('Radio test passed')
        pass


logger = logging.getLogger('logger.xg_radio_check')