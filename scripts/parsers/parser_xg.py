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
    """Parse a XG diagnostic card and fill the class instance in.

    Input - text (dc_string - string, dc_list - list)
    Output:

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
        ge0, ge1, sfp
            Status
            Speed
            Duplex
            Negotiation
            Rx CRC
            Tx CRC

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

        pattern_g_fw = re.compile(r'H\d{2}S\d{2}[v\d.-]+')
        pattern_g_model = re.compile(r'([XU]m/\dX?.\d{3,4}.\dx\d{3})(.2x\d{2})?')
        pattern_g_sn = re.compile(r'SN:(\d+)')
        pattern_g_uptime = re.compile(r'Uptime: ([\d\w :]*)')
        pattern_g_reboot_reason = re.compile(r'Last reboot reason: ([\w ]*)')

        if pattern_g_fw.search(general_text):
            firmware = pattern_g_fw.search(general_text).group()

        pattern = pattern_g_model.search(general_text)
        if pattern:
            model = pattern.group()
            if '500.2x500' in model or '500.2x200' in model:
                subfamily = 'XG 500'
            elif '1000.4x150' in model or '1000.4x300' in model:
                subfamily = 'XG 1000'
            else:
                model = 'XG Unknown model'
                subfamily = 'XG 500'

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
    settings = {'Role': None, 'Bandwidth': None, 'DL Frequency': {'Carrier 0': None, 'Carrier 1': None},
                'UL Frequency': {'Carrier 0': None, 'Carrier 1': None}, 'Short CP': 'Disabled', 'Max distance': None,
                'Frame size': None, 'DL/UL Ratio': None, 'Tx Power': None, 'Control Block Boost': 'Disabled',
                'ATPC': 'Disabled', 'AMC Strategy': None, 'Max MCS': None, 'Traffic prioritization': 'Disabled',
                'IDFS': 'Disabled', 'ADLP': 'Disabled',
                'Interface Status': {'ge0': 'down', 'ge1': 'down', 'sfp': 'down', 'radio': 'down'}}

    try:
        # Find "conf show"
        pattern_start = re.compile(r'==\[\s+config show\s+\]')
        pattern_end = re.compile(r'==\[\s+xg stat\s+\]')
        settings_text = cut_text(dc_list, pattern_start, pattern_end, 2, 0)

        # Parse settings
        pattern_set_role = re.compile(r'xg -type( |=)(\w+)')
        pattern_set_band = re.compile(r'xg -channel-width( |=)(\d+)')
        pattern_set_freq_dl_xg = re.compile(r'xg -freq-dl (\d+)')
        pattern_set_freq_ul_xg = re.compile(r'xg -freq-ul (\d+)')
        pattern_set_freq_dl_xg1k = re.compile(r'xg -freq-dl \[0\](\d+),\[1\](\d+)')
        pattern_set_freq_ul_xg1k = re.compile(r'xg -freq-ul \[0\](\d+),\[1\](\d+)')
        pattern_set_scp = re.compile(r'xg -short-cp (1)')
        pattern_set_max_dist = re.compile(r'xg -max-distance( |=)(\d+)')
        pattern_set_frame = re.compile(r'xg -sframelen( |=)(\d+)')
        pattern_set_pwr = re.compile(r'xg -txpwr( |=)(\[0\])?([\-\d]+)(,(\[1\])?([\-\d]+))?')
        pattern_set_cbb = re.compile(r'xg -ctrl-block-boost (1)')
        pattern_set_atpc = re.compile(r'xg -atpc-master-enable (1)')
        pattern_set_amc = re.compile(r'xg -amc-strategy( |=)(\w+)')
        pattern_set_mcs = re.compile(r'xg -max-mcs (\d+)')
        pattern_set_idfs = re.compile(r'xg -idfs-enable (1)')
        pattern_set_tp = re.compile(r'xg -traffic-prioritization (1)')
        pattern_set_ifc = re.compile(r'ifc (ge\d|sfp|radio)')
        pattern_set_adlp = re.compile(r'-tdd-profile-auto-switching (1)')
        pattern_set_dlp = re.compile(r'DL/UL Ratio\s+\|(\d+/\d+)')

        for line in settings_text:
            if pattern_set_role.search(line):
                settings['Role'] = pattern_set_role.search(line).group(2)

            if pattern_set_band.search(line):
                settings['Bandwidth'] = pattern_set_band.search(line).group(2)

            if pattern_set_freq_dl_xg.search(line):
                settings['DL Frequency']['Carrier 0'] = pattern_set_freq_dl_xg.search(line).group(1)

            if pattern_set_freq_ul_xg.search(line):
                settings['UL Frequency']['Carrier 0'] = pattern_set_freq_ul_xg.search(line).group(1)

            if pattern_set_freq_dl_xg1k.search(line):
                settings['DL Frequency']['Carrier 0'] = pattern_set_freq_dl_xg1k.search(line).group(1)
                settings['DL Frequency']['Carrier 1'] = pattern_set_freq_dl_xg1k.search(line).group(2)

            if pattern_set_freq_ul_xg1k.search(line):
                settings['UL Frequency']['Carrier 0'] = pattern_set_freq_ul_xg1k.search(line).group(1)
                settings['UL Frequency']['Carrier 1'] = pattern_set_freq_ul_xg1k.search(line).group(2)

            if pattern_set_scp.search(line):
                settings['Short CP'] = 'Enabled'

            if pattern_set_max_dist.search(line):
                settings['Max distance'] = pattern_set_max_dist.search(line).group(2)

            if pattern_set_frame.search(line):
                settings['Frame size'] = pattern_set_frame.search(line).group(2)

            if pattern_set_pwr.search(line):
                if not pattern_set_pwr.search(line).group(6):
                    settings['Tx Power'] = pattern_set_pwr.search(line).group(3)
                else:
                    pattern = pattern_set_pwr.search(line)
                    settings['Tx Power'] = max(pattern.group(3), pattern.group(6))

            if pattern_set_cbb.search(line):
                settings['Control Block Boost'] = 'Enabled'

            if pattern_set_atpc.search(line):
                settings['ATPC'] = 'Enabled'

            if pattern_set_amc.search(line):
                settings['AMC Strategy'] = pattern_set_amc.search(line).group(2)

            if pattern_set_mcs.search(line):
                settings['Max MCS'] = pattern_set_mcs.search(line).group(1)

            if pattern_set_idfs.search(line):
                settings['IDFS'] = 'Enabled'

            if pattern_set_tp.search(line):
                settings['Traffic prioritization'] = 'Enabled'

            if pattern_set_ifc.search(line):
                interface = pattern_set_ifc.search(line).group(1)
                if 'up' in line:
                    settings['Interface Status'][interface] = 'up'

            if pattern_set_adlp.search(line):
                settings['ADLP'] = 'Enabled'

        if pattern_set_dlp.search(dc_string) and settings['ADLP'] == 'Enabled':
            settings['DL/UL Ratio'] = f'{pattern_set_dlp.findall(dc_string)[0]} auto'
        else:
            settings['DL/UL Ratio'] = f'{pattern_set_dlp.findall(dc_string)[0]}'

    except:
        logger.warning('Settings were not parsed')

    logger.debug(f'Settings: {settings}')

    # Radio Status
    stream = {'Tx Power': None, 'Tx Gain': None, 'MCS': None, 'CINR': None, 'RSSI': None, 'Crosstalk': None,
              'Errors Ratio': None}
    carrier = {'Frequency': None, 'Rx Acc FER': None, 'Stream 0': stream, 'Stream 1': deepcopy(stream)}
    role = {'Role': None, 'Carrier 0': carrier, 'Carrier 1': deepcopy(carrier)}
    radio_status = {'Link status': None, 'Measured Distance': None, 'Master': role, 'Slave': deepcopy(role)}

    try:
        # Find "xginfo stat"
        pattern_start = re.compile(r'==\[\s+xg stat\s+\]')
        pattern_end = re.compile(r'==\[\s+ctl\s+\]')
        radio_text = cut_text(dc_list, pattern_start, pattern_end, 1, -1)

        # Split it to carriers
        pattern_carrier = re.compile(r'\|\s+Carrier (\d)')
        slices = []
        for index, line in enumerate(radio_text):
            if pattern_carrier.search(line):
                slices.append(index)
        slices.append(len(radio_text))

        carriers_text = slice_text(radio_text, slices)

        # Parse carriers
        pattern_rs_status = re.compile(r'Wireless Link( status)?\s+\|(\w+)')
        pattern_rs_dist = re.compile(r'Distance\s+\|(\d+)\s+(meters)?')
        pattern_rs_freq = re.compile(r'(\d+)( MHz)?')
        pattern_rs_accfer = re.compile(r'\(([\.\d]+)%\)')
        pattern_rs_pwr = re.compile(r'([\.\-\d]+)')
        pattern_rs_gain = re.compile(r'([\.\-\d]+)')
        pattern_rs_mcs = re.compile(r'((QPSK|QAM)(\d+)? \d+/\d+) \(\d+\)')
        pattern_rs_cinr = re.compile(r'([\.\-\d]+)')
        pattern_rs_rssi = re.compile(r'([\.\-\d]+) dBm')
        pattern_rs_crosstalk = re.compile(r'([\.\-\d]+)')
        pattern_rs_tber = re.compile(r'\(([\.\d]+)%\)')

        if settings['Role'] == 'master':
            radio_status['Master']['Role'] = 'Local'
            radio_status['Slave']['Role'] = 'Remote'
            local = radio_status['Master']
            remote = radio_status['Slave']
        else:
            radio_status['Master']['Role'] = 'Remote'
            radio_status['Slave']['Role'] = 'Local'
            local = radio_status['Slave']
            remote = radio_status['Master']

        for line in radio_text:
            if pattern_rs_status.search(line):
                radio_status['Link status'] = pattern_rs_status.search(line).group(2)

            if pattern_rs_dist.search(line):
                radio_status['Measured Distance'] = pattern_rs_dist.search(line).group(1)

        for index, carrier_text in enumerate(carriers_text):

            carrier = f'Carrier {index}'

            for line in carrier_text:
                if line.startswith('|Tx/Rx Frequency'):
                    if len(pattern_rs_freq.findall(line)) == 2:
                        local[carrier]['Frequency'] = pattern_rs_freq.findall(line)[0][0]
                        remote[carrier]['Frequency'] = pattern_rs_freq.findall(line)[1][0]
                    else:
                        local[carrier]['Frequency'] = pattern_rs_freq.findall(line)[0][0]

                if line.startswith('|Rx Acc FER'):
                    if len(pattern_rs_accfer.findall(line)) == 2:
                        local[carrier]['Rx Acc FER'] = pattern_rs_accfer.findall(line)[0]
                        remote[carrier]['Rx Acc FER'] = pattern_rs_accfer.findall(line)[1]
                    else:
                        local[carrier]['Rx Acc FER'] = pattern_rs_accfer.findall(line)[0]

                if line.startswith('|    |Power'):
                    if len(pattern_rs_pwr.findall(line)) == 4:
                        local[carrier]['Stream 0']['Tx Power'] = pattern_rs_pwr.findall(line)[0]
                        local[carrier]['Stream 1']['Tx Power'] = pattern_rs_pwr.findall(line)[1]
                        remote[carrier]['Stream 0']['Tx Power'] = pattern_rs_pwr.findall(line)[2]
                        remote[carrier]['Stream 1']['Tx Power'] = pattern_rs_pwr.findall(line)[3]
                    else:
                        local[carrier]['Stream 0']['Tx Power'] = pattern_rs_pwr.findall(line)[0]
                        local[carrier]['Stream 1']['Tx Power'] = pattern_rs_pwr.findall(line)[1]

                if line.startswith('|    |Gain'):
                    if len(pattern_rs_gain.findall(line)) == 4:
                        local[carrier]['Stream 0']['Tx Gain'] = pattern_rs_gain.findall(line)[0]
                        local[carrier]['Stream 1']['Tx Gain'] = pattern_rs_gain.findall(line)[1]
                        remote[carrier]['Stream 0']['Tx Gain'] = pattern_rs_gain.findall(line)[2]
                        remote[carrier]['Stream 1']['Tx Gain'] = pattern_rs_gain.findall(line)[3]
                    else:
                        local[carrier]['Stream 0']['Tx Gain'] = pattern_rs_gain.findall(line)[0]
                        local[carrier]['Stream 1']['Tx Gain'] = pattern_rs_gain.findall(line)[1]

                if line.startswith('|RX  |MCS'):
                    if len(pattern_rs_mcs.findall(line)) == 4:
                        local[carrier]['Stream 0']['MCS'] = pattern_rs_mcs.findall(line)[0][0]
                        local[carrier]['Stream 1']['MCS'] = pattern_rs_mcs.findall(line)[1][0]
                        remote[carrier]['Stream 0']['MCS'] = pattern_rs_mcs.findall(line)[2][0]
                        remote[carrier]['Stream 1']['MCS'] = pattern_rs_mcs.findall(line)[3][0]
                    else:
                        local[carrier]['Stream 0']['MCS'] = pattern_rs_mcs.findall(line)[0][0]
                        local[carrier]['Stream 1']['MCS'] = pattern_rs_mcs.findall(line)[1][0]

                if line.startswith('|    |CINR'):
                    if len(pattern_rs_cinr.findall(line)) == 4:
                        local[carrier]['Stream 0']['CINR'] = pattern_rs_cinr.findall(line)[0]
                        local[carrier]['Stream 1']['CINR'] = pattern_rs_cinr.findall(line)[1]
                        remote[carrier]['Stream 0']['CINR'] = pattern_rs_cinr.findall(line)[2]
                        remote[carrier]['Stream 1']['CINR'] = pattern_rs_cinr.findall(line)[3]
                    else:
                        local[carrier]['Stream 0']['CINR'] = pattern_rs_cinr.findall(line)[0]
                        local[carrier]['Stream 1']['CINR'] = pattern_rs_cinr.findall(line)[1]

                if line.startswith('|    |RSSI'):
                    if len(pattern_rs_rssi.findall(line)) == 4:
                        local[carrier]['Stream 0']['RSSI'] = pattern_rs_rssi.findall(line)[0]
                        local[carrier]['Stream 1']['RSSI'] = pattern_rs_rssi.findall(line)[1]
                        remote[carrier]['Stream 0']['RSSI'] = pattern_rs_rssi.findall(line)[2]
                        remote[carrier]['Stream 1']['RSSI'] = pattern_rs_rssi.findall(line)[3]
                    else:
                        local[carrier]['Stream 0']['RSSI'] = pattern_rs_rssi.findall(line)[0]
                        local[carrier]['Stream 1']['RSSI'] = pattern_rs_rssi.findall(line)[1]

                if line.startswith('|    |Crosstalk'):
                    if len(pattern_rs_crosstalk.findall(line)) == 4:
                        local[carrier]['Stream 0']['Crosstalk'] = pattern_rs_crosstalk.findall(line)[0]
                        local[carrier]['Stream 1']['Crosstalk'] = pattern_rs_crosstalk.findall(line)[1]
                        remote[carrier]['Stream 0']['Crosstalk'] = pattern_rs_crosstalk.findall(line)[2]
                        remote[carrier]['Stream 1']['Crosstalk'] = pattern_rs_crosstalk.findall(line)[3]
                    else:
                        local[carrier]['Stream 0']['Crosstalk'] = pattern_rs_crosstalk.findall(line)[0]
                        local[carrier]['Stream 1']['Crosstalk'] = pattern_rs_crosstalk.findall(line)[1]

                if line.startswith('|    |Errors Ratio'):
                    if len(pattern_rs_tber.findall(line)) == 4:
                        local[carrier]['Stream 0']['Errors Ratio'] = pattern_rs_tber.findall(line)[0]
                        local[carrier]['Stream 1']['Errors Ratio'] = pattern_rs_tber.findall(line)[1]
                        remote[carrier]['Stream 0']['Errors Ratio'] = pattern_rs_tber.findall(line)[2]
                        remote[carrier]['Stream 1']['Errors Ratio'] = pattern_rs_tber.findall(line)[3]
                    else:
                        local[carrier]['Stream 0']['Errors Ratio'] = pattern_rs_tber.findall(line)[0]
                        local[carrier]['Stream 1']['Errors Ratio'] = pattern_rs_tber.findall(line)[1]
                elif line.startswith('|    |TBER'):
                    if len(pattern_rs_tber.findall(line)) == 4:
                        local[carrier]['Stream 0']['Errors Ratio'] = pattern_rs_tber.findall(line)[0]
                        local[carrier]['Stream 1']['Errors Ratio'] = pattern_rs_tber.findall(line)[1]
                        remote[carrier]['Stream 0']['Errors Ratio'] = pattern_rs_tber.findall(line)[2]
                        remote[carrier]['Stream 1']['Errors Ratio'] = pattern_rs_tber.findall(line)[3]
                    else:
                        local[carrier]['Stream 0']['Errors Ratio'] = pattern_rs_tber.findall(line)[0]
                        local[carrier]['Stream 1']['Errors Ratio'] = pattern_rs_tber.findall(line)[1]
                elif line.startswith('|    |Acc TBER'):
                    if len(pattern_rs_tber.findall(line)) == 4:
                        local[carrier]['Stream 0']['Errors Ratio'] = pattern_rs_tber.findall(line)[0]
                        local[carrier]['Stream 1']['Errors Ratio'] = pattern_rs_tber.findall(line)[1]
                        remote[carrier]['Stream 0']['Errors Ratio'] = pattern_rs_tber.findall(line)[2]
                        remote[carrier]['Stream 1']['Errors Ratio'] = pattern_rs_tber.findall(line)[3]
                    else:
                        local[carrier]['Stream 0']['Errors Ratio'] = pattern_rs_tber.findall(line)[0]
                        local[carrier]['Stream 1']['Errors Ratio'] = pattern_rs_tber.findall(line)[1]
    except:
        logger.warning('Radio Status was not parsed')

    logger.debug(f'Radio Status: {radio_status}')

    # Ethernet Status
    ethernet_statuses = {'Status': 'down', 'Speed': None, 'Duplex': None, 'Negotiation': None, 'Rx CRC': 0,
                         'Tx CRC': 0}
    ethernet_status = {'ge0': ethernet_statuses, 'ge1': deepcopy(ethernet_statuses), 'sfp': deepcopy(ethernet_statuses)}

    try:
        # Find "ifc -a"
        pattern_start = re.compile(r'==\[\s+ifc -a\s+\]')
        pattern_end = re.compile(r'==\[\s+sys info -full\s+\]')
        intefaces_text = cut_text(dc_list, pattern_start, pattern_end, 1, -1)

        slices = []
        for index, line in enumerate(intefaces_text):
            if line.startswith('ge0: flags'):
                slices.append(index)
                slices.append(index + 33)
            elif line.startswith('ge1: flags'):
                slices.append(index)
                slices.append(index + 33)
            elif line.startswith('sfp: flags'):
                slices.append(index)
                slices.append(index + 33)

        interfaces_text_cut = slice_text(intefaces_text, slices)

        # Parse interfaces
        pattern_es_ifc = re.compile(r'([\w\d]+): flags')
        pattern_es_status = re.compile(r'Physical link is (\w+)')
        pattern_es_speed = re.compile(r'Physical link is \w+, (\d+) Mbps')
        pattern_es_duplex = re.compile(r'Physical link is \w+, \d+ Mbps\s+(\w+)-duplex')
        pattern_es_autoneg = re.compile(r'Physical link is \w+, \d+ Mbps\s+\w+-duplex, (\w+)')
        pattern_es_crc = re.compile(r'CRC errors\s+(\d+)')

        for interface_text in interfaces_text_cut:
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

                if pattern_es_crc.search(line):
                    ethernet_status[interface]['Rx CRC'] = pattern_es_crc.findall(line)[0]
                    ethernet_status[interface]['Tx CRC'] = pattern_es_crc.findall(line)[1]

    except:
        logger.warning('Ethernet Status was not parsed')

    logger.debug(f'Ethernet Status: {ethernet_status}')

    # Panic
    try:
        pattern_start = re.compile(r'==\[\s+panic show\s+\]')
        pattern_end = re.compile(r'==\[\s+sys log show\s+\]')
        panic_text = cut_text(dc_list, pattern_start, pattern_end, 1, -1)

        panic = []
        pattern_panic = re.compile(r'Panic info : \[\w+\]: case "(\w+)"')
        pattern_assert = re.compile(r'Panic info : \[\w+\]: (ASS.+)')

        for line in panic_text:
            if pattern_panic.search(line):
                panic.append(pattern_panic.search(line).group(1))
            if pattern_assert.search(line):
                panic.append(pattern_assert.search(line).group(1))
        panic = set(panic)
    except:
        logger.warning('Panic messages were not parsed')

    logger.debug(f'Panic: {panic}')

    # Prepare result to create a class instance
    result = (model, subfamily, serial_number, firmware,
              uptime, reboot_reason, dc_list, dc_string,
              settings, radio_status, ethernet_status, panic)

    return result


logger = logging.getLogger('logger.parser_xg')