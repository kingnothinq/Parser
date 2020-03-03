#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search


def test(device):
    """Check radio parameters and return conclusion."""

    def check_carrier(position, carrier_name, carrier_data):
        """Check important carrier parameters and return the conclusion."""

        if carrier_data['Frequency'] is None:
            return

        pattern = float(search(r'\(([\d\.]+)%\)', carrier_data['Rx Acc FER']).group(1))
        if pattern > 1.5:
            result.append('* Rx Acc FER errors ({} %) detected in the {} on the {} side. '
                          'Please check other radio link parameters and find better frequency.'
                          .format(pattern, carrier_name, position))

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
                result.append('* RSSI is -{} dBm in the {} of the {} on the {} side. '
                              'Please decrease Tx power on the remote side in order to avoid damage to the radio module.'
                              .format(rssi, stream_name, carrier_name, position))
            elif position == 'remote' and rssi < 40:
                result.append('* RSSI is -{} dBm in the {} of the {} on the {} side. '
                              'Please decrease Tx power on the local side in order to avoid damage to the radio module.'
                              'The current Tx power set as {} dBm.'
                              .format(rssi, stream_name, carrier_name, position, settings['Tx Power']))
            elif position == 'local' and rssi > 80:
                result.append('* RSSI is -{} dBm in the {} of the {} on the {} side. '
                              'Please increase Tx power or improve alignment on the remote side in order to reach better signal.'
                              .format(rssi, stream_name, carrier_name, position))
            elif position == 'remote' and rssi > 80:
                result.append('* RSSI is -{} dBm in the {} of the {} on the {} side. '
                              'Please increase Tx power or improve alignment on the local side in order to reach better signal.'
                              'The current Tx power set as {} dBm.'
                              .format(rssi, stream_name, carrier_name, position, settings['Tx Power']))
        except TypeError:
            pass
        finally:
            pass

    def check_cinr(position, carrier_name, stream_name, cinr):
        """Check CINR and return the conclusion."""

        try:
            cinr = int(search(r'(\d+)', cinr).group(1))
            if position == 'local' and cinr < 10:
                result.append('* CINR is {} dB in the {} of the {} on the {} side. '
                              'The quality of the signal is very low. '
                              'Only low-level modulations are available. '
                              'Please improve the quality of the signal to reach better modulations. '
                              'Possible solutions: '
                              '1) Increase Tx power on the remote side; '
                              '2) Find better frequency for the remote side (the spectrum analyzer can be used to do that); '
                              '3) Reduce bandwidth on the master device '
                              'in order to improve the sensitivity of the radio module. '
                              'The current bandwidth is {} MHz.'
                              .format(cinr, stream_name, carrier_name, position, settings['Bandwidth']))
            elif position == 'remote' and cinr < 10:
                result.append('* CINR is {} dB in the {} of the {} on the {} side. '
                              'The quality of the signal is very low. '
                              'Only low-level modulations are available. '
                              'Please improve the quality of the signal to reach better modulations. '
                              'Possible solutions: '
                              '1) Increase Tx power on the local side. The current Tx power set as {}; '
                              '2) Find better frequency for the remote side (the spectrum analyzer can be used to do that); '
                              '3) Reduce bandwidth on the master device '
                              'in order to improve the sensitivity of the radio module. '
                              'The current bandwidth is {} MHz.'
                              .format(cinr, stream_name, carrier_name, position, settings['Tx Power'],
                                      settings['Bandwidth']))
            elif position == 'local' and cinr < 20:
                result.append('* CINR is {} dB in the {} of the {} on the {} side. '
                              'The quality of the signal is very low. '
                              'Only middle-level modulations are available. '
                              'Please improve the quality of the signal to reach better modulations. '
                              'Possible solutions: '
                              '1) Increase Tx power on the remote side; '
                              '2) Find better frequency for the remote side (the spectrum analyzer can be used to do that); '
                              '3) Reduce bandwidth on the master device '
                              'in order to improve the sensitivity of the radio module. '
                              'The current bandwidth is {} MHz.'
                              .format(cinr, stream_name, carrier_name, position, settings['Bandwidth']))
            elif position == 'remote' and cinr < 20:
                result.append('* CINR is {} dB in the {} of the {} on the {} side. '
                              'The quality of the signal is very low. '
                              'Only middle-level modulations are available. '
                              'Please improve the quality of the signal to reach better modulations. '
                              'Possible solutions: '
                              '1) Increase Tx power on the local side. The current Tx power set as {}; '
                              '2) Find better frequency for the remote side (the spectrum analyzer can be used to do that); '
                              '3) Reduce bandwidth on the master device '
                              'in order to improve the sensitivity of the radio module. '
                              'The current bandwidth is {} MHz.'
                              .format(cinr, stream_name, carrier_name, position, settings['Tx Power'],
                                      settings['Bandwidth']))
        except TypeError:
            pass
        finally:
            pass

    def check_crosstalk(position, carrier_name, stream_name, crosstalk):
        """Check Crosstalk and return the conclusion."""

        try:
            crosstalk = int(search(r'(\d+)', crosstalk).group(1))
            if crosstalk < 20:
                result.append('* Crosstalk is -{} dB in the {} of the {} on the {} side. '
                              'Please check the installation of the antenna and LOS.'
                              .format(crosstalk, stream_name, carrier_name, position))
        except TypeError:
            pass
        finally:
            pass

    def check_errors_ratio(position, carrier_name, stream_name, errors_ratio):
        """Check Errors Ratio in the stream and return the conclusion."""

        try:
            errors_ratio = float(search(r'([\d\.]+)', errors_ratio).group(1))
            if errors_ratio > 1.5:
                result.append('* TBER Errors ({} %) detected in the {} of the {} on the {} side. '
                              'XG does not support ARQ. '
                              'Therefore, some important data may be lost. '
                              'Please check other radio link parameters and find better frequency.'
                              .format(errors_ratio, stream_name, carrier_name, position))
        except TypeError:
            pass
        finally:
            pass

    def check_gain(position, carrier_name, gain_stream_0, gain_stream_1):
        """Check Gain and return the conclusion."""

        try:
            gain_stream_0 = float(search(r'([\d\.]+)', gain_stream_0).group(1))
            gain_stream_1 = float(search(r'([\d\.]+)', gain_stream_1).group(1))

            delta = abs(gain_stream_0 - gain_stream_1)

            if delta > 10:
                result.append('* Gain skew detected between '
                              'the streams 0 and 1 of the {} on the {} side. '
                              'Please check the radio module. It may be faulty.'
                              .format(carrier_name, position))
        except TypeError:
            pass
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

    if len(result) > 0:
        return '\nRadio issues: \n' + '\n'.join(result)
    else:
        pass

    for line in device.dc_list:
        if "Warning: Abnormal transmit power disbalance!" in line:
            return '* Abnormal transmit power disbalance is detected. The radio module of the device {} is faulty. Please approve RMA.\n'.format(
                    device.serial_number)