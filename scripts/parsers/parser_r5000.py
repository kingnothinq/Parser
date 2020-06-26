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
    """Parse an R5000 diagnostic card and fill the class instance in

    Input - text (dc_string - string, dc_list - list)
    Output:

    This function returns result (a tuple to create a class instance) included the next variables:
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
        Current Frequency

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

    def cut_text(text, pattern_start, pattern_end, offset_start, offset_end):
        """Cut text from patter_start to pattern_end
        Input - text, patterns - re.compile, offsets - int
        Output - a list with the cut text
        """
        try:
            for index, line in enumerate(text):
                if pattern_start.search(line):
                    text_start = index + offset_start
                if pattern_end.search(line):
                    text_end = index + offset_end
            new_text = text[text_start:text_end]
        except:
            new_text = text
            logger.warning(f'Text has not been cut. Patterns: {pattern_start} - {pattern_end}')
        return new_text

    def slice_text(text, slices):
        """Slice text by line index
        Input -  text and a list with position of rows (indexes)
        Output - a list contains the sliced text (from position to position in accordance with the input list)
        """
        new_text = []
        for index, slice in enumerate(slices):
            try:
                text_start = slices[index]
                text_end = slices[index + 1]
            except IndexError:
                # Index + 1 cannot be performed for the last element in the arrange
                text_end = slices[index]
            finally:
                new_text.append(text[text_start:text_end])
        # Drop the element created in the exception
        new_text.pop()
        return new_text


    # General info
    try:
        general_text = ''.join(dc_list[:15])

        pattern_g_fw = re.compile(r'H\d{2}S\d{2}-(MINT|TDMA)[v\d.]+')
        pattern_g_model = re.compile(r'(R5000-[QMOSL][mxnbtcs]{2,5}/[\dX\*]'
                                     r'{1,3}.300.2x\d{2,3})(.2x\d{2})?')
        pattern_g_sn = re.compile(r'SN:(\d+)')
        pattern_g_uptime = re.compile(r'Uptime: ([\d\w :]*)')
        pattern_g_reboot_reason = re.compile(r'Last reboot reason: ([\w ]*)')

        if pattern_g_fw.search(general_text):
            firmware = pattern_g_fw.search(general_text).group()

        pattern = pattern_g_model.search(general_text)
        if pattern:
            model = pattern.group()
            if ('L' in model or 'S' in model) and '2x19' in model:
                subfamily = 'R5000 Lite (low cost CPE)'
            elif 'L' in model or 'S' in model:
                subfamily = 'R5000 Lite'
            else:
                subfamily = 'R5000 Pro'
        elif pattern and 'H11' in firmware:
            model = 'R5000 Unknown model'
            subfamily = 'R5000 Lite'
        else:
            model = 'R5000 Unknown model'
            subfamily = 'R5000 Pro'

        if pattern_g_sn.search(general_text):
            serial_number = pattern_g_sn.search(general_text).group(1)

        if pattern_g_uptime.search(general_text):
            uptime = pattern_g_uptime.search(general_text).group(1)

        if pattern_g_reboot_reason.search(general_text):
            reboot_reason = pattern_g_reboot_reason.search(general_text).group(1)

    except:
        logger.warning('General info was not parsed')

    logger.debug(f'General info: Firmware - {firmware}, Model - {model}, Subfamily - {subfamily}, '
                 f'SN - {serial_number}, Uptime - {uptime}, Last reboot reason - {reboot_reason}')

    # Settings
    radio_profile = {'Frequency': None, 'Bandwidth': None, 'Max bitrate': None, 'Auto bitrate': 'Disabled',
                     'MIMO': None, 'SID': None, 'Status': 'Enabled', 'Greenfield': 'Disabled', 'State': 'Idle'}
    radio_settings = {'Type': 'slave', 'ATPC': 'Disabled', 'Tx Power': None, 'Extnoise': None, 'DFS': None,
                      'Polling': 'Disabled', 'Frame size': None, 'DL/UL ratio': None, 'Distance': None,
                      'Target RSSI': None, 'TSync': 'Disabled', 'Scrambling': 'Disabled', 'Profile': radio_profile}
    switch_group_settings = {'Order': None, 'Flood': 'Disabled', 'STP': 'Disabled', 'Management': 'Disabled',
                             'Mode': 'Normal', 'Interfaces': None, 'Rules': None}
    switch_settings = {'Status': 'Disabled', 'Switch Group': switch_group_settings}
    interfaces_settings = {'eth0': 'down', 'eth1': 'down', 'rf5.0': 'down'}
    qos_settings = {'Options': None, 'Rules': None, 'License': None}
    settings = {'Radio': radio_settings, 'Switch': switch_settings, 'Interface Status': interfaces_settings,
                'QoS': qos_settings}

    try:
        pattern_start = re.compile(r'# R5000 WANFleX H')
        pattern_end = re.compile(r'#LLDP parameters')
        settings_text = cut_text(dc_list, pattern_start, pattern_end, 0, 2)

        # Radio Settings
        pattern_set_type = re.compile(r'mint rf5\.0 -type (\w+)')
        pattern_set_pwr = re.compile(r'rf rf5.0 txpwr ([\-\d]+)')
        pattern_set_atpc = re.compile(r'rf rf5.0 txpwr [\-\d]+ (pwrctl)')
        pattern_set_extnoise = re.compile(r'extnoise ([\-+\d+])')
        pattern_set_dfs = re.compile(r'dfs rf5\.0 (dfsradar|dfsonly|dfsoff)')
        pattern_set_scrambling = re.compile(r'mint rf5.0 -scrambling')
        pattern_set_tdma_frame = re.compile(r'tdma mode=Master win=(\d+)')
        pattern_set_tdma_dist = re.compile(r'mode=Master win=\d+ dist=(\d+)')
        pattern_set_tdma_dlp = re.compile(r'mode=Master win=\d+ dist=\d+ dlp=(\d+)')
        pattern_set_tdma_target = re.compile(r'mint rf5\.0 tdma rssi=([\-\d]+)')
        pattern_set_tdma_tsync = re.compile(r'tsync enable')
        pattern_set_polling = re.compile(r'mint rf5\.0 poll start')
        pattern_set_m_freq = re.compile(r'rf rf5\.0 freq ([\.\d]+)')
        pattern_set_m_bitr = re.compile(r'rf rf5\.0 freq [\.\d]+ bitr (\d+)')
        pattern_set_m_sid = re.compile(r'rf rf5\.0 freq [\.\d]+ bitr \d+ sid ([\d\w]+)')
        pattern_set_m_band = re.compile(r'rf rf5\.0 band (\d+)')
        pattern_set_m_afbitr = re.compile(r'mint rf5\.0 -(auto|fixed)bitrate')
        pattern_set_m_afbitr_offset = re.compile(r'mint rf5\.0 -(auto|fixed)bitrate ([\-+\d]+)')
        pattern_set_m_mimo = re.compile(r'rf rf5\.0 (mimo|miso|siso)')
        pattern_set_m_greenfield = re.compile(r'rf rf5\.0 (mimo|miso|siso) (greenfield)')
        pattern_set_s_status = re.compile(r'mint rf5\.0 prof \d+ disable')
        pattern_set_s_state = re.compile(r'[\w\d]+ band \d+ freq [\-\d]+ snr \d+ links \d+, prof (\d+)')
        pattern_set_s_band = re.compile(r'-band (\d+)')
        pattern_set_s_freq = re.compile(r'-freq ([\.\d\w]+)')
        pattern_set_s_bitr = re.compile(r'-bitr (\d+)')
        pattern_set_s_sid = re.compile(r'-sid ([\d\w]+)')
        pattern_set_s_afbitr = re.compile(r'-(auto|fixed)bitr')
        pattern_set_s_afbitr_offset = re.compile(r'-(auto|fixed)bitr (([\-+])?([\d]+))')
        pattern_set_s_mimo = re.compile(r'-(mimo|miso|siso)')
        pattern_set_s_greenfield = re.compile(r'(greenfield)')

        for line in settings_text:
            # Common settings
            if pattern_set_type.search(line):
                radio_settings['Type'] = pattern_set_type.search(line).group(1)

            if pattern_set_pwr.search(line):
                radio_settings['Tx Power'] = pattern_set_pwr.search(line).group(1)

            if pattern_set_atpc.search(line):
                radio_settings['ATPC'] = 'Enabled'

            if pattern_set_extnoise.search(line):
                radio_settings['Extnoise'] = pattern_set_extnoise.search(line).group(1)

            if pattern_set_dfs.search(line):
                radio_settings['DFS'] = pattern_set_dfs.search(line).group(1)

            if pattern_set_scrambling.search(line):
                radio_settings['Scrambling'] = 'Enabled'

            # TDMA Settings
            if pattern_set_tdma_frame.search(line):
                radio_settings['Frame size'] = pattern_set_tdma_frame.search(line).group(1)

            if pattern_set_tdma_dist.search(line):
                radio_settings['Distance'] = pattern_set_tdma_dist.search(line).group(1)

            if pattern_set_tdma_dlp.search(line):
                radio_settings['DL/UL ratio'] = pattern_set_tdma_dlp.search(line).group(1)

            if pattern_set_tdma_target.search(line):
                radio_settings['Target RSSI'] = pattern_set_tdma_target.search(line).group(1)

            if pattern_set_tdma_tsync.search(line):
                radio_settings['TSync'] = 'Enabled'

            # MINT Settings
            if pattern_set_polling.search(line):
                radio_settings['Polling'] = 'Enabled'

        if radio_settings['Type'] == 'slave':
            radio_settings['Polling'] = None
            radio_settings['TSync'] = None
        elif 'TDMA' in firmware:
            radio_settings['Polling'] = None
        elif 'MINT' in firmware:
            radio_settings['TSync'] = None

    except:
        logger.warning('Common settings were not parsed')


    # Master profile
    try:
        if radio_settings['Type'] == 'master':
            radio_settings['Profile'] = {'M': deepcopy(radio_profile)}
            profile = radio_settings['Profile']['M']

            # Master has always active and enabled profile
            profile['State'] = 'Active'

            for line in settings_text:
                if pattern_set_m_freq.search(line):
                    profile['Frequency'] = pattern_set_m_freq.search(line).group(1)

                if pattern_set_m_bitr.search(line):
                    profile['Max bitrate'] = pattern_set_m_bitr.search(line).group(1)

                if pattern_set_m_sid.search(line):
                    profile['SID'] = pattern_set_m_sid.search(line).group(1)

                if pattern_set_m_band.search(line):
                    profile['Bandwidth'] = pattern_set_m_band.search(line).group(1)

                if pattern_set_m_afbitr.search(line):
                    if pattern_set_m_afbitr.search(line).group(1) == 'auto' \
                            and pattern_set_m_afbitr_offset.search(line):
                        profile['Auto bitrate'] = f'Enabled. Modification is ' \
                                                  f'{pattern_set_m_afbitr_offset.search(line).group(2)}'
                    elif pattern_set_m_afbitr.search(line).group(1) == 'auto':
                        profile['Auto bitrate'] = 'Enabled'
                    elif pattern_set_m_afbitr.search(line).group(1) == 'fixed':
                        profile['Auto bitrate'] = f'Disabled. Fixed bitrate is {profile["Max bitrate"]}'

                if pattern_set_m_mimo.search(line):
                    profile['MIMO'] = str.upper(pattern_set_m_mimo.search(line).group(1))

                if pattern_set_m_greenfield.search(line):
                    profile['Greenfield'] = pattern_set_m_greenfield.search(line).group(2)

        # Slave profiles
        else:
            # Find each string contains profile
            pattern_profile = re.compile(r'mint rf5\.0 prof (\d+)')
            slices = []
            profiles_text = []
            for index, line in enumerate(settings_text):
                if pattern_profile.search(line):
                    slices.append(index)
                    profiles_text.append(pattern_profile.search(line).group(1))
            slices.append(slices[-1] + 5)

            # Slice the profile text by profiles
            profiles = dict(zip(profiles_text, slice_text(settings_text, slices)))

            # Parse each profile
            radio_settings['Profile'] = {profile: deepcopy(radio_profile) for profile in profiles.keys()}

            if pattern_set_s_state.findall(dc_string):
                profile_active = str(pattern_set_s_state.findall(dc_string)[-1])
            else:
                profile_active = list(radio_settings['Profile'].keys())[0]

            for key in radio_settings['Profile']:
                profile = radio_settings['Profile'][key]
                if key == profile_active:
                    profile['State'] = 'Active'
                for line in profiles[key]:
                    if pattern_set_s_status.search(line):
                        # Slave may have idle (not used at this moment) and disabled profiles
                        profile['Status'] = 'Disabled'
                        # Profile cannot be Active if it is disabled
                        profile['State'] = 'Idle'

                    if pattern_set_s_band.search(line):
                        profile['Bandwidth'] = pattern_set_s_band.search(line).group(1)

                    if pattern_set_s_freq.search(line):
                        profile['Frequency'] = pattern_set_s_freq.search(line).group(1)

                    if pattern_set_s_bitr.search(line):
                        profile['Max bitrate'] = pattern_set_s_bitr.search(line).group(1)

                    if pattern_set_s_sid.search(line):
                        profile['SID'] = pattern_set_s_sid.search(line).group(1)

                    if pattern_set_s_afbitr.search(line):
                        if pattern_set_s_afbitr.search(line).group(1) == 'auto' \
                                and pattern_set_s_afbitr_offset.search(line):
                            profile['Auto bitrate'] = f'Enabled. Modification is ' \
                                                      f'{pattern_set_s_afbitr_offset.search(line).group(2)}'
                        elif pattern_set_s_afbitr.search(line).group(1) == 'auto':
                            profile['Auto bitrate'] = 'Enabled'
                        elif pattern_set_s_afbitr.search(line).group(1) == 'fixed':
                            profile['Auto bitrate'] = f'Disabled. Fixed bitrate is {profile["Max bitrate"]}'

                    if pattern_set_s_mimo.search(line):
                        profile['MIMO'] = str.upper(pattern_set_s_mimo.search(line).group(1))

                    if pattern_set_s_greenfield.search(line):
                        profile['Greenfield'] = pattern_set_s_greenfield.search(line).group(1)

    except:
        logger.warning('Radio settings were not parsed')

    logger.debug(f'Radio Settings: {settings["Radio"]}')

    # Switch Settings
    try:
        pattern_start = re.compile(r'#MAC Switch config')
        pattern_end = re.compile(r'#SNMP configuration')
        pattern_set_sw = re.compile(r'switch start')
        if pattern_set_sw.search(dc_string):
            switch_settings['Status'] = 'Enabled'
            sw_settings_text_cut = cut_text(settings_text, pattern_start, pattern_end, 1, -1)
            pattern_set_sw_id = re.compile(r'switch group (\d+) add')
            slices = []
            groups = []
            for index, line in enumerate(sw_settings_text_cut):
                if pattern_set_sw_id.search(line):
                    slices.append(index)
                    groups.append(pattern_set_sw_id.search(line).group(1))
            slices.append(len(sw_settings_text_cut))

            # Slice the profile text by profiles
            sw_settings_text = dict(zip(groups, slice_text(sw_settings_text_cut, slices)))

            # Find switch groups
            switch_settings['Switch Group'] = {id: deepcopy(switch_group_settings) for id in sw_settings_text.keys()}

            pattern_set_sw_order = re.compile(r'switch group \d+ add (\d+)')
            pattern_set_sw_ifc = re.compile(r'switch group \d+ add \d+ (.+)')
            pattern_set_sw_flood = re.compile(r'flood-unicast on')
            pattern_set_sw_stp = re.compile(r'stp on')
            pattern_set_sw_mode_trunk = re.compile(r'trunk on')
            pattern_set_sw_mode_intrunk = re.compile(r'in-trunk (\d+)')
            pattern_set_sw_mode_upstream = re.compile(r'upstream')
            pattern_set_sw_mode_downstream = re.compile(r'downstream')
            pattern_set_sw_rule = re.compile(r'switch group \d+ rule \d+\s+(permit|deny) match (\w+)')
            pattern_set_sw_rule_list = re.compile(r'switch list (\w+) match add ([\w\d\-,\s\S]+)')
            pattern_set_sw_rule_default = re.compile(r'switch group \d+ (deny|permit)')
            pattern_set_sw_rule_vlan = re.compile(r'switch group \d+ (vlan [\d\-,]+)')
            pattern_set_sw_mngt = re.compile(r'svi (\d+) group (\d+)')

            rule_list = {}
            for line in sw_settings_text_cut:
                if pattern_set_sw_rule_list.search(line):
                    pattern = pattern_set_sw_rule_list.search(line)
                    rule_name = pattern.group(1)
                    rule_list[rule_name] = pattern.group(2).replace('\'', '').replace('\r', '').replace('\n', '')

            for key in switch_settings['Switch Group']:
                group = switch_settings['Switch Group'][key]
                check_rule = False
                for line in sw_settings_text[key]:
                    if pattern_set_sw_order.search(line):
                        group['Order'] = pattern_set_sw_order.search(line).group(1)

                    if pattern_set_sw_ifc.search(line):
                        group['Interfaces'] = pattern_set_sw_ifc.search(line).group(1).split(' ')
                        # Drop '\r'
                        group['Interfaces'].pop()
                        group['Interfaces'] = ', '.join(group['Interfaces'])

                    if pattern_set_sw_flood.search(line):
                        group['Flood'] = 'Enabled'

                    if pattern_set_sw_stp.search(line):
                        group['STP'] = 'Enabled'

                    if pattern_set_sw_mode_trunk.search(line):
                        group['Mode'] = 'Trunk'
                    elif pattern_set_sw_mode_intrunk.search(line):
                        group['Mode'] = f'In-Trunk {pattern_set_sw_mode_intrunk.search(line).group(1)}'
                    elif pattern_set_sw_mode_upstream.search(line):
                        group['Mode'] = 'Upstream'
                    elif pattern_set_sw_mode_downstream.search(line):
                        group['Mode'] = 'Downstream'

                    if pattern_set_sw_rule_vlan.search(line):
                        group['Rules'] = f'permit: {pattern_set_sw_rule_vlan.search(line).group(1)}; deny: any any'

                    if pattern_set_sw_rule.search(line):
                        rule_action = pattern_set_sw_rule.search(line).group(1)
                        rule = pattern_set_sw_rule.search(line).group(2)
                        check_rule = True

                    if pattern_set_sw_rule_default.search(line):
                        rule_default = pattern_set_sw_rule_default.search(line).group(1)

                if check_rule:
                    if rule in rule_list.keys():
                        group['Rules'] = f'{rule_action}: {rule} ({rule_list[rule]}); {rule_default}: any any'
                    else:
                        group['Rules'] = f'{rule_action}: {rule} ; {rule_default}: any any'

            for line in sw_settings_text_cut:
                if pattern_set_sw_mngt.search(line):
                    group = pattern_set_sw_mngt.search(line).group(2)
                    switch_settings['Switch Group'][group]['Management'] = 'Enabled'

    except:
        logger.warning('Switch settings were not parsed')

    logger.debug(f'Switch Settings: {settings["Switch"]}')

    # Interface Settings
    try:
        pattern_start = re.compile(r'#Interfaces parameters')
        pattern_end = re.compile(r'#QoS manager')
        ifc_settings_text = cut_text(settings_text, pattern_start, pattern_end, 1, -1)

        pattern_set_ifc = re.compile(r'ifc (eth\d+|rf5\.0)')
        for line in ifc_settings_text:
            if pattern_set_ifc.search(line):
                interface = pattern_set_ifc.search(line).group(1)
                if 'up' in line:
                    settings['Interface Status'][interface] = 'up'

    except:
        logger.warning('Interface Settings were not parsed')

    logger.debug(f'Interface Settings: {settings["Interface Status"]}')

    # QoS Settings
    try:
        pattern_start = re.compile(r'#QoS manager')
        pattern_end = re.compile(r'#Routing parameters')
        qm_settings_text_cut = cut_text(settings_text, pattern_start, pattern_end, 1, -1)

        pattern_set_qm_channel = re.compile(r'qm (ch\d+)')
        slices = []
        channels = []
        for index, line in enumerate(qm_settings_text_cut):
            if pattern_set_qm_channel.search(line):
                slices.append(index)
                channels.append(pattern_set_qm_channel.search(line).group(1))
        slices.append(len(qm_settings_text_cut))
        qm_settings_text = dict(zip(channels, slice_text(qm_settings_text_cut, slices)))

        pattern_set_qm_options = re.compile(r'qm option ([\w\s]+)')

        for line in qm_settings_text_cut:
            if pattern_set_qm_options.search(line):
                pattern = pattern_set_qm_options.search(line).group(1).replace('\r', '').replace('\n', '')
                qos_settings['Options'] = pattern.replace(' ', ', ')

        qos_settings['Rules'] = {channel: None for channel in qm_settings_text.keys()}
        for channel, text in qm_settings_text.items():
            qos_settings['Rules'][channel] = '; '.join(text).replace('\r', '').replace('\n', '')

        pattern_start = re.compile(r"License 'Factory License'")
        pattern_end = re.compile(r'</license>')
        license_text = cut_text(dc_list, pattern_start, pattern_end, 0, -1)

        pattern_set_qm_throughput = re.compile(r'MaximumTransmitRate="(\d+)"')

        qos_settings['License'] = {}
        for line in license_text:
            if pattern_set_qm_throughput.search(line):
                qos_settings['License']['Throughput'] = pattern_set_qm_throughput.search(line).group(1)

    except:
        logger.warning('QoS settings were not parsed')

    logger.debug(f'QoS Settings: {settings["QoS"]}')

    # Radio Status
    link_status = {'Name': None, 'Level Rx': None, 'Level Tx': None, 'Bitrate Rx': None, 'Bitrate Tx': None,
                   'Load Rx': None, 'Load Tx': None, 'PPS Rx': None, 'PPS Tx': None, 'Cost': None, 'Retry Rx': None,
                   'Retry Tx': None, 'Power Rx': None, 'Power Tx': None, 'RSSI Rx': None, 'RSSI Tx': None,
                   'SNR Rx': None, 'SNR Tx': None, 'Distance': None, 'Firmware': None, 'Uptime': None}
    radio_status = {'Links': None, 'Pulses': None, 'Interference Level': None, 'Interference RSSI': None,
                    'Interference PPS': None, 'RX Medium Load': None, 'TX Medium Load': None,
                    'Total Medium Busy': None, 'Excessive Retries': None, 'Aggr Full Retries': None,
                    'Current Frequency': None}

    try:
        pattern_rs_mac = re.compile(r'(00[\dA-F]{10})')
        pattern_rs_prf = re.compile(r'(join|prf)')
        pattern_rs_name = re.compile(r'[\.\d]+\s+([\w\d\S \-]+)\s+00[\dA-F]{10}')
        pattern_rs_spaces = re.compile(r"(\s{2,})")
        pattern_rs_level = re.compile(r'00[\w\d]+\s+(\d+)/(\d+)')
        pattern_rs_bitrate = re.compile(r'00[\w\d]+\s+\d+/\d+\s+(\d+)/(\d+)')
        pattern_rs_retry = re.compile(r'00[\w\d]+\s+\d+/\d+\s+\d+/\d+\s+(\d+)/(\d+)')
        pattern_rs_load = re.compile(r'load (\d+)/(\d+)')
        pattern_rs_pps = re.compile(r'pps (\d+)/(\d+)')
        pattern_rs_cost = re.compile(r'cost ([\-\d+\.]+)')
        pattern_rs_pwr = re.compile(r'pwr ([\*\-\d+\.]+)/([\*\-\d+\.]+)')
        pattern_rs_rssi = re.compile(r'rssi ([\*\-\d+\.]+)/([\*\-\d+\.]+)')
        pattern_rs_rssi_rf_scanner = re.compile(r'\d+\/([\-\d]+)')
        pattern_rs_snr = re.compile(r'snr (\d+)/(\d+)')
        pattern_rs_distance = re.compile(r'dist ([\.\d+]+)')
        pattern_rs_firmware = re.compile(r'(H\d{2}v[v\d.]+)')
        pattern_rs_uptime = re.compile(r'up ([\d\w :]*)')

        # Find mint map det text
        pattern_start = re.compile(r'Id\s+Name\s+Node\s+Level')
        pattern_end = re.compile(r'Total nodes in area')
        links_text = cut_text(dc_list, pattern_start, pattern_end, 1, -1)

        # Find each string contains MAC
        slices = []
        for index, line in enumerate(links_text):
            if pattern_rs_mac.search(line):
                slices.append(index)
        slices.append(len(links_text))

        links = slice_text(links_text, slices)

        # Need to remove prf and join links
        temp = []
        for link in links:
            if not pattern_rs_prf.search(link[0]):
                temp.append(link)
        links = temp

        # Create dictionary from the links arrange. MAC-addresses are keys
        radio_status['Links'] = {mac: deepcopy(link_status) for mac in
                                 [pattern_rs_mac.search(link[0]).group(1) for link in links]}

        # Fill the link_status variable for each link
        for mac in radio_status['Links']:
            for index, link in enumerate(links):
                if mac == pattern_rs_mac.search(link[0]).group(1):
                    link = ''.join(link)

                    name = pattern_rs_name.search(link).group(1)
                    spaces = pattern_rs_spaces.search(name).group(1)
                    radio_status['Links'][mac]['Name'] = name.replace(spaces, '')

                    if pattern_rs_level.search(link):
                        radio_status['Links'][mac]['Level Rx'] = pattern_rs_level.search(link).group(1)
                        radio_status['Links'][mac]['Level Tx'] = pattern_rs_level.search(link).group(2)
                    else:
                        logger.debug(f'Link {mac}: Level was not parsed')

                    if pattern_rs_bitrate.search(link):
                        radio_status['Links'][mac]['Bitrate Rx'] = pattern_rs_bitrate.search(link).group(1)
                        radio_status['Links'][mac]['Bitrate Tx'] = pattern_rs_bitrate.search(link).group(2)
                    else:
                        logger.debug(f'Link {mac}: Bitrate was not parsed')

                    if pattern_rs_retry.search(link):
                        radio_status['Links'][mac]['Retry Rx'] = pattern_rs_retry.search(link).group(1)
                        radio_status['Links'][mac]['Retry Tx'] = pattern_rs_retry.search(link).group(2)
                    else:
                        logger.debug(f'Link {mac}: Retry was not parsed')

                    if pattern_rs_load.search(link):
                        radio_status['Links'][mac]['Load Rx'] = pattern_rs_load.search(link).group(1)
                        radio_status['Links'][mac]['Load Tx'] = pattern_rs_load.search(link).group(2)
                    else:
                        logger.debug(f'Link {mac}: Load was not parsed')

                    if pattern_rs_pps.search(link):
                        radio_status['Links'][mac]['PPS Rx'] = pattern_rs_pps.search(link).group(1)
                        radio_status['Links'][mac]['PPS Tx'] = pattern_rs_pps.search(link).group(2)
                    else:
                        logger.debug(f'Link {mac}: PPS was not parsed')

                    if pattern_rs_cost.search(link):
                        radio_status['Links'][mac]['Cost'] = pattern_rs_cost.search(link).group(1)
                    else:
                        logger.debug(f'Link {mac}: Cost was not parsed')

                    if pattern_rs_pwr.search(link):
                        radio_status['Links'][mac]['Power Rx'] = pattern_rs_pwr.search(link).group(1)
                        radio_status['Links'][mac]['Power Tx'] = pattern_rs_pwr.search(link).group(2)
                    else:
                        logger.debug(f'Link {mac}: Power was not parsed')

                    if pattern_rs_snr.search(link):
                        radio_status['Links'][mac]['SNR Rx'] = pattern_rs_snr.search(link).group(1)
                        radio_status['Links'][mac]['SNR Tx'] = pattern_rs_snr.search(link).group(2)
                    else:
                        logger.debug(f'Link {mac}: SNR was not parsed')

                    if pattern_rs_distance.search(link):
                        radio_status['Links'][mac]['Distance'] = pattern_rs_distance.search(link).group(1)
                    else:
                        logger.debug(f'Link {mac}: Distance was not parsed')

                    if pattern_rs_firmware.search(link):
                        radio_status['Links'][mac]['Firmware'] = pattern_rs_firmware.search(link).group(1)
                    else:
                        logger.debug(f'Link {mac}: Firmware was not parsed')

                    if pattern_rs_uptime.search(link):
                        radio_status['Links'][mac]['Uptime'] = pattern_rs_uptime.search(link).group(1)
                    else:
                        logger.debug(f'Link {mac}: Uptime was not parsed')

                    # MINT firmare does not contain RSSI in the mint map det text
                    if 'TDMA' in firmware and pattern_rs_rssi.search(link):
                        radio_status['Links'][mac]['RSSI Rx'] = pattern_rs_rssi.search(link).group(1)
                        radio_status['Links'][mac]['RSSI Tx'] = pattern_rs_rssi.search(link).group(2)
                    elif 'TDMA' in firmware and pattern_rs_rssi.search(link):
                        logger.debug(f'Link {mac}: RSSI was not parsed')

        pattern_start = re.compile(r'rf5.0 Source Analysis')
        pattern_end = re.compile(r'rf5.0: NOL is empty')
        rf_scanner_text = cut_text(dc_list, pattern_start, pattern_end, 2, 0)

        # Get RSSI from muffer (MINT only)
        for mac in radio_status['Links']:
            for line in rf_scanner_text:
                if pattern_rs_mac.search(line) \
                        and mac == pattern_rs_mac.search(line).group(1) \
                        and 'MINT' in firmware:
                    radio_status['Links'][mac]['RSSI Rx'] = pattern_rs_rssi_rf_scanner.search(line).group(1)

        # Fill the radio_status variable
        pattern_rs_pulses = re.compile(r'Pulses: (\d+)')
        pattern_rs_pulses_level = re.compile(r'level\s+(\d+)')
        pattern_rs_pulses_rssi = re.compile(r'level\s+\d+\s+\(([\-\d]+)\)')
        pattern_rs_pulses_pps = re.compile(r'pps ([\.\d]+)')
        pattern_rs_rx_load = re.compile(r'RX Medium Load\s+([\d\.]+%)')
        pattern_rs_tx_load = re.compile(r'TX Medium Load\s+([\d\.]+%)')
        pattern_rs_total_load = re.compile(r'Total Medium Busy\s+([\d\.]+%)')
        pattern_rs_ex_retries = re.compile(r'Excessive Retries\s+(\d+)')
        pattern_rs_af_retries = re.compile(r'Aggr Full Retries\s+(\d+)')
        pattern_rs_cur_freq = re.compile(r'\(band \d+, freq (\d+)\)')

        for line in rf_scanner_text:
            if pattern_rs_pulses.search(line):
                radio_status['Pulses'] = pattern_rs_pulses.search(line).group(1)

            if pattern_rs_pulses_level.search(line):
                radio_status['Interference Level'] = pattern_rs_pulses_level.search(line).group(1)

            if pattern_rs_pulses_rssi.search(line):
                radio_status['Interference RSSI'] = pattern_rs_pulses_rssi.search(line).group(1)

            if pattern_rs_pulses_pps.search(line):
                radio_status['Interference PPS'] = pattern_rs_pulses_pps.search(line).group(1)

        pattern_start = re.compile(r'rf5.0 Statistics')
        pattern_end = re.compile(r'Software Priority Queues')
        rf_stat_text = cut_text(dc_list, pattern_start, pattern_end, 3, -2)

        for line in rf_stat_text:
            if pattern_rs_rx_load.search(line):
                radio_status['RX Medium Load'] = pattern_rs_rx_load.search(line).group(1)

            if pattern_rs_tx_load.search(line):
                radio_status['TX Medium Load'] = pattern_rs_tx_load.search(line).group(1)

            if pattern_rs_total_load.search(line):
                radio_status['Total Medium Busy'] = pattern_rs_total_load.search(line).group(1)

            if pattern_rs_ex_retries.search(line):
                radio_status['Excessive Retries'] = pattern_rs_ex_retries.search(line).group(1)

            if pattern_rs_af_retries.search(line):
                radio_status['Aggr Full Retries'] = pattern_rs_af_retries.search(line).group(1)

            if pattern_rs_cur_freq.search(line):
                radio_status['Current Frequency'] = pattern_rs_cur_freq.search(line).group(1)

    except:
        logger.warning('Radio Status was not parsed')

    logger.debug(f'Radio Status: {radio_status}')

    # Ethernet Status
    ethernet_statuses = {'Status': 'down', 'Speed': None, 'Duplex': None, 'Negotiation': None, 'Rx CRC': 0,
                         'Tx CRC': 0}
    ethernet_status = {'eth0': ethernet_statuses, 'eth1': deepcopy(ethernet_statuses)}

    try:
        pattern_start = re.compile(r'eth0: flags=')
        pattern_end = re.compile(r'Name\s+Network')
        ifc_stat_text = cut_text(dc_list, pattern_start, pattern_end, 0, -2)

        slices = []
        for index, line in enumerate(ifc_stat_text):
            if line.startswith('eth0: flags'):
                slices.append(index)
                slices.append(index + 36)
            elif line.startswith('eth1: flags'):
                slices.append(index)
                slices.append(index + 36)

        interfaces_text = slice_text(ifc_stat_text, slices)

        # Parse interfaces
        pattern_es_ifc = re.compile(r'([\w\d]+): flags')
        pattern_es_status = re.compile(r'Physical link is (\w+)')
        pattern_es_speed = re.compile(r'Physical link is \w+, (\d+) Mbps')
        pattern_es_duplex = re.compile(r'Physical link is \w+, \d+ Mbps\s+(\w+)-duplex')
        pattern_es_autoneg = re.compile(r'Physical link is \w+, \d+ Mbps\s+\w+-duplex, (\w+)')
        pattern_es_crc = re.compile(r'CRC errors\s+(\d+)')

        for interface_text in interfaces_text:
            for line in interface_text:
                if pattern_es_ifc.search(line):
                    interface = pattern_es_ifc.search(line).group(1)

                if pattern_es_status.search(line):
                    ethernet_status[interface]['Status'] = str.lower(pattern_es_status.search(line).group(1))

                if pattern_es_speed.search(line):
                    ethernet_status[interface]['Speed'] = pattern_es_speed.search(line).group(1)

                if pattern_es_duplex.search(line):
                    ethernet_status[interface]['Duplex'] = pattern_es_duplex.search(line).group(1)

                if pattern_es_autoneg.search(line):
                    ethernet_status[interface]['Negotiation'] = pattern_es_autoneg.search(line).group(1)

                if len(pattern_es_crc.findall(line)) == 2:
                    ethernet_status[interface]['Rx CRC'] = pattern_es_crc.findall(line)[0]
                    ethernet_status[interface]['Tx CRC'] = pattern_es_crc.findall(line)[1]
                elif len(pattern_es_crc.findall(line)) == 1:
                    ethernet_status[interface]['Rx CRC'] = pattern_es_crc.findall(line)[0]
                    ethernet_status[interface]['Tx CRC'] = 0

    except:
        logger.warning('Ethernet Status was not parsed')

    logger.debug(f'Ethernet Status: {ethernet_status}')

    # Switch Status
    try:
        pattern_start = re.compile(r'Switch statistics:')
        pattern_end = re.compile(r'DB Records')
        sw_stat_text = ''.join(cut_text(dc_list, pattern_start, pattern_end, 6, -2))

        pattern_ss_stat = re.findall(r'(\d+)\s+'
                             r'>?(\d+)\s+'
                             r'>?(\d+)\s+'
                             r'>?(\d+)\s+'
                             r'>?(\d+)\s+'
                             r'>?(\d+)\s+'
                             r'>?(\d+)\s+'
                             r'>?(\d+)\s+'
                             r'>?(\d+)\s+'
                             r'>?(\d+)', sw_stat_text)

        switch_status = {pattern_ss_stat[id][0]: sw_group[1:] for id, sw_group in enumerate(pattern_ss_stat)}
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
    except:
        logger.warning('Switch Status was not parsed')

    logger.debug(f'Switch Status: {switch_status}')

    # QoS status
    try:
        pattern_start = re.compile(r'Software Priority Queues rf5.0')
        pattern_end = re.compile(r'Phy errors: total \d+')
        qos_stat_text = ''.join(cut_text(dc_list, pattern_start, pattern_end, 0, 1))

        pattern_qs_stat = re.findall(r'(q\d+)\s+(\((P\d+)\))?(\s+\(cos\d\))?\s+(\d+)\s+\/\s+(\d+)?', qos_stat_text)
        qos_status = {channel[0]: channel[2:] for channel in pattern_qs_stat}
        for channel, status in qos_status.items():
            qos_status[channel] = {}
            qos_status[channel]['Prio'] = status[0]
            qos_status[channel]['Count'] = status[2]
            if status[3] != '':
                qos_status[channel]['Drops'] = status[3]
            else:
                qos_status[channel]['Drops'] = '777'
    except:
        logger.warning('QoS status was not parsed')

    logger.debug(f'QoS Status: {qos_status}')

    # Prepare result to create a class instance
    result = (model, subfamily, serial_number, firmware,
              uptime, reboot_reason, dc_list, dc_string,
              settings, radio_status, ethernet_status,
              switch_status, qos_status)

    return result


logger = logging.getLogger('logger.parser_r5000')
