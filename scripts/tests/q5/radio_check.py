# -*- coding: utf-8 -*-

import logging


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

        try:
            rssi = float(rssi)

            if position == 'downlink' and settings['Role'] == 'master' and rssi > -40:
                result.append(f'* RSSI is {rssi} dBm in the {stream_name} on the slave device. '
                              f'Please decrease Tx power on the master device '
                              f'in order to avoid damage to the radio module. '
                              f'The recommended RSSI is -55 dBm. '
                              f'The current Tx power set as {settings["Tx Power"]} dBm.')
            elif position == 'downlink' and settings['Role'] == 'slave' and rssi > -40:
                result.append(f'* RSSI is {rssi} dBm in the {stream_name} on the slave device. '
                              f'Please decrease Tx power on the master device '
                              f'in order to avoid damage to the radio module. '
                              f'The recommended RSSI is -55 dBm.')
            elif position == 'uplink' and settings['Role'] == 'master' and rssi > -40:
                result.append(f'* RSSI is {rssi} dBm in the {stream_name} on the master device. '
                              f'Please decrease Tx power on the slave device '
                              f'in order to avoid damage to the radio module. '
                              f'The recommended RSSI is -55 dBm.')
            elif position == 'uplink' and settings['Role'] == 'slave' and rssi > -40:
                result.append(f'* RSSI is {rssi} dBm in the {stream_name} on the master device. '
                              f'Please decrease Tx power on the slave device '
                              f'in order to avoid damage to the radio module. '
                              f'The recommended RSSI is -55 dBm. '
                              f'The current Tx power set as {settings["Tx Power"]} dBm.')

            elif position == 'downlink' and settings['Role'] == 'master' and rssi < -80:
                result.append(f'* RSSI is {rssi} dBm in the {stream_name} on the slave device. '
                              f'Please increase Tx power or improve alignment '
                              f'on the master device in order to reach better signal. '
                              f'The recommended RSSI is -55 dBm. '
                              f'The current Tx power set as {settings["Tx Power"]} dBm.')
            elif position == 'downlink' and settings['Role'] == 'slave' and rssi < -80:
                result.append(f'* RSSI is {rssi} dBm in the {stream_name} on the slave device. '
                              f'Please increase Tx power or improve alignment '
                              f'on the master device in order to reach better signal. '
                              f'The recommended RSSI is -55 dBm.')
            elif position == 'uplink' and settings['Role'] == 'master' and rssi < -80:
                result.append(f'* RSSI is {rssi} dBm in the {stream_name} on the master device. '
                              f'Please increase Tx power or improve alignment '
                              f'on the slave device in order to reach better signal. '
                              f'The recommended RSSI is -55 dBm.')
            elif position == 'uplink' and settings['Role'] == 'slave' and rssi < -80:
                result.append(f'* RSSI is {rssi} dBm in the {stream_name} on the master device. '
                              f'Please increase Tx power or improve alignment '
                              f'on the slave device in order to reach better signal. '
                              f'The recommended RSSI is -55 dBm.'
                              f'The current Tx power set as {settings["Tx Power"]} dBm.')
        except TypeError:
            logger.exception('Radio RSSI TypeError')
        finally:
            pass


    def check_evm(position, stream_name, evm):
        """Check EVM and return the conclusion."""

        try:
            evm = float(evm)

            if position == 'downlink' and settings['Role'] == 'master' and evm > -10:
                result.append(f'* EVM is {evm} dB in the {stream_name} on the slave device. '
                              f'The quality of the signal is very low. '
                              f'Only low-level modulations are available. '
                              f'Please improve the quality of the signal to reach better modulations. '
                              f'Possible solutions: '
                              f'1) Increase Tx power on the master device. '
                              f'The current Tx power set as {settings["Tx Power"]} dBm; '
                              f'2) Find better frequency for the slave device '
                              f'(the spectrum analyzer can be used to do that); '
                              f'3) Reduce bandwidth on the master device '
                              f'in order to improve the sensitivity of the radio module. '
                              f'The current bandwidth is {settings["Bandwidth"]} MHz.')
            elif position == 'downlink' and settings['Role'] == 'slave' and evm > -10:
                result.append(f'* EVM is {evm} dB in the {stream_name} on the slave device. '
                              f'The quality of the signal is very low. '
                              f'Only low-level modulations are available. '
                              f'Please improve the quality of the signal to reach better modulations. '
                              f'Possible solutions: '
                              f'1) Increase Tx power on the master device; '
                              f'2) Find better frequency for the slave device '
                              f'(the spectrum analyzer can be used to do that); '
                              f'3) Reduce bandwidth on the master device '
                              f'in order to improve the sensitivity of the radio module. ')
            elif position == 'uplink' and settings['Role'] == 'master' and evm > -10:
                result.append(f'* EVM is {evm} dB in the {stream_name} on the master device. '
                              f'The quality of the signal is very low. '
                              f'Only low-level modulations are available. '
                              f'Please improve the quality of the signal to reach better modulations. '
                              f'Possible solutions: '
                              f'1) Increase Tx power on the slave device; '
                              f'2) Find better frequency for the master device '
                              f'(the spectrum analyzer can be used to do that); '
                              f'3) Reduce bandwidth on the master device '
                              f'in order to improve the sensitivity of the radio module. '
                              f'The current bandwidth is {settings["Bandwidth"]} MHz. ')
            elif position == 'uplink' and settings['Role'] == 'slave' and evm > -10:
                result.append(f'* EVM is {evm} dB in the {stream_name} on the master device. '
                              f'The quality of the signal is very low. '
                              f'Only low-level modulations are available. '
                              f'Please improve the quality of the signal to reach better modulations. '
                              f'Possible solutions: '
                              f'1) Increase Tx power on the slave device. '
                              f'The current Tx power set as {settings["Tx Power"]} dBm; '
                              f'2) Find better frequency for the master device '
                              f'(the spectrum analyzer can be used to do that); '
                              f'3) Reduce bandwidth on the master device '
                              f'in order to improve the sensitivity of the radio module. ')

            elif position == 'downlink' and settings['Role'] == 'master' and evm > -15:
                result.append(f'* EVM is {evm} dB in the {stream_name} on the slave device. '
                              f'The quality of the signal is very low. '
                              f'Only middle-level modulations are available. '
                              f'Please improve the quality of the signal to reach better modulations. '
                              f'Possible solutions: '
                              f'1) Increase Tx power on the master device. '
                              f'The current Tx power set as {settings["Tx Power"]} dBm; '
                              f'2) Find better frequency for the slave device '
                              f'(the spectrum analyzer can be used to do that); '
                              f'3) Reduce bandwidth on the master device '
                              f'in order to improve the sensitivity of the radio module. '
                              f'The current bandwidth is {settings["Bandwidth"]} MHz. ')
            elif position == 'downlink' and settings['Role'] == 'slave' and evm > -15:
                result.append(f'* EVM is {evm} dB in the {stream_name} on the slave device. '
                              f'The quality of the signal is very low. '
                              f'Only middle-level modulations are available. '
                              f'Please improve the quality of the signal to reach better modulations. '
                              f'Possible solutions: '
                              f'1) Increase Tx power on the master device; '
                              f'2) Find better frequency for the slave device '
                              f'(the spectrum analyzer can be used to do that); '
                              f'3) Reduce bandwidth on the master device '
                              f'in order to improve the sensitivity of the radio module.')
            elif position == 'uplink' and settings['Role'] == 'master' and evm > -15:
                result.append(f'* EVM is {evm} dB in the {stream_name} on the master device. '
                              f'The quality of the signal is very low. '
                              f'Only middle-level modulations are available. '
                              f'Please improve the quality of the signal to reach better modulations. '
                              f'Possible solutions: '
                              f'1) Increase Tx power on the slave device; '
                              f'2) Find better frequency for the master device '
                              f'(the spectrum analyzer can be used to do that); '
                              f'3) Reduce bandwidth on the master device '
                              f'in order to improve the sensitivity of the radio module. '
                              f'The current bandwidth is {settings["Bandwidth"]} MHz.')
            elif position == 'uplink' and settings['Role'] == 'slave' and evm > -15:
                result.append(f'* EVM is {evm} dB in the {stream_name} on the master device. '
                              f'The quality of the signal is very low. '
                              f'Only middle-level modulations are available. '
                              f'Please improve the quality of the signal to reach better modulations. '
                              f'Possible solutions: '
                              f'1) Increase Tx power on the slave device. '
                              f'The current Tx power set as {settings["Tx Power"]} dBm; '
                              f'2) Find better frequency for the master device '
                              f'(the spectrum analyzer can be used to do that); '
                              f'3) Reduce bandwidth on the master device '
                              f'in order to improve the sensitivity of the radio module. ')
        except TypeError:
            logger.exception('Radio EVM TypeError')
        finally:
            pass


    def check_crosstalk(position, stream_name, crosstalk):
        """Check Crosstalk and return the conclusion."""

        try:
            crosstalk = float(crosstalk)

            if position == 'downlink' and crosstalk > -15:
                result.append(f'* Crosstalk is {crosstalk} dB in the {stream_name} on the slave device. '
                              f'Please check the installation of the antenna and LOS.')
            elif position == 'uplink' and crosstalk > -15:
                result.append(f'* Crosstalk is {crosstalk} dB in the {stream_name} on the master device. '
                              f'Please check the installation of the antenna and LOS.')
        except TypeError:
            logger.exception('Radio Crosstalk TypeError')
        finally:
            pass


    def check_arq_ratio(position, stream_name, arq):
        """Check ARQ Ratio in the stream and return the conclusion."""

        try:
            arq = float(arq)

            if position == 'downlink' and arq > 5:
                result.append(f'* ARQ ratio is {arq} % in the {stream_name} on the slave device. '
                              f'It is recommended to keep the ARQ ratio less than 5%. '
                              f'Please check other radio link parameters and find better frequency.')
            elif position == 'uplink' and arq > 5:
                result.append(f'* ARQ ratio is {arq} % in the {stream_name} on the master device. '
                              f'It is recommended to keep the ARQ ratio less than 5%. '
                              f'Please check other radio link parameters and find better frequency.')
        except TypeError:
            logger.exception('Radio ARQ TypeError')
        finally:
            pass


    def check_mixed_polarisations(position, carrier):
        """Check if V and H polarizations were mixed up during installation."""

        try:
            gain_skew = abs(float(carrier['Stream 0']['Tx Power']) - float(carrier['Stream 1']['Tx Power']))
            crosstalk_0 = float(carrier['Stream 0']['Crosstalk'])
            crosstalk_1 = float(carrier['Stream 1']['Crosstalk'])

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
        except TypeError:
            logger.exception('Radio TX power TypeError')
        finally:
            pass


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

    elif device.radio_status['Link status'] == 'connecting':
        result.append('* ??????')

    elif device.radio_status['Link status'] == 'standby':
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

    result = list(set(result))
    if result:
        logger.info('Radio test failed')
        return ('Radio issues', result)
    else:
        logger.info('Radio test passed')
        pass


logger = logging.getLogger('logger.quanta_radio_check')