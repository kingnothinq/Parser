#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from copy import deepcopy

from my_classes import *


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

    result = R5000Card(model, subfamily, serial_number, firmware, uptime, rebootreason, dcard_raw_text_list,
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
                'IDFS': None, 'Traffic prioritization': None,
                'Interface Status': {'Ge0': None, 'Ge1': None, 'SFP': None, 'Radio': None}}

    settings['Role'] = re.search(r"# xg -type (\w+)", dcard_raw_text_string).group(1)
    settings['Bandwidth'] = re.search(r"# xg -channel-width (\d+)", dcard_raw_text_string).group(1)

    pattern = re.findall(r"# xg -freq-(u|d)l (\[0\])?(\d+),?(\[1\])?(\d+)?", dcard_raw_text_string)
    settings['DL Frequency']['Carrier 0'] = pattern[0][2]
    settings['DL Frequency']['Carrier 1'] = pattern[0][4]
    settings['UL Frequency']['Carrier 0'] = pattern[1][2]
    settings['UL Frequency']['Carrier 1'] = pattern[1][4]

    pattern = re.search(r"# xg -short-cp (\d+)", dcard_raw_text_string).group(1)
    settings['Short CP'] = 'Enabled' if pattern is '1' else 'Disabled'

    settings['Max distance'] = re.search(r"# xg -max-distance (\d+)", dcard_raw_text_string).group(1)
    settings['Frame size'] = re.search(r"# xg -sframelen (\d+)", dcard_raw_text_string).group(1)
    settings['UL/DL Ratio'] = re.search(r"DL\/UL\sRatio\s+\|(\d+/\d+(\s\(auto\))?)", dcard_raw_text_string).group(1)
    settings['Tx Power'] = re.search(r"# xg -txpwr (\d+)", dcard_raw_text_string).group(1)

    pattern = re.search(r"# xg -ctrl-block-boost (\d+)",dcard_raw_text_string).group(1)
    settings['Control Block Boost'] = 'Enabled' if pattern is '1' else 'Disabled'

    pattern = re.search(r"# xg -atpc-master-enable (\d+)", dcard_raw_text_string).group(1)
    settings['ATPC'] = 'Enabled' if pattern is '1' else 'Disabled'

    settings['AMC Strategy'] = re.search(r"# xg -amc-strategy (\w+)", dcard_raw_text_string).group(1)
    settings['Max MCS'] = re.search(r"# xg -max-mcs (\d+)", dcard_raw_text_string).group(1)

    pattern = re.search(r"# xg -idfs-enable (\d+)", dcard_raw_text_string).group(1)
    settings['IDFS'] = 'Enabled' if pattern is '1' else 'Disabled'

    pattern = re.search(r"# xg -traffic-prioritization (\d+)", dcard_raw_text_string).group(1)
    settings['Traffic prioritization'] = 'Enabled' if pattern is '1' else 'Disabled'

    pattern = re.findall(r"ifc\s(ge0|ge1|sfp|radio)\s+(media\s([\w\d-]+)\s)?(mtu\s\d+\s)?(\w+)",
                         dcard_raw_text_string)
    settings['Interface Status']['Ge0'] = pattern[0][4]
    settings['Interface Status']['Ge1'] = pattern[1][4]
    settings['Interface Status']['SFP'] = pattern[2][4]
    settings['Interface Status']['Radio'] = pattern[3][4]

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

    stream = {'Tx Power': None, 'Tx Gain': None, 'MCS': None, 'CINR': None, 'RSSI': None, 'Crosstalk': None,
              'Errors Ratio': None}
    carrier = {'Frequency': None, 'DFS': None, 'Rx Acc FER': None, 'Stream 0': stream, 'Stream 1': deepcopy(stream)}
    role = {'Role': None, 'Carrier 0': carrier, 'Carrier 1': deepcopy(carrier)}
    radio_status = {'Link status': None, 'Measured Distance': None, 'Master': role, 'Slave': deepcopy(role)}

    radio_status['Link status'] = re.search(r"Wireless Link\s+\|(\w+)", dcard_raw_text_string).group(1)

    pattern = re.search(r"Device Type\s+\|\s+(Master|Slave)\s+(\()?(\w+)?", dcard_raw_text_string)
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
        radio_status['Measured Distance'] = re.search(r"Measured Distance\s+\|(\d+\smeters|-+)",
                                                      dcard_raw_text_string).group(1)

        pattern = re.findall(r"Frequency\s+\|\s+(\d+)\sMHz(\s+\|\s+(\d+)\sMHz)?", dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Frequency'] = pattern[0][0]
            radio_status['Slave']['Carrier 0']['Frequency'] = pattern[0][2]
        else:
            radio_status['Master']['Carrier 0']['Frequency'] = pattern[0][0]
            radio_status['Slave']['Carrier 0']['Frequency'] = pattern[0][2]
            radio_status['Master']['Carrier 1']['Frequency'] = pattern[1][0]
            radio_status['Slave']['Carrier 1']['Frequency'] = pattern[1][2]

        pattern = re.findall(r"DFS status\s+\|\s+(\w+)", dcard_raw_text_string)
        radio_status['Master']['Carrier 0']['DFS'] = pattern[0]
        radio_status['Slave']['Carrier 0']['DFS'] = pattern[0]
        radio_status['Master']['Carrier 1']['DFS'] = pattern[0]
        radio_status['Slave']['Carrier 1']['DFS'] = pattern[0]

        pattern = re.findall(r"Rx\sAcc\sFER\s+\|\s+([\w\d.e-]+\s\([\d.%]+\))(\s+\|\s+([\w\d.e-]+\s\([\d.%]+\)))?",
                             dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Rx Acc FER'] = pattern[0][0]
            radio_status['Slave']['Carrier 0']['Rx Acc FER'] = pattern[0][2]
        else:
            radio_status['Master']['Carrier 0']['Rx Acc FER'] = pattern[0][0]
            radio_status['Slave']['Carrier 0']['Rx Acc FER'] = pattern[0][2]
            radio_status['Master']['Carrier 1']['Rx Acc FER'] = pattern[1][0]
            radio_status['Slave']['Carrier 1']['Rx Acc FER'] = pattern[1][2]

        pattern = re.findall(r"Power\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)(\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm))?",
                             dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['Tx Power'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['Tx Power'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0']['Tx Power'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1']['Tx Power'] = pattern[0][4]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['Tx Power'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['Tx Power'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0']['Tx Power'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1']['Tx Power'] = pattern[0][4]
            radio_status['Master']['Carrier 1']['Stream 0']['Tx Power'] = pattern[1][0]
            radio_status['Master']['Carrier 1']['Stream 1']['Tx Power'] = pattern[1][1]
            radio_status['Slave']['Carrier 1']['Stream 0']['Tx Power'] = pattern[1][3]
            radio_status['Slave']['Carrier 1']['Stream 1']['Tx Power'] = pattern[1][4]

        pattern = re.findall(r"Gain\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)(\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB))?",
                             dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['Tx Gain'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['Tx Gain'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0']['Tx Gain'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1']['Tx Gain'] = pattern[0][4]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['Tx Gain'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['Tx Gain'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0']['Tx Gain'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1']['Tx Gain'] = pattern[0][4]
            radio_status['Master']['Carrier 1']['Stream 0']['Tx Gain'] = pattern[1][0]
            radio_status['Master']['Carrier 1']['Stream 1']['Tx Gain'] = pattern[1][1]
            radio_status['Slave']['Carrier 1']['Stream 0']['Tx Gain'] = pattern[1][3]
            radio_status['Slave']['Carrier 1']['Stream 1']['Tx Gain'] = pattern[1][4]

        pattern = re.findall(
            r"RX\s+\|MCS\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))(\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\)))?",
            dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['MCS'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['MCS'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0']['MCS'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1']['MCS'] = pattern[0][4]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['MCS'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['MCS'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0']['MCS'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1']['MCS'] = pattern[0][4]
            radio_status['Master']['Carrier 1']['Stream 0']['MCS'] = pattern[1][0]
            radio_status['Master']['Carrier 1']['Stream 1']['MCS'] = pattern[1][1]
            radio_status['Slave']['Carrier 1']['Stream 0']['MCS'] = pattern[1][3]
            radio_status['Slave']['Carrier 1']['Stream 1']['MCS'] = pattern[1][4]

        pattern = re.findall(r"CINR\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)(\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB))?",
                             dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['CINR'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['CINR'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0']['CINR'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1']['CINR'] = pattern[0][4]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['CINR'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['CINR'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0']['CINR'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1']['CINR'] = pattern[0][4]
            radio_status['Master']['Carrier 1']['Stream 0']['CINR'] = pattern[1][0]
            radio_status['Master']['Carrier 1']['Stream 1']['CINR'] = pattern[1][1]
            radio_status['Slave']['Carrier 1']['Stream 0']['CINR'] = pattern[1][3]
            radio_status['Slave']['Carrier 1']['Stream 1']['CINR'] = pattern[1][4]

        pattern = re.findall(
            r"RSSI\s+\|([-\d.]+\sdBm)(\s\([\d-]+\))?\s+\|([-\d.]+\sdBm)(\s\([\d-]+\))?(\s+\|([-\d.]+\sdBm)(\s\([\d-]+\))?\s+\|([-\d.]+\sdBm)(\s\([\d-]+\))?)?",
            dcard_raw_text_string)
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

        pattern = re.findall(r"Crosstalk\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)(\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB))?",
                             dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['Crosstalk'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['Crosstalk'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0']['Crosstalk'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1']['Crosstalk'] = pattern[0][4]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['Crosstalk'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['Crosstalk'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0']['Crosstalk'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1']['Crosstalk'] = pattern[0][4]
            radio_status['Master']['Carrier 1']['Stream 0']['Crosstalk'] = pattern[1][0]
            radio_status['Master']['Carrier 1']['Stream 1']['Crosstalk'] = pattern[1][1]
            radio_status['Slave']['Carrier 1']['Stream 0']['Crosstalk'] = pattern[1][3]
            radio_status['Slave']['Carrier 1']['Stream 1']['Crosstalk'] = pattern[1][4]

        pattern = re.findall(
            r"(TBER|Errors\sRatio)\s+\|[\d\.e-]+\s\(([\d.]+%)\)\s+\|[\d\.e-]+\s\(([\d.]+%)\)(\s+\|[\d\.e-]+\s\(([\d.]+%)\)\s+\|[\d\.e-]+\s\(([\d.]+%)\))?",
            dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['Errors Ratio'] = pattern[0][1]
            radio_status['Master']['Carrier 0']['Stream 1']['Errors Ratio'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['Errors Ratio'] = pattern[0][4]
            radio_status['Slave']['Carrier 0']['Stream 1']['Errors Ratio'] = pattern[0][5]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['Errors Ratio'] = pattern[0][1]
            radio_status['Master']['Carrier 0']['Stream 1']['Errors Ratio'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['Errors Ratio'] = pattern[0][4]
            radio_status['Slave']['Carrier 0']['Stream 1']['Errors Ratio'] = pattern[0][5]
            radio_status['Master']['Carrier 1']['Stream 0']['Errors Ratio'] = pattern[1][1]
            radio_status['Master']['Carrier 1']['Stream 1']['Errors Ratio'] = pattern[1][2]
            radio_status['Slave']['Carrier 1']['Stream 0']['Errors Ratio'] = pattern[1][4]
            radio_status['Slave']['Carrier 1']['Stream 1']['Errors Ratio'] = pattern[1][5]

    # Ethernet Status
    ethernet_statuses = {'Status': None, 'Speed': None, 'Duplex': None, 'Negotiation': None, 'Rx CRC': None,
                         'Tx CRC': None}
    ethernet_status = {'ge0': ethernet_statuses, 'ge1': deepcopy(ethernet_statuses), 'sfp': deepcopy(ethernet_statuses)}

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

    result = XGCard(model, subfamily, serial_number, firmware, uptime, rebootreason, dcard_raw_text_list,
                    dcard_raw_text_string, settings, radio_status, ethernet_status, panic)

    return result


def parse_Quanta(dcard_raw_text_string, dcard_raw_text_list):
    """Parse a Quanta 5 diagnostic card and fill the class instance in"""

    # Model (Part Number)
    model = re.search(r'([QV](5|70)-[\dE]+)', dcard_raw_text_string).group(1)

    # Subfamily
    #global subfamily
    if 'Q5' in model:
        subfamily = 'Quanta 5'
    elif 'V5' in model:
        subfamily = 'Vector 5'
    elif 'Q70' in model:
        subfamily = 'Quanta 70'
    elif 'V70' in model:
        subfamily = 'Vector 70'

    # Firmware
    firmware = re.search(r"(H\d{2}S\d{2}-OCTOPUS_PTPv[\d.]+)", dcard_raw_text_string).group(1)

    # Serial number
    serial_number = re.search(r"SN:(\d+)", dcard_raw_text_string).group(1)

    # Uptime
    uptime = re.search(r"Uptime: ([\d\w :]*)", dcard_raw_text_string).group(1)

    # Last Reboot Reason
    rebootreason = re.search(r"Last reboot reason: ([\w ]*)", dcard_raw_text_string).group(1)

    # Settings
    settings = {'Role': None, 'Bandwidth': None, 'DL Frequency': None, 'UL Frequency': None, 'Frame size': None,
                'Guard Interval': None, 'UL/DL Ratio': None, 'Tx Power': None, 'ATPC': None, 'AMC Strategy': None,
                'Max DL MCS': None, 'Max UL MCS': None, 'DFS': None, 'ARQ': None,
                'Interface Status': {'Ge0': None, 'Radio': None}}

    settings['Role'] = re.search(r"ptp_role (\w+)", dcard_raw_text_string).group(1)
    settings['Bandwidth'] = re.search(r"bw (\d+)", dcard_raw_text_string).group(1)
    settings['DL Frequency'] = re.search(r"freq_dl (\d+)", dcard_raw_text_string).group(1)
    settings['UL Frequency'] = re.search(r"freq_ul (\d+)", dcard_raw_text_string).group(1)
    settings['Frame size'] = re.search(r"frame_length (\d+)", dcard_raw_text_string).group(1)
    settings['Guard Interval'] = re.search(r"guard_interval (\d+\/\d+)", dcard_raw_text_string).group(1)

    if re.search(r"auto_dl_ul_ratio (\w+)", dcard_raw_text_string).group(1) == 'on':
        settings['UL/DL Ratio'] = re.search(r"dl_ul_ratio (\d+)", dcard_raw_text_string).group(1) + ' (auto)'
    else:
        settings['UL/DL Ratio'] = re.search(r"dl_ul_ratio (\d+)", dcard_raw_text_string).group(1)

    settings['Tx Power'] = re.search(r"tx_power (\d+)", dcard_raw_text_string).group(1)
    settings['ATPC'] = 'Enabled' if re.search(r"atpc (on|off)", dcard_raw_text_string).group(1) == 'on' else 'Disabled'
    settings['AMC Strategy'] = re.search(r"amc_strategy (\w+)", dcard_raw_text_string).group(1)
    settings['Max DL MCS'] = re.search(r"dl_mcs (([\d-]+)?(QPSK|QAM)-\d+\/\d+)", dcard_raw_text_string).group(1)
    settings['Max UL MCS'] = re.search(r"ul_mcs (([\d-]+)?(QPSK|QAM)-\d+\/\d+)", dcard_raw_text_string).group(1)
    settings['DFS'] = 'Enabled' if re.search(r"dfs (dfs_rd|off)", dcard_raw_text_string).group(
        1) == 'dfs_rd' else 'Disabled'
    settings['ARQ'] = 'Enabled' if re.search(r"harq (on|off)", dcard_raw_text_string).group(1) == 'on' else 'Disabled'
    pattern = re.findall(r"ifc\sge0\s+media\s([\w\d]+)\smtu\s\d+\s(up|down)", dcard_raw_text_string)
    settings['Interface Status']['Ge0'] = pattern[0][1]

    # Radio Status
    """radio_status structure

        Link status
        Measured Distance
        Downlink OR Uplink
             Frequency
             Tx Power
             Stream 0 OR 1
                 MCS
                 RSSI
                 EVM
                 Crosstalk
                 ARQ ratio

        Example: radio_status['Downlink'][Stream 0']['MCS']
        """

    stream = {'Tx Power': None, 'MCS': None, 'RSSI': None, 'EVM': None, 'Crosstalk': None, 'ARQ ratio': None}
    role = {'Frequency': None, 'Stream 0': stream, 'Stream 1': deepcopy(stream)}
    radio_status = {'Link status': None, 'Measured Distance': None, 'Downlink': role, 'Uplink': deepcopy(role)}

    radio_status['Link status'] = re.search(r"State\s+(\w+)", dcard_raw_text_string).group(1)
    radio_status['Measured Distance'] = re.search(r"Distance\s+(\d+\sm)", dcard_raw_text_string).group(1)
    pattern = re.search(r"Frequency\s+\|\s(\d+)\sMHz\s+\|\s(\d+)\sMHz", dcard_raw_text_string)
    radio_status['Downlink']['Frequency'] = pattern.group(1)
    radio_status['Uplink']['Frequency'] = pattern.group(2)

    if radio_status['Link status'] == 'connected':
        if settings['Role'] == 'master':
            pattern = re.search(r"\| TX power\s+([\d\.]+)\s\/\s([\d\.]+)\sdBm", dcard_raw_text_string)
            radio_status['Downlink']['Stream 0']['Tx Power'] = pattern.group(1)
            radio_status['Downlink']['Stream 1']['Tx Power'] = pattern.group(2)
            pattern = re.search(r"Remote TX power\s+([\d\.]+)\s\/\s([\d\.]+)\sdBm", dcard_raw_text_string)
            radio_status['Uplink']['Stream 0']['Tx Power'] = pattern.group(1)
            radio_status['Uplink']['Stream 1']['Tx Power'] = pattern.group(2)
        else:
            pattern = re.search(r"\| TX power\s+([\d\.]+)\s\/\s([\d\.]+)\sdBm", dcard_raw_text_string)
            radio_status['Uplink']['Stream 0']['Tx Power'] = pattern.group(1)
            radio_status['Uplink']['Stream 1']['Tx Power'] = pattern.group(2)
            pattern = re.search(r"Remote TX power\s+([\d\.]+)\s\/\s([\d\.]+)\sdBm", dcard_raw_text_string)
            radio_status['Downlink']['Stream 0']['Tx Power'] = pattern.group(1)
            radio_status['Downlink']['Stream 1']['Tx Power'] = pattern.group(2)

        for line in dcard_raw_text_list:
            if line.startswith('| MCS'):
                pattern = re.findall(r"(([\d-]+)?(QPSK|QAM)-\d+\/\d+)", line)
                radio_status['Downlink']['Stream 0']['MCS'] = pattern[0][0]
                radio_status['Downlink']['Stream 1']['MCS'] = pattern[1][0]
                radio_status['Uplink']['Stream 0']['MCS'] = pattern[2][0]
                radio_status['Uplink']['Stream 1']['MCS'] = pattern[3][0]
            elif line.startswith('| RSSI'):
                pattern = re.findall(r"([-\d.]+\sdBm)", line)
                radio_status['Downlink']['Stream 0']['RSSI'] = pattern[0]
                radio_status['Downlink']['Stream 1']['RSSI'] = pattern[1]
                radio_status['Uplink']['Stream 0']['RSSI'] = pattern[2]
                radio_status['Uplink']['Stream 1']['RSSI'] = pattern[3]
            elif line.startswith('| EVM'):
                pattern = re.findall(r"([-\d.]+\sdB)", line)
                radio_status['Downlink']['Stream 0']['EVM'] = pattern[0]
                radio_status['Downlink']['Stream 1']['EVM'] = pattern[1]
                radio_status['Uplink']['Stream 0']['EVM'] = pattern[2]
                radio_status['Uplink']['Stream 1']['EVM'] = pattern[3]
            elif line.startswith('| Crosstalk'):
                pattern = re.findall(r"([-\d.]+\sdB)", line)
                radio_status['Downlink']['Stream 0']['Crosstalk'] = pattern[0]
                radio_status['Downlink']['Stream 1']['Crosstalk'] = pattern[1]
                radio_status['Uplink']['Stream 0']['Crosstalk'] = pattern[2]
                radio_status['Uplink']['Stream 1']['Crosstalk'] = pattern[3]
            elif line.startswith('| ARQ ratio'):
                pattern = re.findall(r"(\d+\.\d+\s%)", line)
                radio_status['Downlink']['Stream 0']['ARQ ratio'] = pattern[0]
                radio_status['Downlink']['Stream 1']['ARQ ratio'] = pattern[1]
                radio_status['Uplink']['Stream 0']['ARQ ratio'] = pattern[2]
                radio_status['Uplink']['Stream 1']['ARQ ratio'] = pattern[3]

    # Ethernet Status
    ethernet_status = {'ge0': {'Status': None, 'Speed': None, 'Duplex': None, 'Negotiation': None, 'CRC': None}}

    pattern = re.findall(r"Physical link is (\w+)(, (\d+ Mbps) ([\w-]+), (\w+))?", dcard_raw_text_string)
    ethernet_status['ge0']['Status'] = pattern[0][0]
    ethernet_status['ge0']['Speed'] = pattern[0][2]
    ethernet_status['ge0']['Duplex'] = pattern[0][3]
    ethernet_status['ge0']['Negotiation'] = pattern[0][4]

    pattern = re.findall(r"CRC errors\s+(\d+)", dcard_raw_text_string)
    ethernet_status['ge0']['CRC'] = pattern[0]

    result = QCard(model, subfamily, serial_number, firmware, uptime, rebootreason, dcard_raw_text_list,
                   dcard_raw_text_string, settings, radio_status,
                   ethernet_status)

    return result
