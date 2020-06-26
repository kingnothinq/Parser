# -*- coding: utf-8 -*-

import logging
import re


def test(device):
    """Check radio parameters and return conclusion."""

    def check_rssi(status):
        """Check RSSI and return the conclusion."""

        try:
            if '*' in status['RSSI Rx']:
                result.append(f'* Polarisation skew detected on the link {status["Name"]}. '
                              f'Please check alignment, crosstalk, LOS, etc.')

            if status['RSSI Tx'] is not None and '*' in status['RSSI Tx']:
                result.append(f'* Polarisation skew detected on the link {status["Name"]}. '
                              f'Please check alignment, crosstalk, LOS, etc.')

            # Remove "*" before RSSI
            rssi = float(status['RSSI Rx'].replace('*', ''))
            if rssi > -40:
                result.append(f'* RSSI is {rssi} dBm. Please decrease Tx power on '
                              f'the remote device {status["Name"]} in order to avoid damage '
                              f'to the radio module. '
                              f'It is not recommended RSSI greater than -40.')
            elif rssi < -80:
                result.append(f'* RSSI is {rssi} dBm. Please increase Tx power on '
                              f'the remote device {status["Name"]} in order to avoid damage '
                              f'to the radio module. '
                              f'It is not recommended RSSI less than -80.')
        except TypeError:
            logger.exception('Radio RSSI TypeError')
        finally:
            pass


    def check_power(status):
        """Check Power and return the conclusion."""

        try:
            if '*' in status['Power Rx'] or '*' in status['Power Tx']:
                result.append(f'* Power issues detected on the link {status["Name"]}. '
                              f'Please check Abnormal power disbalance on the remote device')
        except:
            logger.exception('Power exception')
        finally:
            pass


    def check_level(status):
        """Check Level and return the conclusion."""

        try:
            level_rx = int(status['Level Rx'])
            level_tx = int(status['Level Tx'])
            # Remove "*" before Power level
            power_rx = float(status['Power Rx'].replace('*', ''))
            power_tx = float(status['Power Tx'].replace('*', ''))
            snr_rx = int(status['SNR Rx'])
            snr_tx = int(status['SNR Tx'])
            power_skew = abs(power_rx - power_tx)
            level_skew = abs(level_rx - level_tx)
            snr_skew = abs(snr_rx - snr_tx)
            total_skew = abs(snr_skew - level_skew)
            if power_skew != level_skew and total_skew > 8:
                result.append(f'* Level skew detected on the link {status["Name"]}. '
                              f'Rx level is {level_rx}, Tx level is {level_tx}. '
                              f'Tx power is {power_rx} dBm, Rx power is {power_tx} dBm. '
                              f'Please pay attention.')
        except TypeError:
            logger.exception('Radio Level TypeError')
        finally:
            pass


    def check_snr(status):
        """Check SNR and return the conclusion."""

        try:
            snr_rx = int(status['SNR Rx'])
            snr_tx = int(status['SNR Tx'])

            if (snr_rx < 7 or snr_tx < 7) and radio_settings['Type'] == 'master':
                result.append(f'* The quality of the signal of the link {status["Name"]} is very low '
                              f'due to bad SNR (Rx {snr_rx}dB/Tx {snr_tx}dB). '
                              f'Only low-level modulations are available. '
                              f'Please improve the quality of the signal to reach better modulations. '
                              f'Possible solutions: '
                              f'1) Increase Tx power on the remote side; '
                              f'2) Find better frequency for the remote side '
                              f'(the spectrum analyzer can be used to do that); '
                              f'3) Reduce bandwidth on the master device '
                              f'in order to improve the sensitivity of the radio module. '
                              f'The current bandwidth is {radio_settings["Profile"]["M"]["Bandwidth"]} MHz.')
            elif (snr_rx < 7 or snr_tx < 7) and radio_settings['Type'] == 'slave':
                result.append('* The quality of the signal in the link {format(status["Name"]} is very low '
                              'due to bad SNR (Rx {snr_rx}dB/ Tx {snr_tx}dB). '
                              'Only low-level modulations are available. '
                              'Please improve the quality of the signal to reach better modulations. '
                              'Possible solutions: '
                              '1) Increase Tx power on the remote side; '
                              '2) Find better frequency for the remote side '
                              '(the spectrum analyzer can be used to do that); '
                              '3) Reduce bandwidth on the master device '
                              'in order to improve the sensitivity of the radio module.')
        except TypeError:
            logger.exception('Radio SNR TypeError')
        finally:
            pass


    def check_retries(status):
        """Check Retries and return the conclusion."""

        try:
            retries_rx = int(status['Retry Rx'])
            retries_tx = int(status['Retry Tx'])
            if retries_rx > 7 or retries_tx > 7:
                result.append(f'* Retries detected on the link {status["Name"]}. '
                              f'Rx {retries_rx}%/Tx {retries_tx}%. '
                              f'The recommended value is no more than 10%. '
                              f'Please pay attention.')
        except TypeError:
            logger.exception('Radio Retries TypeError')
        finally:
            pass


    radio_status = device.radio_status
    radio_settings = device.settings['Radio']
    result = []

    # Abnormal transmit power disbalance and calibrations
    pattern = re.search(r'Warning: Abnormal transmit power disbalance', device.dc_string)
    if pattern is not None:
        for index, line in enumerate(device.dc_list):
            pattern = re.search(r'rf5.0 Calibration', line)
            if pattern is not None:
                vpd_calc_start = index
            pattern = re.search(r'chain 1 count \d+ max \d+ min \d+ avg \d+ cur \d+', line)
            if pattern is not None:
                vpd_calc_end = index + 1
        vpd_calc = device.dc_list[vpd_calc_start:vpd_calc_end]
        vpd_pwr = [pwr for pwr in re.findall(r'([\-\d]+)', vpd_calc[2])]
        vpd_chain = re.findall(r'(chain \d count \d+ max \d+ min \d+ avg \d+ cur \d+)', ''.join(vpd_calc))
        vpd_calc = vpd_calc[3:len(vpd_calc) - 4]

        # Find each calibration partition
        pattern = re.compile(r'(-)+')
        slices = []
        for index, line in enumerate(vpd_calc):
            if pattern.search(line):
                slices.append(index)

        """
        Create a dictionary with calibrations
        {frequency: ({power levels : calibrations chain 0}, {power levels : calibrations chain 1})}
        """
        pattern_freq = re.compile(r'(\d+): vpd 0')
        pattern_cal = re.compile(r'(\d+)')
        vpd = {}
        for slice in slices:
            vpd_0 = pattern_cal.findall(vpd_calc[slice+1])[2:]
            vpd_0 = dict(zip(vpd_pwr, vpd_0))
            vpd_1 = pattern_cal.findall(vpd_calc[slice + 2])[1:]
            vpd_1 = dict(zip(vpd_pwr, vpd_1))
            vpd[pattern_freq.search(vpd_calc[slice+1]).group(1)] = (vpd_0, vpd_1)

        # Find Tx Power
        pwr = [device.radio_status['Links'][link]['Power Tx'] for link in device.radio_status['Links']]
        pwr = max(map(lambda x: int(x.replace('*', '')), pwr))

        # Find the closest calibration frequency to the current frequency
        vpd_freq = list(map(lambda x: abs(int(device.radio_status['Current Frequency']) - int(x)), vpd.keys()))
        vpd_freq_min_abs = min(vpd_freq)
        vpd_freq = vpd_freq.index(vpd_freq_min_abs)
        vpd_freq_cur = list(vpd.keys())[vpd_freq]

        # Find the closest calibration power to the current tx power
        vpd_pwr_cur = list(map(lambda x: abs(int(pwr) - int(x)), vpd_pwr))
        vpd_pwr_min_abs = min(vpd_pwr_cur)
        vpd_pwr_cur = vpd_pwr_cur.index(vpd_pwr_min_abs)
        vpd_pwr_cur = vpd_pwr[vpd_pwr_cur]
        vpd_0_cal = vpd[vpd_freq_cur][0][vpd_pwr_cur]
        vpd_1_cal = vpd[vpd_freq_cur][1][vpd_pwr_cur]

        result.append(f'* Abnormal transmit power disbalance detected. '
                      f'The radio module of the device {device.serial_number} may be faulty. \n'
                      f'Calibration for the current frequency ({device.radio_status["Current Frequency"]} MHz) '
                      f'and power ({pwr} dBm):\n'
                      f'VPD 0 - {vpd_0_cal}, VPD 1 - {vpd_1_cal}.\n'
                      f'Chains:\n'
                      f'{vpd_chain[0]}\n, {vpd_chain[1]}\n'
                      f'Please approve RMA if the calibrations are correct.')

    # Wireless link flaps (Too many retransmit/physical errors)
    flap_counter = 0
    links = {}
    problem_links = []
    for line in device.dc_list:
        pattern = re.search(r'Link "([\w\d]+)" \(([\w\d]+)\) '
                         r'DOWN: ".oo many ((transmit|physical) )?errors"', line)
        if pattern is not None:
            flap_counter += 1
            links[pattern.group(2)] = flap_counter, pattern.group(1)
    for link, counter in links.items():
        if counter[0] > 3:
            problem_links.append(counter[1])
    if problem_links:
        result.append(f'* Too many transmission errors (above a certain threshold) detected. '
                      f'Please pay attention to the links: {", ".join(problem_links)}. '
                      f'This issue may be caused by '
                      f'interference on the remote side.')

    # Wireless link flaps (No signal)
    flap_counter = 0
    links = {}
    problem_links = []
    for line in device.dc_list:
        pattern = re.search(r'Link "([\w\d]+)" \(([\w\d]+)\) '
                         r'DOWN: "no signal"', line)
        if pattern is not None:
            flap_counter += 1
            links[pattern.group(2)] = flap_counter, pattern.group(1)
    for link, counter in links.items():
        if counter[0] > 3:
            problem_links.append(counter[1])
    if problem_links:
        result.append(f'* No signal from the remote side detected. '
                      f'Please pay attention to the links: {", ".join(problem_links)}. ')

    # Wireless link flaps (Lost control/command channel)
    flap_counter = 0
    links = {}
    problem_links = []
    for line in device.dc_list:
        pattern = re.search(r'Link "([\w\d]+)" \(([\w\d]+)\) '
                         r'DOWN: ".ost (control|command) channel"', line)
        if pattern is not None:
            flap_counter += 1
            links[pattern.group(2)] = flap_counter, pattern.group(1)
    for link, counter in links.items():
        if counter[0] > 3:
            problem_links.append(counter[1])
    if problem_links:
        result.append(f'* Lost control channel detected. '
                      f'The device was not able to successfully send '
                      f'important service messages to the remote side. '
                      f'Please pay attention to the links: {", ".join(problem_links)}.')

    # Wireless link flaps (Timeout Expired)
    flap_counter = 0
    links = {}
    problem_links = []
    for line in device.dc_list:
        pattern = re.search(r'Link "([\w\d]+)" \(([\w\d]+)\) '
                         r'DOWN: ".imeout expired"', line)
        if pattern is not None:
            flap_counter += 1
            links[pattern.group(2)] = flap_counter, pattern.group(1)
    for link, counter in links.items():
        if counter[0] > 3:
            problem_links.append(counter[1])
    if problem_links:
        result.append(f'* The next links were timed out too many times '
                      f'due to lack of service and data traffic: {", ".join(problem_links)}. '
                      f'Please pay attention. ')

    # Wireless link flaps (Link reconnecting)
    flap_counter = 0
    links = {}
    problem_links = []
    for line in device.dc_list:
        pattern = re.search(r'Link "([\w\d]+)" \(([\w\d]+)\) '
                         r'DOWN: ".ink reconnecting"', line)
        if pattern is not None:
            flap_counter += 1
            links[pattern.group(2)] = flap_counter, pattern.group(1)
    for link, counter in links.items():
        if counter[0] > 5:
            problem_links.append(counter[1])
    if problem_links:
        result.append(f'* The next links were lost '
                      f'due to the remote side disconnected: {", ".join(problem_links)}. '
                      f'Please pay attention. ')

    # Wireless link flaps (System reconfiguration)
    flap_counter = 0
    links = {}
    problem_links = []
    for line in device.dc_list:
        pattern = re.search(r'Link "([\w\d]+)" \(([\w\d]+)\) '
                         r'DOWN: ".ystem reconfiguration"', line)
        if pattern is not None:
            flap_counter += 1
            links[pattern.group(2)] = flap_counter, pattern.group(1)
    for link, counter in links.items():
        if counter[0] > 5:
            problem_links.append(counter[1])
    if problem_links:
        result.append(f'* The next links were lost due to the configuration '
                      f'of the remote side was changed: {", ".join(problem_links)}. '
                      f'Please pay attention. ')

    # Interference
    scanner_rssi = []
    if radio_status['Interference PPS'] is not None \
            and float(radio_status['Interference PPS']) > 50:
        for link in radio_status['Links'].values():
            scanner_rssi.append(f'      {link["Name"]}: {link["RSSI Rx"]} dBm')
        scanner_rssi = '\n'.join(scanner_rssi)
        result.append(f'* A lot of pulses in the second ({radio_status["Interference PPS"]} pps) '
                      f'are detected. Perhaps there is interference. '
                      f'The interference RSSI is {radio_status["Interference RSSI"]} dBm.\n'
                      f'    The connected devices\' RSSI are: \n{scanner_rssi}\n'
                      f'Please find a better frequency or deal with '
                      f'it in another way.')

    if radio_status['Total Medium Busy'] is not None \
            and float(radio_status['Total Medium Busy'].replace('%', '')) > 50:
        result.append(f'* The spectrum is very noisy. '
                      f'Please find a better frequency or deal with '
                      f'it in another way. '
                      f'Total Medium Busy: {radio_status["Total Medium Busy"]}, '
                      f'RX Medium Load: {radio_status["RX Medium Load"]}, '
                      f'TX Medium Load: {radio_status["TX Medium Load"]}.')

    # Retries
    tx_packets = int(re.search(r'Transmitted OK\s+(\d+)', device.dc_string).group(1))
    retries_excessive = int(radio_status['Excessive Retries'])
    ratio_tx_ret = round((retries_excessive / tx_packets) * 100, 2)
    if ratio_tx_ret > 0.5:
        result.append(f'* Too many Exscessive Retries ({retries_excessive}) detected. '
                      f'The Exscessive Retries are the number of frames '
                      f'failed to send after all attempts to resend. '
                      f'In other words, completely lost. '
                      f'The number of retransmission attempts can be '
                      f'configured with the CLI command: "rf rf5.0 txrt <number>"'
                      f'(TDMA default value is 10, MINT default value is 5. '
                      f'This is an absolute counter that starts '
                      f'counting from the device\'s boot time. '
                      f'So, please consider uptime ({device.uptime}) during analyze. '
                      f'Retries to Tx frames ratio is {ratio_tx_ret}%. '
                      f'It is recommended this value be kept below 0.5%. '
                      f'Perhaps there may be issue with radio links.\n')

    # Check each link
    for status in radio_status['Links'].values():
        check_rssi(status)
        check_power(status)
        check_level(status)
        check_snr(status)
        check_retries(status)

    # Polling status
    if 'MINT' in device.firmware and device.settings['Radio']['Polling'] == 'Disabled':
        result.append('* Polling disabled. '
                      'It is strongly recommend to enabled it.')

    result = list(set(result))
    if result:
        logger.info('Radio test failed')
        return ('Radio issues', result)
    else:
        logger.info('Radio test passed')
        pass


logger = logging.getLogger('logger.r5000_radio_check')
