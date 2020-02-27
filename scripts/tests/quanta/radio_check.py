#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search


def test(device):
    """Check radio parameters and return conclusion."""

    def check_carrier(position, carrier):
        """Check important carrier parameters and return the conclusion."""

        check_mixed_polarisations(position, carrier)

        for stream in ['Stream 0', 'Stream 1']:
            check_stream(position, str.lower(stream), carrier[stream])

    def check_stream(position, stream_name, stream_data):
        """Check important stream parameters and return the conclusion."""

        check_rssi(position, stream_name, stream_data['RSSI'])
        check_evm(position, stream_name, stream_data['EVM'])
        check_crosstalk(position, stream_name, stream_data['Crosstalk'])
        check_arq_ratio(position, stream_name, stream_data['ARQ ratio'])

    def check_rssi(position, stream_name, rssi):
        """Check RSSI and return the conclusion."""

        rssi = float(search(r'([-\d\.]+)', rssi).group(1))

        if position == 'downlink' and settings['Role'] == 'master' and rssi < -40:
            result.append('* RSSI is {} dBm in the {} on the slave device. '
                          'Please decrease Tx power on the master device '
                          'in order to avoid damage to the radio module. '
                          'The recommended RSSI is -55 dBm. '
                          'The current Tx power set as {} dBm.'
                          .format(rssi, stream_name, settings['Tx Power']))
        elif position == 'downlink' and settings['Role'] == 'slave' and rssi < -40:
            result.append('* RSSI is {} dBm in the {} on the slave device. '
                          'Please decrease Tx power on the master device '
                          'in order to avoid damage to the radio module. '
                          'The recommended RSSI is -55 dBm.'
                          .format(rssi, stream_name))
        elif position == 'uplink' and settings['Role'] == 'master' and rssi < -40:
            result.append('* RSSI is {} dBm in the {} on the master device. '
                          'Please decrease Tx power on the slave device '
                          'in order to avoid damage to the radio module. '
                          'The recommended RSSI is -55 dBm.'
                          .format(rssi, stream_name))
        elif position == 'uplink' and settings['Role'] == 'slave' and rssi < -40:
            result.append('* RSSI is {} dBm in the {} on the master device. '
                          'Please decrease Tx power on the slave device '
                          'in order to avoid damage to the radio module. '
                          'The recommended RSSI is -55 dBm. '
                          'The current Tx power set as {} dBm.'
                          .format(rssi, stream_name, settings['Tx Power']))

        elif position == 'downlink' and settings['Role'] == 'master' and rssi > -80:
            result.append('* RSSI is {} dBm in the {} on the slave device. '
                          'Please increase Tx power or improve alignment '
                          'on the master device in order to reach better signal. '
                          'The recommended RSSI is -55 dBm. '
                          'The current Tx power set as {} dBm.'
                          .format(rssi, stream_name, settings['Tx Power']))
        elif position == 'downlink' and settings['Role'] == 'slave' and rssi > -80:
            result.append('* RSSI is {} dBm in the {} on the slave device. '
                          'Please increase Tx power or improve alignment '
                          'on the master device in order to reach better signal. '
                          'The recommended RSSI is -55 dBm.'
                          .format(rssi, stream_name))
        elif position == 'uplink' and settings['Role'] == 'master' and rssi > -80:
            result.append('* RSSI is {} dBm in the {} on the master device. '
                          'Please increase Tx power or improve alignment '
                          'on the slave device in order to reach better signal. '
                          'The recommended RSSI is -55 dBm.'
                          .format(rssi, stream_name))
        elif position == 'uplink' and settings['Role'] == 'slave' and rssi > -80:
            result.append('* RSSI is {} dBm in the {} on the master device. '
                          'Please increase Tx power or improve alignment '
                          'on the slave device in order to reach better signal. '
                          'The recommended RSSI is -55 dBm.'
                          'The current Tx power set as {} dBm.'
                          .format(rssi, stream_name, settings['Tx Power']))

    def check_evm(position, stream_name, evm):
        """Check EVM and return the conclusion."""

        evm = float(search(r'([-\d\.]+)', evm).group(1))
        if position == 'downlink' and settings['Role'] == 'master' and evm < -10:
            result.append('* EVM is {} dB in the {} on the slave device. '
                          'The quality of the signal is very low. '
                          'Only low-level modulations are available. '
                          'Please improve the quality of the signal to reach better modulations. '
                          'Possible solutions: '
                          '1) Increase Tx power on the master device. '
                          'The current Tx power set as {} dBm; '
                          '2) Find better frequency for the slave device '
                          '(the spectrum analyzer can be used to do that); '
                          '3) Reduce bandwidth on the master device '
                          'in order to improve the sensitivity of the radio module. '
                          'The current bandwidth is {} MHz. '
                          .format(evm, stream_name, settings['Tx Power'], settings['Bandwidth']))
        elif position == 'downlink' and settings['Role'] == 'slave' and evm < -10:
            result.append('* EVM is {} dB in the {} on the slave device. '
                          'The quality of the signal is very low. '
                          'Only low-level modulations are available. '
                          'Please improve the quality of the signal to reach better modulations. '
                          'Possible solutions: '
                          '1) Increase Tx power on the master device; '
                          '2) Find better frequency for the slave device '
                          '(the spectrum analyzer can be used to do that); '
                          '3) Reduce bandwidth on the master device '
                          'in order to improve the sensitivity of the radio module. '
                          .format(evm, stream_name))
        elif position == 'uplink' and settings['Role'] == 'master' and evm < -10:
            result.append('* EVM is {} dB in the {} on the master device. '
                          'The quality of the signal is very low. '
                          'Only low-level modulations are available. '
                          'Please improve the quality of the signal to reach better modulations. '
                          'Possible solutions: '
                          '1) Increase Tx power on the slave device; '
                          '2) Find better frequency for the master device '
                          '(the spectrum analyzer can be used to do that); '
                          '3) Reduce bandwidth on the master device '
                          'in order to improve the sensitivity of the radio module. '
                          'The current bandwidth is {} MHz. '
                          .format(evm, stream_name, settings['Bandwidth']))
        elif position == 'uplink' and settings['Role'] == 'slave' and evm < -10:
            result.append('* EVM is {} dB in the {} on the master device. '
                          'The quality of the signal is very low. '
                          'Only low-level modulations are available. '
                          'Please improve the quality of the signal to reach better modulations. '
                          'Possible solutions: '
                          '1) Increase Tx power on the slave device. '
                          'The current Tx power set as {} dBm; '
                          '2) Find better frequency for the master device '
                          '(the spectrum analyzer can be used to do that); '
                          '3) Reduce bandwidth on the master device '
                          'in order to improve the sensitivity of the radio module. '
                          .format(evm, stream_name, settings['Tx Power']))

        elif position == 'downlink' and settings['Role'] == 'master' and evm < -15:
            result.append('* EVM is {} dB in the {} on the slave device. '
                          'The quality of the signal is very low. '
                          'Only middle-level modulations are available. '
                          'Please improve the quality of the signal to reach better modulations. '
                          'Possible solutions: '
                          '1) Increase Tx power on the master device. '
                          'The current Tx power set as {} dBm; '
                          '2) Find better frequency for the slave device '
                          '(the spectrum analyzer can be used to do that); '
                          '3) Reduce bandwidth on the master device '
                          'in order to improve the sensitivity of the radio module. '
                          'The current bandwidth is {} MHz. '
                          .format(evm, stream_name, settings['Tx Power'], settings['Bandwidth']))
        elif position == 'downlink' and settings['Role'] == 'slave' and evm < -15:
            result.append('* EVM is {} dB in the {} on the slave device. '
                          'The quality of the signal is very low. '
                          'Only middle-level modulations are available. '
                          'Please improve the quality of the signal to reach better modulations. '
                          'Possible solutions: '
                          '1) Increase Tx power on the master device; '
                          '2) Find better frequency for the slave device '
                          '(the spectrum analyzer can be used to do that); '
                          '3) Reduce bandwidth on the master device '
                          'in order to improve the sensitivity of the radio module. '
                          .format(evm, stream_name))
        elif position == 'uplink' and settings['Role'] == 'master' and evm < -15:
            result.append('* EVM is {} dB in the {} on the master device. '
                          'The quality of the signal is very low. '
                          'Only middle-level modulations are available. '
                          'Please improve the quality of the signal to reach better modulations. '
                          'Possible solutions: '
                          '1) Increase Tx power on the slave device; '
                          '2) Find better frequency for the master device '
                          '(the spectrum analyzer can be used to do that); '
                          '3) Reduce bandwidth on the master device '
                          'in order to improve the sensitivity of the radio module. '
                          'The current bandwidth is {} MHz. '
                          .format(evm, stream_name, settings['Bandwidth']))
        elif position == 'uplink' and settings['Role'] == 'slave' and evm < -15:
            result.append('* EVM is {} dB in the {} on the master device. '
                          'The quality of the signal is very low. '
                          'Only middle-level modulations are available. '
                          'Please improve the quality of the signal to reach better modulations. '
                          'Possible solutions: '
                          '1) Increase Tx power on the slave device. '
                          'The current Tx power set as {} dBm; '
                          '2) Find better frequency for the master device '
                          '(the spectrum analyzer can be used to do that); '
                          '3) Reduce bandwidth on the master device '
                          'in order to improve the sensitivity of the radio module. '
                          .format(evm, stream_name, settings['Tx Power']))

    def check_crosstalk(position, stream_name, crosstalk):
        """Check Crosstalk and return the conclusion."""

        crosstalk = float(search(r'([-\d\.]+)', crosstalk).group(1))
        if position == 'downlink' and crosstalk < -15:
            result.append('* Crosstalk is {} dB in the {} on the slave device. '
                          'Please check the installation of the antenna and LOS.'
                          .format(crosstalk, stream_name))
        elif position == 'uplink' and crosstalk < -15:
            result.append('* Crosstalk is {} dB in the {} on the master device. '
                          'Please check the installation of the antenna and LOS.'
                          .format(crosstalk, stream_name))

    def check_arq_ratio(position, stream_name, arq):
        """Check ARQ Ratio in the stream and return the conclusion."""
        arq = float(search(r'([\d\.]+)', arq).group(1))
        if position == 'downlink' and arq > 5:
            result.append('* ARQ ratio is {} % in the {} on the slave device. '
                          'It is recommended to keep the ARQ ratio less than 5%. '
                          'Please check other radio link parameters and find better frequency.'
                          .format(arq, stream_name, position))
        elif position == 'uplink' and arq > 5:
            result.append('* ARQ ratio is {} % in the {} on the master device. '
                          'It is recommended to keep the ARQ ratio less than 5%. '
                          'Please check other radio link parameters and find better frequency.'
                          .format(arq, stream_name, position))

    def check_mixed_polarisations(position, carrier):
        """Check if V and H polarizations were mixed up during installation."""

        gain_skew = abs(float(carrier['Stream 0']['Tx Power']) - float(carrier['Stream 1']['Tx Power']))
        crosstalk_0 = float(search(r'([-\d\.]+)', carrier['Stream 0']['Crosstalk']).group(1))
        crosstalk_1 = float(search(r'([-\d\.]+)', carrier['Stream 1']['Crosstalk']).group(1))

        if position == 'downlink' and gain_skew > 10 and (crosstalk_0 >= 0 or crosstalk_1 >= 0):
            result.append('* Perhaps vertical and horizontal polarizations '
                          'were mixed up on the slave device during installation. '
                          'Please check the installation. '
                          'The ATPC feature will not work correctly '
                          'until the problem is resolved.'
                          'Please disable it.')
        elif position == 'uplink' and gain_skew > 10 and (crosstalk_0 >= 0 or crosstalk_1 >= 0):
            result.append('* Perhaps vertical and horizontal polarizations'
                          'were mixed up on the master device during installation. '
                          'Please check the installation. '
                          'The ATPC feature will not work correctly '
                          'until the problem is resolved. '
                          'Please disable it.')

    downlink = device.radio_status['Downlink']
    uplink = device.radio_status['Uplink']
    settings = device.settings
    result = []

    # Check Link statuses
    if device.radio_status['Link status'] == 'started':
        result.append('* The link is not established. '
                      'The master device is not receiving the signal from the slave. '
                      'Please check the alignment, '
                      'settings of the remote side, '
                      'LOS, the spectrum, etc.')

    elif device.radio_status['Link status'] == 'init':
        result.append('* ??????')

    elif device.radio_status['Link status'] == 'sector_detection':
        result.append('* The link is not established. '
                      'The slave device is waiting for the signal from the master. '
                      'Please check the alignment, '
                      'settings of the remote side, '
                      'LOS, the spectrum, etc.')
    else:
        # If Link Status is OK, check radio parameters
        check_carrier('downlink', downlink)
        check_carrier('uplink', uplink)

    if len(result) > 0:
        return '\nRadio issues: \n' + '\n'.join(result)
    else:
        pass