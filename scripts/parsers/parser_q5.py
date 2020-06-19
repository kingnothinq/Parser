# -*- coding: utf-8 -*-

import logging
import re
from copy import deepcopy
from time import time


def timer(function):
    """Estimate time"""
    def wrapper(dc_string, dc_list):
        time_start = time()
        function_result = function(dc_string, dc_list)
        time_end = time()
        logger.info(f'Diagnostic card parsed, Elapsed Time: {time_end - time_start}')
        return function_result
    return wrapper


@timer
def parse(dc_string, dc_list):
    """Parse a Quanta 5 diagnostic card and fill the class instance in.

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

    __________________
    settings structure
	    Role
        Bandwidth
        DL Frequency
        UL Frequency
        Frame size
        Guard Interval
        DL/UL Ratio
        Tx Power
        ATPC
        AMC Strategy
        Max DL MCS
        Max UL MCS
        DFS
        ARQ
        Interface Status
            Ge0

    Example of request: settings['Interface Status']['Ge0']

    ______________________
    radio_status structure
        Link status
        Measured Distance
        Downlink OR Uplink
             Frequency
             Stream 0 OR Stream 1
                 Tx Power
                 MCS
                 RSSI
                 EVM
                 Crosstalk
                 ARQ ratio

    Example of request: radio_status['Downlink'][Stream 0']['MCS']

    _________________________
    ethernet_status structure
        ge0
            Status
            Speed
            Duplex
            Negotiation
            CRC

    Example of request: ethernet_status['ge0']['Speed']
    """

    # General info
    pattern = re.search(r'([QV](5)-[\dE]+)', dc_string)
    if pattern is not None:
        model = pattern.group(1)
    else:
        model = 'Quanta unknown model'
    if 'Q5' in model:
        subfamily = 'Quanta 5'
    elif 'V5' in model:
        subfamily = 'Vector 5'
    elif 'Q70' in model:
        subfamily = 'Quanta 70'
    elif 'V70' in model:
        subfamily = 'Vector 70'
    else:
        subfamily = 'Quanta unknown model'
    logger.debug(f'Model: {model}; Subfamily: {subfamily}')

    firmware = re.search(r'#\sOCTOPUS-PTP\sWANFleX\s'
                         r'(H\d{2}S\d{2}-OCTOPUS_PTPv[\d.]+)', dc_string).group(1)
    logger.debug(f'Firmware: {firmware}')

    serial_number = re.search(r'SN:(\d+)', dc_string).group(1)
    logger.debug(f'SN: {serial_number}')

    uptime = re.search(r'Uptime: ([\d\w :]*)', dc_string).group(1)
    logger.debug(f'Uptime: {uptime}')

    reboot_reason = re.search(r'Last reboot reason: ([\w ]*)', dc_string).group(1)
    logger.debug(f'Last reboot reason: {reboot_reason}')

    # Settings
    settings = {'Role': None, 'Bandwidth': None, 'DL Frequency': None, 'UL Frequency': None, 'Frame size': None,
                'Guard Interval': None, 'DL/UL Ratio': None, 'Tx Power': None, 'ATPC': None, 'AMC Strategy': None,
                'Max DL MCS': None, 'Max UL MCS': None, 'DFS': None, 'ARQ': None, 'Interface Status': {'Ge0': None, }}

    settings['Role'] = re.search(r'ptp_role (\w+)', dc_string).group(1)
    settings['Bandwidth'] = re.search(r'bw (\d+)', dc_string).group(1)
    settings['DL Frequency'] = re.search(r'freq_dl (\d+)', dc_string).group(1)
    settings['UL Frequency'] = re.search(r'freq_ul (\d+)', dc_string).group(1)
    settings['Frame size'] = re.search(r'frame_length (\d+)', dc_string).group(1)
    settings['Guard Interval'] = re.search(r'guard_interval (\d+\/\d+)', dc_string).group(1)

    if re.search(r'auto_dl_ul_ratio (\w+)', dc_string).group(1) == 'on':
        settings['DL/UL Ratio'] = re.search(r'dl_ul_ratio (\d+)', dc_string).group(1) + ' (auto)'
    else:
        settings['DL/UL Ratio'] = re.search(r'dl_ul_ratio (\d+)', dc_string).group(1)

    settings['Tx Power'] = re.search(r'tx_power (\d+)', dc_string).group(1)
    settings['ATPC'] = 'Enabled' if re.search(r'atpc (on|off)', dc_string).group(1) == 'on' else 'Disabled'
    settings['AMC Strategy'] = re.search(r'amc_strategy (\w+)', dc_string).group(1)
    settings['Max DL MCS'] = re.search(r'dl_mcs (([\-\d]+)?(QPSK|QAM)-\d+\/\d+)', dc_string).group(1)
    settings['Max UL MCS'] = re.search(r'ul_mcs (([\-\d]+)?(QPSK|QAM)-\d+\/\d+)', dc_string).group(1)
    settings['DFS'] = 'Enabled' if re.search(r'dfs (dfs_rd|off)', dc_string).group(1) == 'dfs_rd' else 'Disabled'
    settings['ARQ'] = 'Enabled' if re.search(r'harq (on|off)', dc_string).group(1) == 'on' else 'Disabled'
    pattern = re.findall(r'ifc\sge0\s+media\s([\-\w\d]+)(\smtu\s(\d+))?\s(up|down)', dc_string)
    settings['Interface Status']['Ge0'] = pattern[0][3]

    logger.debug(f'Settings: {settings}')

    # Radio Status
    stream = {'Tx Power': None, 'MCS': None, 'RSSI': None, 'EVM': None, 'Crosstalk': None, 'ARQ ratio': None}
    role = {'Frequency': None, 'Stream 0': stream, 'Stream 1': deepcopy(stream)}
    radio_status = {'Link status': None, 'Measured Distance': None, 'Downlink': role, 'Uplink': deepcopy(role)}

    radio_status['Link status'] = re.search(r'\s+State[^\n]\s+(\w+)', dc_string).group(1)

    if radio_status['Link status'] == 'connected':

        radio_status['Measured Distance'] = re.search(r'Distance\s+([\.\d]+\sk?m)', dc_string).group(1)
        pattern = re.search(r'Frequency\s+\|'
                            r'\s(-)?((\d+)\sMHz)?\s+\|'
                            r'\s(-)?((\d+)\sMHz)?', dc_string)
        radio_status['Downlink']['Frequency'] = pattern.group(2)
        radio_status['Uplink']['Frequency'] = pattern.group(5)

        if settings['Role'] == 'master':
            pattern = re.search(r'\| TX power\s+([-\d\.]+)\s\/\s([-\d\.]+)\sdBm', dc_string)
            radio_status['Downlink']['Stream 0']['Tx Power'] = pattern.group(1)
            radio_status['Downlink']['Stream 1']['Tx Power'] = pattern.group(2)
            pattern = re.search(r'Remote TX power\s+([-\d\.]+)\s\/\s([-\d\.]+)\sdBm', dc_string)
            radio_status['Uplink']['Stream 0']['Tx Power'] = pattern.group(1)
            radio_status['Uplink']['Stream 1']['Tx Power'] = pattern.group(2)
        else:
            pattern = re.search(r'\| TX power\s+([-\d\.]+)\s\/\s([-\d\.]+)\sdBm', dc_string)
            radio_status['Uplink']['Stream 0']['Tx Power'] = pattern.group(1)
            radio_status['Uplink']['Stream 1']['Tx Power'] = pattern.group(2)
            pattern = re.search(r'Remote TX power\s+([-\d\.]+)\s\/\s([-\d\.]+)\sdBm', dc_string)
            radio_status['Downlink']['Stream 0']['Tx Power'] = pattern.group(1)
            radio_status['Downlink']['Stream 1']['Tx Power'] = pattern.group(2)

        for line in dc_list:

            if line.startswith('| MCS'):
                pattern = re.findall(r'(([\-\d]+)?(QPSK|QAM)-\d+\/\d+)', line)
                radio_status['Downlink']['Stream 0']['MCS'] = pattern[0][0]
                radio_status['Downlink']['Stream 1']['MCS'] = pattern[1][0]
                radio_status['Uplink']['Stream 0']['MCS'] = pattern[2][0]
                radio_status['Uplink']['Stream 1']['MCS'] = pattern[3][0]
            elif line.startswith('| RSSI'):
                pattern = re.findall(r'([\-\d\.]+)( \([\-\d\.]+\))? dBm', line)
                radio_status['Downlink']['Stream 0']['RSSI'] = pattern[0][0]
                radio_status['Downlink']['Stream 1']['RSSI'] = pattern[1][0]
                radio_status['Uplink']['Stream 0']['RSSI'] = pattern[2][0]
                radio_status['Uplink']['Stream 1']['RSSI'] = pattern[3][0]
            elif line.startswith('| EVM'):
                pattern = re.findall(r'([\-\d.]+)\sdB', line)
                radio_status['Downlink']['Stream 0']['EVM'] = pattern[0]
                radio_status['Downlink']['Stream 1']['EVM'] = pattern[1]
                radio_status['Uplink']['Stream 0']['EVM'] = pattern[2]
                radio_status['Uplink']['Stream 1']['EVM'] = pattern[3]
            elif line.startswith('| Crosstalk'):
                pattern = re.findall(r'([-\d.]+)\sdB', line)
                radio_status['Downlink']['Stream 0']['Crosstalk'] = pattern[0]
                radio_status['Downlink']['Stream 1']['Crosstalk'] = pattern[1]
                radio_status['Uplink']['Stream 0']['Crosstalk'] = pattern[2]
                radio_status['Uplink']['Stream 1']['Crosstalk'] = pattern[3]
            elif line.startswith('| ARQ ratio'):
                pattern = re.findall(r'(\d+(\.\d+)?)\s%', line)
                radio_status['Downlink']['Stream 0']['ARQ ratio'] = pattern[0][0]
                radio_status['Downlink']['Stream 1']['ARQ ratio'] = pattern[1][0]
                radio_status['Uplink']['Stream 0']['ARQ ratio'] = pattern[2][0]
                radio_status['Uplink']['Stream 1']['ARQ ratio'] = pattern[3][0]

    logger.debug(f'Radio Status: {radio_status}')

    # Ethernet Status
    ethernet_status = {'ge0': {'Status': None, 'Speed': None, 'Duplex': None, 'Negotiation': None, 'CRC': None}}

    pattern = re.findall(r'Physical link is (\w+)(, (\d+ Mbps) ([\w-]+), (\w+))?', dc_string)
    ethernet_status['ge0']['Status'] = pattern[0][0]
    ethernet_status['ge0']['Speed'] = pattern[0][2]
    ethernet_status['ge0']['Duplex'] = pattern[0][3]
    ethernet_status['ge0']['Negotiation'] = pattern[0][4]

    pattern = re.findall(r'CRC errors\s+(\d+)', dc_string)
    ethernet_status['ge0']['CRC'] = pattern[0]

    logger.debug(f'Ethernet Status: {ethernet_status}')

    result = (model, subfamily, serial_number, firmware,
              uptime, reboot_reason, dc_list, dc_string,
              settings, radio_status, ethernet_status)

    return result


logger = logging.getLogger('logger.parser_q5')