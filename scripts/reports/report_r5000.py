# -*- coding: utf-8 -*-

import logging
from time import time


def timer(function):
    """Estimate time"""
    def wrapper(dc_string, dc_list):
        time_start = time()
        created_report = function(dc_string, dc_list)
        time_end = time()
        logger.info(f'Report prepared, Elapsed Time: {time_end - time_start}')
        return created_report
    return wrapper

@timer
def jira(device, tests):
    """Prepare a report for JIRA."""

    settings = device.settings
    radio_settings = settings['Radio']
    radio_status = device.radio_status
    ethernet_status = device.ethernet_status
    message = []

    # General
    message.append(f'*General*\n'
                   f'|*Serial Number*|{device.serial_number}|\n'
                   f'|*Model*|{device.model}|\n'
                   f'|*Firmware version*|{device.firmware}|\n')

    # Settings
    if 'MINT' in device.firmware:
        message.append(f'*Settings*\n'
                       f'|*Role*|{str.capitalize(radio_settings["Type"])}'
                       f'|*Tx Power*|{radio_settings["Tx Power"]} dBm'
                       f'|*DFS*|{radio_settings["DFS"]}| | |\n')
        if radio_settings["Type"] == 'master':
            message.append(f'|*Polling*|{radio_settings["Polling"]}'
                           f'|*ATPC*|{radio_settings["ATPC"]}'
                           f'|*Scrambling*|{radio_settings["Scrambling"]}| | |\n')
        else:
            message.append(f'| | '
                           f'|*ATPC*|{radio_settings["ATPC"]}'
                           f'|*Scrambling*|{radio_settings["Scrambling"]}| | |\n')
        message.append(f'| | |*Extnoise*|{radio_settings["Extnoise"]} dB| | | | |\n'
                       f'| | | | | | | | |\n'
                       f'|*Profile (State/Status)*|*Frequency*|*Bandwidth*|*Max bitrate*'
                       f'|*Auto bitrate*|*MIMO*|*SID*|*Greenfield*|\n')
        for id, profile in radio_settings['Profile'].items():
            message.append(f'|{id.replace("M", "Master profile")} '
                           f'({profile["State"]} / {str(profile["Status"]).replace("None", "Enabled")})'
                           f'|{profile["Frequency"]} MHz|{profile["Bandwidth"]} MHz'
                           f'|{profile["Max bitrate"]}|{profile["Auto bitrate"]}'
                           f'|{str.upper(profile["MIMO"])}'
                           f'|{profile["SID"]}'
                           f'|{profile["Greenfield"]}|\n')

    else:
        message.append(f'*Settings*\n'
                       f'|*Role*|{str.capitalize(radio_settings["Type"])} '
                       f'|*Tx Power*| {radio_settings["Tx Power"]} dBm '
                       f'|*DFS*| {radio_settings["DFS"]} |   |   | \n')
        if radio_settings["Type"] == 'master':
            message.append(f'|*Frame size*|{radio_settings["Frame size"]} ms'
                           f'|*ATPC*|{radio_settings["ATPC"]}'
                           f'|*Scrambling*|{radio_settings["Scrambling"]}| | |\n'
                           f'|*DL/UL ratio*|{radio_settings["DL/UL ratio"]} %'
                           f'|*Extnoise*|{radio_settings["Extnoise"]} dB| | | | |\n'
                           f'|*Distance*|{radio_settings["Distance"]} km| | | | | | |\n'
                           f'|*Target RSSI*|{radio_settings["Target RSSI"]} dBm| | | | | | |\n'
                           f'|*TSync*|{radio_settings["TSync"]}| | | | | | |\n')
        else:
            message.append(f'| |'
                           f'|*ATPC*|{radio_settings["ATPC"]}'
                           f'|*Scrambling*|{radio_settings["Scrambling"]}| | |\n'
                           f'| | '
                           f'|*Extnoise*|{radio_settings["Extnoise"]} dB| | | | |\n')
        message.append(f'| | | | | | | | |\n'
                       f'|*Profile (State)*|*Frequency*|*Bandwidth*'
                       f'|*Max bitrate*|*Auto bitrate*|*MIMO*|*SID*|*Greenfield*|\n')
        # Fill the table for each profile
        for id, profile in radio_settings['Profile'].items():
            message.append(f'|{id.replace("M", "Master profile")} '
                           f'({profile["State"]} / {str(profile["Status"]).replace("None", "Enabled")})'
                           f'|{profile["Frequency"]} MHz|{profile["Bandwidth"]} MHz'
                           f'|{profile["Max bitrate"]}|{profile["Auto bitrate"]}'
                           f'|{str.upper(profile["MIMO"])}'
                           f'|{profile["SID"]}'
                           f'|{profile["Greenfield"]}|\n')

    # Radio status
    message.append(f'*Radio status*\n'
                   f'|*Interference*| | | | | | | |\n'
                   f'|*Pulses*|{radio_status["Pulses"]} pps'
                   f'|*Interference RSSI*|{radio_status["Interference RSSI"]} dBm| | | | |\n'
                   f'|*Links*| | | | | | | |\n'
                   f'|*Name*|*MAC*|*Bitrate Rx/Tx*|*Retries Rx/Tx %*'
                   f'|*RSSI Rx/Tx dBm*|*SNR Rx/Tx dB*|*Level Rx/Tx dB*|*Power Rx/Tx dBm*|\n')
    # Fill the table for each link
    if radio_status['Links']:
        for id, link in radio_status['Links'].items():
            message.append(f'|{link["Name"]}|{id}'
                           f'|{link["Bitrate Rx"]}/{link["Bitrate Tx"]}'
                           f'|{link["Retry Rx"]}/{link["Retry Tx"]}'
                           f'|{link["RSSI Rx"]}/{str(link["RSSI Tx"]).replace("None","NA")}'
                           f'|{link["SNR Rx"]}/{link["SNR Tx"]}'
                           f'|{link["Level Rx"]}/{link["Level Tx"]}'
                           f'|{link["Power Rx"]}/{link["Power Tx"]}|\n')

    # Physical interfaces status
    message.append(f'*Physical interfaces status*\n'
                   f'|*Eth0*|{ethernet_status["eth0"]["Status"]}|\n'
                   f'|*Eth1*|{ethernet_status["eth1"]["Status"]}|\n')

    # Issues and recommendations
    message.append(f'*Issues and recommendations*\n')
    for test in tests:
        message.append(f'{test}\n')

    return device.model, device.family, device.subfamily, device.serial_number, device.firmware, message


@timer
def web():
    pass


@timer
def cli():
    pass


logger = logging.getLogger('logger.report_r5000')