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
    logger.debug(f'Firmware: {firmware}')

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
    logger.debug(f'Model: {model}; Subfamily: {subfamily}')

    serial_number = re.search(r'SN:(\d+)', dc_string).group(1)
    logger.debug(f'SN: {serial_number}')

    uptime = re.search(r'Uptime: ([\d\w :]*)', dc_string).group(1)
    logger.debug(f'Uptime: {uptime}')

    reboot_reason = re.search(r'Last reboot reason: ([\w ]*)', dc_string).group(1)
    logger.debug(f'Last reboot reason: {reboot_reason}')

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

    pattern = re.search(r'dfs rf5\.0 (dfsradar|dfsonly|dfsoff)', dc_string)
    if pattern is not None:
        radio_settings['DFS'] = pattern.group(1)

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
            profile['Auto bitrate'] = f'Enabled. Modification is {str(pattern.group(3))}'
        else:
            profile['Auto bitrate'] = f'Disabled. Fixed bitrate is {profile["Max bitrate"]}'

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
                profile[prodile_id]['Auto bitrate'] = f'Enabled. Modification is {pattern[key][13]}'
            else:
                profile[prodile_id]['Auto bitrate'] = f'Disabled. Fixed bitrate is ' \
                                                      f'{profile[prodile_id]["Max bitrate"]}'

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
                profile[prodile_id]['Frequency'] = f'{pattern_2[0]} (auto)'
            elif pattern_2 and prodile_id == pattern_2[1]:
                profile[prodile_id]['State'] = 'Active'
            else:
                profile[prodile_id]['State'] = 'Idle'

    logger.debug(f'Radio Settings: {settings["Radio"]}')

    # Switch Settings
    # This section will be added in the future
    switch_groups = set(re.findall(r'switch group (\d+)?', dc_string))
    settings['Switch'] = {sw_group_id: deepcopy(switch_group_settings) for sw_group_id in switch_groups}

    logger.debug(f'Switch Settings: {settings["Switch"]}')

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

    logger.debug(f'Interface Settings: {settings["Interface Status"]}')

    # QoS
    # This section will be added in the future

    logger.debug(f'QoS Settings: {settings["QoS"]}')

    # Radio Status
    link_status = {'Name': None, 'Level Rx': None, 'Level Tx': None, 'Bitrate Rx': None, 'Bitrate Tx': None,
                   'Load Rx': None, 'Load Tx': None, 'PPS Rx': None, 'PPS Tx': None, 'Cost': None, 'Retry Rx': None,
                   'Retry Tx': None, 'Power Rx': None, 'Power Tx': None, 'RSSI Rx': None, 'RSSI Tx': None,
                   'SNR Rx': None, 'SNR Tx': None, 'Distance': None, 'Firmware': None, 'Uptime': None}
    radio_status = {'Links': None, 'Pulses': None, 'Interference Level': None, 'Interference RSSI': None,
                    'Interference PPS': None, 'RX Medium Load': None, 'TX Medium Load': None,
                    'Total Medium Busy': None,
                    'Excessive Retries': None, 'Aggr Full Retries': None}

    pattern_mac = re.compile(r'(00[\dA-F]{10})')
    pattern_name = re.compile(r'[\.\d]+\s+([\w\d\S]+)\s+00[\w\d]+')
    pattern_level = re.compile(r'00[\w\d]+\s+(\d+)/(\d+)')
    pattern_bitrate = re.compile(r'00[\w\d]+\s+\d+/\d+\s+(\d+)/(\d+)')
    pattern_retry = re.compile(r'00[\w\d]+\s+\d+/\d+\s+\d+/\d+\s+(\d+)/(\d+)')
    pattern_load = re.compile(r'load (\d+)/(\d+)')
    pattern_pps = re.compile(r'pps (\d+)/(\d+)')
    pattern_cost = re.compile(r'cost ([\-\d+\.]+)')
    pattern_pwr = re.compile(r'pwr ([\*\-\d+\.]+)/([\*\-\d+\.]+)')
    pattern_rssi = re.compile(r'rssi ([\*\-\d+\.]+)/([\*\-\d+\.]+)')
    pattern_rssi_muffer = re.compile(r'\d+\/([\-\d]+)')
    pattern_snr = re.compile(r'snr (\d+)/(\d+)')
    pattern_distance = re.compile(r'dist ([\.\d+]+)')
    pattern_firmware = re.compile(r'(H\d{2}v[v\d.]+)')
    pattern_uptime = re.compile(r'up ([\d\w :]*)')

    # Find mint map det text
    for index, line in enumerate(dc_list):
        pattern = re.search(r'Id\s+Name\s+Node\s+Level', line)
        if pattern is not None:
            links_text_start = index + 2
        pattern = re.search(r'Total nodes in area', line)
        if pattern is not None:
            links_text_end = index - 3
    links_text = dc_list[links_text_start:links_text_end]

    # Find each string contains MAC
    slices = []
    for index, line in enumerate(links_text):
        if pattern_mac.search(line):
            slices.append(index)
    slices.append(len(links_text))

    """
    The number of strings after the first string may be different (from 1 to 4 excluding the firts one)
    Need to slice the mint map det text to links
    """
    links = []
    for index, slice in enumerate(slices):
        try:
            link_start = slices[index]
            link_end = slices[index + 1]
        except IndexError:
            link_end = slices[index]
        finally:
            links.append(links_text[link_start:link_end])
    links.pop()

    # Create dictionary from the links arrange. MAC-addresses are keys
    radio_status['Links'] = {mac: deepcopy(link_status) for mac in
                             [pattern_mac.search(link[0]).group(1) for link in links]}

    # Fill the link_status variable for each link
    for mac in radio_status['Links']:
        for index, link in enumerate(links):
            if mac == pattern_mac.search(link[0]).group(1):
                link = ''.join(link)

                radio_status['Links'][mac]['Name'] = pattern_name.search(link).group(1)

                if pattern_level.search(link) is not None:
                    radio_status['Links'][mac]['Level Rx'] = pattern_level.search(link).group(1)
                    radio_status['Links'][mac]['Level Tx'] = pattern_level.search(link).group(2)
                else:
                    logger.debug(f'Link {mac}: Level was not parsed')

                if pattern_bitrate.search(link) is not None:
                    radio_status['Links'][mac]['Bitrate Rx'] = pattern_bitrate.search(link).group(1)
                    radio_status['Links'][mac]['Bitrate Tx'] = pattern_bitrate.search(link).group(2)
                else:
                    logger.debug(f'Link {mac}: Bitrate was not parsed')

                if pattern_retry.search(link) is not None:
                    radio_status['Links'][mac]['Retry Rx'] = pattern_retry.search(link).group(1)
                    radio_status['Links'][mac]['Retry Tx'] = pattern_retry.search(link).group(2)
                else:
                    logger.debug(f'Link {mac}: Retry was not parsed')

                if pattern_load.search(link) is not None:
                    radio_status['Links'][mac]['Load Rx'] = pattern_load.search(link).group(1)
                    radio_status['Links'][mac]['Load Tx'] = pattern_load.search(link).group(2)
                else:
                    logger.debug(f'Link {mac}: Load was not parsed')

                if pattern_pps.search(link) is not None:
                    radio_status['Links'][mac]['PPS Rx'] = pattern_pps.search(link).group(1)
                    radio_status['Links'][mac]['PPS Tx'] = pattern_pps.search(link).group(2)
                else:
                    logger.debug(f'Link {mac}: PPS was not parsed')

                if pattern_cost.search(link) is not None:
                    radio_status['Links'][mac]['Cost'] = pattern_cost.search(link).group(1)
                else:
                    logger.debug(f'Link {mac}: Cost was not parsed')

                if pattern_pwr.search(link) is not None:
                    radio_status['Links'][mac]['Power Rx'] = pattern_pwr.search(link).group(1)
                    radio_status['Links'][mac]['Power Tx'] = pattern_pwr.search(link).group(2)
                else:
                    logger.debug(f'Link {mac}: Power was not parsed')

                if pattern_snr.search(link) is not None:
                    radio_status['Links'][mac]['SNR Rx'] = pattern_snr.search(link).group(1)
                    radio_status['Links'][mac]['SNR Tx'] = pattern_snr.search(link).group(2)
                else:
                    logger.debug(f'Link {mac}: SNR was not parsed')

                if pattern_distance.search(link) is not None:
                    radio_status['Links'][mac]['Distance'] = pattern_distance.search(link).group(1)
                else:
                    logger.debug(f'Link {mac}: Distance was not parsed')

                if pattern_firmware.search(link) is not None:
                    radio_status['Links'][mac]['Firmware'] = pattern_firmware.search(link).group(1)
                else:
                    logger.debug(f'Link {mac}: Firmware was not parsed')

                if pattern_uptime.search(link) is not None:
                    radio_status['Links'][mac]['Uptime'] = pattern_uptime.search(link).group(1)
                else:
                    logger.debug(f'Link {mac}: Uptime was not parsed')

                # MINT firmare does not contain RSSI in the mint map det text
                if 'TDMA' in firmware and pattern_rssi.search(link) is not None:
                    radio_status['Links'][mac]['RSSI Rx'] = pattern_rssi.search(link).group(1)
                    radio_status['Links'][mac]['RSSI Tx'] = pattern_rssi.search(link).group(2)
                elif 'TDMA' in firmware and pattern_rssi.search(link) is None:
                    logger.debug(f'Link {mac}: RSSI was not parsed')

    for index, line in enumerate(dc_list):
        pattern = re.search(r'rf5.0 Source Analysis', line)
        if pattern is not None:
            muffer_text_start = index + 2
        pattern = re.search(r'rf5.0: NOL is empty', line)
        if pattern is not None:
            muffer_text_end = index
    muffer_text = dc_list[muffer_text_start:muffer_text_end]

    # Get RSSI from muffer (MINT only)
    for mac in radio_status['Links']:
        for line in muffer_text:
            if pattern_mac.search(line) is not None \
                    and mac == pattern_mac.search(line).group(1) \
                    and 'MINT' in firmware:
                radio_status['Links'][mac]['RSSI Rx'] = pattern_rssi_muffer.search(line).group(1)

    # Fill the radio_status variable
    pattern_pulses = re.compile(r'Pulses: (\d+)')
    pattern_pulses_level = re.compile(r'level\s+(\d+)')
    pattern_pulses_rssi = re.compile(r'level\s+\d+\s+\((\d+)\)')
    pattern_pulses_pps = re.compile(r'pps ([\.\d]+)')
    for line in muffer_text:
        if pattern_pulses.search(line) is not None:
            radio_status['Pulses'] = pattern_pulses.search(line).group(1)
        if pattern_pulses_level.search(line) is not None:
            radio_status['Interference Level'] = pattern_pulses_level.search(line).group(1)
        if pattern_pulses_rssi.search(line) is not None:
            radio_status['Interference RSSI'] = pattern_pulses_rssi.search(line).group(1)
        if pattern_pulses_pps.search(line) is not None:
            radio_status['Interference PPS'] = pattern_pulses_pps.search(line).group(1)

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


    logger.debug(f'Radio Status: {radio_status}')

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

    logger.debug(f'Ethernet Status: {ethernet_status}')

    # Switch Status
    for index, line in enumerate(dc_list):
        pattern = re.search(r'Switch statistics:\r\n', line)
        if pattern is not None:
            sw_text_start = index
        pattern = re.search(r'DB Records', line)
        if pattern is not None:
            sw_text_end = index + 1
    sw_text = ''.join(dc_list[sw_text_start:sw_text_end])
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

    logger.debug(f'Switch Status: {switch_status}')

    # QoS status
    for index, line in enumerate(dc_list):
        pattern = re.search(r'Software Priority Queues rf5.0', line)
        if pattern is not None:
            qos_text_start = index
        pattern = re.search(r'Phy errors: total \d+', line)
        if pattern is not None:
            qos_text_end = index - 1
    qos_text = ''.join(dc_list[qos_text_start:qos_text_end])
    pattern = re.findall(r'(q\d+)\s+(\((P\d+)\))?(\s+\(cos\d\))?\s+(\d+)\s+\/\s+(\d+)', qos_text)
    qos_status = {channel[0]: channel[2:] for channel in pattern}
    for channel, status in qos_status.items():
        qos_status[channel] = {}
        qos_status[channel]['Prio'] = status[0]
        qos_status[channel]['Count'] = status[2]
        qos_status[channel]['Drops'] = status[3]

    logger.debug(f'QoS Status: {qos_status}')

    result = (model, subfamily, serial_number, firmware,
              uptime, reboot_reason, dc_list, dc_string,
              settings, radio_status, ethernet_status,
              switch_status, qos_status)

    return result


logger = logging.getLogger('logger.parser_r5000')
