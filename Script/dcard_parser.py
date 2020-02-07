#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from myclasses import *


def parse_R5000(dcard_raw_text_string, dcard_raw_text_list):
    """Parse an R5000 diagnostic card and fill the class instance in"""

    for line in dcard_raw_text_list:

        # Model (Part Number)

        if re.search(r"\b(R5000-[QMOSL][mxnbtcs]{2,5}/[\dX\*]{1,3}.300.2x\d{3})(.2x\d{2})?\b", line) is not None:
            model = re.search(r"\b(R5000-[QMOSL][mxnbtcs]{2,5}/[\dX\*]{1,3}.300.2x\d{3})(.2x\d{2})?\b", line).group()
            if 'Lm' in model or 'Sm' in model:
                subfamily = 'R5000 Lite'
            else:
                subfamily = 'R5000 Pro'

        # Serial number

        if re.search(r"\bSN:(\d{6})\b", line) is not None:
            serial_number = re.search(r"\bSN:(\d{6})\b", line).group(1)

        # Firmware

        if re.search(r"\bH\d{2}S\d{2}-(MINT|TDMA)[v\d.]+\b", line) is not None:
            firmware = re.search(r"\bH\d{2}S\d{2}-(MINT|TDMA)[v\d.]+\b", line).group()

        # Uptime

        if re.search(r"^Uptime: ([\d\w :]*)$", line) is not None:
            uptime = re.search(r"^Uptime: ([\d\w :]*)$", line).group(1)

        # Last Reboot Reason

        if re.search(r"^Last reboot reason: ([\w ]*)$", line) is not None:
            rebootreason = re.search(r"^Last reboot reason: ([\w ]*)$", line).group(1)

    ethernet = {'eth0': 0, 'eth1': 1}
    radio = {'link1': {'rssi': 1, 'cinr': 2}, 'link2': {'rssi': 1, 'cinr': 2}}

    result = R5000Card(subfamily, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text_list,
                       dcard_raw_text_string, str(ethernet),
                       str(radio))

    return result


def parse_XG(dcard_raw_text_string, dcard_raw_text_list):
    """Parse a XG diagnostic card and fill the class instance in"""

    # Model (Part Number)
    model = re.search(r'(([XU]m/\dX?.\d{3,4}.\dx\d{3})(.2x\d{2})?)', dcard_raw_text_string).group(1)

    # Subfamily
    if '500.2x500' in model:
        subfamily = 'XG 500'
    else:
        subfamily = 'XG 1000'

    # Firmware
    firmware = re.search(r"(\bH\d{2}S\d{2}[v\d.-]+\b)", dcard_raw_text_string).group(1)

    # Serial number

    serial_number = re.search(r"SN:(\d+)", dcard_raw_text_string).group(1)

    # Uptime

    uptime = re.search(r"Uptime: ([\d\w :]*)", dcard_raw_text_string).group(1)

    # Last Reboot Reason

    rebootreason = re.search(r"Last reboot reason: ([\w ]*)", dcard_raw_text_string).group(1)

    # Settings

    settings = {'Role': None, 'Bandwidth': None, 'DL Frequency': {'Carrier 0': None, 'Carrier 1': None},
                'UL Frequency': {'Carrier 0': None, 'Carrier 1': None}, 'Short CP': None,
                'Max distance': None, 'Frame size': None, 'UL/DL Ratio': None, 'Tx Power': None,
                'Control Block Boost': None, 'ATPC': None, 'AMC Strategy': None, 'Max MCS': None,
                'IDFS': None,
                'Traffic prioritization': None}

    settings['Role'] = re.search(r"# xg -type (\w+)", dcard_raw_text_string).group(1)
    settings['Bandwidth'] = re.search(r"# xg -channel-width (\d+)", dcard_raw_text_string).group(1)
    settings['DL Frequency']['Carrier 0'] = re.search(r"# xg -freq-dl (\[0\])?(\d+),?(\[1\])?(\d+)?",
                                                      dcard_raw_text_string).group(2)
    settings['DL Frequency']['Carrier 1'] = re.search(r"# xg -freq-dl (\[0\])?(\d+),?(\[1\])?(\d+)?",
                                                      dcard_raw_text_string).group(4)
    settings['UL Frequency']['Carrier 0'] = re.search(r"# xg -freq-ul (\[0\])?(\d+),?(\[1\])?(\d+)?",
                                                      dcard_raw_text_string).group(2)
    settings['UL Frequency']['Carrier 1'] = re.search(r"# xg -freq-ul (\[0\])?(\d+),?(\[1\])?(\d+)?",
                                                      dcard_raw_text_string).group(4)
    settings['Short CP'] = 'Enabled' if re.search(r"# xg -short-cp (\d+)", dcard_raw_text_string).group(
        1) is '1' else 'Disabled'
    settings['Max distance'] = re.search(r"# xg -max-distance (\d+)", dcard_raw_text_string).group(1)
    settings['Frame size'] = re.search(r"# xg -sframelen (\d+)", dcard_raw_text_string).group(1)
    settings['UL/DL Ratio'] = re.search(r"DL\/UL\sRatio\s+\|(\d+/\d+(\s\(auto\))?)", dcard_raw_text_string).group(1)
    settings['Tx Power'] = re.search(r"# xg -txpwr (\d+)", dcard_raw_text_string).group(1)
    settings['Control Block Boost'] = 'Enabled' if re.search(r"# xg -ctrl-block-boost (\d+)",
                                                             dcard_raw_text_string).group(1) is '1' else 'Disabled'
    settings['ATPC'] = 'Enabled' if re.search(r"# xg -atpc-master-enable (\d+)", dcard_raw_text_string).group(
        1) is '1' else 'Disabled'
    settings['AMC Strategy'] = re.search(r"# xg -amc-strategy (\w+)", dcard_raw_text_string).group(1)
    settings['Max MCS'] = re.search(r"# xg -max-mcs (\d+)", dcard_raw_text_string).group(1)
    settings['IDFS'] = 'Enabled' if re.search(r"# xg -idfs-enable (\d+)", dcard_raw_text_string).group(
        1) is '1' else 'Disabled'
    settings['Traffic prioritization'] = 'Enabled' if re.search(r"# xg -traffic-prioritization (\d+)",
                                                                dcard_raw_text_string).group(1) is '1' else 'Disabled'

    # Radio Status

    """radio_status structure

    Link status
    Measured Distance
    Master OR Slave
        Role
        Carrier 0 OR 1
            Frequency
            DFS
            Rx Acc FER
            Stream 0 OR 1
                Tx Power
                Tx Gain
                MCS
                CINR
                RSSI
                Crosstalk
                Errors Ratio

    Example: radio_status['Master']['Carrier 0']['Stream 0']['Tx Power']
    """

    radio_status = {'Link status': None, 'Measured Distance': None, 'Master': {
        'Role': None,
        'Carrier 0': {'Frequency': None, 'DFS': None, 'Rx Acc FER': None,
                      'Stream 0': {'Tx Power': None, 'Tx Gain': None, 'MCS': None, 'CINR': None, 'RSSI': None,
                                   'Crosstalk': None, 'Errors Ratio': None},
                      'Stream 1': {'Tx Power': None, 'Tx Gain': None, 'MCS': None, 'CINR': None, 'RSSI': None,
                                   'Crosstalk': None, 'Errors Ratio': None}},
        'Carrier 1': {'Frequency': None, 'DFS': None, 'Rx Acc FER': None,
                      'Stream 0': {'Tx Power': None, 'Tx Gain': None, 'MCS': None, 'CINR': None, 'RSSI': None,
                                   'Crosstalk': None, 'Errors Ratio': None},
                      'Stream 1': {'Tx Power': None, 'Tx Gain': None, 'MCS': None, 'CINR': None, 'RSSI': None,
                                   'Crosstalk': None, 'Errors Ratio': None}}}, 'Slave': {
        'Role': None,
        'Carrier 0': {'Frequency': None, 'DFS': None, 'Rx Acc FER': None,
                      'Stream 0': {'Tx Power': None, 'Tx Gain': None, 'MCS': None, 'CINR': None, 'RSSI': None,
                                   'Crosstalk': None, 'Errors Ratio': None},
                      'Stream 1': {'Tx Power': None, 'Tx Gain': None, 'MCS': None, 'CINR': None, 'RSSI': None,
                                   'Crosstalk': None, 'Errors Ratio': None}},
        'Carrier 1': {'Frequency': None, 'DFS': None, 'Rx Acc FER': None,
                      'Stream 0': {'Tx Power': None, 'Tx Gain': None, 'MCS': None, 'CINR': None, 'RSSI': None,
                                   'Crosstalk': None, 'Errors Ratio': None},
                      'Stream 1': {'Tx Power': None, 'Tx Gain': None, 'MCS': None, 'CINR': None, 'RSSI': None,
                                   'Crosstalk': None, 'Errors Ratio': None}}}}

    radio_status['Link status'] = re.search(r"Wireless Link\s+\|(\w+)", dcard_raw_text_string).group(1)
    radio_status['Measured Distance'] = re.search(r"Measured Distance\s+\|(\d+\smeters)", dcard_raw_text_string).group(
        1)

    if 'local' in re.search(r"Device Type\s+\|\s+Master\s\((local|remote)\)", dcard_raw_text_string).group(1):
        radio_status['Master']['Role'] = 'Local'
        radio_status['Slave']['Role'] = 'Remote'
    else:
        radio_status['Master']['Role'] = 'Remote'
        radio_status['Slave']['Role'] = 'Local'

    pattern = re.findall(r"(\d+)\sMHz\s+\|\s+(\d+)", dcard_raw_text_string)
    if len(pattern) is 1:
        radio_status['Master']['Carrier 0']['Frequency'] = pattern[0][0]
        radio_status['Slave']['Carrier 0']['Frequency'] = pattern[0][1]
    else:
        radio_status['Master']['Carrier 0']['Frequency'] = pattern[0][0]
        radio_status['Slave']['Carrier 0']['Frequency'] = pattern[0][1]
        radio_status['Master']['Carrier 1']['Frequency'] = pattern[1][0]
        radio_status['Slave']['Carrier 1']['Frequency'] = pattern[1][1]

    pattern = re.findall(r"DFS status\s+\|\s+(\w+)", dcard_raw_text_string)
    radio_status['Master']['Carrier 0']['DFS'] = pattern[0]
    radio_status['Slave']['Carrier 0']['DFS'] = pattern[0]
    radio_status['Master']['Carrier 1']['DFS'] = pattern[0]
    radio_status['Slave']['Carrier 1']['DFS'] = pattern[0]

    pattern = re.findall(r"([\w\d.e-]+\s\([\d.%]+\))\s+\|\s+([\w\d.e-]+\s\([\d.%]+\))", dcard_raw_text_string)
    if len(pattern) is 1:
        radio_status['Master']['Carrier 0']['Rx Acc FER'] = pattern[0][0]
        radio_status['Slave']['Carrier 0']['Rx Acc FER'] = pattern[0][1]
    else:
        radio_status['Master']['Carrier 0']['Rx Acc FER'] = pattern[0][0]
        radio_status['Slave']['Carrier 0']['Rx Acc FER'] = pattern[0][1]
        radio_status['Master']['Carrier 1']['Rx Acc FER'] = pattern[1][0]
        radio_status['Slave']['Carrier 1']['Rx Acc FER'] = pattern[1][1]

    pattern = re.findall(r"Power\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)",
                         dcard_raw_text_string)
    if len(pattern) is 1:
        radio_status['Master']['Carrier 0']['Stream 0']['Tx Power'] = pattern[0][0]
        radio_status['Master']['Carrier 0']['Stream 1']['Tx Power'] = pattern[0][1]
        radio_status['Slave']['Carrier 0']['Stream 0']['Tx Power'] = pattern[0][2]
        radio_status['Slave']['Carrier 0']['Stream 1']['Tx Power'] = pattern[0][3]
    else:
        radio_status['Master']['Carrier 0']['Stream 0']['Tx Power'] = pattern[0][0]
        radio_status['Master']['Carrier 0']['Stream 1']['Tx Power'] = pattern[0][1]
        radio_status['Slave']['Carrier 0']['Stream 0']['Tx Power'] = pattern[0][2]
        radio_status['Slave']['Carrier 0']['Stream 1']['Tx Power'] = pattern[0][3]
        radio_status['Master']['Carrier 1']['Stream 0']['Tx Power'] = pattern[1][0]
        radio_status['Master']['Carrier 1']['Stream 1']['Tx Power'] = pattern[1][1]
        radio_status['Slave']['Carrier 1']['Stream 0']['Tx Power'] = pattern[1][2]
        radio_status['Slave']['Carrier 1']['Stream 1']['Tx Power'] = pattern[1][3]

    pattern = re.findall(r"Gain\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)",
                         dcard_raw_text_string)
    if len(pattern) is 1:
        radio_status['Master']['Carrier 0']['Stream 0']['Tx Gain'] = pattern[0][0]
        radio_status['Master']['Carrier 0']['Stream 1']['Tx Gain'] = pattern[0][1]
        radio_status['Slave']['Carrier 0']['Stream 0']['Tx Gain'] = pattern[0][2]
        radio_status['Slave']['Carrier 0']['Stream 1']['Tx Gain'] = pattern[0][3]
    else:
        radio_status['Master']['Carrier 0']['Stream 0']['Tx Gain'] = pattern[0][0]
        radio_status['Master']['Carrier 0']['Stream 1']['Tx Gain'] = pattern[0][1]
        radio_status['Slave']['Carrier 0']['Stream 0']['Tx Gain'] = pattern[0][2]
        radio_status['Slave']['Carrier 0']['Stream 1']['Tx Gain'] = pattern[0][3]
        radio_status['Master']['Carrier 1']['Stream 0']['Tx Gain'] = pattern[1][0]
        radio_status['Master']['Carrier 1']['Stream 1']['Tx Gain'] = pattern[1][1]
        radio_status['Slave']['Carrier 1']['Stream 0']['Tx Gain'] = pattern[1][2]
        radio_status['Slave']['Carrier 1']['Stream 1']['Tx Gain'] = pattern[1][3]

    pattern = re.findall(
        r"RX\s+\|MCS\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))",
        dcard_raw_text_string)
    if len(pattern) is 1:
        radio_status['Master']['Carrier 0']['Stream 0']['MCS'] = pattern[0][0]
        radio_status['Master']['Carrier 0']['Stream 1']['MCS'] = pattern[0][1]
        radio_status['Slave']['Carrier 0']['Stream 0']['MCS'] = pattern[0][2]
        radio_status['Slave']['Carrier 0']['Stream 1']['MCS'] = pattern[0][3]
    else:
        radio_status['Master']['Carrier 0']['Stream 0']['MCS'] = pattern[0][0]
        radio_status['Master']['Carrier 0']['Stream 1']['MCS'] = pattern[0][1]
        radio_status['Slave']['Carrier 0']['Stream 0']['MCS'] = pattern[0][2]
        radio_status['Slave']['Carrier 0']['Stream 1']['MCS'] = pattern[0][3]
        radio_status['Master']['Carrier 1']['Stream 0']['MCS'] = pattern[1][0]
        radio_status['Master']['Carrier 1']['Stream 1']['MCS'] = pattern[1][1]
        radio_status['Slave']['Carrier 1']['Stream 0']['MCS'] = pattern[1][2]
        radio_status['Slave']['Carrier 1']['Stream 1']['MCS'] = pattern[1][3]

    pattern = re.findall(r"CINR\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)",
                         dcard_raw_text_string)
    if len(pattern) is 1:
        radio_status['Master']['Carrier 0']['Stream 0']['CINR'] = pattern[0][0]
        radio_status['Master']['Carrier 0']['Stream 1']['CINR'] = pattern[0][1]
        radio_status['Slave']['Carrier 0']['Stream 0']['CINR'] = pattern[0][2]
        radio_status['Slave']['Carrier 0']['Stream 1']['CINR'] = pattern[0][3]
    else:
        radio_status['Master']['Carrier 0']['Stream 0']['CINR'] = pattern[0][0]
        radio_status['Master']['Carrier 0']['Stream 1']['CINR'] = pattern[0][1]
        radio_status['Slave']['Carrier 0']['Stream 0']['CINR'] = pattern[0][2]
        radio_status['Slave']['Carrier 0']['Stream 1']['CINR'] = pattern[0][3]
        radio_status['Master']['Carrier 1']['Stream 0']['CINR'] = pattern[1][0]
        radio_status['Master']['Carrier 1']['Stream 1']['CINR'] = pattern[1][1]
        radio_status['Slave']['Carrier 1']['Stream 0']['CINR'] = pattern[1][2]
        radio_status['Slave']['Carrier 1']['Stream 1']['CINR'] = pattern[1][3]

    pattern = re.findall(
        r"RSSI\s+\|([-\d.]+\sdBm)(\s\([\d-]+\))?\s+\|([-\d.]+\sdBm)(\s\([\d-]+\))?\s+\|([-\d.]+\sdBm)(\s\([\d-]+\))?\s+\|([-\d.]+\sdBm)(\s\([\d-]+\))?",
        dcard_raw_text_string)
    if len(pattern) is 1:
        radio_status['Master']['Carrier 0']['Stream 0']['RSSI'] = pattern[0][0]
        radio_status['Master']['Carrier 0']['Stream 1']['RSSI'] = pattern[0][2]
        radio_status['Slave']['Carrier 0']['Stream 0']['RSSI'] = pattern[0][4]
        radio_status['Slave']['Carrier 0']['Stream 1']['RSSI'] = pattern[0][6]
    else:
        radio_status['Master']['Carrier 0']['Stream 0']['RSSI'] = pattern[0][0]
        radio_status['Master']['Carrier 0']['Stream 1']['RSSI'] = pattern[0][2]
        radio_status['Slave']['Carrier 0']['Stream 0']['RSSI'] = pattern[0][4]
        radio_status['Slave']['Carrier 0']['Stream 1']['RSSI'] = pattern[0][6]
        radio_status['Master']['Carrier 1']['Stream 0']['RSSI'] = pattern[1][0]
        radio_status['Master']['Carrier 1']['Stream 1']['RSSI'] = pattern[1][2]
        radio_status['Slave']['Carrier 1']['Stream 0']['RSSI'] = pattern[1][4]
        radio_status['Slave']['Carrier 1']['Stream 1']['RSSI'] = pattern[1][6]

    pattern = re.findall(r"Crosstalk\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)",
                         dcard_raw_text_string)
    if len(pattern) is 1:
        radio_status['Master']['Carrier 0']['Stream 0']['Crosstalk'] = pattern[0][0]
        radio_status['Master']['Carrier 0']['Stream 1']['Crosstalk'] = pattern[0][1]
        radio_status['Slave']['Carrier 0']['Stream 0']['Crosstalk'] = pattern[0][2]
        radio_status['Slave']['Carrier 0']['Stream 1']['Crosstalk'] = pattern[0][3]
    else:
        radio_status['Master']['Carrier 0']['Stream 0']['Crosstalk'] = pattern[0][0]
        radio_status['Master']['Carrier 0']['Stream 1']['Crosstalk'] = pattern[0][1]
        radio_status['Slave']['Carrier 0']['Stream 0']['Crosstalk'] = pattern[0][2]
        radio_status['Slave']['Carrier 0']['Stream 1']['Crosstalk'] = pattern[0][3]
        radio_status['Master']['Carrier 1']['Stream 0']['Crosstalk'] = pattern[1][0]
        radio_status['Master']['Carrier 1']['Stream 1']['Crosstalk'] = pattern[1][1]
        radio_status['Slave']['Carrier 1']['Stream 0']['Crosstalk'] = pattern[1][2]
        radio_status['Slave']['Carrier 1']['Stream 1']['Crosstalk'] = pattern[1][3]

    pattern = re.findall(
        r"Errors\sRatio\s+\|[\d\.e-]+\s\(([\d.]+%)\)\s+\|[\d\.e-]+\s\(([\d.]+%)\)\s+\|[\d\.e-]+\s\(([\d.]+%)\)\s+\|[\d\.e-]+\s\(([\d.]+%)\)",
        dcard_raw_text_string)
    if len(pattern) is 1:
        radio_status['Master']['Carrier 0']['Stream 0']['Errors Ratio'] = pattern[0][0]
        radio_status['Master']['Carrier 0']['Stream 1']['Errors Ratio'] = pattern[0][1]
        radio_status['Slave']['Carrier 0']['Stream 0']['Errors Ratio'] = pattern[0][2]
        radio_status['Slave']['Carrier 0']['Stream 1']['Errors Ratio'] = pattern[0][3]
    else:
        radio_status['Master']['Carrier 0']['Stream 0']['Errors Ratio'] = pattern[0][0]
        radio_status['Master']['Carrier 0']['Stream 1']['Errors Ratio'] = pattern[0][1]
        radio_status['Slave']['Carrier 0']['Stream 0']['Errors Ratio'] = pattern[0][2]
        radio_status['Slave']['Carrier 0']['Stream 1']['Errors Ratio'] = pattern[0][3]
        radio_status['Master']['Carrier 1']['Stream 0']['Errors Ratio'] = pattern[1][0]
        radio_status['Master']['Carrier 1']['Stream 1']['Errors Ratio'] = pattern[1][1]
        radio_status['Slave']['Carrier 1']['Stream 0']['Errors Ratio'] = pattern[1][2]
        radio_status['Slave']['Carrier 1']['Stream 1']['Errors Ratio'] = pattern[1][3]

    # Ethernet Status

    ethernet_status = {
        'ge0': {'Status': None, 'Speed': None, 'Duplex': None, 'Negotiation': None, 'Rx CRC': None, 'Tx CRC': None},
        'ge1': {'Status': None, 'Speed': None, 'Duplex': None, 'Negotiation': None, 'Rx CRC': None, 'Tx CRC': None},
        'sfp': {'Status': None, 'Speed': None, 'Duplex': None, 'Negotiation': None, 'Rx CRC': None, 'Tx CRC': None}}

    pattern = re.findall(r"Physical link is (\w+)(, (\d+ Mbps) ([\w-]+), (\w+))?", dcard_raw_text_string)
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

    pattern = re.findall(r"CRC errors\s+(\d+)", dcard_raw_text_string)
    ethernet_status['ge0']['Rx CRC'] = pattern[0]
    ethernet_status['ge1']['Rx CRC'] = pattern[2]
    ethernet_status['sfp']['Rx CRC'] = pattern[4]
    ethernet_status['ge0']['Tx CRC'] = pattern[1]
    ethernet_status['ge1']['Tx CRC'] = pattern[3]
    ethernet_status['sfp']['Tx CRC'] = pattern[5]

    # Panic

    panic = []
    for line in dcard_raw_text_list:
        if re.search(r"^Panic info : [\W\w]+$", line) is not None:
            panic.append(line)

    result = XGCard(subfamily, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text_list,
                    dcard_raw_text_string, settings, radio_status, ethernet_status, panic)

    return result


def parse_Quanta(dcard_raw_text_string, dcard_raw_text_list):
    """Parse a Quanta 5 diagnostic card and fill the class instance in"""

    for line in dcard_raw_text_list:
        # Model (Part Number)
        if re.search(r"[QV]5-[\dE]+", line) is not None:
            model = re.search(r"[QV]5-[\dE]+", line).group()
            if 'Q5' in model or 'V5' in model:
                subfamily = 'Quanta 5'
            else:
                subfamily = 'Quanta 70'

        # Serial number
        if re.search(r"\bSN:\d{6}\b", line) is not None:
            serial_number = re.search(r"\bSN:(\d{6})\b", line).group(1)

        # Firmware
        if re.search(r"\bH\d{2}S\d{2}[v\d.-]+\b", line) is not None:
            firmware = re.search(r"\bH\d{2}S\d{2}[v\d.-]+\b", line).group()

        # Uptime
        if re.search(r"^Uptime: ([\d\w :]*)$", line) is not None:
            uptime = re.search(r"^Uptime: ([\d\w :]*)$", line).group(1)

        # Last Reboot Reason
        if re.search(r"^Last reboot reason: ([\w ]*)$", line) is not None:
            rebootreason = re.search(r"^Last reboot reason: ([\w ]*)$", line).group(1)

    result = QCard(subfamily, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text_list,
                   dcard_raw_text_string, '1', '1', '1', '1')

    return result
