#!/usr/bin/python
# -*- coding: utf-8 -*-

from classes import *
from re import search


def parse_R5000(dcard_raw_text):
    """Parse an R5000 diagnostic card and fill the class instance in"""

    for line in dcard_raw_text:

        # Model (Part Number)

        if search(r"\b(R5000-[QMOSL][mxnbtcs]{2,5}/[\dX\*]{1,3}.300.2x\d{3})(.2x\d{2})?\b", line) is not None:
            model = search(r"\b(R5000-[QMOSL][mxnbtcs]{2,5}/[\dX\*]{1,3}.300.2x\d{3})(.2x\d{2})?\b", line).group()
            if 'Lm' in model or 'Sm' in model:
                subfamily = 'R5000 Lite'
            else:
                subfamily = 'R5000 Pro'

        # Serial number

        if search(r"\bSN:(\d{6})\b", line) is not None:
            serial_number = search(r"\bSN:(\d{6})\b", line).group(1)

        # Firmware

        if search(r"\bH\d{2}S\d{2}-(MINT|TDMA)[v\d.]+\b", line) is not None:
            firmware = search(r"\bH\d{2}S\d{2}-(MINT|TDMA)[v\d.]+\b", line).group()

        # Uptime

        if search(r"^Uptime: ([\d\w :]*)$", line) is not None:
            uptime = search(r"^Uptime: ([\d\w :]*)$", line).group(1)

        # Last Reboot Reason

        if search(r"^Last reboot reason: ([\w ]*)$", line) is not None:
            rebootreason = search(r"^Last reboot reason: ([\w ]*)$", line).group(1)

    ethernet = {'eth0': 0, 'eth1': 1}
    radio = {'link1': {'rssi': 1, 'cinr': 2}, 'link2': {'rssi': 1, 'cinr': 2}}

    result = R5000Card(subfamily, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text, str(ethernet),
                       str(radio))

    return result


def parse_XG(dcard_raw_text):
    """Parse a XG diagnostic card and fill the class instance in"""

    settings = {'Role': None, 'Bandwidth': None, 'UL Frequency': None, 'DL Frequency': None, 'Short CP': None,
                'Max distance': None, 'Frame size': None, 'UL/DL Ratio': None, 'Tx Power': None,
                'Control Block Boost': None, 'ATPC': None, 'AMC Strategy': None, 'MCS limit': None,
                'IDFS': None,
                'Traffic prioritization': None}

    """radio_status structure

    radio_status structure
    
    Link status
    Measured Distance
    Master OR Slave
        Local OR Remote
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

    for line in dcard_raw_text:

        # Model (Part Number)

        if search(r"[XU]m/\dX?.\d{3,4}.\dx\d{3}(.2x\d{2})?", line) is not None:
            pattern = search(r"[XU]m/\dX?.\d{3,4}.\dx\d{3}(.2x\d{2})?", line)
            model = pattern.group()
            if '500.2x500' in model:
                subfamily = 'XG 500'
            else:
                subfamily = 'XG 1000'

        # Serial number

        if search(r"\bSN:(\d{6})\b", line) is not None:
            pattern = search(r"\bSN:(\d{6})\b", line)
            serial_number = pattern.group(1)

        # Firmware

        if search(r"\bH\d{2}S\d{2}[v\d.-]+\b", line) is not None:
            pattern = search(r"\bH\d{2}S\d{2}[v\d.-]+\b", line)
            firmware = pattern.group()

        # Uptime

        if search(r"^Uptime: ([\d\w :]*)$", line) is not None:
            pattern = search(r"^Uptime: ([\d\w :]*)$", line)
            uptime = pattern.group(1)

        # Last Reboot Reason

        if search(r"^Last reboot reason: ([\w ]*)$", line) is not None:
            pattern = search(r"^Last reboot reason: ([\w ]*)$", line)
            rebootreason = pattern.group(1)

        # Settings

        if search(r"^  # xg -type (\w+)$", line) is not None:
            pattern = search(r"^  # xg -type (\w+)$", line)
            settings['Role'] = pattern.group(1)

        if search(r"^  # xg -channel-width (\d+)$", line) is not None:
            pattern = search(r"^  # xg -channel-width (\d+)$", line)
            settings['Bandwidth'] = pattern.group(1)

        if search(r"^  # xg -freq-ul (\d+)$", line) is not None:
            pattern = search(r"^  # xg -freq-ul (\d+)$", line)
            settings['UL Frequency'] = pattern.group(1)

        if search(r"^  # xg -freq-dl (\d+)$", line) is not None:
            pattern = search(r"^  # xg -freq-dl (\d+)$", line)
            settings['DL Frequency'] = pattern.group(1)

        if search(r"^  # xg -short-cp (\d)$", line) is not None:
            pattern = search(r"^  # xg -short-cp (\d)$", line)
            settings['Short CP'] = pattern.group(1)

        if search(r"^  # xg -max-distance (\d)$", line) is not None:
            pattern = search(r"^  # xg -max-distance (\d)$", line)
            settings['Max distance'] = pattern.group(1)

        if search(r"^  # xg -sframelen (\d)$", line) is not None:
            pattern = search(r"^  # xg -sframelen (\d)$", line)
            settings['Frame size'] = pattern.group(1)

        if search(r"^\|DL\/UL\sRatio\s+\|(\d+/\d+)\s?(\(auto\))\s+\|$", line) is not None:
            pattern = search(r"^\|DL\/UL\sRatio\s+\|(\d+/\d+)\s?(\(auto\))\s+\|$", line)
            settings['UL/DL Ratio'] = pattern.group(1) + pattern.group(2)

        if search(r"^  # xg -txpwr (\d+)$", line) is not None:
            pattern = search(r"^  # xg -txpwr (\d+)$", line)
            settings['Tx Power'] = pattern.group(1)

        if search(r"^  # xg -ctrl-block-boost (\d+)$", line) is not None:
            pattern = search(r"^  # xg -ctrl-block-boost (\d+)$", line)
            settings['Control Block Boost'] = pattern.group(1)

        if search(r"^  # xg -atpc-master-enable (\d+)$", line) is not None:
            pattern = search(r"^  # xg -atpc-master-enable (\d+)$", line)
            settings['ATPC'] = pattern.group(1)

        if search(r"^  # xg -amc-strategy (\w+)$", line) is not None:
            pattern = search(r"^  # xg -amc-strategy (\w+)$", line)
            settings['AMC Strategy'] = pattern.group(1)

        if search(r"^  # xg -max-mcs (\d+)$", line) is not None:
            pattern = search(r"^  # xg -max-mcs (\d+)$", line)
            settings['MCS limit'] = pattern.group(1)

        if search(r"^  # xg -idfs-enable (\d+)$", line) is not None:
            pattern = search(r"^  # xg -idfs-enable (\d+)$", line)
            settings['IDFS'] = pattern.group(1)

        if search(r"^  # xg -traffic-prioritization (\d+)$", line) is not None:
            pattern = search(r"^  # xg -traffic-prioritization (\d+)$", line)
            settings['Traffic prioritization'] = pattern.group(1)

        # Radio Status

        if search(r"^\|Wireless\sLink\s+\|(\w+)\s+\|$", line) is not None:
            pattern = search(r"^\|Wireless\sLink\s+\|(\w+)\s+\|$", line)
            radio_status['Link status'] = pattern.group(1)

        if search(r"^\|Measured\sDistance\s+\|(\d+\smeters)\s+\|$", line) is not None:
            pattern = search(r"^\|Measured\sDistance\s+\|(\d+\smeters)\s+\|$", line)
            radio_status['Measured Distance'] = pattern.group(1)

        if search(r"^\|\s+Device\sType\s+\|\s+Master\s+\((\w+)\)\s+\|\s+Slave\s+\((\w+)\)\s+\|$", line) is not None:
            pattern = search(r"^\|\s+Device\sType\s+\|\s+Master\s+\((\w+)\)\s+\|\s+Slave\s+\((\w+)\)\s+\|$", line)
            if 'local' in pattern.group(1):
                radio_status['Master']['Role'] = 'Local'
                radio_status['Slave']['Role'] = 'Remote'
            else:
                radio_status['Master']['Role'] = 'Remote'
                radio_status['Slave']['Role'] = 'Local'

        if search(r"^\|Tx\/Rx\sFrequency\s+\|\s+(\d+)\sMHz\s+\|\s+(\d+)\sMHz\s+\|$", line) is not None:
            pattern = search(r"^\|Tx\/Rx\sFrequency\s+\|\s+(\d+)\sMHz\s+\|\s+(\d+)\sMHz\s+\|$", line)
            radio_status['Master']['Carrier 0']['Frequency'] = pattern.group(1)
            radio_status['Slave']['Carrier 0']['Frequency'] = pattern.group(2)

        if search(r"^\|DFS\sstatus\s+\|(\s+(\w+)\s+\|)\1", line) is not None:
            pattern = search(r"^\|DFS\sstatus\s+\|(\s+(\w+)\s+\|)\1", line)
            radio_status['Master']['Carrier 0']['DFS'] = pattern.group(2)
            radio_status['Slave']['Carrier 0']['DFS'] = pattern.group(2)

        if search(r"^\|Rx\sAcc\sFER\s+\|(\s+[\d\.e-]+\s\((\d+%)\)\s+)\|(\s+[\d\.e-]+\s\((\d+%)\)\s+)\|$",
                  line) is not None:
            pattern = search(r"^\|Rx\sAcc\sFER\s+\|(\s+[\d\.e-]+\s\((\d+%)\)\s+)\|(\s+[\d\.e-]+\s\((\d+%)\)\s+)\|$",
                             line)
            radio_status['Master']['Carrier 0']['Rx Acc FER'] = pattern.group(2)
            radio_status['Slave']['Carrier 0']['Rx Acc FER'] = pattern.group(4)

        if search(r"Power\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)\s+\|$",
                  line) is not None:
            pattern = search(r"Power\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)\s+\|$",
                             line)
            radio_status['Master']['Carrier 0']['Stream 0']['Tx Power'] = pattern.group(1)
            radio_status['Master']['Carrier 0']['Stream 1']['Tx Power'] = pattern.group(2)
            radio_status['Slave']['Carrier 0']['Stream 0']['Tx Power'] = pattern.group(3)
            radio_status['Slave']['Carrier 0']['Stream 1']['Tx Power'] = pattern.group(4)

        if search(r"Gain\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|$",line) is not None:
            pattern = search(r"Gain\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|$",line)
            radio_status['Master']['Carrier 0']['Stream 0']['Tx Gain'] = pattern.group(1)
            radio_status['Master']['Carrier 0']['Stream 1']['Tx Gain'] = pattern.group(2)
            radio_status['Slave']['Carrier 0']['Stream 0']['Tx Gain'] = pattern.group(3)
            radio_status['Slave']['Carrier 0']['Stream 1']['Tx Gain'] = pattern.group(4)

        if search(
                r"^\|RX\s+\|MCS\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|$",
                line) is not None:
            pattern = search(
                r"^\|RX\s+\|MCS\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|$",
                line)
            radio_status['Master']['Carrier 0']['Stream 0']['MCS'] = pattern.group(1)
            radio_status['Master']['Carrier 0']['Stream 1']['MCS'] = pattern.group(2)
            radio_status['Slave']['Carrier 0']['Stream 0']['MCS'] = pattern.group(3)
            radio_status['Slave']['Carrier 0']['Stream 1']['MCS'] = pattern.group(4)

        if search(r"CINR\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|$",
                  line) is not None:
            pattern = search(r"CINR\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|$",
                             line)
            radio_status['Master']['Carrier 0']['Stream 0']['CINR'] = pattern.group(1)
            radio_status['Master']['Carrier 0']['Stream 1']['CINR'] = pattern.group(2)
            radio_status['Slave']['Carrier 0']['Stream 0']['CINR'] = pattern.group(3)
            radio_status['Slave']['Carrier 0']['Stream 1']['CINR'] = pattern.group(4)

        if search(r"RSSI\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)\s+\|$",
                  line) is not None:
            pattern = search(r"RSSI\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)\s+\|$",
                             line)
            radio_status['Master']['Carrier 0']['Stream 0']['RSSI'] = pattern.group(1)
            radio_status['Master']['Carrier 0']['Stream 1']['RSSI'] = pattern.group(2)
            radio_status['Slave']['Carrier 0']['Stream 0']['RSSI'] = pattern.group(3)
            radio_status['Slave']['Carrier 0']['Stream 1']['RSSI'] = pattern.group(4)

        if search(r"Crosstalk\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|$",
                  line) is not None:
            pattern = search(r"Crosstalk\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)\s+\|$",
                             line)
            radio_status['Master']['Carrier 0']['Stream 0']['Crosstalk'] = pattern.group(1)
            radio_status['Master']['Carrier 0']['Stream 1']['Crosstalk'] = pattern.group(2)
            radio_status['Slave']['Carrier 0']['Stream 0']['Crosstalk'] = pattern.group(3)
            radio_status['Slave']['Carrier 0']['Stream 1']['Crosstalk'] = pattern.group(4)

        if search(
                r"Errors\sRatio\s+\|[\d\.e-]+\s\(([\d.]+%)\)\s+\|[\d\.e-]+\s\(([\d.]+%)\)\s+\|[\d\.e-]+\s\(([\d.]+%)\)\s+\|[\d\.e-]+\s\(([\d.]+%)\)\s+\|$",
                line) is not None:
            pattern = search(
                r"Errors\sRatio\s+\|[\d\.e-]+\s\(([\d.]+%)\)\s+\|[\d\.e-]+\s\(([\d.]+%)\)\s+\|[\d\.e-]+\s\(([\d.]+%)\)\s+\|[\d\.e-]+\s\(([\d.]+%)\)\s+\|$",
                line)
            radio_status['Master']['Carrier 0']['Stream 0']['Errors Ratio'] = pattern.group(1)
            radio_status['Master']['Carrier 0']['Stream 1']['Errors Ratio'] = pattern.group(2)
            radio_status['Slave']['Carrier 0']['Stream 0']['Errors Ratio'] = pattern.group(3)
            radio_status['Slave']['Carrier 0']['Stream 1']['Errors Ratio'] = pattern.group(4)


    #print(subfamily)
    #print(radio_status)

    result = XGCard(subfamily, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text, settings, radio_status, '1',
                    '1')

    return result


def parse_Quanta(dcard_raw_text):
    """Parse a Quanta 5 diagnostic card and fill the class instance in"""

    for line in dcard_raw_text:
        # Model (Part Number)
        if search(r"[QV]5-[\dE]+", line) is not None:
            model = search(r"[QV]5-[\dE]+", line).group()
            if 'Q5' in model or 'V5' in model:
                subfamily = 'Quanta 5'
            else:
                subfamily = 'Quanta 70'

        # Serial number
        if search(r"\bSN:\d{6}\b", line) is not None:
            serial_number = search(r"\bSN:(\d{6})\b", line).group(1)

        # Firmware
        if search(r"\bH\d{2}S\d{2}[v\d.-]+\b", line) is not None:
            firmware = search(r"\bH\d{2}S\d{2}[v\d.-]+\b", line).group()

        # Uptime
        if search(r"^Uptime: ([\d\w :]*)$", line) is not None:
            uptime = search(r"^Uptime: ([\d\w :]*)$", line).group(1)

        # Last Reboot Reason
        if search(r"^Last reboot reason: ([\w ]*)$", line) is not None:
            rebootreason = search(r"^Last reboot reason: ([\w ]*)$", line).group(1)

    result = QCard(subfamily, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text, '1', '1', '1', '1')

    return result
