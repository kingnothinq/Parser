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
    master = radio_status['Master']
    m_c_0 = radio_status['Master']['Carrier 0']
    m_c_1 = radio_status['Master']['Carrier 1']
    slave = radio_status['Slave']
    s_c_0 = radio_status['Slave']['Carrier 0']
    s_c_1 = radio_status['Slave']['Carrier 1']
    ethernet_status = device.ethernet_status
    message = []

    # General
    message.append(f'*General*\n'
                   f'| *Serial Number* | {device.serial_number} |\n'
                   f'| *Model* | {device.model} |\n'
                   f'| *Firmware version* | {device.firmware} |\n')

    # Settings
    message.append(f'\n*Settings*\n'
                   f'| *Role* | {str.capitalize(settings["Role"])} |  |  |  |  |  |  |\n')
    if device.subfamily == 'XG 500':
        message.append(f'| *Frequencies* | Carrier 0 DL - {settings["DL Frequency"]["Carrier 0"]} MHz '
                       f' Carrier 0 UL - {settings["UL Frequency"]["Carrier 0"]} MHz |')
    else:
        message.append(f'| *Frequencies* | Carrier 0 DL - {settings["DL Frequency"]["Carrier 0"]} MHz '
                       f' Carrier 0 UL - {settings["UL Frequency"]["Carrier 0"]} MHz '
                       f' Carrier 1 DL - {settings["DL Frequency"]["Carrier 1"]} MHz '
                       f' Carrier 1 UL - {settings["UL Frequency"]["Carrier 1"]} MHz |')
    message.append(f'  | *Tx Power* | {settings["Tx Power"]} dBm | '
                   f' | *Control Block Boost* | {settings["Control Block Boost"]} |\n'
                   f'| *Bandwidth* | {settings["Bandwidth"]} MHz | '
                   f' | *ATPC* | {settings["ATPC"]} | '
                   f' | *Short CP* | {settings["Short CP"]} |\n'
                   f'| *Frame size* | {settings["Frame size"]} ms | '
                   f' | *AMC Strategy* | {str.capitalize(settings["AMC Strategy"])} | '
                   f' | *IDFS* | {settings["IDFS"]} |\n'
                   f'| *DL/UL Ratio* | {settings["DL/UL Ratio"]} % | '
                   f' | *Max MCS* | {settings["Max MCS"]} | '
                   f' | *Traffic prioritization* | {settings["Traffic prioritization"]} |\n')

    # Radio status
    message.append(f'\n*Radio status*\n'
                   f'| *Link status* | {radio_status["Link status"]} |  |  |  |\n'
                   f'| *Measured Distance* | {radio_status["Measured Distance"]} meters |  |  |  |\n'
                   f'|  |  |  |  |  |\n')
    if device.subfamily == 'XG 500':
        message.append(f'| *Side* | Master | *Role* | {master["Role"]} |  |\n'
                       f'|  | _Carrier 0_ | _Carrier 0_ |  |  |\n'
                       f'| *Tx Frequency* | {m_c_0["Frequency"]} MHz |  |  |  |\n'
                       f'|  | _Stream 0_ | _Stream 1_ |  |  |\n'
                       f'| *Tx Power* | {m_c_0["Stream 0"]["Tx Power"]} dBm '
                       f'| {m_c_0["Stream 1"]["Tx Power"]} dBm |  |  |\n'
                       f'| *Rx RSSI* | {m_c_0["Stream 0"]["RSSI"]} dBm '
                       f'| {m_c_0["Stream 1"]["RSSI"]} dBm |  |  |\n'
                       f'| *Rx CINR* | {m_c_0["Stream 0"]["CINR"]} dB '
                       f'| {m_c_0["Stream 1"]["CINR"]} dB |  |  |\n'
                       f'| *Rx Crosstalk* | {m_c_0["Stream 0"]["Crosstalk"]} dB '
                       f'| {m_c_0["Stream 1"]["Crosstalk"]} dB |  |  |\n'
                       f'| *Rx MCS* | {m_c_0["Stream 0"]["MCS"]} '
                       f'| {m_c_0["Stream 1"]["MCS"]} |  |  |\n'
                       f'| *Rx Errors* | {m_c_0["Stream 0"]["Errors Ratio"]} % '
                       f'| {m_c_0["Stream 1"]["Errors Ratio"]} % |  |  |\n'
                       f'|  |  |  |  |  |\n'
                       f'| *Side* | Slave | *Role* | {slave["Role"]} |  |\n'
                       f'|  | _Carrier 0_ | _Carrier 0_ |  |  |\n'
                       f'| *Tx Frequency* | {s_c_0["Frequency"]} MHz |  |  |  |\n'
                       f'|  | _Stream 0_ | _Stream 1_ |  |  |\n'
                       f'| *Tx Power* | {s_c_0["Stream 0"]["Tx Power"]} dBm '
                       f'| {s_c_0["Stream 1"]["Tx Power"]} dBm |  |  |\n'
                       f'| *Rx RSSI* | {s_c_0["Stream 0"]["RSSI"]} dBm '
                       f'| {s_c_0["Stream 1"]["RSSI"]} dBm |  |  |\n'
                       f'| *Rx CINR* | {s_c_0["Stream 0"]["CINR"]} dB '
                       f'| {s_c_0["Stream 1"]["CINR"]} dB |  |  |\n'
                       f'| *Rx Crosstalk* **| {s_c_0["Stream 0"]["Crosstalk"]} dB '
                       f'| {s_c_0["Stream 1"]["Crosstalk"]} dB |  |  |\n'
                       f'| *Rx MCS* | {s_c_0["Stream 0"]["MCS"]} '
                       f'| {s_c_0["Stream 1"]["MCS"]} |  |  |\n'
                       f'| *Rx Errors* | {s_c_0["Stream 0"]["Errors Ratio"]} % '
                       f'| {s_c_0["Stream 1"]["Errors Ratio"]} % |  |  |\n')
    else:
        message.append(f'| *Side* | Master | *Role* | {master["Role"]} |  |\n'
                       f'|  | _Carrier 0_ | _Carrier 0_ | _Carrier 1_ | _Carrier 1_ |\n'
                       f'| *Tx Frequency* | {m_c_0["Frequency"]} MHz |  | {m_c_1["Frequency"]} MHz |  |\n'
                       f'|  | _Stream 0_ | _Stream 1_ | _Stream 0_ | _Stream 1_ |\n'
                       f'| *Tx Power* | {m_c_0["Stream 0"]["Tx Power"]} dBm '
                       f'| {m_c_0["Stream 1"]["Tx Power"]} dBm '
                       f'| {m_c_1["Stream 0"]["Tx Power"]} dBm '
                       f'| {m_c_1["Stream 1"]["Tx Power"]} dBm |\n'
                       f'| *Rx RSSI* | {m_c_0["Stream 0"]["RSSI"]} dBm '
                       f'| {m_c_0["Stream 1"]["RSSI"]} dBm '
                       f'| {m_c_1["Stream 0"]["RSSI"]} dBm '
                       f'| {m_c_1["Stream 1"]["RSSI"]} dBm |\n'
                       f'| *Rx CINR* | {m_c_0["Stream 0"]["CINR"]} dB '
                       f'| {m_c_0["Stream 1"]["CINR"]} dB '
                       f'| {m_c_1["Stream 0"]["CINR"]} dB '
                       f'| {m_c_1["Stream 1"]["CINR"]} dB |\n'
                       f'| *Rx Crosstalk* | {m_c_0["Stream 0"]["Crosstalk"]} dB '
                       f'| {m_c_0["Stream 1"]["Crosstalk"]} dB '
                       f'| {m_c_1["Stream 0"]["Crosstalk"]} dB '
                       f'| {m_c_1["Stream 1"]["Crosstalk"]} dB |\n'
                       f'| *Rx MCS* | {m_c_0["Stream 0"]["MCS"]} '
                       f'| {m_c_0["Stream 1"]["MCS"]} '
                       f'| {m_c_1["Stream 0"]["MCS"]} '
                       f'| {m_c_1["Stream 1"]["MCS"]} |\n'
                       f'| *Rx Errors* | {m_c_0["Stream 0"]["Errors Ratio"]} % '
                       f'| {m_c_0["Stream 1"]["Errors Ratio"]} % '
                       f'| {m_c_1["Stream 0"]["Errors Ratio"]} % '
                       f'| {m_c_1["Stream 1"]["Errors Ratio"]} % |\n'
                       f'|  |  |  |  |  |\n'
                       f'| *Side* | Slave | *Role* | {slave["Role"]} |  |\n'
                       f'|  | _Carrier 0_ | _Carrier 0_ | _Carrier 1_ | _Carrier 1_ |\n'
                       f'| *Tx Frequency* | {s_c_0["Frequency"]} MHz |  | {s_c_1["Frequency"]} MHz |  |\n'
                       f'|  | _Stream 0_ | _Stream 1_ | _Stream 0_ | _Stream 1_ |\n'
                       f'| *Tx Power* | {s_c_0["Stream 0"]["Tx Power"]} dBm '
                       f'| {s_c_0["Stream 1"]["Tx Power"]} dBm '
                       f'| {s_c_1["Stream 0"]["Tx Power"]} dBm '
                       f'| {s_c_1["Stream 1"]["Tx Power"]} dBm |\n'
                       f'| *Rx RSSI* | {s_c_0["Stream 0"]["RSSI"]} dBm '
                       f'| {s_c_0["Stream 1"]["RSSI"]} dBm '
                       f'| {s_c_1["Stream 0"]["RSSI"]} dBm '
                       f'| {s_c_1["Stream 1"]["RSSI"]} dBm |\n'
                       f'| *Rx CINR* | {s_c_0["Stream 0"]["CINR"]} dB '
                       f'| {s_c_0["Stream 1"]["CINR"]} dB '
                       f'| {s_c_1["Stream 0"]["CINR"]} dB '
                       f'| {s_c_1["Stream 1"]["CINR"]} dB |\n'
                       f'| *Rx Crosstalk* **| {s_c_0["Stream 0"]["Crosstalk"]} dB '
                       f'| {s_c_0["Stream 1"]["Crosstalk"]} dB '
                       f'| {s_c_1["Stream 0"]["Crosstalk"]} dB '
                       f'| {s_c_1["Stream 1"]["Crosstalk"]} dB |\n'
                       f'| *Rx MCS* | {s_c_0["Stream 0"]["MCS"]} '
                       f'| {s_c_0["Stream 1"]["MCS"]} '
                       f'| {s_c_1["Stream 0"]["MCS"]} '
                       f'| {s_c_1["Stream 1"]["MCS"]} |\n'
                       f'| *Rx Errors* | {s_c_0["Stream 0"]["Errors Ratio"]} % '
                       f'| {s_c_0["Stream 1"]["Errors Ratio"]} % '
                       f'| {s_c_1["Stream 0"]["Errors Ratio"]} % '
                       f'| {s_c_1["Stream 1"]["Errors Ratio"]} % |\n')

    # Physical interfaces status
    message.append(f'\n*Physical interfaces status*\n'
                   f'| *Ge0* | {ethernet_status["ge0"]["Status"]} |\n'
                   f'| *Ge1* | {ethernet_status["ge1"]["Status"]} |\n'
                   f'| *SFP* | {ethernet_status["sfp"]["Status"]} |\n')

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

    return device.model, device.family, device.subfamily, device.serial_number, device.firmware, message


@timer
def web():
    pass


@timer
def cli():
    pass


logger = logging.getLogger('logger.report_xg')