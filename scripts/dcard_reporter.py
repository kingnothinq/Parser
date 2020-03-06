#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search

from jira import JIRA


def r5000_report(device):
    settings = device.settings
    radio_settings = settings['Radio']
    radio_status = device.radio_status
    ethernet_status = device.ethernet_status
    message = []

    # Show settings
    message.append('Settings: ')
    message.append(' Role: {}'.format(str.capitalize(radio_settings['Type'])))

    for profile in radio_settings['Profile'].items():
        # print(profile)
        pass

    if True:
        pass  # message.append(' Frequency: {} MHz'.format(radio_settings['Profile']['Frequency']))
    else:
        for id, profile in settings['Radio']['Profile'].items():
            pass

    return '\n'.join(message)


def xg_report(device):
    """Show parsed information."""

    def radio_message(carrier, carrier_name):
        """Show information about carriers."""

        message.append('  ' + carrier_name + ':\n'
                                             '   Current Tx Frequency: {};\n'
                                             '   Stream 0 RSSI: {}, '
                                             'Stream 1 RSSI: {};\n'
                                             '   Stream 0 CINR: {}, '
                                             'Stream 1 CINR: {};\n'
                                             '   Stream 0 MCS: {}, '
                                             'Stream 1 MCS: {};\n'
                                             '   Stream 0 Errors: {}, '
                                             'Stream 1 Errors: {}. '
                       .format(carrier['Frequency'],
                               carrier['Stream 0']['RSSI'],
                               carrier['Stream 1']['RSSI'],
                               carrier['Stream 0']['CINR'],
                               carrier['Stream 1']['CINR'],
                               carrier['Stream 0']['MCS'],
                               carrier['Stream 1']['MCS'],
                               carrier['Stream 0']['Errors Ratio'],
                               carrier['Stream 1']['Errors Ratio']))

    settings = device.settings
    radio_status = device.radio_status
    master = radio_status['Master']
    slave = radio_status['Slave']
    ethernet_status = device.ethernet_status
    message = []

    # Show settings
    message.append('Settings: ')
    message.append(' Role: {}'.format(str.capitalize(settings['Role'])))
    if device.subfamily == 'XG 500':
        message.append(' Frequencies: '
                       'Carrier 0 DL - {} MHz, '
                       'Carrier 0 UL - {} MHz.'
                       .format(settings['DL Frequency']['Carrier 0'],
                               settings['UL Frequency']['Carrier 0']))
    else:
        message.append(' Frequencies: '
                       'Carrier 0 DL - {} MHz, '
                       'Carrier 0 UL - {} MHz, '
                       'Carrier 1 DL - {} MHz, '
                       'Carrier 1 UL - {} MHz.'
                       .format(settings['DL Frequency']['Carrier 0'],
                               settings['UL Frequency']['Carrier 0'],
                               settings['DL Frequency']['Carrier 1'],
                               settings['UL Frequency']['Carrier 1']))
    message.append(' Bandwidth: {} MHz.'.format(settings['Bandwidth']))
    message.append(' Frame size: {} ms.'.format(settings['Frame size']))
    message.append(' DL/UL Ratio: {}.'.format(settings['DL/UL Ratio']))
    message.append(' Control Block Boost: {}.'.format(settings['Control Block Boost']))
    message.append(' Short CP: {}.'.format(settings['Short CP']))
    message.append(' IDFS: {}.'.format(settings['IDFS']))
    message.append(' Traffic prioritization: {}.'.format(settings['Traffic prioritization']))
    message.append(' Tx Power: {} dBm.'.format(settings['Tx Power']))
    message.append(' ATPC: {}.'.format(settings['ATPC']))
    if settings['ATPC'] == 'Enabled':
        message.append(' AMC Strategy: {}.'.format(str.capitalize(settings['AMC Strategy'])))
    message.append(' Max MCS: {}.'.format(settings['Max MCS']))
    message.append('\n')

    # Show Radio Status
    message.append('Radio: ')
    message.append(' Link status: {}.'.format(radio_status['Link status']))
    message.append(' Measured Distance: {}.'.format(radio_status['Measured Distance']))

    if device.subfamily == 'XG 500':
        message.append(' * Master: ')
        message.append('  Role: {}.'.format(master['Role']))
        radio_message(master['Carrier 0'], 'Carrier 0')
        message.append(' * Slave: ')
        message.append('  Role: {}.'.format(slave['Role']))
        radio_message(slave['Carrier 0'], 'Carrier 0')
    elif device.subfamily == 'XG 1000':
        message.append(' * Master: ')
        message.append('  Role: {}.'.format(master['Role']))
        for carrier in ['Carrier 0', 'Carrier 1']:
            radio_message(master[carrier], carrier)
        message.append(' * Slave: ')
        message.append('  Role: {}.'.format(slave['Role']))
        for carrier in ['Carrier 0', 'Carrier 1']:
            radio_message(slave[carrier], carrier)

    message.append('\n')

    # Show Ethernet Status
    message.append('Interfaces: ')
    for interface in ethernet_status:
        message.append(' {} is {}.'.format(interface, ethernet_status[interface]['Status']))
    message.append('\n')

    return '\n'.join(message)


def quanta_report(device):
    """Show parsed information."""

    def radio_message(carrier):
        """Show information about carriers."""

        message.append('  Stream 0 RSSI: {}, '
                       'Stream 1 RSSI: {};\n'
                       '  Stream 0 EVM: {}, '
                       'Stream 1 EVM: {};\n'
                       '  Stream 0 Crosstalk: {}, '
                       'Stream 1 Crosstalk: {};\n'
                       '  Stream 0 MCS: {}, '
                       'Stream 1 MCS: {};\n'
                       '  Stream 0 ARQ ratio: {}, '
                       'Stream 1 ARQ ratio: {}. '
                       .format(carrier['Stream 0']['RSSI'],
                               carrier['Stream 1']['RSSI'],
                               carrier['Stream 0']['EVM'],
                               carrier['Stream 1']['EVM'],
                               carrier['Stream 0']['Crosstalk'],
                               carrier['Stream 1']['Crosstalk'],
                               carrier['Stream 0']['MCS'],
                               carrier['Stream 1']['MCS'],
                               carrier['Stream 0']['ARQ ratio'],
                               carrier['Stream 1']['ARQ ratio']))

    settings = device.settings
    radio_status = device.radio_status
    downlink = radio_status['Downlink']
    uplink = radio_status['Uplink']
    ethernet_status = device.ethernet_status['ge0']
    message = []

    # Show settings
    message.append('Settings: ')
    message.append(' Role: {}.'.format(str.capitalize(settings['Role'])))
    message.append(' Frequencies: DL - {} MHz, UL - {} MHz.'
                   .format(settings['DL Frequency'], settings['UL Frequency']))
    message.append(' Bandwidth: {} MHz.'.format(settings['Bandwidth']))
    message.append(' Frame size: {} ms.'.format(settings['Frame size']))
    message.append(' Guard Interval: {}.'.format(settings['Guard Interval']))

    pattern = search(r'(\d+)( \((\w+)\))?', settings['DL/UL Ratio'])
    if pattern.group(3) is not None:
        message.append(' DL/UL Ratio: {}/{} ({}).'
                       .format(pattern.group(1), 100 - int(pattern.group(1)), pattern.group(3)))
    else:
        message.append(' DL/UL Ratio: {}/{}.'
                       .format(pattern.group(1), 100 - int(pattern.group(1))))

    message.append(' DFS: {}.'.format(settings['DFS']))
    message.append(' ARQ: {}.'.format(settings['ARQ']))
    message.append(' Tx Power: {} dBm.'.format(settings['Tx Power']))
    message.append(' ATPC: {}.'.format(settings['ATPC']))
    if settings['ATPC'] == 'Enabled':
        message.append(' AMC Strategy: {}.'
                       .format(str.capitalize(settings['AMC Strategy'])))
    message.append(' Max MCS: DL - {}, UL - {}.'
                   .format(settings['Max DL MCS'], settings['Max UL MCS']))
    message.append('\n')

    # Show Radio Status
    message.append('Radio: ')
    message.append(' Link status: {}.'.format(radio_status['Link status']))
    message.append(' Measured Distance: {}.'.format(radio_status['Measured Distance']))
    message.append(' * Downlink: ')
    radio_message(downlink)
    message.append(' * Uplink: ')
    radio_message(uplink)

    message.append('\n')

    # Show Ethernet Status
    message.append('Interfaces: ')
    message.append(' Ge0 is {}.'.format(ethernet_status['Status']))
    message.append('\n')

    return '\n'.join(message)


def create_report(device, tests_report, dc_path):
    """Create a report."""

    message_1 = '\nParsing diagnostic card: {}'.format(dc_path.name)
    message_1_complete = '{}{}\n{}\n'.format('-' * len(message_1), message_1,
                                             '-' * len(message_1))
    message_2 = 'Serial Number is {}\nModel is {}\n' \
                'Firmware version: {}\n' \
        .format(device.serial_number, device.model, device.firmware)

    if device.family == 'R5000':
        message_3 = r5000_report(device)
    elif device.family == 'XG':
        message_3 = xg_report(device)
    elif device.family == 'Quanta':
        message_3 = quanta_report(device)

    message_4 = 'This device is OK.\n'
    message_5 = 'The next issues were detected:'

    if not list(filter(None, tests_report)):
        report_text = [message_1_complete, message_2, message_3, message_4]
    else:
        report_text = [message_1_complete, message_2, message_3, message_5] + list(
                filter(None, tests_report))

    return report_text


def error_report(dc_path):
    """Create an error report."""

    message_1 = '\nParsing diagnostic card: {}'.format(dc_path.name)
    message_1_complete = '{}{}\n{}\n'.format('-' * len(message_1), message_1,
                                             '-' * len(message_1))
    message_2 = 'This is not a valid diagnostic card. Please analyze it manually.'

    report_text = [message_1_complete, message_2]

    return report_text


def write_report(report_text, serial_number):
    """Save report."""

    report_name = 'diagcard_{}_report.txt'.format(serial_number)
    report_path = Path.joinpath(Path.cwd() / 'reports', report_name)

    # Create a folder if it does not exist
    if Path.is_dir(report_path.parent) is False:
        Path.mkdir(report_path.parent)

    report_name_counter = 0
    while Path.exists(report_path):
        report_name_counter += 1
        report_name = 'diagcard_{}_report_{}.txt'.format(
                serial_number, report_name_counter)
        report_path = Path.joinpath(Path.cwd() / 'reports', report_name)

    # Write report in the folder
    with open(report_path, 'w') as report:
        for line in report_text:
            report.write(line)


def jira_report(report):
    """Send report in Jira."""

    jira_options = {'server':'https://jira.infinet.ru/'}
    login = input('Login: ')
    password = input('Password: ')
    jira = JIRA(options=jira_options, basic_auth=(login, password))
    comment = jira.add_comment('DESK-53647', '\n'.join(report))

    return comment


def debug_report(report_text):
    """Print report in console."""

    for line in report_text:
        print(line)