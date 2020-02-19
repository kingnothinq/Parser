#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from copy import deepcopy

from my_classes import *


def parse_R5000(dcard_raw_text_string, dcard_raw_text_list):
    """Parse an R5000 diagnostic card and fill the class instance in"""

    # Model (Part Number)
    model = re.search(r'(R5000-[QMOSL][mxnbtcs]{2,5}/[\dX\*]{1,3}.300.2x\d{3})(.2x\d{2})?',
                      dcard_raw_text_string).group()

    # Subfamily
    if 'L' in model or 'Sm' in model:
        subfamily = 'R5000 Lite'
    else:
        subfamily = 'R5000 Pro'

    # Serial number
    serial_number = re.search(r'SN:(\d+)', dcard_raw_text_string).group(1)

    # Firmware
    firmware = re.search(r'H\d{2}S\d{2}-(MINT|TDMA)[v\d.]+', dcard_raw_text_string).group()

    # Uptime
    uptime = re.search(r'Uptime: ([\d\w :]*)', dcard_raw_text_string).group(1)

    # Last Reboot Reason
    reboot_reason = re.search(r'Last reboot reason: ([\w ]*)', dcard_raw_text_string).group(1)

    # Settings
    radio_profile = {'Frequency': None, 'Bandwidth': None, 'Max bitrate': None, 'Auto bitrate': None, 'MIMO': None,
                     'SID': None, 'Status': None, 'Greenfield': None}
    radio_settings = {'Type': None, 'ATPC': None, 'Tx Power': None, 'Extnoise': None, 'DFS': None, 'Polling': None,
                      'Frame size': None, 'UL/DL ratio': None, 'Distance': None, 'Target RSSI': None, 'TSync': None,
                      'Scrambling': None, 'Profile': radio_profile}
    switch_group_settings = {'Order': None, 'Flood': None, 'STP': None, 'Management': None, 'Mode': None,
                             'Interfaces': None, 'Vlan': None, 'Rules': None}
    interfaces_settings = {'eth0': None, 'eth1': None, 'rf5.0': None}
    qos_settings = {'Rules': None, 'License': None}
    settings = {'Radio': radio_settings, 'Switch': switch_group_settings, 'Interface Status': interfaces_settings,
                'QoS': qos_settings}

    # Radio Settings
    radio_settings['Type'] = re.search(r'mint rf5\.0 -type (\w+)', dcard_raw_text_string).group(1)

    pattern = re.search(r'rf5\.0 txpwr (\d+)\s?(pwrctl)?\s?(extnoise (\d+))?', dcard_raw_text_string)
    radio_settings['Tx Power'] = pattern.group(1)
    radio_settings['ATPC'] = 'Disabled' if not pattern.group(2) else 'Enabled'
    if pattern.group(3): radio_settings['Extnoise'] = pattern.group(4)

    radio_settings['DFS'] = re.search(r'dfs rf5\.0 (dfsradar|dfsonly|dfsoff)', dcard_raw_text_string).group(1)

    pattern = re.search(r'mint rf5\.0 -(scrambling)', dcard_raw_text_string)
    radio_settings['Scrambling'] = 'Disabled' if pattern is None else 'Enabled'

    if 'TDMA' in firmware:
        pattern = re.search(r'mint rf5\.0 tdma mode=Master win=(\d+) dist=(\d+) dlp=(\d+)', dcard_raw_text_string)
        radio_settings['Frame size'] = pattern.group(1)
        radio_settings['Distance'] = pattern.group(2)
        radio_settings['UL/DL ratio'] = pattern.group(3)

        pattern = re.search(r'mint rf5\.0 tdma rssi=([-\d]+)', dcard_raw_text_string)
        radio_settings['Target RSSI'] = pattern.group(1)

        pattern = re.search(r'tsync enable', dcard_raw_text_string)
        radio_settings['TSync'] = 'Enabled' if pattern is None else 'Disabled'

    else:
        pattern = re.search(r'mint rf5\.0 poll start (qos)?', dcard_raw_text_string)
        radio_settings['Polling'] = 'Enabled' if pattern is None else 'Disabled'

    if radio_settings['Type'] == 'master':
        pattern = re.search(r'rf rf5\.0 freq (\d+) bitr (\d+) sid ([\d\w]+)', dcard_raw_text_string)
        radio_profile['Frequency'] = pattern.group(1)
        radio_profile['Max bitrate'] = pattern.group(2)
        radio_profile['SID'] = pattern.group(3)

        pattern = re.search(r'rf rf5\.0 band (\d+)', dcard_raw_text_string)
        radio_profile['Bandwidth'] = pattern.group(1)

        pattern = re.search(r'mint rf5\.0 -(auto|fixed)bitrate( ([\d-]+))?', dcard_raw_text_string)
        if pattern.group(1) == 'auto' and pattern.group(3) is None:
            radio_profile['Auto bitrate'] = 'Enabled'
        elif pattern.group(1) == 'auto' and pattern.group(3) is not None:
            radio_profile['Auto bitrate'] = 'Enabled. Modification is ' + str(pattern.group(3))
        else:
            radio_profile['Auto bitrate'] = 'Disabled. Fixed bitrate is ' + radio_profile['Max bitrate']

        pattern = re.search(r'rf rf5\.0 (mimo|miso|siso)( (greenfield))?', dcard_raw_text_string)
        radio_profile['MIMO'] = pattern.group(1)
        radio_profile['Greenfield'] = 'Enabled' if pattern.group(3) == 'greenfield' else 'Disabled'

    else:
        pattern = re.findall(r'mint rf5\.0 prof (\d+)'
                             r'( (disable))?'
                             r' -band (\d+)'
                             r' -freq ([\d\w]+)'
                             r'( -bitr (\d+))?'
                             r' -sid ([\d\w]+) \\'
                             r'\n\s+-nodeid (\d+)'
                             r' -type slave \\'
                             r'\n\s+-(auto|fixed)bitr( ([-+\d]+))?'
                             r' -(mimo|miso|siso)'
                             r' (greenfield)?', dcard_raw_text_string, re.DOTALL)

        radio_settings['Profile'] = {profile_id: deepcopy(radio_profile)
                                     for profile_id in [profile[0] for profile in pattern]}

        for key, prodile_id in enumerate(radio_settings['Profile']):
            radio_settings['Profile'][prodile_id]['Frequency'] = pattern[key][4]
            radio_settings['Profile'][prodile_id]['Bandwidth'] = pattern[key][3]
            radio_settings['Profile'][prodile_id]['Max bitrate'] = pattern[key][6] if pattern[key][6] != '' else 'Max'

            if pattern[key][9] == 'auto' and pattern[key][11] == '':
                radio_settings['Profile'][prodile_id]['Auto bitrate'] = 'Enabled'
            elif pattern[key][9] == 'auto' and pattern[key][11] != '':
                radio_settings['Profile'][prodile_id]['Auto bitrate'] = \
                    'Enabled. Modification is ' + pattern[key][11]
            else:
                radio_settings['Profile'][prodile_id]['Auto bitrate'] = \
                    'Disabled. Fixed bitrate is ' + radio_settings['Profile'][prodile_id]['Max bitrate']

            radio_settings['Profile'][prodile_id]['MIMO'] = pattern[key][12]
            radio_settings['Profile'][prodile_id]['SID'] = pattern[key][7]
            radio_settings['Profile'][prodile_id]['Status'] = 'Disabled' \
                if pattern[key][2] == 'disable' else 'Enabled'
            radio_settings['Profile'][prodile_id]['Greenfield'] = 'Enabled' \
                if pattern[key][13] == 'greenfield' else 'Disabled'

    # Switch Settings
    # This section will be added in the future
    switch_groups = set(re.findall(r'switch group (\d+)?', dcard_raw_text_string))
    settings['Switch'] = {sw_group_id: deepcopy(switch_group_settings) for sw_group_id in switch_groups}

    # Interface Settings
    pattern = re.findall(r'ifc\s(eth\d+|rf5\.0)\s+(media\s([\w\d-]+)\s)?(mtu\s\d+\s)?(up|down)', dcard_raw_text_string)
    for interface in pattern:
        if interface[0] == 'eth0':
            settings['Interface Status']['eth0'] = pattern[0][4]
        elif interface[0] == 'eth1':
            settings['Interface Status']['eth1'] = pattern[1][4]
        elif interface[0] == 'rf5.0' and len(pattern) is 3:
            settings['Interface Status']['rf5.0'] = pattern[2][4]
        elif interface[0] == 'rf5.0' and len(pattern) is 2:
            settings['Interface Status']['rf5.0'] = pattern[1][4]

    # QoS
    # This section will be added in the future

    # Radio Status
    link_status = {'Remote Name': None, 'Level Rx': None, 'Level Tx': None, 'Bitrate Rx': None,
                   'Bitrate Tx': None, 'Load Rx': None, 'Load Tx': None, 'PPS Rx': None, 'PPS Tx': None, 'Cost': None,
                   'Retry Rx': None, 'Retry Tx': None, 'Power Rx': None, 'Power Tx': None,
                   'RSSI Rx': None, 'RSSI Tx': None, 'SNR Rx': None, 'SNR Tx': None, 'Distance': None, 'Firmware': None,
                   'Uptime': None}

    if 'TDMA' in firmware:
        pattern = re.findall(r'\s+\d+\s+([\w\d\S]+)\s+([\w\d]+) '
                             r'(\d+)\/(\d+)\s+(\d+)\/(\d+)\s+(\d+)\/(\d+)\s+([\/\w])+'
                             r'\s+load (\d+)\/(\d+), pps (\d+)\/(\d+), cost (\d+)'
                             r'\s+pwr ([\d\.-]+)\/([\d\.-]+), rssi ([\d\.\-\*]+)\/([\d\.\-\*]+), snr (\d+)\/(\d+)'
                             r'\s+dist ([\d\.-]+)'
                             r'\s+(H\d{2}v[v\d.]+), IP=([\d\.])+, up ([\d\w :]*)'
                             , dcard_raw_text_string, re.DOTALL)

        radio_status = {mac: deepcopy(link_status) for mac in [link[1] for link in pattern]}

        for key, mac in enumerate(radio_status):
            radio_status[mac]['Remote Name'] = pattern[key][0]
            radio_status[mac]['Level Rx'] = pattern[key][2]
            radio_status[mac]['Level Tx'] = pattern[key][3]
            radio_status[mac]['Bitrate Rx'] = pattern[key][4]
            radio_status[mac]['Bitrate Tx'] = pattern[key][5]
            radio_status[mac]['Retry Rx'] = pattern[key][6]
            radio_status[mac]['Retry Tx'] = pattern[key][7]
            radio_status[mac]['Load Rx'] = pattern[key][9]
            radio_status[mac]['Load Tx'] = pattern[key][10]
            radio_status[mac]['PPS Rx'] = pattern[key][11]
            radio_status[mac]['PPS Tx'] = pattern[key][12]
            radio_status[mac]['Cost'] = pattern[key][13]
            radio_status[mac]['Power Rx'] = pattern[key][14]
            radio_status[mac]['Power Tx'] = pattern[key][15]
            radio_status[mac]['RSSI Rx'] = pattern[key][16]
            radio_status[mac]['RSSI Tx'] = pattern[key][17]
            radio_status[mac]['SNR Rx'] = pattern[key][18]
            radio_status[mac]['SNR Tx'] = pattern[key][19]
            radio_status[mac]['Distance'] = pattern[key][20]
            radio_status[mac]['Firmware'] = pattern[key][21]
            radio_status[mac]['Uptime'] = pattern[key][23]
    else:
        pattern = re.findall(r'\s+\d+\s+([\w\d\S]+)\s+([\w\d]+) '
                             r'(\d+)\/(\d+)\s+(\d+)\/(\d+)\s+(\d+)\/(\d+)\s+([\/\w])+'
                             r'\s+load (\d+)\/(\d+), pps (\d+)\/(\d+), cost (\d+)'
                             r'\s+pwr ([\d\.-]+)\/([\d\.-]+), snr (\d+)\/(\d+), dist ([\d\.-]+)'
                             r'\s+(H\d{2}v[v\d.]+), IP=([\d\.])+, up ([\d\w :]*)'
                             , dcard_raw_text_string, re.DOTALL)

        radio_status = {mac: deepcopy(link_status) for mac in [link[1] for link in pattern]}

        for key, mac in enumerate(radio_status):
            radio_status[mac]['Remote Name'] = pattern[key][0]
            radio_status[mac]['Level Rx'] = pattern[key][2]
            radio_status[mac]['Level Tx'] = pattern[key][3]
            radio_status[mac]['Bitrate Rx'] = pattern[key][4]
            radio_status[mac]['Bitrate Tx'] = pattern[key][5]
            radio_status[mac]['Retry Rx'] = pattern[key][6]
            radio_status[mac]['Retry Tx'] = pattern[key][7]
            radio_status[mac]['Load Rx'] = pattern[key][9]
            radio_status[mac]['Load Tx'] = pattern[key][10]
            radio_status[mac]['PPS Rx'] = pattern[key][11]
            radio_status[mac]['PPS Tx'] = pattern[key][12]
            radio_status[mac]['Cost'] = pattern[key][13]
            radio_status[mac]['Power Rx'] = pattern[key][14]
            radio_status[mac]['Power Tx'] = pattern[key][15]
            radio_status[mac]['SNR Rx'] = pattern[key][16]
            radio_status[mac]['SNR Tx'] = pattern[key][17]
            radio_status[mac]['Distance'] = pattern[key][18]
            radio_status[mac]['Firmware'] = pattern[key][19]
            radio_status[mac]['Uptime'] = pattern[key][21]

    ethernet_status = '1'

    result = R5000Card(model, subfamily, serial_number, firmware, uptime,
                       reboot_reason, dcard_raw_text_list, dcard_raw_text_string,
                       settings, radio_status, ethernet_status)

    return result


def parse_XG(dcard_raw_text_string, dcard_raw_text_list):
    """Parse a XG diagnostic card and fill the class instance in"""

    # Model (Part Number)
    model = re.search(r'(([XU]m/\dX?.\d{3,4}.\dx\d{3})(.2x\d{2})?)',
                      dcard_raw_text_string).group(1)

    # Subfamily
    if '500.2x500' in model:
        subfamily = 'XG 500'
    else:
        subfamily = 'XG 1000'

    # Serial number
    serial_number = re.search(r'SN:(\d+)', dcard_raw_text_string).group(1)

    # Firmware
    firmware = re.search(r'(\bH\d{2}S\d{2}[v\d.-]+\b)',
                         dcard_raw_text_string).group(1)
    # Uptime
    uptime = re.search(r'Uptime: ([\d\w :]*)', dcard_raw_text_string).group(1)

    # Last Reboot Reason
    reboot_reason = re.search(r'Last reboot reason: ([\w ]*)',
                              dcard_raw_text_string).group(1)

    # Settings
    settings = {
        'Role': None,
        'Bandwidth': None,
        'DL Frequency': {
            'Carrier 0': None,
            'Carrier 1': None
        },
        'UL Frequency': {
            'Carrier 0': None,
            'Carrier 1': None
        },
        'Short CP': None,
        'Max distance': None,
        'Frame size': None,
        'UL/DL Ratio': None,
        'Tx Power': None,
        'Control Block Boost': None,
        'ATPC': None,
        'AMC Strategy': None,
        'Max MCS': None,
        'IDFS': None,
        'Traffic prioritization': None,
        'Interface Status': {
            'Ge0': None,
            'Ge1': None,
            'SFP': None,
            'Radio': None
        }
    }

    settings['Role'] = re.search(r'# xg -type (\w+)',
                                 dcard_raw_text_string).group(1)
    settings['Bandwidth'] = re.search(r'# xg -channel-width (\d+)',
                                      dcard_raw_text_string).group(1)

    pattern = re.findall(r'# xg -freq-(u|d)l (\[0\])?(\d+),?(\[1\])?(\d+)?',
                         dcard_raw_text_string)
    settings['DL Frequency']['Carrier 0'] = pattern[0][2]
    settings['DL Frequency']['Carrier 1'] = pattern[0][4]
    settings['UL Frequency']['Carrier 0'] = pattern[1][2]
    settings['UL Frequency']['Carrier 1'] = pattern[1][4]

    pattern = re.search(r'# xg -short-cp (\d+)',
                        dcard_raw_text_string).group(1)
    settings['Short CP'] = 'Enabled' if pattern is '1' else 'Disabled'

    settings['Max distance'] = re.search(r'# xg -max-distance (\d+)',
                                         dcard_raw_text_string).group(1)
    settings['Frame size'] = re.search(r'# xg -sframelen (\d+)',
                                       dcard_raw_text_string).group(1)
    settings['UL/DL Ratio'] = re.search(
        r'DL\/UL\sRatio\s+\|(\d+/\d+(\s\(auto\))?)',
        dcard_raw_text_string).group(1)
    settings['Tx Power'] = re.search(r'# xg -txpwr (\d+)',
                                     dcard_raw_text_string).group(1)

    pattern = re.search(r'# xg -ctrl-block-boost (\d+)',
                        dcard_raw_text_string).group(1)
    settings[
        'Control Block Boost'] = 'Enabled' if pattern is '1' else 'Disabled'

    pattern = re.search(r'# xg -atpc-master-Enabled (\d+)',
                        dcard_raw_text_string).group(1)
    settings['ATPC'] = 'Enabled' if pattern is '1' else 'Disabled'

    settings['AMC Strategy'] = re.search(r'# xg -amc-strategy (\w+)',
                                         dcard_raw_text_string).group(1)
    settings['Max MCS'] = re.search(r'# xg -max-mcs (\d+)',
                                    dcard_raw_text_string).group(1)

    pattern = re.search(r'# xg -idfs-Enabled (\d+)',
                        dcard_raw_text_string).group(1)
    settings['IDFS'] = 'Enabled' if pattern is '1' else 'Disabled'

    pattern = re.search(r'# xg -traffic-prioritization (\d+)',
                        dcard_raw_text_string).group(1)
    settings[
        'Traffic prioritization'] = 'Enabled' if pattern is '1' else 'Disabled'

    pattern = re.findall(
        r'ifc\s(ge0|ge1|sfp|radio)\s+(media\s([\w\d-]+)\s)?(mtu\s\d+\s)?(\w+)',
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

    stream = {
        'Tx Power': None,
        'Tx Gain': None,
        'MCS': None,
        'CINR': None,
        'RSSI': None,
        'Crosstalk': None,
        'Errors Ratio': None
    }
    carrier = {
        'Frequency': None,
        'DFS': None,
        'Rx Acc FER': None,
        'Stream 0': stream,
        'Stream 1': deepcopy(stream)
    }
    role = {'Role': None, 'Carrier 0': carrier, 'Carrier 1': deepcopy(carrier)}
    radio_status = {
        'Link status': None,
        'Measured Distance': None,
        'Master': role,
        'Slave': deepcopy(role)
    }

    radio_status['Link status'] = re.search(r'Wireless Link\s+\|(\w+)',
                                            dcard_raw_text_string).group(1)

    pattern = re.search(r'Device Type\s+\|\s+(Master|Slave)\s+(\()?(\w+)?',
                        dcard_raw_text_string)
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
        radio_status['Measured Distance'] = re.search(
            r'Measured Distance\s+\|(\d+\smeters|-+)',
            dcard_raw_text_string).group(1)

        pattern = re.findall(
            r'Frequency\s+\|\s+(\d+)\sMHz(\s+\|\s+(\d+)\sMHz)?',
            dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Frequency'] = pattern[0][0]
            radio_status['Slave']['Carrier 0']['Frequency'] = pattern[0][2]
        else:
            radio_status['Master']['Carrier 0']['Frequency'] = pattern[0][0]
            radio_status['Slave']['Carrier 0']['Frequency'] = pattern[0][2]
            radio_status['Master']['Carrier 1']['Frequency'] = pattern[1][0]
            radio_status['Slave']['Carrier 1']['Frequency'] = pattern[1][2]

        pattern = re.findall(r'DFS status\s+\|\s+(\w+)', dcard_raw_text_string)
        radio_status['Master']['Carrier 0']['DFS'] = pattern[0]
        radio_status['Slave']['Carrier 0']['DFS'] = pattern[0]
        radio_status['Master']['Carrier 1']['DFS'] = pattern[0]
        radio_status['Slave']['Carrier 1']['DFS'] = pattern[0]

        pattern = re.findall(
            r'Rx\sAcc\sFER\s+\|\s+([\w\d.e-]+\s\([\d.%]+\))(\s+\|\s+([\w\d.e-]+\s\([\d.%]+\)))?',
            dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Rx Acc FER'] = pattern[0][0]
            radio_status['Slave']['Carrier 0']['Rx Acc FER'] = pattern[0][2]
        else:
            radio_status['Master']['Carrier 0']['Rx Acc FER'] = pattern[0][0]
            radio_status['Slave']['Carrier 0']['Rx Acc FER'] = pattern[0][2]
            radio_status['Master']['Carrier 1']['Rx Acc FER'] = pattern[1][0]
            radio_status['Slave']['Carrier 1']['Rx Acc FER'] = pattern[1][2]

        pattern = re.findall(
            r'Power\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm)(\s+\|([-\d.]+\sdBm)\s+\|([-\d.]+\sdBm))?',
            dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0'][
                'Tx Power'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1'][
                'Tx Power'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0'][
                'Tx Power'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1'][
                'Tx Power'] = pattern[0][4]
        else:
            radio_status['Master']['Carrier 0']['Stream 0'][
                'Tx Power'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1'][
                'Tx Power'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0'][
                'Tx Power'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1'][
                'Tx Power'] = pattern[0][4]
            radio_status['Master']['Carrier 1']['Stream 0'][
                'Tx Power'] = pattern[1][0]
            radio_status['Master']['Carrier 1']['Stream 1'][
                'Tx Power'] = pattern[1][1]
            radio_status['Slave']['Carrier 1']['Stream 0'][
                'Tx Power'] = pattern[1][3]
            radio_status['Slave']['Carrier 1']['Stream 1'][
                'Tx Power'] = pattern[1][4]

        pattern = re.findall(
            r'Gain\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)(\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB))?',
            dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0'][
                'Tx Gain'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1'][
                'Tx Gain'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0'][
                'Tx Gain'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1'][
                'Tx Gain'] = pattern[0][4]
        else:
            radio_status['Master']['Carrier 0']['Stream 0'][
                'Tx Gain'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1'][
                'Tx Gain'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0'][
                'Tx Gain'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1'][
                'Tx Gain'] = pattern[0][4]
            radio_status['Master']['Carrier 1']['Stream 0'][
                'Tx Gain'] = pattern[1][0]
            radio_status['Master']['Carrier 1']['Stream 1'][
                'Tx Gain'] = pattern[1][1]
            radio_status['Slave']['Carrier 1']['Stream 0'][
                'Tx Gain'] = pattern[1][3]
            radio_status['Slave']['Carrier 1']['Stream 1'][
                'Tx Gain'] = pattern[1][4]

        pattern = re.findall(
            r'RX\s+\|MCS\s+\|([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|'
            r'([\w\d]+\s\d+\/\d+\s\(\d+\))(\s+\|'
            r'([\w\d]+\s\d+\/\d+\s\(\d+\))\s+\|'
            r'([\w\d]+\s\d+\/\d+\s\(\d+\)))?',
            dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['MCS'] = pattern[
                0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['MCS'] = pattern[
                0][1]
            radio_status['Slave']['Carrier 0']['Stream 0']['MCS'] = pattern[0][
                3]
            radio_status['Slave']['Carrier 0']['Stream 1']['MCS'] = pattern[0][
                4]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['MCS'] = pattern[
                0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['MCS'] = pattern[
                0][1]
            radio_status['Slave']['Carrier 0']['Stream 0']['MCS'] = pattern[0][
                3]
            radio_status['Slave']['Carrier 0']['Stream 1']['MCS'] = pattern[0][
                4]
            radio_status['Master']['Carrier 1']['Stream 0']['MCS'] = pattern[
                1][0]
            radio_status['Master']['Carrier 1']['Stream 1']['MCS'] = pattern[
                1][1]
            radio_status['Slave']['Carrier 1']['Stream 0']['MCS'] = pattern[1][
                3]
            radio_status['Slave']['Carrier 1']['Stream 1']['MCS'] = pattern[1][
                4]

        pattern = re.findall(
            r'CINR\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)(\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB))?',
            dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['CINR'] = pattern[
                0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['CINR'] = pattern[
                0][1]
            radio_status['Slave']['Carrier 0']['Stream 0']['CINR'] = pattern[
                0][3]
            radio_status['Slave']['Carrier 0']['Stream 1']['CINR'] = pattern[
                0][4]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['CINR'] = pattern[
                0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['CINR'] = pattern[
                0][1]
            radio_status['Slave']['Carrier 0']['Stream 0']['CINR'] = pattern[
                0][3]
            radio_status['Slave']['Carrier 0']['Stream 1']['CINR'] = pattern[
                0][4]
            radio_status['Master']['Carrier 1']['Stream 0']['CINR'] = pattern[
                1][0]
            radio_status['Master']['Carrier 1']['Stream 1']['CINR'] = pattern[
                1][1]
            radio_status['Slave']['Carrier 1']['Stream 0']['CINR'] = pattern[
                1][3]
            radio_status['Slave']['Carrier 1']['Stream 1']['CINR'] = pattern[
                1][4]

        pattern = re.findall(
            r'RSSI\s+\|([-\d.]+\sdBm)(\s\([\d-]+\))?\s+\|'
            r'([-\d.]+\sdBm)(\s\([\d-]+\))?(\s+\|'
            r'([-\d.]+\sdBm)(\s\([\d-]+\))?\s+\|'
            r'([-\d.]+\sdBm)(\s\([\d-]+\))?)?',
            dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0']['RSSI'] = pattern[
                0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['RSSI'] = pattern[
                0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['RSSI'] = pattern[
                0][5]
            radio_status['Slave']['Carrier 0']['Stream 1']['RSSI'] = pattern[
                0][7]
        else:
            radio_status['Master']['Carrier 0']['Stream 0']['RSSI'] = pattern[
                0][0]
            radio_status['Master']['Carrier 0']['Stream 1']['RSSI'] = pattern[
                0][2]
            radio_status['Slave']['Carrier 0']['Stream 0']['RSSI'] = pattern[
                0][5]
            radio_status['Slave']['Carrier 0']['Stream 1']['RSSI'] = pattern[
                0][7]
            radio_status['Master']['Carrier 1']['Stream 0']['RSSI'] = pattern[
                1][0]
            radio_status['Master']['Carrier 1']['Stream 1']['RSSI'] = pattern[
                1][2]
            radio_status['Slave']['Carrier 1']['Stream 0']['RSSI'] = pattern[
                1][5]
            radio_status['Slave']['Carrier 1']['Stream 1']['RSSI'] = pattern[
                1][7]

        pattern = re.findall(
            r'Crosstalk\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB)(\s+\|([-\d.]+\sdB)\s+\|([-\d.]+\sdB))?',
            dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0'][
                'Crosstalk'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1'][
                'Crosstalk'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0'][
                'Crosstalk'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1'][
                'Crosstalk'] = pattern[0][4]
        else:
            radio_status['Master']['Carrier 0']['Stream 0'][
                'Crosstalk'] = pattern[0][0]
            radio_status['Master']['Carrier 0']['Stream 1'][
                'Crosstalk'] = pattern[0][1]
            radio_status['Slave']['Carrier 0']['Stream 0'][
                'Crosstalk'] = pattern[0][3]
            radio_status['Slave']['Carrier 0']['Stream 1'][
                'Crosstalk'] = pattern[0][4]
            radio_status['Master']['Carrier 1']['Stream 0'][
                'Crosstalk'] = pattern[1][0]
            radio_status['Master']['Carrier 1']['Stream 1'][
                'Crosstalk'] = pattern[1][1]
            radio_status['Slave']['Carrier 1']['Stream 0'][
                'Crosstalk'] = pattern[1][3]
            radio_status['Slave']['Carrier 1']['Stream 1'][
                'Crosstalk'] = pattern[1][4]

        pattern = re.findall(
            r'(TBER|Errors\sRatio)\s+\|[\d\.e-]+\s\(([\d.]+%)\)\s+\|'
            r'[\d\.e-]+\s\(([\d.]+%)\)(\s+\|'
            r'[\d\.e-]+\s\(([\d.]+%)\)\s+\|'
            r'[\d\.e-]+\s\(([\d.]+%)\))?',
            dcard_raw_text_string)
        if len(pattern) is 1:
            radio_status['Master']['Carrier 0']['Stream 0'][
                'Errors Ratio'] = pattern[0][1]
            radio_status['Master']['Carrier 0']['Stream 1'][
                'Errors Ratio'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0'][
                'Errors Ratio'] = pattern[0][4]
            radio_status['Slave']['Carrier 0']['Stream 1'][
                'Errors Ratio'] = pattern[0][5]
        else:
            radio_status['Master']['Carrier 0']['Stream 0'][
                'Errors Ratio'] = pattern[0][1]
            radio_status['Master']['Carrier 0']['Stream 1'][
                'Errors Ratio'] = pattern[0][2]
            radio_status['Slave']['Carrier 0']['Stream 0'][
                'Errors Ratio'] = pattern[0][4]
            radio_status['Slave']['Carrier 0']['Stream 1'][
                'Errors Ratio'] = pattern[0][5]
            radio_status['Master']['Carrier 1']['Stream 0'][
                'Errors Ratio'] = pattern[1][1]
            radio_status['Master']['Carrier 1']['Stream 1'][
                'Errors Ratio'] = pattern[1][2]
            radio_status['Slave']['Carrier 1']['Stream 0'][
                'Errors Ratio'] = pattern[1][4]
            radio_status['Slave']['Carrier 1']['Stream 1'][
                'Errors Ratio'] = pattern[1][5]

    # Ethernet Status
    ethernet_statuses = {
        'Status': None,
        'Speed': None,
        'Duplex': None,
        'Negotiation': None,
        'Rx CRC': None,
        'Tx CRC': None
    }
    ethernet_status = {
        'ge0': ethernet_statuses,
        'ge1': deepcopy(ethernet_statuses),
        'sfp': deepcopy(ethernet_statuses)
    }

    pattern = re.findall(
        r'Physical link is (\w+)(, (\d+ Mbps) ([\w-]+), (\w+))?',
        dcard_raw_text_string)
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

    pattern = re.findall(r'CRC errors\s+(\d+)', dcard_raw_text_string)
    ethernet_status['ge0']['Rx CRC'] = pattern[0]
    ethernet_status['ge1']['Rx CRC'] = pattern[2]
    ethernet_status['sfp']['Rx CRC'] = pattern[4]
    ethernet_status['ge0']['Tx CRC'] = pattern[1]
    ethernet_status['ge1']['Tx CRC'] = pattern[3]
    ethernet_status['sfp']['Tx CRC'] = pattern[5]

    # Panic
    panic = []
    for line in dcard_raw_text_list:
        if re.search(r'^Panic info : [\W\w]+$', line) is not None:
            panic.append(line)

    result = XGCard(model, subfamily, serial_number, firmware, uptime,
                    reboot_reason, dcard_raw_text_list, dcard_raw_text_string,
                    settings, radio_status, ethernet_status, panic)

    return result


def parse_Quanta(dcard_raw_text_string, dcard_raw_text_list):
    """Parse a Quanta 5 diagnostic card and fill the class instance in"""

    # Model (Part Number)
    model = re.search(r'([QV](5|70)-[\dE]+)', dcard_raw_text_string).group(1)

    # Subfamily
    # global subfamily
    if 'Q5' in model:
        subfamily = 'Quanta 5'
    elif 'V5' in model:
        subfamily = 'Vector 5'
    elif 'Q70' in model:
        subfamily = 'Quanta 70'
    elif 'V70' in model:
        subfamily = 'Vector 70'

    # Firmware
    firmware = re.search(r'(H\d{2}S\d{2}-OCTOPUS_PTPv[\d.]+)',
                         dcard_raw_text_string).group(1)

    # Serial number
    serial_number = re.search(r'SN:(\d+)', dcard_raw_text_string).group(1)

    # Uptime
    uptime = re.search(r'Uptime: ([\d\w :]*)', dcard_raw_text_string).group(1)

    # Last Reboot Reason
    reboot_reason = re.search(r'Last reboot reason: ([\w ]*)',
                              dcard_raw_text_string).group(1)

    # Settings
    settings = {
        'Role': None,
        'Bandwidth': None,
        'DL Frequency': None,
        'UL Frequency': None,
        'Frame size': None,
        'Guard Interval': None,
        'UL/DL Ratio': None,
        'Tx Power': None,
        'ATPC': None,
        'AMC Strategy': None,
        'Max DL MCS': None,
        'Max UL MCS': None,
        'DFS': None,
        'ARQ': None,
        'Interface Status': {
            'Ge0': None,
            'Radio': None
        }
    }

    settings['Role'] = re.search(r'ptp_role (\w+)',
                                 dcard_raw_text_string).group(1)
    settings['Bandwidth'] = re.search(r'bw (\d+)',
                                      dcard_raw_text_string).group(1)
    settings['DL Frequency'] = re.search(r'freq_dl (\d+)',
                                         dcard_raw_text_string).group(1)
    settings['UL Frequency'] = re.search(r'freq_ul (\d+)',
                                         dcard_raw_text_string).group(1)
    settings['Frame size'] = re.search(r'frame_length (\d+)',
                                       dcard_raw_text_string).group(1)
    settings['Guard Interval'] = re.search(r'guard_interval (\d+\/\d+)',
                                           dcard_raw_text_string).group(1)

    if re.search(r'auto_dl_ul_ratio (\w+)',
                 dcard_raw_text_string).group(1) == 'on':
        settings['UL/DL Ratio'] = re.search(
            r'dl_ul_ratio (\d+)', dcard_raw_text_string).group(1) + ' (auto)'
    else:
        settings['UL/DL Ratio'] = re.search(r'dl_ul_ratio (\d+)',
                                            dcard_raw_text_string).group(1)

    settings['Tx Power'] = re.search(r'tx_power (\d+)',
                                     dcard_raw_text_string).group(1)
    settings['ATPC'] = 'Enabled' if re.search(
        r'atpc (on|off)',
        dcard_raw_text_string).group(1) == 'on' else 'Disabled'
    settings['AMC Strategy'] = re.search(r'amc_strategy (\w+)',
                                         dcard_raw_text_string).group(1)
    settings['Max DL MCS'] = re.search(
        r'dl_mcs (([\d-]+)?(QPSK|QAM)-\d+\/\d+)',
        dcard_raw_text_string).group(1)
    settings['Max UL MCS'] = re.search(
        r'ul_mcs (([\d-]+)?(QPSK|QAM)-\d+\/\d+)',
        dcard_raw_text_string).group(1)
    settings['DFS'] = 'Enabled' if re.search(
        r'dfs (dfs_rd|off)',
        dcard_raw_text_string).group(1) == 'dfs_rd' else 'Disabled'
    settings['ARQ'] = 'Enabled' if re.search(
        r'harq (on|off)',
        dcard_raw_text_string).group(1) == 'on' else 'Disabled'
    pattern = re.findall(r'ifc\sge0\s+media\s([\w\d]+)\smtu\s\d+\s(up|down)',
                         dcard_raw_text_string)
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

    stream = {
        'Tx Power': None,
        'MCS': None,
        'RSSI': None,
        'EVM': None,
        'Crosstalk': None,
        'ARQ ratio': None
    }
    role = {
        'Frequency': None,
        'Stream 0': stream,
        'Stream 1': deepcopy(stream)
    }
    radio_status = {
        'Link status': None,
        'Measured Distance': None,
        'Downlink': role,
        'Uplink': deepcopy(role)
    }

    radio_status['Link status'] = re.search(r'State\s+(\w+)',
                                            dcard_raw_text_string).group(1)
    radio_status['Measured Distance'] = re.search(
        r'Distance\s+(\d+\sm)', dcard_raw_text_string).group(1)
    pattern = re.search(r'Frequency\s+\|\s(\d+)\sMHz\s+\|\s(\d+)\sMHz',
                        dcard_raw_text_string)
    radio_status['Downlink']['Frequency'] = pattern.group(1)
    radio_status['Uplink']['Frequency'] = pattern.group(2)

    if radio_status['Link status'] == 'connected':
        if settings['Role'] == 'master':
            pattern = re.search(r'\| TX power\s+([\d\.]+)\s\/\s([\d\.]+)\sdBm',
                                dcard_raw_text_string)
            radio_status['Downlink']['Stream 0']['Tx Power'] = pattern.group(1)
            radio_status['Downlink']['Stream 1']['Tx Power'] = pattern.group(2)
            pattern = re.search(
                r'Remote TX power\s+([\d\.]+)\s\/\s([\d\.]+)\sdBm',
                dcard_raw_text_string)
            radio_status['Uplink']['Stream 0']['Tx Power'] = pattern.group(1)
            radio_status['Uplink']['Stream 1']['Tx Power'] = pattern.group(2)
        else:
            pattern = re.search(r'\| TX power\s+([\d\.]+)\s\/\s([\d\.]+)\sdBm',
                                dcard_raw_text_string)
            radio_status['Uplink']['Stream 0']['Tx Power'] = pattern.group(1)
            radio_status['Uplink']['Stream 1']['Tx Power'] = pattern.group(2)
            pattern = re.search(
                r'Remote TX power\s+([\d\.]+)\s\/\s([\d\.]+)\sdBm',
                dcard_raw_text_string)
            radio_status['Downlink']['Stream 0']['Tx Power'] = pattern.group(1)
            radio_status['Downlink']['Stream 1']['Tx Power'] = pattern.group(2)

        for line in dcard_raw_text_list:
            if line.startswith('| MCS'):
                pattern = re.findall(r'(([\d-]+)?(QPSK|QAM)-\d+\/\d+)', line)
                radio_status['Downlink']['Stream 0']['MCS'] = pattern[0][0]
                radio_status['Downlink']['Stream 1']['MCS'] = pattern[1][0]
                radio_status['Uplink']['Stream 0']['MCS'] = pattern[2][0]
                radio_status['Uplink']['Stream 1']['MCS'] = pattern[3][0]
            elif line.startswith('| RSSI'):
                pattern = re.findall(r'([-\d.]+\sdBm)', line)
                radio_status['Downlink']['Stream 0']['RSSI'] = pattern[0]
                radio_status['Downlink']['Stream 1']['RSSI'] = pattern[1]
                radio_status['Uplink']['Stream 0']['RSSI'] = pattern[2]
                radio_status['Uplink']['Stream 1']['RSSI'] = pattern[3]
            elif line.startswith('| EVM'):
                pattern = re.findall(r'([-\d.]+\sdB)', line)
                radio_status['Downlink']['Stream 0']['EVM'] = pattern[0]
                radio_status['Downlink']['Stream 1']['EVM'] = pattern[1]
                radio_status['Uplink']['Stream 0']['EVM'] = pattern[2]
                radio_status['Uplink']['Stream 1']['EVM'] = pattern[3]
            elif line.startswith('| Crosstalk'):
                pattern = re.findall(r'([-\d.]+\sdB)', line)
                radio_status['Downlink']['Stream 0']['Crosstalk'] = pattern[0]
                radio_status['Downlink']['Stream 1']['Crosstalk'] = pattern[1]
                radio_status['Uplink']['Stream 0']['Crosstalk'] = pattern[2]
                radio_status['Uplink']['Stream 1']['Crosstalk'] = pattern[3]
            elif line.startswith('| ARQ ratio'):
                pattern = re.findall(r'(\d+\.\d+\s%)', line)
                radio_status['Downlink']['Stream 0']['ARQ ratio'] = pattern[0]
                radio_status['Downlink']['Stream 1']['ARQ ratio'] = pattern[1]
                radio_status['Uplink']['Stream 0']['ARQ ratio'] = pattern[2]
                radio_status['Uplink']['Stream 1']['ARQ ratio'] = pattern[3]

    # Ethernet Status
    ethernet_status = {
        'ge0': {
            'Status': None,
            'Speed': None,
            'Duplex': None,
            'Negotiation': None,
            'CRC': None
        }
    }

    pattern = re.findall(
        r'Physical link is (\w+)(, (\d+ Mbps) ([\w-]+), (\w+))?',
        dcard_raw_text_string)
    ethernet_status['ge0']['Status'] = pattern[0][0]
    ethernet_status['ge0']['Speed'] = pattern[0][2]
    ethernet_status['ge0']['Duplex'] = pattern[0][3]
    ethernet_status['ge0']['Negotiation'] = pattern[0][4]

    pattern = re.findall(r'CRC errors\s+(\d+)', dcard_raw_text_string)
    ethernet_status['ge0']['CRC'] = pattern[0]

    result = QCard(model, subfamily, serial_number, firmware, uptime,
                   reboot_reason, dcard_raw_text_list, dcard_raw_text_string,
                   settings, radio_status, ethernet_status)

    return result
