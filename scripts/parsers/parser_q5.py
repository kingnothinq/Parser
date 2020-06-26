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

    def cut_text(dc_list, pattern_start, pattern_end, offset_start, offset_end):
        """Cut text from patter_start to pattern_end
        Input - text, patterns - re.compile, offsets - int
        Output - a list with the cut text
        """
        try:
            for index, line in enumerate(dc_list):
                if pattern_start.search(line):
                    text_start = index + offset_start
                if pattern_end.search(line):
                    text_end = index + offset_end
            text = dc_list[text_start:text_end]
        except:
            text = dc_list
            logger.warning(f'Text has not been cut. Patterns: {pattern_start} - {pattern_end}')
        return text

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
        general_text = ''.join(dc_list[:20])

        pattern_g_fw = re.compile(r'H\d{2}S\d{2}-OCTOPUS_PTPv[\d.]+')
        pattern_g_model = re.compile(r'([QV]5-[\dE]+)')
        pattern_g_sn = re.compile(r'SN:(\d+)')
        pattern_g_uptime = re.compile(r'Uptime: ([\d\w :]*)')
        pattern_g_reboot_reason = re.compile(r'Last reboot reason: ([\w ]*)')

        if pattern_g_fw.search(general_text):
            firmware = pattern_g_fw.search(general_text).group()

        pattern = pattern_g_model.search(general_text)
        if pattern:
            model = pattern.group()
            if 'Q5' in model:
                subfamily = 'Quanta 5'
            elif 'V5' in model:
                subfamily = 'Vector 5'
            else:
                model = 'Quanta Unknown model'
                subfamily = 'Quanta 5'

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
    settings = {'Role': None, 'Bandwidth': None, 'DL Frequency': None, 'UL Frequency': None, 'Frame size': None,
                'Guard Interval': None, 'DL/UL Ratio': None, 'Tx Power': None, 'ATPC': 'Disabled',
                'AMC Strategy': None, 'ADLP': 'Disabled', 'Max DL MCS': None, 'Max UL MCS': None, 'DFS': 'Disabled',
                'ARQ': 'Disabled', 'Interface Status': {'ge0': 'down'}}

    try:
        # Find "conf show"
        pattern_start = re.compile(r'#System parameters')
        pattern_end = re.compile(r'oct swmac_info')
        settings_text = cut_text(dc_list, pattern_start, pattern_end, 0, 0)

        # Parse settings
        pattern_set_role = re.compile(r'ptp_role (\w+)')
        pattern_set_band = re.compile(r'bw (\d+)')
        pattern_set_freq_dl = re.compile(r'freq_dl (\d+)')
        pattern_set_freq_ul = re.compile(r'freq_ul (\d+)')
        pattern_set_frame = re.compile(r'frame_length ([\.\d]+)')
        pattern_set_gi = re.compile(r'guard_interval ([auto\d\/]+)')
        pattern_set_adlp = re.compile(r'radio.auto_dl_ul_ratio (on)')
        pattern_set_dlp = re.compile(r'radio.dl_ul_ratio (\d+)')
        pattern_set_pwr = re.compile(r'tx_power ([\-\d]+)')
        pattern_set_atpc = re.compile(r'atpc (on)')
        pattern_set_amc = re.compile(r'amc_strategy (\w+)')
        pattern_set_dl_mcs = re.compile(r'dl_mcs (([\-\d]+)?(QPSK|QAM)-\d+\/\d+)')
        pattern_set_ul_mcs = re.compile(r'ul_mcs (([\-\d]+)?(QPSK|QAM)-\d+\/\d+)')
        pattern_set_dfs = re.compile(r'dfs (dfs_rd|on)')
        pattern_set_harq = re.compile(r'harq (on)')
        pattern_set_ifc = re.compile(r'ifc (ge0)')

        for line in settings_text:
            if pattern_set_role.search(line):
                settings['Role'] = pattern_set_role.search(line).group(1)

            if pattern_set_band.search(line):
                settings['Bandwidth'] = pattern_set_band.search(line).group(1)

            if pattern_set_freq_dl.search(line):
                settings['DL Frequency'] = pattern_set_freq_dl.search(line).group(1)

            if pattern_set_freq_ul.search(line):
                settings['UL Frequency'] = pattern_set_freq_ul.search(line).group(1)

            if pattern_set_frame.search(line):
                settings['Frame size'] = pattern_set_frame.search(line).group(1)

            if pattern_set_gi.search(line):
                settings['Guard Interval'] = pattern_set_gi.search(line).group(1)

            if pattern_set_adlp.search(line):
                settings['ADLP'] = 'Enabled'

            if pattern_set_dlp.search(line):
                pattern = pattern_set_dlp.search(line).group(1)
                settings['DL/UL Ratio'] = f'{pattern}/{100 - int(pattern)}'

            if pattern_set_pwr.search(line):
                settings['Tx Power'] = pattern_set_pwr.search(line).group(1)

            if pattern_set_atpc.search(line):
                settings['ATPC'] = 'Enabled'

            if pattern_set_amc.search(line):
                settings['AMC Strategy'] = pattern_set_amc.search(line).group(1)

            if pattern_set_dl_mcs.search(line):
                settings['Max DL MCS'] = pattern_set_dl_mcs.search(line).group(1)

            if pattern_set_ul_mcs.search(line):
                settings['Max UL MCS'] = pattern_set_ul_mcs.search(line).group(1)

            if pattern_set_dfs.search(line):
                settings['DFS'] = 'Enabled'

            if pattern_set_harq.search(line):
                settings['ARQ'] = 'Enabled'

            if pattern_set_ifc.search(line):
                interface = pattern_set_ifc.search(line).group(1)
                if 'up' in line:
                    settings['Interface Status'][interface] = 'up'

    except:
        logger.warning('Settings were not parsed')

    logger.debug(f'Settings: {settings}')

    # Radio Status
    stream = {'Tx Power': None, 'MCS': None, 'RSSI': None, 'EVM': None, 'Crosstalk': None, 'ARQ ratio': None}
    role = {'Frequency': None, 'Stream 0': stream, 'Stream 1': deepcopy(stream)}
    radio_status = {'Link status': None, 'Measured Distance': None, 'Downlink': role, 'Uplink': deepcopy(role)}
    dowlink = radio_status['Downlink']
    uplink = radio_status['Uplink']

    try:
        # Find "oct radio stat"
        pattern_start = re.compile(r'#Radio diagnostic')
        pattern_end = re.compile(r'oct show calibration')
        radio_text = cut_text(dc_list, pattern_start, pattern_end, 2, 0)

        # Parse radio status
        pattern_rs_status = re.compile(r'State\s+(\w+)')
        pattern_rs_dist = re.compile(r'Distance\s+(\d+ k?m)')
        pattern_rs_pwr = re.compile(r'([\-\.\d]+) \/ ([\-\.\d]+) dBm')
        pattern_rs_freq = re.compile(r'(\d+) MHz')
        pattern_rs_mcs = re.compile(r'(([\-\d]+)?(QPSK|QAM)-\d+\/\d+)')
        pattern_rs_rssi = re.compile(r'([\.\-\d]+)( \([\.\-\d]+\))? dBm')
        pattern_rs_evm = re.compile(r'([\.\-\d]+) dB')
        pattern_rs_crosstalk = re.compile(r'([\.\-\d]+) dB')
        pattern_rs_arq = re.compile(r'([\.\d]+) %')

        for line in radio_text:
            if pattern_rs_status.search(line):
                radio_status['Link status'] = pattern_rs_status.search(line).group(1)

            if pattern_rs_dist.search(line):
                radio_status['Measured Distance'] = pattern_rs_dist.search(line).group(1)

            if settings['Role'] == 'master':
                if line.startswith('| TX power'):
                    dowlink['Stream 0']['Tx Power'] = pattern_rs_pwr.search(line).group(1)
                    dowlink['Stream 1']['Tx Power'] = pattern_rs_pwr.search(line).group(2)
                elif line.startswith('| Remote TX power') and radio_status['Link status'] == 'connected':
                    uplink['Stream 0']['Tx Power'] = pattern_rs_pwr.search(line).group(1)
                    uplink['Stream 1']['Tx Power'] = pattern_rs_pwr.search(line).group(2)
            else:
                if line.startswith('| TX power'):
                    uplink['Stream 0']['Tx Power'] = pattern_rs_pwr.search(line).group(1)
                    uplink['Stream 1']['Tx Power'] = pattern_rs_pwr.search(line).group(2)
                elif line.startswith('| Remote TX power') and radio_status['Link status'] == 'connected':
                    dowlink['Stream 0']['Tx Power'] = pattern_rs_pwr.search(line).group(1)
                    dowlink['Stream 1']['Tx Power'] = pattern_rs_pwr.search(line).group(2)

            if radio_status['Link status'] == 'connected':
                if line.startswith('| Frequency'):
                    if pattern_rs_freq.search(line):
                        dowlink['Frequency'] = pattern_rs_freq.findall(line)[0]
                        uplink['Frequency'] = pattern_rs_freq.findall(line)[1]

                if line.startswith('| MCS'):
                    if pattern_rs_mcs.search(line):
                        dowlink['Stream 0']['MCS'] = pattern_rs_mcs.findall(line)[0][0]
                        dowlink['Stream 1']['MCS'] = pattern_rs_mcs.findall(line)[1][0]
                        uplink['Stream 0']['MCS'] = pattern_rs_mcs.findall(line)[2][0]
                        uplink['Stream 1']['MCS'] = pattern_rs_mcs.findall(line)[3][0]

                if line.startswith('| RSSI'):
                    if pattern_rs_rssi.search(line):
                        dowlink['Stream 0']['RSSI'] = pattern_rs_rssi.findall(line)[0][0]
                        dowlink['Stream 1']['RSSI'] = pattern_rs_rssi.findall(line)[1][0]
                        uplink['Stream 0']['RSSI'] = pattern_rs_rssi.findall(line)[2][0]
                        uplink['Stream 1']['RSSI'] = pattern_rs_rssi.findall(line)[3][0]

                if line.startswith('| EVM'):
                    if pattern_rs_evm.search(line):
                        dowlink['Stream 0']['EVM'] = pattern_rs_evm.findall(line)[0]
                        dowlink['Stream 1']['EVM'] = pattern_rs_evm.findall(line)[1]
                        uplink['Stream 0']['EVM'] = pattern_rs_evm.findall(line)[2]
                        uplink['Stream 1']['EVM'] = pattern_rs_evm.findall(line)[3]

                if line.startswith('| Crosstalk'):
                    if pattern_rs_crosstalk.search(line):
                        dowlink['Stream 0']['Crosstalk'] = pattern_rs_crosstalk.findall(line)[0]
                        dowlink['Stream 1']['Crosstalk'] = pattern_rs_crosstalk.findall(line)[1]
                        uplink['Stream 0']['Crosstalk'] = pattern_rs_crosstalk.findall(line)[2]
                        uplink['Stream 1']['Crosstalk'] = pattern_rs_crosstalk.findall(line)[3]

                if line.startswith('| ARQ ratio'):
                    if pattern_rs_arq.search(line):
                        dowlink['Stream 0']['ARQ ratio'] = pattern_rs_arq.findall(line)[0]
                        dowlink['Stream 1']['ARQ ratio'] = pattern_rs_arq.findall(line)[1]
                        uplink['Stream 0']['ARQ ratio'] = pattern_rs_arq.findall(line)[2]
                        uplink['Stream 1']['ARQ ratio'] = pattern_rs_arq.findall(line)[3]

    except:
        logger.warning('Radio Status was not parsed')

    logger.debug(f'Radio Status: {radio_status}')

    # Ethernet Status
    ethernet_status = {'ge0': {'Status': 'down', 'Speed': None, 'Duplex': None, 'Negotiation': None, 'CRC': 0}}

    try:
        # Find "ifc -a"
        pattern_start = re.compile(r'#Interface statistic')
        pattern_end = re.compile(r'Radio port statistics')
        interface_text = cut_text(dc_list, pattern_start, pattern_end, 1, 12)

        # Parse interfaces
        pattern_es_status = re.compile(r'Physical link is (\w+)')
        pattern_es_speed = re.compile(r'Physical link is \w+, (\d+) Mbps')
        pattern_es_duplex = re.compile(r'Physical link is \w+, \d+ Mbps\s+(\w+)-duplex')
        pattern_es_autoneg = re.compile(r'Physical link is \w+, \d+ Mbps\s+\w+-duplex, (\w+)')
        pattern_es_crc = re.compile(r'CRC errors\s+(\d+)')

        for line in interface_text:
            if pattern_es_status.search(line):
                ethernet_status['ge0']['Status'] = str.lower(pattern_es_status.search(line).group(1))

            if pattern_es_speed.search(line):
                ethernet_status['ge0']['Speed'] = pattern_es_speed.search(line).group(1)

            if pattern_es_duplex.search(line):
                ethernet_status['ge0']['Duplex'] = pattern_es_duplex.search(line).group(1)

            if pattern_es_autoneg.search(line):
                ethernet_status['ge0']['Negotiation'] = pattern_es_autoneg.search(line).group(1)

            if pattern_es_crc.search(line):
                ethernet_status['ge0']['CRC'] = pattern_es_crc.search(line).group(1)

    except:
        logger.warning('Ethernet Status was not parsed')

    logger.debug(f'Ethernet Status: {ethernet_status}')

    # Prepare result to create a class instance
    result = (model, subfamily, serial_number, firmware,
              uptime, reboot_reason, dc_list, dc_string,
              settings, radio_status, ethernet_status)

    return result


logger = logging.getLogger('logger.parser_q5')