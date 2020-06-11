# -*- coding: utf-8 -*-

import logging
import re
from copy import deepcopy
from time import time


def timer(function):
    def wrapper(dc_string, dc_list):
        time_start = time()
        created_class = function(dc_string, dc_list)
        time_end = time()
        logger.info(f'Diagnostic card parsed, Elapsed Time: {time_end - time_start}')
        return created_class
    return wrapper


@timer
def parse(dc_string, dc_list):
    """Parse a XG diagnostic card and fill the class instance in.

    This function returns result (the class instance) included the next variables:
    model (type str) - a device model
    subfamily (type str) - XG 500, XG 1000
    serial_number (type str) - a serial number
    firmware (type str) - an installed firmware
    uptime (type str) - device's uptime
    reboot_reason (type str) - a last reboot reason
    dc_list (type list) - a diagnostic card text as a list (array of strings divided by \n)
    dc_string (type str) - a diagnostic card text as a string (whole text in the string)
    settings (type dict) - all important settings (in more detail below)
    radio_status (type dict) - information about all wireless links (in more detail below)
    ethernet_status (type dict) - information about all wire links (in more detail below)
    panic (type set) - panic and asserts as a set

    __________________
    settings structure
        Role
        Bandwidth
        DL Frequency OR UL Frequency
            Carrier 0
            Carrier 1 (XG 1000 Only)
        Short CP
        Max distance
        Frame size
        DL/UL Ratio
        Tx Power
        Control Block Boost
        ATPC
        AMC Strategy
        Max MCS
        IDFS
        Traffic prioritization
        Interface Status
            ge0
            ge1
            sfp
            radio

    Example of request: settings['DL Frequency']['Carrier 0']

    ______________________
    radio_status structure
        Link status
        Measured Distance
        Master OR Slave
            Role
            Carrier 0 OR Carrier 1 (XG 1000 Only)
                Frequency
                DFS
                Rx Acc FER
                Stream 0 OR Stream 1
                    Tx Power
                    Tx Gain
                    MCS
                    CINR
                    RSSI
                    Crosstalk
                    Errors Ratio

    Example of request: radio_status['Master']['Carrier 0']['Stream 0']['Tx Power']

    _________________________
    ethernet_status structure
        eth0 OR eth1 (R5000 Lite Only)
            Status
            Speed
            Duplex
            Negotiation
            Rx CRC
            Tx CRC

    Example of request: ethernet_status['eth0']['Speed']
    """

    def no_empty(pattern):
        """Remove empty string."""

        for key_1, value_1 in enumerate(pattern):
            pattern[key_1] = list(value_1)
            for key_2, value_2 in enumerate(pattern[key_1]):
                if value_2 == '' or value_2 == '---' or value_2 == '--- dB' or value_2 == '--- dBm':
                    pattern[key_1][key_2] = None
            pattern[key_1] = tuple(pattern[key_1])

        return pattern

    # General info
    try:
        model = re.search(r'(([XU]m/\dX?.\d{3,4}.\dx\d{3})(.2x\d{2})?)', dc_string).group(1)
        if '500.2x500' in model:
            subfamily = 'XG 500'
        else:
            subfamily = 'XG 1000'
    except:
        model = 'XG Unknown model'
        subfamily = 'XG 500'
    logger.debug(f'Model: {model}; Subfamily: {subfamily}')

    serial_number = re.search(r'SN:(\d+)', dc_string).group(1)
    logger.debug(f'SN: {serial_number}')

    firmware = re.search(r'#\sXG\sWANFleX\s(\bH\d{2}S\d{2}[v\d.-]+\b)', dc_string).group(1)
    logger.debug(f'Firmware: {firmware}')

    uptime = re.findall(r'Uptime: ([\d\w :]*)', dc_string)[0]
    logger.debug(f'Uptime: {uptime}')

    reboot_reason = re.search(r'Last reboot reason: ([\w ]*)', dc_string).group(1)
    logger.debug(f'Last reboot reason: {reboot_reason}')

    # Settings
    settings = {'Role': None, 'Bandwidth': None, 'DL Frequency': {'Carrier 0': None, 'Carrier 1': None},
                'UL Frequency': {'Carrier 0': None, 'Carrier 1': None}, 'Short CP': None, 'Max distance': None,
                'Frame size': None, 'DL/UL Ratio': None, 'Tx Power': None, 'Control Block Boost': None, 'ATPC': None,
                'AMC Strategy': None, 'Max MCS': None, 'IDFS': None, 'Traffic prioritization': None,
                'Interface Status': {'Ge0': None, 'Ge1': None, 'SFP': None, 'Radio': None}}

    settings['Role'] = re.search(r'# xg -type( |=)(\w+)', dc_string).group(2)
    settings['Bandwidth'] = re.search(r'# xg -channel-width( |=)(\d+)', dc_string).group(2)

    pattern = re.findall(r'# xg -freq-(u|d)l( |=)(\[0\])?(\d+),?(\[1\])?(\d+)?', dc_string)
    settings['DL Frequency']['Carrier 0'] = pattern[0][3]
    settings['DL Frequency']['Carrier 1'] = pattern[0][5]
    settings['UL Frequency']['Carrier 0'] = pattern[1][3]
    settings['UL Frequency']['Carrier 1'] = pattern[1][5]

    pattern = re.search(r'# xg -short-cp (\d+)', dc_string)
    if pattern is not None:
        settings['Short CP'] = 'Enabled' if pattern.group(1) is '1' else 'Disabled'

    settings['Max distance'] = re.search(r'# (\* )?xg -max-distance( |=)(\d+)', dc_string).group(3)
    settings['Frame size'] = re.search(r'# xg -sframelen( |=)(\d+)', dc_string).group(2)
    settings['DL/UL Ratio'] = re.search(r'DL\/UL\sRatio\s+\|'
                                        r'(\d+/\d+(\s\(auto\))?)', dc_string).group(1)

    pattern = re.search(r'# xg -txpwr( |=)(\[0\])?([\-\d]+)(,(\[1\])?([\-\d]+))?', dc_string)
    if not pattern.group(6):
        settings['Tx Power'] = pattern.group(3)
    else:
        settings['Tx Power'] = max(pattern.group(3), pattern.group(6))

    pattern = re.search(r'# xg -ctrl-block-boost (\d+)', dc_string)
    if pattern is not None:
        settings['Control Block Boost'] = 'Enabled' if pattern.group(1) is '1' else 'Disabled'

    pattern = re.search(r'# xg -atpc-master-enable (\d+)', dc_string)
    if pattern is not None:
        settings['ATPC'] = 'Enabled' if pattern.group(1) is '1' else 'Disabled'

    settings['AMC Strategy'] = re.search(r'# xg -amc-strategy( |=)(\w+)', dc_string).group(2)

    pattern = re.search(r'# xg -max-mcs (\d+)', dc_string)
    if pattern is not None:
        settings['Max MCS'] = pattern.group(1)

    pattern = re.search(r'# xg -idfs-enable (\d+)', dc_string)
    if pattern is not None:
        settings['IDFS'] = 'Enabled' if pattern.group(1) is '1' else 'Disabled'

    pattern = re.search(r'# xg -traffic-prioritization (\d+)', dc_string)
    if pattern is not None:
        settings['Traffic prioritization'] = 'Enabled' if pattern.group(1) is '1' else 'Disabled'

    pattern = re.findall(r'ifc\s(ge0|ge1|sfp|radio)'
                         r'\s+(media\s([\w\d-]+)\s)?'
                         r'(mtu\s\d+\s)?(\w+)', dc_string)
    settings['Interface Status']['ge0'] = pattern[0][4]
    settings['Interface Status']['ge1'] = pattern[1][4]
    settings['Interface Status']['sfp'] = pattern[2][4]
    settings['Interface Status']['radio'] = pattern[3][4]

    logger.debug(f'Settings: {settings}')

    # Radio Status
    stream = {'Tx Power': None, 'Tx Gain': None, 'MCS': None, 'CINR': None, 'RSSI': None, 'Crosstalk': None,
              'Errors Ratio': None}
    carrier = {'Frequency': None, 'DFS': None, 'Rx Acc FER': None, 'Stream 0': stream, 'Stream 1': deepcopy(stream)}
    role = {'Role': None, 'Carrier 0': carrier, 'Carrier 1': deepcopy(carrier)}
    radio_status = {'Link status': None, 'Measured Distance': None, 'Master': role, 'Slave': deepcopy(role)}

    radio_status['Link status'] = re.search(r'Wireless Link( status)?\s+\|(\w+)', dc_string).group(2)

    pattern = re.search(r'Device Type\s+\|\s+(Master|Slave)\s+(\()?(\w+)?', dc_string)
    if not pattern.group(3) and pattern.group(1) == 'Master':
        radio_status['Master']['Role'] = 'Local'
        radio_status['Slave']['Role'] = 'Remote'
    elif not pattern.group(3) and pattern.group(1) == 'Slave':
        radio_status['Master']['Role'] = 'Remote'
        radio_status['Slave']['Role'] = 'Local'
    elif pattern.group(3) == 'local':
        radio_status['Master']['Role'] = 'Local'
        radio_status['Slave']['Role'] = 'Remote'
    else:
        radio_status['Master']['Role'] = 'Remote'
        radio_status['Slave']['Role'] = 'Local'

    if radio_status['Link status'] == 'UP':
        radio_status['Measured Distance'] = re.search(r'Measured Distance\s+\|'
                                                      r'(\d+\smeters|-+)', dc_string).group(1)

        pattern = no_empty(re.findall(r'Frequency\s+\|'
                                      r'\s+([\-\d]+)(\/([\-\d]+))?\s+MHz\s+\|'
                                      r'(\s+([\-\d]+)(\/([\-\d]+))?\s+MHz)?', dc_string))
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Frequency'] = pattern[0][0]
            radio_status['Slave']['Carrier 0']['Frequency'] = pattern[0][4]
        else:
            radio_status['Master']['Carrier 0']['Frequency'] = pattern[0][0]
            radio_status['Slave']['Carrier 0']['Frequency'] = pattern[0][4]
            radio_status['Master']['Carrier 1']['Frequency'] = pattern[1][0]
            radio_status['Slave']['Carrier 1']['Frequency'] = pattern[1][4]

        pattern = re.findall(r'DFS status\s+\|\s+(\w+)', dc_string)
        if len(pattern) > 0:
            radio_status['Master']['Carrier 0']['DFS'] = pattern[0]
            radio_status['Slave']['Carrier 0']['DFS'] = pattern[0]
            radio_status['Master']['Carrier 1']['DFS'] = pattern[0]
            radio_status['Slave']['Carrier 1']['DFS'] = pattern[0]

        pattern = no_empty(re.findall(r'Rx\sAcc\sFER\s+\|'
                                      r'\s+([\w\d.e-]+(\s\([\d.%]+\))?)(\s+\|'
                                      r'\s+([\-\w\d.e-]+\s\([\d.%]+\)))?', dc_string))
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Rx Acc FER'] = pattern[0][0]
            radio_status['Slave']['Carrier 0']['Rx Acc FER'] = pattern[0][3]
        else:
            radio_status['Master']['Carrier 0']['Rx Acc FER'] = pattern[0][0]
            radio_status['Slave']['Carrier 0']['Rx Acc FER'] = pattern[0][3]
            radio_status['Master']['Carrier 1']['Rx Acc FER'] = pattern[1][0]
            radio_status['Slave']['Carrier 1']['Rx Acc FER'] = pattern[1][3]

        pattern = no_empty(re.findall(r'Power\s+\|'
                                      r'([\-\d.]+(\sdBm)?)\s+\|'
                                      r'([\-\d.]+(\sdBm)?)\s+\|'
                                      r'(([\-\d.]+(\sdBm)?)\s+\|'
                                      r'([\-\d.]+(\sdBm)?))?', dc_string))
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['Tx Power'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['Tx Power'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['Tx Power'] = pattern[0][5]
            radio_status['Slave']['Carrier 0']['Stream 1']['Tx Power'] = pattern[0][7]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['Tx Power'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['Tx Power'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['Tx Power'] = pattern[0][5]
            radio_status['Slave']['Carrier 0']['Stream 1']['Tx Power'] = pattern[0][7]
            radio_status['Master']['Carrier 1']['Stream 0']['Tx Power'] = pattern[1][0]
            radio_status['Master']['Carrier 1']['Stream 1']['Tx Power'] = pattern[1][2]
            radio_status['Slave']['Carrier 1']['Stream 0']['Tx Power'] = pattern[1][5]
            radio_status['Slave']['Carrier 1']['Stream 1']['Tx Power'] = pattern[1][7]

        pattern = no_empty(re.findall(r'Gain\s+\|'
                                      r'([\-\d.]+(\sdB)?)\s+\|'
                                      r'([\-\d.]+(\sdB)?)\s+\|'
                                      r'(([\-\d.]+(\sdB)?)\s+\|'
                                      r'([\-\d.]+(\sdB)?))?', dc_string))
        if len(pattern) is 0:
            pass
        elif len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['Tx Gain'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['Tx Gain'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['Tx Gain'] = pattern[0][5]
            radio_status['Slave']['Carrier 0']['Stream 1']['Tx Gain'] = pattern[0][7]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['Tx Gain'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['Tx Gain'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['Tx Gain'] = pattern[0][5]
            radio_status['Slave']['Carrier 0']['Stream 1']['Tx Gain'] = pattern[0][7]
            radio_status['Master']['Carrier 1']['Stream 0']['Tx Gain'] = pattern[1][0]
            radio_status['Master']['Carrier 1']['Stream 1']['Tx Gain'] = pattern[1][2]
            radio_status['Slave']['Carrier 1']['Stream 0']['Tx Gain'] = pattern[1][5]
            radio_status['Slave']['Carrier 1']['Stream 1']['Tx Gain'] = pattern[1][7]

        pattern = no_empty(re.findall(r'RX\s+\|MCS\s+\|'
                                      r'([\-\w\d]+(\s\d+\/\d+\s\(\d+\))?)\s+\|'
                                      r'([\-\w\d]+(\s\d+\/\d+\s\(\d+\))?)\s+\|'
                                      r'(([\-\w\d]+(\s\d+\/\d+\s\(\d+\))?)\s+\|'
                                      r'([\-\w\d]+(\s\d+\/\d+\s\(\d+\))?))?', dc_string))
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['MCS'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['MCS'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['MCS'] = pattern[0][5]
            radio_status['Slave']['Carrier 0']['Stream 1']['MCS'] = pattern[0][7]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['MCS'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['MCS'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['MCS'] = pattern[0][5]
            radio_status['Slave']['Carrier 0']['Stream 1']['MCS'] = pattern[0][7]
            radio_status['Master']['Carrier 1']['Stream 0']['MCS'] = pattern[1][0]
            radio_status['Master']['Carrier 1']['Stream 1']['MCS'] = pattern[1][2]
            radio_status['Slave']['Carrier 1']['Stream 0']['MCS'] = pattern[1][5]
            radio_status['Slave']['Carrier 1']['Stream 1']['MCS'] = pattern[1][7]

        pattern = no_empty(re.findall(r'CINR\s+\|'
                                      r'([-\d.]+(\sdB)?)\s+\|'
                                      r'([-\d.]+(\sdB)?)(\s+\|'
                                      r'([-\d.]+(\sdB)?)\s+\|'
                                      r'([-\d.]+(\sdB)?))?', dc_string))
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['CINR'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['CINR'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['CINR'] = pattern[0][5]
            radio_status['Slave']['Carrier 0']['Stream 1']['CINR'] = pattern[0][7]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['CINR'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['CINR'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['CINR'] = pattern[0][5]
            radio_status['Slave']['Carrier 0']['Stream 1']['CINR'] = pattern[0][7]
            radio_status['Master']['Carrier 1']['Stream 0']['CINR'] = pattern[1][0]
            radio_status['Master']['Carrier 1']['Stream 1']['CINR'] = pattern[1][2]
            radio_status['Slave']['Carrier 1']['Stream 0']['CINR'] = pattern[1][5]
            radio_status['Slave']['Carrier 1']['Stream 1']['CINR'] = pattern[1][7]

        pattern = no_empty(re.findall(r'RSSI\s+\|([-\d.]+\sdBm)(\s\([\-\d]+\))?\s+\|'
                                      r'([-\d.]+\sdBm)(\s\([\-\d]+\))?(\s+\|'
                                      r'([-\d.]+\sdBm)(\s\([\-\d]+\))?\s+\|'
                                      r'([-\d.]+\sdBm)(\s\([\-\d]+\))?)?', dc_string))
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['RSSI'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['RSSI'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['RSSI'] = pattern[0][5]
            radio_status['Slave']['Carrier 0']['Stream 1']['RSSI'] = pattern[0][7]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['RSSI'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['RSSI'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['RSSI'] = pattern[0][5]
            radio_status['Slave']['Carrier 0']['Stream 1']['RSSI'] = pattern[0][7]
            radio_status['Master']['Carrier 1']['Stream 0']['RSSI'] = pattern[1][0]
            radio_status['Master']['Carrier 1']['Stream 1']['RSSI'] = pattern[1][2]
            radio_status['Slave']['Carrier 1']['Stream 0']['RSSI'] = pattern[1][5]
            radio_status['Slave']['Carrier 1']['Stream 1']['RSSI'] = pattern[1][7]

        pattern = no_empty(re.findall(r'Crosstalk\s+\|'
                                      r'([-\d.]+(\sdB)?)\s+\|'
                                      r'([-\d.]+(\sdB)?)(\s+\|'
                                      r'([-\d.]+(\sdB)?)\s+\|'
                                      r'([-\d.]+(\sdB)?))?', dc_string))
        if len(pattern) is 0:
            pass
        elif len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['Crosstalk'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['Crosstalk'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['Crosstalk'] = pattern[0][5]
            radio_status['Slave']['Carrier 0']['Stream 1']['Crosstalk'] = pattern[0][7]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['Crosstalk'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['Crosstalk'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['Crosstalk'] = pattern[0][5]
            radio_status['Slave']['Carrier 0']['Stream 1']['Crosstalk'] = pattern[0][7]
            radio_status['Master']['Carrier 1']['Stream 0']['Crosstalk'] = pattern[1][0]
            radio_status['Master']['Carrier 1']['Stream 1']['Crosstalk'] = pattern[1][2]
            radio_status['Slave']['Carrier 1']['Stream 0']['Crosstalk'] = pattern[1][5]
            radio_status['Slave']['Carrier 1']['Stream 1']['Crosstalk'] = pattern[1][7]

        pattern = no_empty(re.findall(r'(TBER|Errors\sRatio)\s+\|'
                                      r'[\d\.e\-]+(\s\(([\d.]+%)\))?\s+\|'
                                      r'[\d\.e\-]+(\s\(([\d.]+%)\))?\s+\|'
                                      r'([\d\.e\-]+(\s\(([\d.]+%)\))?\s+\|'
                                      r'[\d\.e\-]+(\s\(([\d.]+%)\))?)?', dc_string))
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['Errors Ratio'] = pattern[0][2]
            radio_status['Master']['Carrier 0']['Stream 1']['Errors Ratio'] = pattern[0][4]
            radio_status['Slave']['Carrier 0']['Stream 0']['Errors Ratio'] = pattern[0][7]
            radio_status['Slave']['Carrier 0']['Stream 1']['Errors Ratio'] = pattern[0][9]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['Errors Ratio'] = pattern[0][2]
            radio_status['Master']['Carrier 0']['Stream 1']['Errors Ratio'] = pattern[0][4]
            radio_status['Slave']['Carrier 0']['Stream 0']['Errors Ratio'] = pattern[0][7]
            radio_status['Slave']['Carrier 0']['Stream 1']['Errors Ratio'] = pattern[0][9]
            radio_status['Master']['Carrier 1']['Stream 0']['Errors Ratio'] = pattern[1][2]
            radio_status['Master']['Carrier 1']['Stream 1']['Errors Ratio'] = pattern[1][4]
            radio_status['Slave']['Carrier 1']['Stream 0']['Errors Ratio'] = pattern[1][7]
            radio_status['Slave']['Carrier 1']['Stream 1']['Errors Ratio'] = pattern[1][9]

    logger.debug(f'Radio Status: {radio_status}')

    # Ethernet Status
    ethernet_statuses = {'Status': None, 'Speed': None, 'Duplex': None, 'Negotiation': None, 'Rx CRC': None,
                         'Tx CRC': None}
    ethernet_status = {'ge0': ethernet_statuses, 'ge1': deepcopy(ethernet_statuses), 'sfp': deepcopy(ethernet_statuses)}

    pattern = no_empty(re.findall(r'Physical link is (\w+)(, (\d+ Mbps) '
                                  r'([\w-]+), (\w+))?', dc_string))
    ethernet_status['ge0']['Status'] = pattern[0][0]
    ethernet_status['ge1']['Status'] = pattern[1][0]
    ethernet_status['sfp']['Status'] = pattern[2][0]
    ethernet_status['ge0']['Speed'] = pattern[0][2]
    ethernet_status['ge1']['Speed'] = pattern[1][2]
    ethernet_status['sfp']['Speed'] = pattern[2][3]
    ethernet_status['ge0']['Duplex'] = pattern[0][3]
    ethernet_status['ge1']['Duplex'] = pattern[1][3]
    ethernet_status['sfp']['Duplex'] = pattern[2][3]
    ethernet_status['ge0']['Negotiation'] = pattern[0][4]
    ethernet_status['ge1']['Negotiation'] = pattern[1][4]
    ethernet_status['sfp']['Negotiation'] = pattern[2][4]

    pattern = re.findall(r'CRC errors\s+(\d+)', dc_string)
    ethernet_status['ge0']['Rx CRC'] = pattern[0]
    ethernet_status['ge1']['Rx CRC'] = pattern[2]
    ethernet_status['sfp']['Rx CRC'] = pattern[4]
    ethernet_status['ge0']['Tx CRC'] = pattern[1]
    ethernet_status['ge1']['Tx CRC'] = pattern[3]
    ethernet_status['sfp']['Tx CRC'] = pattern[5]

    logger.debug(f'Ethernet Status: {ethernet_status}')

    # Panic
    panic = []
    for line in dc_list:
        pattern = re.match(r'Panic info : \[\w+\]: ([\w\s\S\d]+)', line)
        if pattern is not None:
            panic.append(pattern.group(1).rstrip())
    panic = set(panic)

    logger.debug(f'Panic: {panic}')

    result = (model, subfamily, serial_number, firmware,
              uptime, reboot_reason, dc_list, dc_string,
              settings, radio_status, ethernet_status, panic)

    return result


logger = logging.getLogger('logger.parser_xg')