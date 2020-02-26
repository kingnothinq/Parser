#!/usr/bin/python
# -*- coding: utf-8 -*-

def r5000_report(device):
    pass


def xg_report(device):
    """Show parsed information"""

    settings = device.settings
    radio_status = device.radio_status
    master = radio_status['Master']
    slave = radio_status['Slave']
    ethernet_status = device.ethernet_status

    message = []

    # Show settings
    message.append('Settings: ')
    message.append('Role: {}'.format(str.capitalize(settings['Role'])))
    if device.subfamily == 'XG 500':
        message.append('Frequencies: '
                       'Carrier 0 DL - {} MHz, '
                       'Carrier 0 UL - {} MHz'
                       .format(settings['DL Frequency']['Carrier 0'],
                               settings['UL Frequency']['Carrier 0']))
    else:
        message.append('Frequencies: '
                       'Carrier 0 DL - {} MHz, '
                       'Carrier 0 UL - {} MHz, '
                       'Carrier 1 DL - {} MHz, '
                       'Carrier 1 UL - {} MHz'
                       .format(settings['DL Frequency']['Carrier 0'],
                               settings['UL Frequency']['Carrier 0'],
                               settings['DL Frequency']['Carrier 1'],
                               settings['UL Frequency']['Carrier 1']))
    message.append('Bandwidth: {} MHz'.format(settings['Bandwidth']))
    message.append('Frame size: {} ms'.format(settings['Frame size']))
    message.append('UL/DL Ratio: {}'.format(settings['UL/DL Ratio']))
    message.append('Control Block Boost: {}'.format(settings['Control Block Boost']))
    message.append('Short CP: {}'.format(settings['Short CP']))
    message.append('IDFS: {}'.format(settings['IDFS']))
    message.append('Traffic prioritization: {}'.format(settings['Traffic prioritization']))
    message.append('Tx Power: {} dBm'.format(settings['Tx Power']))
    message.append('ATPC: {}'.format(settings['ATPC']))
    if settings['ATPC'] == 'Enabled':
        message.append('AMC Strategy: {}'.format(str.capitalize(settings['AMC Strategy'])))
    message.append('Max MCS: {}'.format(settings['Max MCS']))
    message.append('\n')

    # Show Radio Status (Nado peredelat)
    message.append('Radio: ')
    message.append('Link status: {}'.format(radio_status['Link status']))
    message.append('Measured Distance: {}'.format(radio_status['Measured Distance']))

    if device.subfamily == 'XG 500':

        master = master['Carrier 0']
        slave = slave['Carrier 0']

        message.append('* Master: ')
        message.append('Role: {}'.format(master['Role']))
        message.append('Carrier 0:'
                       'Stream 0 RSSI: {} dBm, '
                       'Stream 1 RSSI: {} dBm \n'
                       'Stream 0 CINR: {} dB, '
                       'Stream 1 CINR: {} dB \n'
                       'Stream 0 MCS: {}, '
                       'Stream 1 MCS: {} \n'
                       'Stream 0 Errors: {}, '
                       'Stream 1 Errors: {} \n'
                       .format(master['Stream 0']['RSSI'],
                               master['Stream 1']['RSSI'],
                               master['Stream 0']['CINR'],
                               master['Stream 1']['CINR'],
                               master['Stream 0']['MCS'],
                               master['Stream 0']['MCS'],
                               master['Stream 0']['Errors Ratio'],
                               master['Stream 0']['Errors Ratio']))

        message.append('* Slave: ')
        message.append('Role: {}'.format(slave['Role']))
        message.append('Carrier 0:'
                       'Stream 0 RSSI: {}, '
                       'Stream 1 RSSI: {} \n'
                       'Stream 0 CINR: {}, '
                       'Stream 1 CINR: {} \n'
                       'Stream 0 MCS: {}, '
                       'Stream 1 MCS: {} \n'
                       'Stream 0 Errors: {}, '
                       'Stream 1 Errors: {} \n'
                       .format(slave['Stream 0']['RSSI'],
                               slave['Stream 1']['RSSI'],
                               slave['Stream 0']['CINR'],
                               slave['Stream 1']['CINR'],
                               slave['Stream 0']['MCS'],
                               slave['Stream 0']['MCS'],
                               slave['Stream 0']['Errors Ratio'],
                               slave['Stream 0']['Errors Ratio']))

    else:
        message.append('* Master: ')
        message.append('Role: {}'.format(master['Role']))
        message.append('Carrier 0:'
                       'Stream 0 RSSI: {}, '
                       'Stream 1 RSSI: {} \n'
                       'Stream 0 CINR: {}, '
                       'Stream 1 CINR: {} \n'
                       'Stream 0 MCS: {}, '
                       'Stream 1 MCS: {} \n'
                       'Stream 0 Errors: {}, '
                       'Stream 1 Errors: {} \n'
                       .format(master['Carrier 0']['Stream 0']['RSSI'],
                               master['Carrier 0']['Stream 1']['RSSI'],
                               master['Carrier 0']['Stream 0']['CINR'],
                               master['Carrier 0']['Stream 1']['CINR'],
                               master['Carrier 0']['Stream 0']['MCS'],
                               master['Carrier 0']['Stream 0']['MCS'],
                               master['Carrier 0']['Stream 0']['Errors Ratio'],
                               master['Carrier 0']['Stream 0']['Errors Ratio']))
        message.append('Carrier 1:'
                       'Stream 0 RSSI: {}, '
                       'Stream 1 RSSI: {} \n'
                       'Stream 0 CINR: {}, '
                       'Stream 1 CINR: {} \n'
                       'Stream 0 MCS: {}, '
                       'Stream 1 MCS: {} \n'
                       'Stream 0 Errors: {}, '
                       'Stream 1 Errors: {} \n'
                       .format(master['Carrier 1']['Stream 0']['RSSI'],
                               master['Carrier 1']['Stream 1']['RSSI'],
                               master['Carrier 1']['Stream 0']['CINR'],
                               master['Carrier 1']['Stream 1']['CINR'],
                               master['Carrier 1']['Stream 0']['MCS'],
                               master['Carrier 1']['Stream 0']['MCS'],
                               master['Carrier 1']['Stream 0']['Errors Ratio'],
                               master['Carrier 1']['Stream 0']['Errors Ratio']))

        message.append('* Slave: ')
        message.append('Role: {}'.format(slave['Role']))
        message.append('Carrier 0:'
                       'Stream 0 RSSI: {}, '
                       'Stream 1 RSSI: {} \n'
                       'Stream 0 CINR: {}, '
                       'Stream 1 CINR: {} \n'
                       'Stream 0 MCS: {}, '
                       'Stream 1 MCS: {} \n'
                       'Stream 0 Errors: {}, '
                       'Stream 1 Errors: {} \n'
                       .format(slave['Carrier 0']['Stream 0']['RSSI'],
                               slave['Carrier 0']['Stream 1']['RSSI'],
                               slave['Carrier 0']['Stream 0']['CINR'],
                               slave['Carrier 0']['Stream 1']['CINR'],
                               slave['Carrier 0']['Stream 0']['MCS'],
                               slave['Carrier 0']['Stream 0']['MCS'],
                               slave['Carrier 0']['Stream 0']['Errors Ratio'],
                               slave['Carrier 0']['Stream 0']['Errors Ratio']))
        message.append('Carrier 1:'
                       'Stream 0 RSSI: {}, '
                       'Stream 1 RSSI: {} \n'
                       'Stream 0 CINR: {}, '
                       'Stream 1 CINR: {} \n'
                       'Stream 0 MCS: {}, '
                       'Stream 1 MCS: {} \n'
                       'Stream 0 Errors: {}, '
                       'Stream 1 Errors: {} \n'
                       .format(slave['Carrier 1']['Stream 0']['RSSI'],
                               slave['Carrier 1']['Stream 1']['RSSI'],
                               slave['Carrier 1']['Stream 0']['CINR'],
                               slave['Carrier 1']['Stream 1']['CINR'],
                               slave['Carrier 1']['Stream 0']['MCS'],
                               slave['Carrier 1']['Stream 0']['MCS'],
                               slave['Carrier 1']['Stream 0']['Errors Ratio'],
                               slave['Carrier 1']['Stream 0']['Errors Ratio']))
    message.append('\n')

    # Show Ethernet Status
    message.append('Interfaces: ')
    for interface in ethernet_status:
        message.append('Interface {} is {}'.format(interface, ethernet_status[interface]['Status']))
    message.append('\n')

    return '\n'.join(message)


def quanta_report(device):
    pass


def create_report(device, tests_report, dc_path):
    """Create report"""

    message_1 = '\nParsing diagnostic card: {}'.format(dc_path)
    message_1_complete = '{}{}\n{}\n'.format('-' * len(message_1), message_1,
                                             '-' * len(message_1))
    message_2 = 'Serial Number is {}\nModel is {}\n'.format(device.serial_number, device.model)

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


def write_report(report_text, serial_number):
    """Save report"""

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


def debug_report(report_text):
    """Print report in console"""

    for line in report_text:
        print(line)