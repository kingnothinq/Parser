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
    radio_status = device.radio_status
    master = radio_status['Master']
    m_c_0 = radio_status['Master']['Carrier 0']
    m_c_1 = radio_status['Master']['Carrier 1']
    slave = radio_status['Slave']
    s_c_0 = radio_status['Slave']['Carrier 0']
    s_c_1 = radio_status['Slave']['Carrier 1']
    ethernet_status = device.ethernet_status
    tests = '\n'.join(tests)

    message = f'''
    *General*
    |*Serial Number*|{device.serial_number}|
    |*Model*|{device.model}|
    |*Firmware version*|{device.firmware}|
    
    *Settings*
    |*Role*|{str.capitalize(settings["Role"])}|
    |*Frequencies*|Carrier 0 DL - {settings["DL Frequency"]["Carrier 0"]} MHz
    Carrier 0 UL - {settings["UL Frequency"]["Carrier 0"]} MHz
    Carrier 1 DL - {settings["DL Frequency"]["Carrier 1"]} MHz
    Carrier 1 UL - {settings["UL Frequency"]["Carrier 1"]} MHz|
    |*Bandwidth*|{settings["Bandwidth"]} MHz|
    |*Frame size*|{settings["Frame size"]} ms|
    |*Tx Power*|{settings["Tx Power"]} dBm|
    |*ATPC*|{settings["ATPC"]}|
    |*AMC Strategy*|{str.capitalize(settings["AMC Strategy"])}|
    |*Max MCS*|{settings["Max MCS"]}|
    |*DL/UL Ratio*|{settings["DL/UL Ratio"]} %|
    |*Control Block Boost*|{settings["Control Block Boost"]}|
    |*Short CP*|{settings["Short CP"]}|
    |*IDFS*|{settings["IDFS"]}|
    |*Traffic prioritization*|{settings["Traffic prioritization"]}|
    
    *Radio status*
    |*Link status*|{radio_status["Link status"]}| | | |
    |*Measured Distance*|{radio_status["Measured Distance"]}| | | |
    |---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|
    |*Side*|Master|*Role*|{master["Role"]}| |
    | |_Carrier 0_|_Carrier 0_|_Carrier 1_|_Carrier 1_|
    |*Tx Frequency*| {m_c_0["Frequency"]}| | {m_c_1["Frequency"]}| |
    | |_Stream 0_|_Stream 1_|_Stream 0_|_Stream 1_|
    |*Tx Power*| {m_c_0["Stream 0"]["Tx Power"]}| {m_c_0["Stream 1"]["Tx Power"]}| {m_c_1["Stream 0"]["Tx Power"]}| {m_c_1["Stream 1"]["Tx Power"]}|
    |*Rx RSSI*| {m_c_0["Stream 0"]["RSSI"]}| {m_c_0["Stream 1"]["RSSI"]}| {m_c_1["Stream 0"]["RSSI"]}| {m_c_1["Stream 1"]["RSSI"]}|
    |*Rx CINR*| {m_c_0["Stream 0"]["CINR"]}| {m_c_0["Stream 1"]["CINR"]}| {m_c_1["Stream 0"]["CINR"]}| {m_c_1["Stream 1"]["CINR"]}|
    |*Rx MCS*| {m_c_0["Stream 0"]["MCS"]}| {m_c_0["Stream 1"]["MCS"]}| {m_c_1["Stream 0"]["MCS"]}| {m_c_1["Stream 1"]["MCS"]}|
    |*Rx Errors*| {m_c_0["Stream 0"]["Errors Ratio"]}| {m_c_0["Stream 1"]["Errors Ratio"]}| {m_c_1["Stream 0"]["Errors Ratio"]}| {m_c_1["Stream 1"]["Errors Ratio"]}|
    |---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|
    |*Side*|Slave|*Role*|{slave["Role"]}| |
    | |_Carrier 0_|_Carrier 0_|_Carrier 1_|_Carrier 1_|
    |*Tx Frequency*| {s_c_0["Frequency"]}| | {s_c_1["Frequency"]}| |
    | |_Stream 0_|_Stream 1_|_Stream 0_|_Stream 1_|
    |*Tx Power*| {s_c_0["Stream 0"]["Tx Power"]}| {s_c_0["Stream 1"]["Tx Power"]}| {s_c_1["Stream 0"]["Tx Power"]}| {s_c_1["Stream 1"]["Tx Power"]}|
    |*Rx RSSI*| {s_c_0["Stream 0"]["RSSI"]}| {s_c_0["Stream 1"]["RSSI"]}| {s_c_1["Stream 0"]["RSSI"]}| {s_c_1["Stream 1"]["RSSI"]}|
    |*Rx CINR*| {s_c_0["Stream 0"]["CINR"]}| {s_c_0["Stream 1"]["CINR"]}| {s_c_1["Stream 0"]["CINR"]}| {s_c_1["Stream 1"]["CINR"]}|
    |*Rx MCS*| {s_c_0["Stream 0"]["MCS"]}| {s_c_0["Stream 1"]["MCS"]}| {s_c_1["Stream 0"]["MCS"]}| {s_c_1["Stream 1"]["MCS"]}|
    |*Rx Errors*| {s_c_0["Stream 0"]["Errors Ratio"]}| {s_c_0["Stream 1"]["Errors Ratio"]}| {s_c_1["Stream 0"]["Errors Ratio"]}| {s_c_1["Stream 1"]["Errors Ratio"]}|

    *Physical interfaces status*
    |*Ge0*|{ethernet_status["ge0"]["Status"]}|
    |*Ge1*|{ethernet_status["ge1"]["Status"]}|
    |*SFP*|{ethernet_status["sfp"]["Status"]}|
    
    *Issues and recommendations*
    {tests}
    '''

    return device.model, device.family, device.subfamily, device.serial_number, device.firmware, message


@timer
def web():
    pass


@timer
def cli():
    pass


logger = logging.getLogger('logger.report_xg')