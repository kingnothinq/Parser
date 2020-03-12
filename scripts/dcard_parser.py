#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from copy import deepcopy

from scripts.my_classes import *


def parse_r5000(dc_string, dc_list):
    """Parse an R5000 diagnostic card and fill the class instance in.

    This function returns result (the class instance) included the next variables:
    model (type str) - a device model
    subfamily (type str) - R5000 Pro, R5000 Lite, R5000 Lite (low cost CPE)
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
        Radio
            Type
            ATPC
            Tx Power
            Extnoise
            DFS
            Polling (MINT Master Only)
            Frame size (TDMA Master Only)
            DL/UL ratio (TDMA Master Only)
            Distance (TDMA Master Only)
            Target RSSI (TDMA Master Only)
            TSync (TDMA Master Only)
            Scrambling
            Profile (Key/Name/ID is Profile ID)
                Frequency
                Bandwidth
                Max bitrate
                Auto bitrate
                MIMO
                SID
                Status
                Greenfield
        Switch
            Status
            Switch Group
                Order
                Flood
                STP
                Management
                Mode
                Interfaces
                Vlan
                Rules
        Interface Status
            eth0
            eth1 (R5000 Lite Only)
            rf5.0
        QoS
            Rules
            License

    Example of request: settings['MAC']['Radio']['Profile']['Frequency']

    ______________________
    radio_status structure
        Links
            All links (Key/Name/ID is Remote MAC)
                Name
                Level Rx
                Level Tx
                Bitrate Rx
                Bitrate Tx
                Load Rx
                Load Tx
                PPS Rx
                PPS Tx
                Cost
                Retry Rx
                Retry Tx
                Flags
                Power Rx
                Power Tx
                RSSI Rx
                RSSI Tx (TDMA Only)
                SNR Rx
                SNR Tx
                Distance
                Firmware
                Uptime
        Pulses
        Interference Level
        Interference RSSI
        Interference PPS
        RX Medium Load
        TX Medium Load
        Total Medium Busy
        Excessive Retries
        Aggr Full Retries

    Example of request: radio_status['Links']['MAC']['RSSI Rx']

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

    # General info
    firmware = re.search(r'H\d{2}S\d{2}-(MINT|TDMA)[v\d.]+', dc_string).group()

    pattern = re.search(r'(R5000-[QMOSL][mxnbtcs]{2,5}/[\dX\*]'
                        r'{1,3}.300.2x\d{3})(.2x\d{2})?', dc_string)
    if pattern is not None:
        model = pattern.group()
        if ('L' in model or 'S' in model) and '2x19' in model:
            subfamily = 'R5000 Lite (low cost CPE)'
        elif 'L' in model or 'S' in model:
            subfamily = 'R5000 Lite'
        else:
            subfamily = 'R5000 Pro'
    elif pattern is None and 'H11' in firmware:
        model = 'R5000 Unknown model'
        subfamily = 'R5000 Lite'
    else:
        model = 'R5000 Unknown model'
        subfamily = 'R5000 Pro'

    serial_number = re.search(r'SN:(\d+)', dc_string).group(1)
    uptime = re.search(r'Uptime: ([\d\w :]*)', dc_string).group(1)
    reboot_reason = re.search(r'Last reboot reason: ([\w ]*)', dc_string).group(1)

    # Settings
    radio_profile = {'Frequency': None, 'Bandwidth': None, 'Max bitrate': None, 'Auto bitrate': None, 'MIMO': None,
                     'SID': None, 'Status': None, 'Greenfield': None, 'State': None}
    radio_settings = {'Type': None, 'ATPC': None, 'Tx Power': None, 'Extnoise': None, 'DFS': None, 'Polling': None,
                      'Frame size': None, 'DL/UL ratio': None, 'Distance': None, 'Target RSSI': None, 'TSync': None,
                      'Scrambling': None, 'Profile': radio_profile}
    switch_group_settings = {'Order': None, 'Flood': None, 'STP': None, 'Management': None, 'Mode': None,
                             'Interfaces': None, 'Vlan': None, 'Rules': None}
    interfaces_settings = {'eth0': None, 'eth1': None, 'rf5.0': None}
    qos_settings = {'Rules': None, 'License': None}
    settings = {'Radio': radio_settings, 'Switch': switch_group_settings, 'Interface Status': interfaces_settings,
                'QoS': qos_settings}

    # Radio Settings
    radio_settings['Type'] = re.search(r'mint rf5\.0 -type (\w+)', dc_string).group(1)

    pattern = re.search(r'rf5\.0 txpwr (-?\d+)\s?(pwrctl)?\s?(extnoise (\d+))?', dc_string)
    radio_settings['Tx Power'] = pattern.group(1)
    radio_settings['ATPC'] = 'Disabled' if not pattern.group(2) else 'Enabled'
    if pattern.group(3):
        radio_settings['Extnoise'] = pattern.group(4)

    radio_settings['DFS'] = re.search(r'dfs rf5\.0 (dfsradar|dfsonly|dfsoff)', dc_string).group(1)

    pattern = re.search(r'mint rf5\.0 -(scrambling)', dc_string)
    radio_settings['Scrambling'] = 'Disabled' if pattern is None else 'Enabled'

    if 'TDMA' in firmware and radio_settings['Type'] == 'master':
        pattern = re.search(r'mint rf5\.0 tdma mode=Master win=(\d+) dist=(\d+) dlp=(\d+)', dc_string)
        radio_settings['Frame size'] = pattern.group(1)
        radio_settings['Distance'] = pattern.group(2)
        radio_settings['DL/UL ratio'] = pattern.group(3)

        pattern = re.search(r'mint rf5\.0 tdma rssi=([\-\d]+)', dc_string)
        radio_settings['Target RSSI'] = pattern.group(1)

        pattern = re.search(r'tsync enable', dc_string)
        radio_settings['TSync'] = 'Disabled' if pattern is None else 'Enabled'

    elif 'MINT' in firmware and radio_settings['Type'] == 'master':
        pattern = re.search(r'mint rf5\.0 poll start (qos)?', dc_string)
        radio_settings['Polling'] = 'Disabled' if pattern is None else 'Enabled'

    if radio_settings['Type'] == 'master':
        radio_settings['Profile'] = {'M': deepcopy(radio_profile)}
        profile = radio_settings['Profile']['M']
        pattern = re.search(r'rf rf5\.0 freq (\d+) bitr (\d+) sid ([\d\w]+)', dc_string)
        profile['Frequency'] = pattern.group(1)
        profile['Max bitrate'] = pattern.group(2)
        profile['SID'] = pattern.group(3)
        pattern = re.search(r'rf rf5\.0 band (\d+)', dc_string)
        profile['Bandwidth'] = pattern.group(1)
        pattern = re.search(r'mint rf5\.0 -(auto|fixed)bitrate( ([\-\d]+))?', dc_string)
        if pattern.group(1) == 'auto' and pattern.group(3) is None:
            profile['Auto bitrate'] = 'Enabled'
        elif pattern.group(1) == 'auto' and pattern.group(3) is not None:
            profile['Auto bitrate'] = 'Enabled. Modification is ' + str(pattern.group(3))
        else:
            profile['Auto bitrate'] = 'Disabled. Fixed bitrate is ' + profile['Max bitrate']

        pattern = re.search(r'rf rf5\.0 (mimo|miso|siso)( (greenfield))?', dc_string)
        profile['MIMO'] = pattern.group(1)
        profile['Greenfield'] = 'Enabled' if pattern.group(3) == 'greenfield' else 'Disabled'
        profile['State'] = 'Active'
    else:
        pattern = re.findall(r'mint rf5\.0 prof (\d+)( (disable))?'
                             r' -band (\d+) -freq ([\d\w]+)'
                             r'( -bitr (\d+))? -sid ([\d\w]+) \\'
                             r'\s+-nodeid (\d+) -type slave '
                             r'(-netid \d+\s+)?\\(\s+-minbitr \d+)?'
                             r'\s+-(auto|fixed)bitr( ([\-+\d]+))?'
                             r' -(mimo|miso|siso)\s?'
                             r'(greenfield)?', dc_string, re.DOTALL)
        pattern_2 = re.findall(r'[\w\d]+ band \d+ freq (\d+) '
                               r'snr \d+ links \d+, prof (\d+)', dc_string)
        if pattern_2:
            pattern_2 = pattern_2[-1]

        radio_settings['Profile'] = {profile_id: deepcopy(radio_profile) for profile_id in
                                     [profile[0] for profile in pattern]}
        profile = radio_settings['Profile']

        for key, prodile_id in enumerate(radio_settings['Profile']):
            profile[prodile_id]['Frequency'] = pattern[key][4]
            profile[prodile_id]['Bandwidth'] = pattern[key][3]

            if pattern[key][6] != '':
                profile[prodile_id]['Max bitrate'] = pattern[key][6]
            else:
                profile[prodile_id]['Max bitrate'] = 'Max'

            if pattern[key][11] == 'auto' and pattern[key][13] == '':
                profile[prodile_id]['Auto bitrate'] = 'Enabled'
            elif pattern[key][11] == 'auto' and pattern[key][13] != '':
                profile[prodile_id]['Auto bitrate'] = 'Enabled. ' \
                                                      'Modification is {}'.format(pattern[key][13])
            else:
                profile[prodile_id]['Auto bitrate'] = 'Disabled. ' \
                                                      'Fixed bitrate is {}'.format(profile[prodile_id]['Max bitrate'])

            profile[prodile_id]['MIMO'] = pattern[key][14]
            profile[prodile_id]['SID'] = pattern[key][7]

            if pattern[key][2] == 'disable':
                profile[prodile_id]['Status'] = 'Disabled'
            else:
                profile[prodile_id]['Status'] = 'Enabled'

            if pattern[key][15] == 'greenfield':
                profile[prodile_id]['Greenfield'] = 'Enabled'
            else:
                profile[prodile_id]['Greenfield'] = 'Disabled'

            if profile[prodile_id]['Frequency'] == 'auto' and pattern_2 and prodile_id == pattern_2[1]:
                profile[prodile_id]['State'] = 'Active'
                profile[prodile_id]['Frequency'] = '{} (auto)'.format(pattern_2[0])
            elif pattern_2 and prodile_id == pattern_2[1]:
                profile[prodile_id]['State'] = 'Active'
            else:
                profile[prodile_id]['State'] = 'Idle'

    # Switch Settings
    # This section will be added in the future
    switch_groups = set(re.findall(r'switch group (\d+)?', dc_string))
    settings['Switch'] = {sw_group_id: deepcopy(switch_group_settings) for sw_group_id in switch_groups}

    # Interface Settings
    pattern = re.findall(r'ifc\s(eth\d+|rf5\.0)\s+(media\s([\w\d-]+)\s)?(mtu\s\d+\s)?(up|down)', dc_string)
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
    link_status = {'Name': None, 'Level Rx': None, 'Level Tx': None, 'Bitrate Rx': None, 'Bitrate Tx': None,
                   'Load Rx': None, 'Load Tx': None, 'PPS Rx': None, 'PPS Tx': None, 'Cost': None, 'Retry Rx': None,
                   'Retry Tx': None, 'Power Rx': None, 'Power Tx': None, 'RSSI Rx': None, 'RSSI Tx': None,
                   'SNR Rx': None, 'SNR Tx': None, 'Distance': None, 'Firmware': None, 'Uptime': None, 'Flags': None}
    radio_status = {'Links': None, 'Pulses': None, 'Interference Level': None, 'Interference RSSI': None,
                    'Interference PPS': None, 'RX Medium Load': None, 'TX Medium Load': None, 'Total Medium Busy': None,
                    'Excessive Retries': None, 'Aggr Full Retries': None}

    if 'TDMA' in firmware:
        pattern = re.findall(r'\s+\d+\s+([\w\d\S]+)\s+([\w\d]+) '
                             r'(\d+)\/(\d+)\s+(\d+)\/(\d+)\s+(\d+)\/(\d+)\s+([\/\w]+)+'
                             r'\s+load (\d+)\/(\d+), pps (\d+)\/(\d+), cost (\d+)'
                             r'\s+pwr ([\d\.-]+)\/([\d\.-]+), rssi ([\d\.\-\*]+)\/([\d\.\-\*]+), snr (\d+)\/(\d+)'
                             r'\s+dist ([\d\.-]+)'
                             r'\s+(H\d{2}v[v\d.]+), IP=([\d\.])+, up ([\d\w :]*)', dc_string, re.DOTALL)

        radio_status['Links'] = {mac: deepcopy(link_status) for mac in [link[1] for link in pattern]}

        for key, mac in enumerate(radio_status['Links']):
            radio_status['Links'][mac]['Name'] = pattern[key][0]
            radio_status['Links'][mac]['Level Rx'] = pattern[key][2]
            radio_status['Links'][mac]['Level Tx'] = pattern[key][3]
            radio_status['Links'][mac]['Bitrate Rx'] = pattern[key][4]
            radio_status['Links'][mac]['Bitrate Tx'] = pattern[key][5]
            radio_status['Links'][mac]['Retry Rx'] = pattern[key][6]
            radio_status['Links'][mac]['Retry Tx'] = pattern[key][7]
            radio_status['Links'][mac]['Flags'] = pattern[key][8]
            radio_status['Links'][mac]['Load Rx'] = pattern[key][9]
            radio_status['Links'][mac]['Load Tx'] = pattern[key][10]
            radio_status['Links'][mac]['PPS Rx'] = pattern[key][11]
            radio_status['Links'][mac]['PPS Tx'] = pattern[key][12]
            radio_status['Links'][mac]['Cost'] = pattern[key][13]
            radio_status['Links'][mac]['Power Rx'] = pattern[key][14]
            radio_status['Links'][mac]['Power Tx'] = pattern[key][15]
            radio_status['Links'][mac]['RSSI Rx'] = pattern[key][16]
            radio_status['Links'][mac]['RSSI Tx'] = pattern[key][17]
            radio_status['Links'][mac]['SNR Rx'] = pattern[key][18]
            radio_status['Links'][mac]['SNR Tx'] = pattern[key][19]
            radio_status['Links'][mac]['Distance'] = pattern[key][20]
            radio_status['Links'][mac]['Firmware'] = pattern[key][21]
            radio_status['Links'][mac]['Uptime'] = pattern[key][23]
    else:
        pattern = re.findall(r'\s+\d+\s+([\w\d\S]+)\s+([\w\d]+) '
                             r'(\d+)\/(\d+)\s+(\d+)\/(\d+)\s+(\d+)\/(\d+)\s+([\/\w]+)+'
                             r'\s+load (\d+)\/(\d+), pps (\d+)\/(\d+), cost (\d+)'
                             r'\s+pwr ([\d\.\-]+)\/([\d\.\-]+), snr (\d+)\/(\d+), dist ([\d\.-]+)'
                             r'\s+(H\d{2}v[v\d.]+), IP=([\d\.])+, up ([\d\w :]*)', dc_string, re.DOTALL)

        radio_status['Links'] = {mac: deepcopy(link_status) for mac in [link[1] for link in pattern]}

        for key, mac in enumerate(radio_status['Links']):
            radio_status['Links'][mac]['Name'] = pattern[key][0]
            radio_status['Links'][mac]['Level Rx'] = pattern[key][2]
            radio_status['Links'][mac]['Level Tx'] = pattern[key][3]
            radio_status['Links'][mac]['Bitrate Rx'] = pattern[key][4]
            radio_status['Links'][mac]['Bitrate Tx'] = pattern[key][5]
            radio_status['Links'][mac]['Retry Rx'] = pattern[key][6]
            radio_status['Links'][mac]['Retry Tx'] = pattern[key][7]
            radio_status['Links'][mac]['Flags'] = pattern[key][8]
            radio_status['Links'][mac]['Load Rx'] = pattern[key][9]
            radio_status['Links'][mac]['Load Tx'] = pattern[key][10]
            radio_status['Links'][mac]['PPS Rx'] = pattern[key][11]
            radio_status['Links'][mac]['PPS Tx'] = pattern[key][12]
            radio_status['Links'][mac]['Cost'] = pattern[key][13]
            radio_status['Links'][mac]['Power Rx'] = pattern[key][14]
            radio_status['Links'][mac]['Power Tx'] = pattern[key][15]
            radio_status['Links'][mac]['SNR Rx'] = pattern[key][16]
            radio_status['Links'][mac]['SNR Tx'] = pattern[key][17]
            radio_status['Links'][mac]['Distance'] = pattern[key][18]
            radio_status['Links'][mac]['Firmware'] = pattern[key][19]
            radio_status['Links'][mac]['Uptime'] = pattern[key][21]

        pattern = re.findall(r'\d+\s+\((\d+)\/([\-\d]+)\)'
                             r'\s+\d+\s+\([\d\S]+\s+MHz\)'
                             r'\s+\w\s+<([\w\d]+)\s+([\w\d\.\_]+)', dc_string, re.DOTALL)
        if radio_status['Links']:
            for mac in pattern:
                radio_status['Links'][mac[2]]['RSSI Rx'] = mac[1]

    if radio_status:
        pattern = re.search(r'Pulses: (\d+), level\s+(\d+) \(([\-\d]+)\), pps ([\.\d]+)', dc_string)
        if pattern is not None:
            radio_status['Pulses'] = pattern.group(1)
            radio_status['Interference Level'] = pattern.group(2)
            radio_status['Interference RSSI'] = pattern.group(3)
            radio_status['Interference PPS'] = pattern.group(4)

        pattern = re.search(r'RX Medium Load\s+([\d\.]+%)', dc_string)
        if pattern is not None:
            radio_status['RX Medium Load'] = pattern.group(1)

        pattern = re.search(r'TX Medium Load\s+([\d\.]+%)', dc_string)
        if pattern is not None:
            radio_status['TX Medium Load'] = pattern.group(1)

        pattern = re.search(r'Total Medium Busy\s+([\d\.]+%)', dc_string)
        if pattern is not None:
            radio_status['Total Medium Busy'] = pattern.group(1)

        pattern = re.search(r'Excessive Retries\s+(\d+)', dc_string)
        radio_status['Excessive Retries'] = pattern.group(1)

        pattern = re.search(r'Aggr Full Retries\s+(\d+)', dc_string)
        radio_status['Aggr Full Retries'] = pattern.group(1)

    # Ethernet Status
    ethernet_statuses = {'Status': None, 'Speed': None, 'Duplex': None, 'Negotiation': None, 'Rx CRC': None,
                         'Tx CRC': None}
    ethernet_status = {'eth0': ethernet_statuses, 'eth1': deepcopy(ethernet_statuses)}

    pattern = re.findall(r'Physical link is (\w+)(, (\d+ Mbps) '
                         r'([\w-]+), (\w+))?', dc_string)
    ethernet_status['eth0']['Status'] = pattern[0][0]
    ethernet_status['eth0']['Speed'] = pattern[0][2]
    ethernet_status['eth0']['Duplex'] = pattern[0][3]
    ethernet_status['eth0']['Negotiation'] = pattern[0][4]

    if subfamily == 'R5000 Lite' and len(pattern) > 1:
        ethernet_status['eth1']['Status'] = pattern[1][0]
        ethernet_status['eth1']['Speed'] = pattern[1][2]
        ethernet_status['eth1']['Duplex'] = pattern[1][3]
        ethernet_status['eth1']['Negotiation'] = pattern[1][4]

    pattern = re.findall(r'CRC errors\s+(\d+)', dc_string)
    if subfamily == 'R5000 Pro':
        ethernet_status['eth0']['Rx CRC'] = pattern[0]
        ethernet_status['eth0']['Tx CRC'] = pattern[1]
        ethernet_status['eth1']['Rx CRC'] = 0
        ethernet_status['eth1']['Tx CRC'] = 0
    elif subfamily == 'R5000 Lite (low cost CPE)' or subfamily == 'R5000 Lite' and len(pattern) is 1:
        ethernet_status['eth0']['Rx CRC'] = pattern[0]
        ethernet_status['eth0']['Tx CRC'] = 0
        ethernet_status['eth1']['Rx CRC'] = 0
        ethernet_status['eth1']['Tx CRC'] = 0
    else:
        ethernet_status['eth0']['Rx CRC'] = pattern[0]
        ethernet_status['eth0']['Tx CRC'] = 0
        ethernet_status['eth1']['Rx CRC'] = pattern[1]
        ethernet_status['eth1']['Tx CRC'] = 0

    # Switch Status
    sw_text_start = dc_list.index('Switch statistics:\n')
    for line in dc_list:
        pattern = re.search(r'DB Records', line)
        if pattern is not None:
            sw_text_end = dc_list.index(line)
    sw_text = ''.join(dc_list[sw_text_start:sw_text_end + 1])
    pattern = re.findall(r'(\d+)\s+'
                         r'>?(\d+)\s+'
                         r'>?(\d+)\s+'
                         r'>?(\d+)\s+'
                         r'>?(\d+)\s+'
                         r'>?(\d+)\s+'
                         r'>?(\d+)\s+'
                         r'>?(\d+)\s+'
                         r'>?(\d+)\s+'
                         r'>?(\d+)', sw_text)
    switch_status = {pattern[id][0]: sw_group[1:] for id, sw_group in enumerate(pattern)}
    for id, status in switch_status.items():
        switch_status[id] = {}
        switch_status[id]['Unicast'] = int(status[0])
        switch_status[id]['Bcast'] = int(status[1])
        switch_status[id]['Flood'] = int(status[2])
        switch_status[id]['STPL'] = int(status[3])
        switch_status[id]['UNRD'] = int(status[4])
        switch_status[id]['FRWL'] = int(status[5])
        switch_status[id]['LOOP'] = int(status[6])
        switch_status[id]['DISC'] = int(status[7])
        switch_status[id]['BACK'] = int(status[8])

    # QoS status
    counter = 0
    for line in dc_list:
        counter += 1
        pattern = re.search(r'Software Priority Queues rf5.0', line)
        if pattern is not None:
            qos_rf_start = counter
        pattern = re.search(r'Phy errors: total \d+', line)
        if pattern is not None:
            qos_rf_end = counter
    qos_status = ''.join(dc_list[qos_rf_start - 1:qos_rf_end - 2])
    pattern = re.findall(r'(q\d+)\s+(\((P\d+)\))?\s+(\d+)\s+\/\s+(\d+)', qos_status)
    qos_status = {channel[0]: channel[2:] for channel in pattern}
    for channel, status in qos_status.items():
        qos_status[channel] = {}
        qos_status[channel]['Prio'] = status[0]
        qos_status[channel]['Count'] = status[1]
        qos_status[channel]['Drops'] = status[2]

    result = R5000Card(model, subfamily, serial_number, firmware, uptime, reboot_reason, dc_list, dc_string, settings,
                       radio_status, ethernet_status, switch_status, qos_status)

    return result


def parse_xg(dc_string, dc_list):
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

    serial_number = re.search(r'SN:(\d+)', dc_string).group(1)
    firmware = re.search(r'#\sXG\sWANFleX\s(\bH\d{2}S\d{2}[v\d.-]+\b)', dc_string).group(1)
    uptime = re.findall(r'Uptime: ([\d\w :]*)', dc_string)[0]
    reboot_reason = re.search(r'Last reboot reason: ([\w ]*)', dc_string).group(1)

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

    # Panic
    panic = []
    for line in dc_list:
        pattern = re.match(r'Panic info : \[\w+\]: ([\w\s\S\d]+)', line)
        if pattern is not None:
            panic.append(pattern.group(1).rstrip())
    panic = set(panic)

    result = XGCard(model, subfamily, serial_number, firmware, uptime, reboot_reason, dc_list, dc_string, settings,
                    radio_status, ethernet_status, panic)

    return result


def parse_quanta(dc_string, dc_list):
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

    # Genral info
    pattern = re.search(r'([QV](5|70)-[\dE]+)', dc_string)
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
    firmware = re.search(r'#\sOCTOPUS-PTP\sWANFleX\s'
                         r'(H\d{2}S\d{2}-OCTOPUS_PTPv[\d.]+)', dc_string).group(1)
    serial_number = re.search(r'SN:(\d+)', dc_string).group(1)
    uptime = re.search(r'Uptime: ([\d\w :]*)', dc_string).group(1)
    reboot_reason = re.search(r'Last reboot reason: ([\w ]*)', dc_string).group(1)

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
    pattern = re.findall(r'ifc\sge0\s+media\s([\-\w\d]+)\smtu\s\d+\s(up|down)', dc_string)
    settings['Interface Status']['Ge0'] = pattern[0][1]

    # Radio Status
    stream = {'Tx Power': None, 'MCS': None, 'RSSI': None, 'EVM': None, 'Crosstalk': None, 'ARQ ratio': None}
    role = {'Frequency': None, 'Stream 0': stream, 'Stream 1': deepcopy(stream)}
    radio_status = {'Link status': None, 'Measured Distance': None, 'Downlink': role, 'Uplink': deepcopy(role)}

    radio_status['Link status'] = re.search(r'State\s+(\w+)', dc_string).group(1)

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
                pattern = re.findall(r'(\d+(\.\d+)?\s%)', line)
                radio_status['Downlink']['Stream 0']['ARQ ratio'] = pattern[0][0]
                radio_status['Downlink']['Stream 1']['ARQ ratio'] = pattern[1][0]
                radio_status['Uplink']['Stream 0']['ARQ ratio'] = pattern[2][0]
                radio_status['Uplink']['Stream 1']['ARQ ratio'] = pattern[3][0]

    # Ethernet Status
    ethernet_status = {'ge0': {'Status': None, 'Speed': None, 'Duplex': None, 'Negotiation': None, 'CRC': None}}

    pattern = re.findall(r'Physical link is (\w+)(, (\d+ Mbps) ([\w-]+), (\w+))?', dc_string)
    ethernet_status['ge0']['Status'] = pattern[0][0]
    ethernet_status['ge0']['Speed'] = pattern[0][2]
    ethernet_status['ge0']['Duplex'] = pattern[0][3]
    ethernet_status['ge0']['Negotiation'] = pattern[0][4]

    pattern = re.findall(r'CRC errors\s+(\d+)', dc_string)
    ethernet_status['ge0']['CRC'] = pattern[0]

    result = QCard(model, subfamily, serial_number, firmware, uptime, reboot_reason, dc_list, dc_string, settings,
                   radio_status, ethernet_status)

    return result