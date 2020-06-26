# -*- coding: utf-8 -*-

import unicodedata
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
    radio_status = device.radio_status
    downlink = radio_status['Downlink']
    uplink = radio_status['Uplink']
    ethernet_status = device.ethernet_status['ge0']
    message = []

    # General
    message.append(f'*General*\n'
                   f'| *Serial Number* | {device.serial_number} |\n'
                   f'| *Model* | {device.model} |\n'
                   f'| *Firmware version* | {device.firmware} |\n')

    # Settings
    message.append(f'\n*Settings*\n'
                   f'| *Role* | {str.capitalize(settings["Role"])} |  |  |  |\n'
                   f'| *Frequencies* | DL - {settings["DL Frequency"]} MHz\n'
                   f' UL - {settings["UL Frequency"]} MHz |  '
                   f'| *Tx Power* | {settings["Tx Power"]} dBm |\n'
                   f'| *DFS* | {settings["DFS"]} |  '
                   f'| *ATPC* | {settings["ATPC"]} |\n'
                   f'| *Bandwidth* | {settings["Bandwidth"]} MHz |  '     
                   f'| *AMC Strategy* | {str.capitalize(settings["AMC Strategy"])} |\n'
                   f'| *Frame size* | {settings["Frame size"]} ms |  '
                   f'| *Max MCS* | DL - {settings["Max DL MCS"]} \n'
                   f' UL - {settings["Max UL MCS"]} |\n'
                   f'| *Guard interval* | {settings["Guard Interval"]} |  '
                   f'| *ARQ* | {settings["ARQ"]} |\n')
    if settings['ADLP'] == 'Enabled':
        message.append(f'| *DL/UL Ratio* | {settings["DL/UL Ratio"]} % (Auto) |  |  |  |\n')
    else:
        message.append(f'| *DL/UL Ratio* | {settings["DL/UL Ratio"]} % |  |  |  |\n')

    # Radio status
    message.append(f'\n*Radio status*\n'
                   f'| *Link status* | {radio_status["Link status"]} |  |  |  |  |\n'
                   f'| *Measured Distance*  | {radio_status["Measured Distance"]} |  |  |  |  |\n'
                   f'|  |  |  |  |  |  |\n')
    if settings["Role"] == 'master':
        message.append(f'| *Role* | Master (Local) |  |  | Slave (Remote)|  |\n')
    else:
        message.append(f'| *Role* | Master (Remote) |  |  | Slave (Local)|  |\n')
    message.append(f'|  | +To slave+ |  |  | +To master+ |  |\n'
                   f'| *Tx Frequency* | {downlink["Frequency"]} MHz |  |  '
                   f'| {uplink["Frequency"]} MHz |  |\n'
                   f'|  | _Stream 0_ | _Stream 1_ |  | _Stream 0_ | _Stream 1_ |\n'
                   f'| *Tx Power* | {downlink["Stream 0"]["Tx Power"]} dBm '
                   f'| {downlink["Stream 1"]["Tx Power"]} dBm |  '
                   f'| {uplink["Stream 0"]["Tx Power"]} dBm '
                   f'| {uplink["Stream 1"]["Tx Power"]} dBm  |\n'
                   f'|  | +From slave (Uplink)+ |  |  | +From master (Downlink)+ |  |\n'
                   f'| *Rx RSSI* | {uplink["Stream 0"]["RSSI"]} dBm '
                   f'| {uplink["Stream 1"]["RSSI"]} dBm |  '
                   f'| {downlink["Stream 0"]["RSSI"]} dBm '
                   f'| {downlink["Stream 1"]["RSSI"]} dBm |\n'
                   f'| *Rx EVM* | {uplink["Stream 0"]["EVM"]} dB '
                   f'| {uplink["Stream 1"]["EVM"]} dB |  '
                   f'| {downlink["Stream 0"]["EVM"]} dB  '
                   f'| {downlink["Stream 1"]["EVM"]} dB |\n'
                   f'| *Rx MCS* | {uplink["Stream 0"]["MCS"]} '
                   f'| {uplink["Stream 1"]["MCS"]} |  '
                   f'| {downlink["Stream 0"]["MCS"]} '
                   f'| {downlink["Stream 1"]["MCS"]} |\n'
                   f'| *Rx ARQ* | {uplink["Stream 0"]["ARQ ratio"]} % '
                   f'| {uplink["Stream 1"]["ARQ ratio"]} % |  '
                   f'| {downlink["Stream 0"]["ARQ ratio"]} % '
                   f'| {downlink["Stream 0"]["ARQ ratio"]} % |\n')

    # Physical interfaces status
    message.append(f'\n*Physical interfaces status*\n'
                   f'| *Ge0* | {ethernet_status["Status"]} |\n')

    # Issues and recommendations
    message.append(f'\n*Issues and recommendations*\n')
    temp = []
    for test in tests:
        temp.append(f'| *{test[0]}* |')
        for result in test[1]:
            temp.append(f' * {result} \n')
        temp.append(' |\n')
    message.append(' '.join(temp))

    temp = []
    for line in message:
        temp.append(unicodedata.normalize('NFKD', line))
    message = temp

    message = ' '.join(message)

    return device.model, device.family, device.subfamily, device.serial_number, device.firmware, message


@timer
def web():
    pass


@timer
def cli():
    pass


logger = logging.getLogger('logger.report_q5')