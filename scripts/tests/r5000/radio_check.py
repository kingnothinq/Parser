#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search


def test(device):
    """Check radio parameters and return conclusion."""


    def check_rssi(status):
        """Check RSSI and return the conclusion."""

        rssi = float(status['RSSI Rx'])
        if rssi > -40:
            result.append('* RSSI is {} dBm. Please decrease Tx power on '
                          'the remote device {} in order to avoid damage '
                          'to the radio module. '
                          'It is not recommended RSSI greater than -40.'.format(rssi, status['Name']))
        elif rssi < -80:
            result.append('* RSSI is {} dBm. Please increase Tx power on '
                          'the remote device {} in order to avoid damage '
                          'to the radio module. '
                          'It is not recommended RSSI less than -80.'.format(rssi, status['Name']))

    def check_level(status):
        """Check Level and return the conclusion."""

        level_rx = int(status['Level Rx'])
        level_tx = int(status['Level Tx'])
        power_rx = int(status['Power Rx'])
        power_tx = int(status['Power Tx'])
        snr_rx = int(status['SNR Rx'])
        snr_tx = int(status['SNR Tx'])
        power_skew = abs(power_rx - power_tx)
        level_skew = abs(level_rx - level_tx)
        snr_skew = abs(snr_rx - snr_tx)
        total_skew = abs(snr_skew - level_skew)
        if power_skew != level_skew and total_skew > 8:
            result.append('* Level skew detected on the link {}. '
                          'Rx level is {}, Tx level is {}. '
                          'Tx power is {} dBm, Rx power is {} dBm. '
                          'Please pay attention.'.format(status['Name'], level_rx, level_tx, power_rx, power_tx))

    def check_snr(status):
        """Check SNR and return the conclusion."""

        snr_rx = int(status['SNR Rx'])
        snr_tx = int(status['SNR Tx'])
        for
        if (snr_rx < 7 or snr_tx < 7) and device.settings['Radio']['Type'] == 'master':
            result.append('* The quality of the signal of the link {} is very low '
                          'due to bad SNR (Rx {}dB/Tx {}dB). '
                          'Only low-level modulations are available. '
                          'Please improve the quality of the signal to reach better modulations. '
                          'Possible solutions: '
                          '1) Increase Tx power on the remote side; '
                          '2) Find better frequency for the remote side (the spectrum analyzer can be used to do that); '
                          '3) Reduce bandwidth on the master device '
                          'in order to improve the sensitivity of the radio module. '
                          'The current bandwidth is {} MHz.'.format(status['Name'], snr_rx, snr_tx,
                                                                    device.settings['Radio']['Profile']['Bandwidth']))
        elif (snr_rx < 7 or snr_tx < 7) and device.settings['Radio']['Type'] == 'slave':
            result.append('* The quality of the signal in the link {} is very low '
                          'due to bad SNR (Rx {}dB/ Tx {}dB). '
                          'Only low-level modulations are available. '
                          'Please improve the quality of the signal to reach better modulations. '
                          'Possible solutions: '
                          '1) Increase Tx power on the remote side; '
                          '2) Find better frequency for the remote side (the spectrum analyzer can be used to do that); '
                          '3) Reduce bandwidth on the master device '
                          'in order to improve the sensitivity of the radio module.'.format(status['Name'], snr_rx,
                                                                                            snr_tx))

    def check_retries(status):
        """Check Retries and return the conclusion."""

        retries_rx = int(status['Retry Rx'])
        retries_tx = int(status['Retry Tx'])
        if retries_rx > 7 or retries_tx > 7:
            result.append('* Retries detected on the link {}. '
                          'Rx {}%/Tx {}%. '
                          'The recommended value is no more than 10%. '
                          'Please pay attention.'.format(status['Name'], retries_rx, retries_tx))

    radio_status = device.radio_status
    result = []

    pattern = search(r'Warning: Abnormal transmit power disbalance', device.dc_string)
    if pattern is not None:
        vpd_start = device.dc_list.index('rf5.0 Calibration\n')
        pattern = search(r'chain 1 count \d+ max \d+ min \d+ avg \d+ cur \d+', device.dc_string).group()
        vpd_end = device.dc_list.index(pattern + '\n')
        vpd_calc = '      '.join(device.dc_list[vpd_start - 1:vpd_end + 1])
        result.append('* Abnormal transmit power disbalance detected. '
                      'The radio module of the device {} may be faulty. \n'
                      '{}\n'
                      'Please approve RMA if the calibrations are correct.'.format(device.serial_number, vpd_calc))

    flap_counter = 0
    links = {}
    problem_links = []
    for line in device.dc_list:
        pattern = search(r'Link "([\w\d]+)" \(([\w\d]+)\) '
                         r'DOWN: ".oo many ((transmit|physical) )?errors"', line)
        if pattern is not None:
            flap_counter += 1
            links[pattern.group(2)] = flap_counter, pattern.group(1)
    for link, counter in links.items():
        if counter[0] > 3:
            problem_links.append(counter[1])
    if problem_links:
        result.append('* Too many transmission errors (above a certain threshold) detected. '
                      'Please pay attention to the links: {}. '
                      'This issue may be caused by '
                      'interference on the remote side.'.format(', '.join(problem_links)))

    flap_counter = 0
    links = {}
    problem_links = []
    for line in device.dc_list:
        pattern = search(r'Link "([\w\d]+)" \(([\w\d]+)\) '
                         r'DOWN: "no signal"', line)
        if pattern is not None:
            flap_counter += 1
            links[pattern.group(2)] = flap_counter, pattern.group(1)
    for link, counter in links.items():
        if counter[0] > 3:
            problem_links.append(counter[1])
    if problem_links:
        result.append('* No signal from the remote side detected. '
                      'Please pay attention to the links: {}. '.format(', '.join(problem_links)))

    flap_counter = 0
    links = {}
    problem_links = []
    for line in device.dc_list:
        pattern = search(r'Link "([\w\d]+)" \(([\w\d]+)\) '
                         r'DOWN: ".ost (control|command) channel"', line)
        if pattern is not None:
            flap_counter += 1
            links[pattern.group(2)] = flap_counter, pattern.group(1)
    for link, counter in links.items():
        if counter[0] > 3:
            problem_links.append(counter[1])
    if problem_links:
        result.append('* Lost control channel detected. '
                      'The device was not able to successfully send '
                      'important service messages to the remote side. '
                      'Please pay attention to the links: {}.'.format(', '.join(problem_links)))

    flap_counter = 0
    links = {}
    problem_links = []
    for line in device.dc_list:
        pattern = search(r'Link "([\w\d]+)" \(([\w\d]+)\) '
                         r'DOWN: ".imeout expired"', line)
        if pattern is not None:
            flap_counter += 1
            links[pattern.group(2)] = flap_counter, pattern.group(1)
    for link, counter in links.items():
        if counter[0] > 3:
            problem_links.append(counter[1])
    if problem_links:
        result.append('* The next links were timed out too many times '
                      'due to lack of service and data traffic: {}. '
                      'Please pay attention. '.format(', '.join(problem_links)))

    flap_counter = 0
    links = {}
    problem_links = []
    for line in device.dc_list:
        pattern = search(r'Link "([\w\d]+)" \(([\w\d]+)\) '
                         r'DOWN: ".ink reconnecting"', line)
        if pattern is not None:
            flap_counter += 1
            links[pattern.group(2)] = flap_counter, pattern.group(1)
    for link, counter in links.items():
        if counter[0] > 5:
            problem_links.append(counter[1])
    if problem_links:
        result.append('* The next links were lost '
                      'due to the remote side disconnected: {}. '
                      'Please pay attention. '.format(', '.join(problem_links)))

    flap_counter = 0
    links = {}
    problem_links = []
    for line in device.dc_list:
        pattern = search(r'Link "([\w\d]+)" \(([\w\d]+)\) '
                         r'DOWN: ".ystem reconfiguration"', line)
        if pattern is not None:
            flap_counter += 1
            links[pattern.group(2)] = flap_counter, pattern.group(1)
    for link, counter in links.items():
        if counter[0] > 5:
            problem_links.append(counter[1])
    if problem_links:
        result.append('* The next links were lost due to the configuration '
                      'of the remote side was changed: {}. '
                      'Please pay attention. '.format(', '.join(problem_links)))

    scanner_rssi = []
    if float(radio_status['Interference PPS']) > 50:
        for link in radio_status['Links'].values():
            scanner_rssi.append('      {}: {} dBm'.format(link['Name'], link['RSSI Rx']))
        scanner_rssi = '\n'.join(scanner_rssi)
        result.append('* A lot of pulses in the second ({} pps) are detected. '
                      'Perhaps there is interference. '
                      'The interference RSSI is {} dBm.\n'
                      '    The connected devices\' RSSI are: \n{}\n'
                      'Please find a better frequency or deal with '
                      'it in another way.'.format(radio_status['Interference PPS'], radio_status['Interference RSSI'],
                                                  scanner_rssi))

    if float(radio_status['Total Medium Busy'].replace('%', '')) > 50:
        result.append('* The spectrum is very noisy. '
                      'Please find a better frequency or deal with '
                      'it in another way. '
                      'Total Medium Busy: {}, '
                      'RX Medium Load: {}, '
                      'TX Medium Load: {}.'.format(radio_status['Total Medium Busy'], radio_status['RX Medium Load'],
                                                   radio_status['TX Medium Load']))

    tx_packets = int(search(r'Transmitted OK\s+(\d+)', device.dc_string).group(1))
    retries_excessive = int(radio_status['Excessive Retries'])
    ratio_tx_ret = round((retries_excessive / tx_packets) * 100, 2)
    counter = 0
    for line in device.dc_list:
        counter += 1
        if line.startswith('           MAC          Out/Rep'):
            muffer_start = counter - 2
        if line.startswith('IP statistics:'):
            muffer_end = counter - 2
    muffer = '      '.join(device.dc_list[muffer_start:muffer_end])
    if ratio_tx_ret > 0.5:
        result.append('* Too many Exscessive Retries ({}) detected. '
                      'The Exscessive Retries are the number of frames '
                      'failed to send after all attempts to resend. '
                      'In other words, completely lost. '
                      'The number of retransmission attempts can be '
                      'configured with the CLI command: "rf rf5.0 txrt <number>"'
                      '(TDMA default value is 10, MINT default value is 5. '
                      'This is an absolute counter that starts '
                      'counting from the device\'s boot time. '
                      'So, please consider uptime ({}) during analyze. '
                      'Retries to Tx frames ratio is {}%. '
                      'It is recommended this value be kept below 0.5%. '
                      'Perhaps there may be issue with radio links.\n'
                      '    Muffer: {}'.format(retries_excessive, device.uptime, ratio_tx_ret, muffer))

    for status in radio_status['Links'].values():
        check_rssi(status)
        check_level(status)
        check_snr(status)
        check_retries(status)

    if 'MINT' in device.firmware and device.settings['Radio']['Polling'] == 'Disabled':
        result.append('* Polling disabled. '
                      'It is strongly recommend to enabled it.')

    if result:
        return '\nRadio issues: \n' + '\n'.join(result)
    else:
        pass